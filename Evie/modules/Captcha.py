from Evie import tbot, CMD_HELP, MONGO_DB_URI
import os, asyncio, re
from telethon import Button, events
from Evie.function import gen_captcha, is_admin
from Evie.events import register
from captcha.image import ImageCaptcha
image_captcha = ImageCaptcha(width = 400, height = 270)
from random import shuffle
import random
from pyrogram import emoji
from pymongo import MongoClient
client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["evie"]
captcha = db.capta
welcome = db.wlc

from Evie.modules.sql.welcome_sql import get_current_welcome_settings

maths = 2
from telethon.tl.types import ChatBannedRights
from telethon.tl.functions.channels import EditBannedRequest

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

def get_chat(id):
    return captcha.find_one({"id": id})

async def kick_restricted_after_delay(delay, event, user_id):
    await asyncio.sleep(delay)
    k = await tbot.get_permissions(event.chat_id, user_id)
    if not k.is_banned:
      return
    await event.delete()
    await tbot.kick_participant(event.chat_id, user_id)

@tbot.on(events.ChatAction())  # pylint:disable=E0602
async def _(event):
  if not event.user_joined:
          return
  user_id = event.user_id
  chats = captcha.find({})
  type = None
  mode = None
  time = None
  for c in chats:
       if event.chat_id == c["id"]:
          type = c["type"]
          time = c["time"]
          mode = c["mode"]
  if mode == None or mode == "off":
      return
  if not type == None:
   if type == "multibutton":
      return await multibutton(event)
   elif type == "math":
      return await math(event)
   elif type == "button":
      return await button(event)
   elif type == "text":
      return await text(event)
  else:
    return


async def multibutton(event):
  user_id = event.user_id
  chats = captcha.find({})
  for c in chats:
       if event.chat_id == c["id"]:
          type = c["type"]
          time = c["time"]
  a_user = await event.get_user()
  mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
  cws = get_current_welcome_settings(event.chat_id)
  if cws:
     wlc = cws.custom_welcome_message
     if "|" in wlc:
       wc, options = wlc.split("|")
       wc = wc.strip()
     else:
       wc = wlc
     a_user = await event.get_user()
     title = event.chat.title
     mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
     first = a_user.first_name
     last = a_user.last_name
     if last:
         fullname = f"{first} {last}"
     else:
         fullname = first
     userid = a_user.id
     current_saved_welcome_message = wc
     text = current_saved_welcome_message.format(
                                mention=mention,
                                title=title,
                                first=first,
                                last=last,
                                fullname=fullname,
                                userid=userid,
                            )
     text += "\n\n**Captcha Verification**"
  else:
   text = f"Hey {event.user.first_name} Welcome to {event.chat.title}!"
  text += f"\n\nClick on the button which include this emoji {emoji.CHECK_MARK_BUTTON}."
  keyboard = [
            Button.inline(
                f"{emoji.BRAIN}",
                data=f'pep-{a_user.id}'
            ),
            Button.inline(
                f"{emoji.CHECK_MARK_BUTTON}",
                data=f'pro-{a_user.id}'
            ),
            Button.inline(
                f"{emoji.CROSS_MARK}",
                data=f"fk-{a_user.id}"
            ),
            Button.inline(
                f"{emoji.ROBOT}",
                data=f'yu-{a_user.id}'
            )
        ]
  shuffle(keyboard)
  button_message = await event.reply(
            text,
            buttons=keyboard
        )
  WELCOME_DELAY_KICK_SEC = time
  try:
    await tbot(EditBannedRequest(event.chat_id, user_id, MUTE_RIGHTS))
  except:
    pass
  if time:
   if not time == 0:
    asyncio.create_task(kick_restricted_after_delay(
            WELCOME_DELAY_KICK_SEC, event, user_id))
    await asyncio.sleep(0.5)


async def math(event):
  user_id = event.user_id
  chats = captcha.find({})
  for c in chats:
       if event.chat_id == c["id"]:
          type = c["type"]
          time = c["time"]
  try:
    await tbot(EditBannedRequest(event.chat_id, user_id, MUTE_RIGHTS))
  except:
    pass
  cws = get_current_welcome_settings(event.chat_id)
  if cws:
     wlc = cws.custom_welcome_message
     if "|" in wlc:
       wc, options = wlc.split("|")
       wc = wc.strip()
     else:
       wc = wlc
     a_user = await event.get_user()
     title = event.chat.title
     mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
     first = a_user.first_name
     last = a_user.last_name
     if last:
         fullname = f"{first} {last}"
     else:
         fullname = first
     userid = a_user.id
     text = wc.format(
                                mention=mention,
                                title=title,
                                first=first,
                                last=last,
                                fullname=fullname,
                                userid=userid,
                            )
     text += "\n\n**Captcha Verification**🤖"
  else:
   text = f"Hey {event.user.first_name} Welcome to {event.chat.title}!"
  buttons = Button.url("Click here to prove you are human", "t.me/MissEvie_Robot?start=math_{}".format(event.chat_id))
  await event.reply(text, buttons=keyboard)
  WELCOME_DELAY_KICK_SEC = time
  if time:
   if not time == 0:
    asyncio.create_task(kick_restricted_after_delay(
            WELCOME_DELAY_KICK_SEC, event, user_id))
    await asyncio.sleep(0.5)

@register(pattern="^/start math_(.*)")
async def h(event):
  if not event.is_private:
   return
  chat = int(event.pattern_match.group(1))
  x = random.randint(1,100)
  y = random.randint(1,100)
  a = x + y
  d = random.randint(1, 100)
  b = random.randint(1, 100)
  c = random.randint(1, 100)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='sikle_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='babe_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='nide_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='nipa_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  await asyncio.sleep(0.5)
  await tbot.send_message(event.chat_id, f"\n**Human Verification:**\n\nWhat is the sum of **{x} + {y}?**\n\nChoose the correct option from Below to get verified.💸", buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"sikle(\_(.*))"))
async def bak(event):
 tata = event.pattern_match.group(1)
 data = tata.decode()
 chat_id = int(data.split("_", 1)[1])
 user_id = event.sender_id
 await event.edit("Successfully Verified✅, now you can message in the chat!", buttons=None)
 try:
   await tbot(EditBannedRequest(chat_id, user_id, UNMUTE_RIGHTS))
 except:
   pass
 global maths
 maths = 3

@tbot.on(events.CallbackQuery(pattern=r"babe(\_(.*))"))
async def bak(event):
  tata = event.pattern_match.group(1)
  data = tata.decode()
  chat = int(data.split("_", 1)[1])
  global maths
  maths -= 1
  if maths == 0:
     maths += 3
     return await event.edit("Your chances are exchausted, verification failed❌", buttons=None)
  await event.answer("Wrong try again!")
  x = random.randint(1,100)
  y = random.randint(1,100)
  a = x + y
  d = random.randint(1, 100)
  b = random.randint(1, 100)
  c = random.randint(1, 100)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='sikle_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='babe_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='nide_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='nipa_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  await asyncio.sleep(0.5)
  await event.edit(f"\n**Human Verification:**\n\nWhat is the sum of **{x} + {y}?**\n\nChoose the correct option from Below to get verified.💸\n**{maths}** Chances Left!", buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"nide(\_(.*))"))
async def bak(event):
  tata = event.pattern_match.group(1)
  data = tata.decode()
  chat = int(data.split("_", 1)[1])
  global maths
  maths -= 1
  if maths == 0:
     maths += 3
     return await event.edit("Your chances are exchausted, verification failed❌", buttons=None)
  await event.answer("Wrong try again!")
  x = random.randint(1,100)
  y = random.randint(1,100)
  a = x + y
  d = random.randint(1, 100)
  b = random.randint(1, 100)
  c = random.randint(1, 100)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='sikle_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='babe_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='nide_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='nipa_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  await asyncio.sleep(0.5)
  await event.edit(f"\n**Human Verification:**\n\nWhat is the sum of **{x} + {y}?**\n\nChoose the correct option from Below to get verified.💸\n**{maths}** Chances Left!", buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"nipa(\_(.*))"))
async def bak(event):
  tata = event.pattern_match.group(1)
  data = tata.decode()
  chat = int(data.split("_", 1)[1])
  global maths
  maths -= 1
  if maths == 0:
     maths += 3
     return await event.edit("Your chances are exchausted, verification failed❌", buttons=None)
  await event.answer("Wrong try again!")
  x = random.randint(1,100)
  y = random.randint(1,100)
  a = x + y
  d = random.randint(1, 100)
  b = random.randint(1, 100)
  c = random.randint(1, 100)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='sikle_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='babe_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='nide_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='nipa_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  await asyncio.sleep(0.5)
  await event.edit(f"\n**Human Verification:**\n\nWhat is the sum of **{x} + {y}?**\n\nChoose the correct option from Below to get verified.💸\n**{maths}** Chances Left!", buttons=keyboard)


async def text(event):
  user_id = event.user_id
  chats = captcha.find({})
  for c in chats:
       if event.chat_id == c["id"]:
          type = c["type"]
          time = c["time"]
  try:
    await tbot(EditBannedRequest(event.chat_id, user_id, MUTE_RIGHTS))
  except:
    pass
  cws = get_current_welcome_settings(event.chat_id)
  if cws:
     a_user = await event.get_user()
     title = event.chat.title
     mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
     first = a_user.first_name
     last = a_user.last_name
     if last:
         fullname = f"{first} {last}"
     else:
         fullname = first
     userid = a_user.id
     current_saved_welcome_message = cws.custom_welcome_message
     text = current_saved_welcome_message.format(
                                mention=mention,
                                title=title,
                                first=first,
                                last=last,
                                fullname=fullname,
                                userid=userid,
                            )
     text += "\n\n**Captcha Verification**"
  else:
   text = f"Hey {event.user.first_name} Welcome to {event.chat.title}!"
  buttons = Button.url("Click here to prove you are human", "t.me/MissEvie_Robot?start=captcha_{}".format(event.chat_id))
  await event.reply(text, buttons=buttons)
  WELCOME_DELAY_KICK_SEC = time
  if time:
   if not time == 0:
    asyncio.create_task(kick_restricted_after_delay(
            WELCOME_DELAY_KICK_SEC, event, user_id))
    await asyncio.sleep(0.5)

chance = 3
 
@register(pattern="^/start captcha_(.*)")
async def h(event):
  if not event.is_private:
   return
  chat = int(event.pattern_match.group(1))
  a = gen_captcha(8)
  b = gen_captcha(8)
  c = gen_captcha(8)
  d = gen_captcha(8)
  image = image_captcha.generate_image(a)
  image_file = "./"+ "captcha.png"
  image_captcha.write(a, image_file)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='pip_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='exec_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='sli_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='paku_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  await asyncio.sleep(0.5)
  await tbot.send_message(event.chat_id, "Please choose the text from image", file='./captcha.png', buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"pip(\_(.*))"))
async def bak(event):
 tata = event.pattern_match.group(1)
 data = tata.decode()
 chat_id = int(data.split("_", 1)[1])
 user_id = event.sender_id
 await event.edit("Successfully Verified✅, now you can message in the chat!", buttons=None)
 try:
   await tbot(EditBannedRequest(chat_id, user_id, UNMUTE_RIGHTS))
 except:
   pass
 global chance
 chance = 3

@tbot.on(events.CallbackQuery(pattern=r"exec(\_(.*))"))
async def bak(event):
  tata = event.pattern_match.group(1)
  data = tata.decode()
  chat = int(data.split("_", 1)[1])
  global chance
  chance -= 1
  await event.answer("Wrong try again!")
  if chance == 0:
     chance += 3
     return await event.edit("Your chances are exchausted, verification failed❌", buttons=None)
  a = gen_captcha(8)
  b = gen_captcha(8)
  c = gen_captcha(8)
  d = gen_captcha(8)
  image = image_captcha.generate_image(a)
  image_file = "./"+ "captcha.png"
  image_captcha.write(a, image_file)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='pip_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='exec_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='sli_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='paku_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  shuffle(keyboard)
  text = f"Try again you have {chance} chances left"
  await event.edit(text, file="./captcha.png", buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"sli(\_(.*))"))
async def bak(event):
  tata = event.pattern_match.group(1)
  data = tata.decode()
  chat = int(data.split("_", 1)[1])
  global chance
  chance -= 1
  await event.answer("Wrong try again❌")
  if chance == 0:
     chance += 3
     return await event.edit("Your chances are exchausted, verification failed❌", buttons=None)
  a = gen_captcha(8)
  b = gen_captcha(8)
  c = gen_captcha(8)
  d = gen_captcha(8)
  image = image_captcha.generate_image(a)
  image_file = "./"+ "captcha.png"
  image_captcha.write(a, image_file)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='pip_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='exec_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='sli_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='paku_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  shuffle(keyboard)
  text = f"Try again you have {chance} chances left"
  await event.edit(text, file="./captcha.png", buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"paku(\_(.*))"))
async def bak(event):
  tata = event.pattern_match.group(1)
  data = tata.decode()
  chat = int(data.split("_", 1)[1])
  global chance
  chance -= 1
  await event.answer("Wrong try again❌")
  if chance == 0:
     chance += 3
     return await event.edit("Your chances are exchausted, verification failed❌", buttons=None)
  a = gen_captcha(8)
  b = gen_captcha(8)
  c = gen_captcha(8)
  d = gen_captcha(8)
  image = image_captcha.generate_image(a)
  image_file = "./"+ "captcha.png"
  image_captcha.write(a, image_file)
  keyboard = [
            [Button.inline(
                f"{a}",
                data='pip_{}'.format(chat)
            ),
            Button.inline(
                f"{b}",
                data='exec_{}'.format(chat)
            ),],
            [Button.inline(
                f"{c}",
                data='sli_{}'.format(chat)
            ),
            Button.inline(
                f"{d}",
                data='paku_{}'.format(chat)
            )]
        ]
  shuffle(keyboard)
  text = f"Try again you have {chance} chances left"
  await event.edit(text, file="./captcha.png", buttons=keyboard)


@tbot.on(events.CallbackQuery(pattern=r"fk-(\d+)"))
async def cbot(event):
    user_id = int(event.pattern_match.group(1))
    chat_id = event.chat_id
    if not event.sender_id == user_id:
        await event.answer("You aren't the person whom should be verified.")
        return
    await event.answer("❌ Wrong Try Again!")
    keyboard = [
            Button.inline(
                f"{emoji.BRAIN}",
                data=f"pep-{user_id}"
            ),
            Button.inline(
                f"{emoji.CHECK_MARK_BUTTON}",
                data=f'pro-{user_id}'
            ),
            Button.inline(
                f"{emoji.CROSS_MARK}",
                data=f"fk-{user_id}"
            ),
            Button.inline(
                f"{emoji.ROBOT}",
                data=f'yu-{user_id}'
            )
        ]
    shuffle(keyboard)
    await event.edit(buttons=keyboard)

@tbot.on(events.CallbackQuery(pattern=r"pep-(\d+)"))
async def cbot(event):
    user_id = int(event.pattern_match.group(1))
    chat_id = event.chat_id
    if not event.sender_id == user_id:
        await event.answer("You aren't the person whom should be verified.")
        return
    await event.answer("❌ Wrong Try Again!")
    keyboard = [
            Button.inline(
                f"{emoji.BRAIN}",
                data=f"pep-{user_id}"
            ),
            Button.inline(
                f"{emoji.CHECK_MARK_BUTTON}",
                data=f'pro-{user_id}'
            ),
            Button.inline(
                f"{emoji.CROSS_MARK}",
                data=f"fk-{user_id}"
            ),
            Button.inline(
                f"{emoji.ROBOT}",
                data=f'yu-{user_id}'
            )
        ]
    shuffle(keyboard)
    await event.edit(buttons=keyboard)
    
@tbot.on(events.CallbackQuery(pattern=r"yu-(\d+)"))
async def cbot(event):
    user_id = int(event.pattern_match.group(1))
    chat_id = event.chat_id
    if not event.sender_id == user_id:
        await event.answer("You aren't the person whom should be verified.")
        return
    await event.answer("❌ Wrong Try Again!")
    keyboard = [
            Button.inline(
                f"{emoji.BRAIN}",
                data=f"pep-{user_id}"
            ),
            Button.inline(
                f"{emoji.CHECK_MARK_BUTTON}",
                data=f'pro-{user_id}'
            ),
            Button.inline(
                f"{emoji.CROSS_MARK}",
                data=f"fk-{user_id}"
            ),
            Button.inline(
                f"{emoji.ROBOT}",
                data=f'yu-{user_id}'
            )
        ]
    shuffle(keyboard)
    await event.edit(buttons=keyboard)
  
@tbot.on(events.CallbackQuery(pattern=r"pro-(\d+)"))
async def cbot(event):
    user_id = int(event.pattern_match.group(1))
    chat_id = event.chat_id
    if not event.sender_id == user_id:
        await event.answer("You aren't the person whom should be verified.")
        return
    await event.answer("Verified Successfully ✅")
    await tbot(EditBannedRequest(event.chat_id, user_id, UNMUTE_RIGHTS))
    await event.edit(buttons=None)

@register(pattern="^/captchakicktime ?(.*)")
async def t(event):
 try:
  time = int(event.pattern_match.group(1))
 except:
  return await event.reply("Please Specify in Seconds **For Now**")
 chats = captcha.find({})
 try:
  for c in chats:
      if event.chat_id == c["id"]:
          to_check = get_chat(id=event.chat_id)
          captcha.update_one(
                {
                    "_id": to_check["_id"],
                    "id": to_check["id"],
                    "type": to_check["type"],
                    "time": to_check["time"],
                    "mode": to_check["mode"],
                },
                {"$set": {"time": time}},
            )
          return await event.reply(f"Updated captcha kick time to **{time}s**")
  captcha.insert_one(
        {"id": event.chat_id, "type": 'text', "time": time, "mode": "on"}
    )
  await event.reply(f"Turned on captcha kick time to **{time}s**/nNow new users who don't complete captcha by **{time}s** gets automatically kicked!")
 except Exception as e:
  print(e)
            

@tbot.on(events.NewMessage(pattern=None))
async def babe(event):
 #inline delete
 if not event.chat.username == 'lunabotsupport':
    return
 if await is_admin(event, event.sender_id):
    return
 if not event.via_bot_id == None:
   await event.delete()

async def button(event):
  user_id = event.user_id
  chats = captcha.find({})
  for c in chats:
       if event.chat_id == c["id"]:
          type = c["type"]
          time = c["time"]
  buttons= Button.inline("Click Here to prove you're Human", data=f"check-bot-{user_id}")
  cws = get_current_welcome_settings(event.chat_id)
  if cws:
     a_user = await event.get_user()
     title = event.chat.title
     mention = "[{}](tg://user?id={})".format(a_user.first_name, a_user.id)
     first = a_user.first_name
     last = a_user.last_name
     if last:
         fullname = f"{first} {last}"
     else:
         fullname = first
     userid = a_user.id
     current_saved_welcome_message = cws.custom_welcome_message
     text = current_saved_welcome_message.format(
                                mention=mention,
                                title=title,
                                first=first,
                                last=last,
                                fullname=fullname,
                                userid=userid,
                            )
     text += "\n\n**Captcha Verification**"
  else:
   text = f"Hey {event.user.first_name} Welcome to {event.chat.title}!"
  button_message = await event.reply(
            text,
            buttons=buttons
        )
  try:
    await tbot(EditBannedRequest(event.chat_id, user_id, MUTE_RIGHTS))
  except:
    pass
  WELCOME_DELAY_KICK_SEC = time
  if time:
   if not time == 0:
    asyncio.create_task(kick_restricted_after_delay(
            WELCOME_DELAY_KICK_SEC, event, user_id))
    await asyncio.sleep(0.5)

@tbot.on(events.CallbackQuery(pattern=r"check-bot-(\d+)"))
async def cbot(event):
    user_id = int(event.pattern_match.group(1))
    chat_id = event.chat_id
    if not event.sender_id == user_id:
        await event.answer("You aren't the person whom should be verified.")
        return
    if event.sender_id == user_id:
      try:
            await tbot(EditBannedRequest(chat_id, user_id, UNMUTE_RIGHTS))
      except:
         pass
      await event.answer("Yep you are verified as a human being")
      await event.edit(buttons=None)

@register(pattern="^/captchamode ?(.*)")
async def t(event):
 arg = event.pattern_match.group(1)
 chats = captcha.find({})
 if not await is_admin(event, event.sender_id):
   return await event.reply("Only Admins can execute this command!")
 if not arg:
   for c in chats:
      if event.chat_id == c["id"]:
         type = c["type"]
         time = c["time"]
   if not time:
     time = 0
   if type:
     return await event.reply(f"Current captcha mode is **{type}**")
   else:
     return await event.reply("Captcha is currently off for this Chat")
 if not arg == "button" and not arg == "text" and not arg == "math" and not arg == "multibutton":
   return await event.reply(f"'{arg}' is not a recognised CAPTCHA mode! Try one of: button/multibutton/math/text")
 type = arg
 if type:
  for c in chats:
      if event.chat_id == c["id"]:
          to_check = get_chat(id=event.chat_id)
          captcha.update_one(
                {
                    "_id": to_check["_id"],
                    "id": to_check["id"],
                    "type": to_check["type"],
                    "time": to_check["time"],
                    "mode": to_check["mode"],
                },
                {"$set": {"type": type, "mode": "on"}},
            )
          await event.reply(f"Successfully updated captchamode to **{type}**")
          return
  captcha.insert_one(
        {"id": event.chat_id, "type": type, "time": time}
    )
  await event.reply(f"Successfully set captchamode to **{type}**.")

@tbot.on(events.NewMessage(pattern="^[!/]captcha ?(.*)"))
async def ba(event):
 pro = ["on", "enable", "yes"]
 arg = event.pattern_match.group(1)
 chats = captcha.find({})
 type = None
 time = None
 mode = None
 for c in chats:
      if event.chat_id == c["id"]:
         mode = c["mode"]
         type = c["type"]
         time = c["time"]
       
 if type == None:
    type = "button"
 if not time:
    time = 0
 if arg:
  if arg == "on" or arg == "enable" or arg == "yes":
   if mode:
    if mode == "on":
     return await event.reply("Captcha is already enabled for this chat.")
    elif mode == "off":
     to_check = get_chat(id=event.chat_id)
     captcha.update_one(
                {
                    "_id": to_check["_id"],
                    "id": to_check["id"],
                    "type": to_check["type"],
                    "time": to_check["time"],
                    "mode": to_check["mode"],
                },
                {"$set": {"mode": "on", "type": type, "time": time}},
            )
     return await event.reply(f"Captcha is enabled with mode **{type}**")
   else:
    captcha.insert_one(
        {"id": event.chat_id, "type": "button", "time": 0, "mode": "on"}
    )
    return await event.reply(f"Successfully enabled captcha mode!")
  elif arg == "off" or arg == "disable" or arg == "no":
   if mode:
    if mode == "off":
      return await event.reply("captcha is not enabled here in the first place!")
    elif mode == "on":
     to_check = get_chat(id=event.chat_id)
     captcha.update_one(
                {
                    "_id": to_check["_id"],
                    "id": to_check["id"],
                    "type": to_check["type"],
                    "time": to_check["time"],
                    "mode": to_check["mode"],
                },
                {"$set": {"mode": "off", "type": type, "time": time}},
            )
     return await event.reply(f"Captcha is successfully disabled")
   else:
    captcha.insert_one(
        {"id": event.chat_id, "type": "button", "time": 0, "mode": "on"}
    )
    return await event.reply(f"Successfully disabled captcha mode!")

@register(pattern="^/welcome ?(.*)")
async def q(event):
 try:
  arg = event.pattern_match.group(1)
  if not arg:
   cp = captcha.find({})
   tp = None
   for c in cp:
      if event.chat_id == c["id"]:
         tp = c["type"]
         tym = c["time"]
   if tp:
    calt = "True"
    mode = tp
    if tym:
     set = tym
    else:
     set = "None"
   else:
    calt = "False"
    mode = "None"
    set = "None"
   chats = welcome.find({})
   for c in chats:
    if event.chat_id == c["id"]:
       settings = c["type"]
   if settings == "on":
     wc = "True"
   elif settings == "off":
     wc = "False"
   return await event.reply(f"Current welcome Stats: `{wc}`\n\nCaptcha Status: `{calt}`\nCaptcha Mode: `{mode}`\nCaptcha kicktime: `{set}`\nCaptcha rules: `disabled`")
 except Exception as e:
  await event.reply(f"{e}")

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
CAPTCHA

Some chats get a lot of users joining just to spam. This could be because they're trolls, or part of a spam network.
To slow them down, you could try enabling CAPTCHAs. New users joining your chat will be required to complete a test to confirm that they're real people.'

Admin commands:
- /captcha <yes/no/on/off>: All users that join will need to solve a CAPTCHA. This proves they aren't a bot!
- /captchamode <button/multibutton/math/text>: Choose which CAPTCHA type to use for your chat.
- /captcharules <yes/no/on/off>: Require new users accept the rules before being able to speak in the chat.
- /captchatime <Xw/d/h/m>: Unmute new users after X time. If a user hasn't solved the CAPTCHA yet, they get automatically unmuted after this period.
- /captchakick <yes/no/on/off>: Kick users that haven't solved the CAPTCHA.
- /captchakicktime <Xw/d/h/m>: Set the time after which to kick CAPTCHA'd users.
- /setcaptchatext <text>: Customise the CAPTCHA button.
- /resetcaptchatext: Reset the CAPTCHA button to the default text.

Examples:
- Enable CAPTCHAs
->` /captcha on`
- Change the CAPTCHA mode to text.
->` /captchamode text`
- Enable CAPTCHA rules, forcing users to read the rules before being allowed to speak.
->` /captcharules on`

NOTE:
captchakicktime now only accept time in Seconds, will fix soon.
captchas Work with or without welcome messages being set.
not finsihed writing.
"""

CMD_HELP.update({file_helpo: [file_helpo, __help__]})

