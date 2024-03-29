import os
import telethon
from telethon.tl.functions.users import GetFullUserRequest
import re, io
from telethon import Button, custom, events
from re import findall
from urllib.parse import quote
from datetime import datetime as stime
import requests
import urllib
from math import ceil
import requests

from telethon import Button, custom, events, functions
from Evie.events import register
import random
from pymongo import MongoClient
import Evie.modules.sql.feds_sql as sql
from Evie.modules.sql.karma_sql import get_couple, save_couple
from Evie.modules.sql.setbio_sql import set_bio, rm_bio, check_bio_status, is_bio, get_all_bio_id
from Evie.modules.sql.setbio_sql import set_bio, rm_bio
from Evie.modules.sql.setbio_sql import SUDO_USERS as boss
from Evie import tbot, OWNER_ID, CMD_HELP, ubot, StartTime, MONGO_DB_URI, BOT_ID, SCREENSHOT_API
import datetime, time
from Evie.function import is_admin, bio

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["evie"]
gbanned = db.gban
blacklist = db.black





async def get_user(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        replied_user = await tbot(GetFullUserRequest(previous_message.sender_id))
    else:
        user = event.pattern_match.group(1)

        if user.isnumeric():
            user = int(user)

        if not user:
            self_user = await event.get_sender()
            user = self_user.id
        try:
            user_object = await tbot.get_entity(user)
            replied_user = await tbot(GetFullUserRequest(user_object.id))
        except (TypeError, ValueError) as err:
            await event.reply("Failed to get user: unable to getChatMember: Bad Request: user not found")
            return None

    return replied_user

async def detail(replied_user, event):
 try:
    user_id = replied_user.user.id
    first_name = replied_user.user.first_name
    last_name = replied_user.user.last_name
    username = replied_user.user.username
    first_name = (
        first_name.replace("\u2060", "")
    )
    last_name = (
        last_name.replace("\u2060", "") if last_name else None
    )
    username = "@{}".format(username) if username else None

    caption = "<b>User Info:</b> \n"
    caption += f"ID: <code>{user_id}</code> \n"
    caption += f"First Name: {first_name} \n"
    if last_name:
      caption += f"Last Name: {last_name} \n"
    if username:
      caption += f"Username: {username} \n"
    caption += f'Permalink: <a href="tg://user?id={user_id}">link</a>'
    fed_id = sql.get_fed_id(event.chat_id)
    if fed_id:
      info = sql.get_fed_info(fed_id)
      name = info["fname"]
      fban, reason, fbantime = sql.get_fban_user(fed_id, int(user_id))
      if fban:
         caption += f"\n\nThis user has been\nfbanned in the current fed, <code>{name}</code>."
         if not reason == '':
            caption += f"\nReason: `{reason[:20]}`"
         else:
            caption += "\nNo reason specified."
    if is_bio(replied_user.user.id):
         smx = boss[replied_user.user.id]
         caption += f"\n\n<b>What others say:</b>\n{smx}"
    a = blacklist.find({})
    for i in a:
         if user_id == i["user"]:
            caption += "\n\n<b>Blacklisted:</b> Yes"
    chats = gbanned.find({})
    for i in chats:
         if user_id == i["user"]:
           caption += "\n\n<b>Globally Banned:</b> Yes"
    return caption
 except Exception as e:
        print(e)


def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)

    return ping_time

@register(pattern="^/setbio ?(.*)")
async def bio(event):
  replied_user = await event.get_reply_message()
  user_id = replied_user.sender_id
  input = event.pattern_match.group(1)
  if event.sender_id == OWNER_ID:
    if input == "None":
       rm_bio(user_id)
       await event.reply(f"Removed Bio of {replied_user.sender.first_name}")
       return
    set_bio(user_id, input)
    await event.reply(f"Updated {replied_user.sender.first_name}'s bio!")
  else:
   if event.sender_id == user_id:
     await event.reply("Are you looking to change your own ... ?? That 's it.")
     return
   else:
     set_bio(user_id, input)
     await event.reply(f"Updated {replied_user.sender.first_name}'s Bio")
     

@register(pattern="^/info(?: |$)(.*)")
async def who(event):
    replied_user = await get_user(event)
    try:
        caption = await detail(replied_user, event)
    except AttributeError:
        event.edit("Could not fetch info of that user.")
        return
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    await event.reply(caption, parse_mode="html")


@register(pattern="^/(ping|ping@MissEvie_Robot)")
async def ping(event):
    
    start_time = datetime.datetime.now()
    message = await event.reply("Pinging.")
    end_time = datetime.datetime.now()
    pingtime = end_time - start_time
    telegram_ping = str(round(pingtime.total_seconds(), 2)) + "s"
    uptime = get_readable_time((time.time() - StartTime))
    await message.edit(
        "PONG !\n"
        "<b>Time Taken:</b> <code>{}</code>\n"
        "<b>Service uptime:</b> <code>{}</code>".format(telegram_ping, uptime),
        parse_mode="html",
    )


@ubot.on(events.NewMessage(pattern="!ping"))
async def ubot(event):
    if not event.sender_id == OWNER_ID:
        return
    if event.fwd_from:
        return
    start_time = datetime.datetime.now()
    message = await event.edit("Pinging.")
    end_time = datetime.datetime.now()
    pingtime = end_time - start_time
    await message.edit("Pinging..")
    telegram_ping = str(round(pingtime.total_seconds(), 2)) + "s"
    uptime = get_readable_time((time.time() - StartTime))
    await message.edit(
        "PONG !\n"
        "<b>Time Taken:</b> <code>{}</code>\n"
        "<b>Service uptime:</b> <code>{}</code>".format(telegram_ping, uptime),
        parse_mode="html",
    )
    

"""RoseLoverX"""
from telethon import events
from telethon.tl import functions
from telethon.tl import types
import asyncio

async def inline_query(client, bot, query):
    from telethon import custom
    #RoseLoverX
    return custom.InlineResults(
        client,
        await client(
            functions.messages.GetInlineBotResultsRequest(
                bot=bot,
                peer="me",
                query=query,
                offset="",
                geo_point=types.InputGeoPointEmpty(),
            )
        ),
    )
@register(pattern="^/music (.*)")
async def lybot(event):
   k = event.pattern_match.group(1)
   async with tbot.conversation("@roseloverx") as bot_conv:
      response = bot_conv.wait_event(
                events.NewMessage(incoming=True, from_users="@RoseLoverx")
            )
      await (await inline_query(ubot, "@lybot", k))[0].click("@MissEvie_Robot")
      response = await response
      await response.forward_to(event.chat_id)
      await response.delete()
#RoseLoverX

@register(pattern="^/gey ?(.*)")
async def gey(event):
   m = event.pattern_match.group(1)
   from telethon.tl.functions.users import GetFullUserRequest
   if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        replied_user = await tbot(GetFullUserRequest(previous_message.sender_id))
        k = replied_user.user.first_name
   elif m:
        k = m
   else:
      sender = await event.get_sender()
      fname = sender.first_name
      k = fname
   async with tbot.conversation("@roseloverx") as bot_conv:
      response = bot_conv.wait_event(
                events.NewMessage(incoming=True, from_users="@RoseLoverx")
            )
      await (await inline_query(ubot, "@HowGayBot", k))[0].click("@MissEvie_Robot")
      response = await response
      await asyncio.sleep(1)
      await tbot.send_message(event.chat_id, response.text)

@register(pattern="^/betagey ?(.*)")
async def bgay(event):
   m = event.pattern_match.group(1)
   from telethon.tl.functions.users import GetFullUserRequest
   if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        replied_user = await tbot(GetFullUserRequest(previous_message.sender_id))
        k = replied_user.user.first_name
   elif m:
        k = m
   else:
      sender = await event.get_sender()
      fname = sender.first_name
      k = fname
   async with ubot.conversation("@Gayroebot") as bot_conv:
      await bot_conv.send_message("/gay")
      response = await bot_conv.get_response()
      s = response.text.replace("◡̈⃝RoseLoverX", k)
      p = s.replace("*", "")
      j = p.replace(k, "")
      gey = j.replace("tg://user?id=1221693726", "")
      uf = gey.replace("[]()", "")
      await event.reply(f"{k} {uf}")



@register(pattern="^/shazam$")
async def _(event):
 try:
    if event.is_group:
      if not await is_admin(event, event.sender_id):
       return
    if event.fwd_from:
        return
    if not event.reply_to_msg_id:
        await event.reply("Reply to an audio message.")
        return
    reply_message = await event.get_reply_message()
    stt = await event.reply("Identifying the song.")
    tmp = './'
    dl = await tbot.download_media(
            reply_message,
            tmp)
    chat = "@auddbot"
    await stt.edit("Identifying the song...")
    async with ubot.conversation(chat) as conv:
        try:
            await conv.send_file(dl)
            check = await conv.get_response()
            if not check.text.startswith("Audio received"):
                return await stt.edit("An error while identifying the song. Try to use a 5-10s long audio message.")
            await stt.edit("Wait just a sec...")
            result = await conv.get_response()
            await ubot.send_read_acknowledge(conv.chat_id)
        except Exception:
            await stt.edit("Error, Report at @Eviesupport")
            return
    namem = f"Song Name : {result.text.splitlines()[0]}\
        \n\nDetails : {result.text.splitlines()[2]}"
    await stt.edit(namem)
 except Exception as e:
      await event.reply(e)

def dt():
    now = stime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(' ')
    return dt_list


def dt_tom():
    a = str(int(dt()[0].split('/')[0]) + 1)+"/" + \
        dt()[0].split('/')[1]+"/" + dt()[0].split('/')[2]
    return a

@tbot.on(events.NewMessage(pattern="^[!/]couple$"))
async def kk(event):
  if event.is_private:
    return await event.reply("This command is group specific")
  today = str(dt()[0])
  tomorrow = str(dt_tom())
  chat_id = event.chat_id
  is_selected = await get_couple(chat_id, today)
  if not is_selected:
      list_of_users = []
      async for i in tbot.iter_participants(chat_id):
           list_of_users.append(i.id)
      if len(list_of_users) < 2:
           await event.reply("Not enough users")
           return
      c1_id = random.choice(list_of_users)
      c2_id = random.choice(list_of_users)
      while c1_id == c2_id:
            c1_id = random.choice(list_of_users)
      arg = await tbot.get_entity(int(c2_id))
      c1_mention = arg.first_name
      gra = await tbot.get_entity(int(c1_id))
      c2_mention = gra.first_name
      couple_selection_message = f"""**Couple of the day:**
[{c1_mention}](tg://user?id={c2_id}) + [{c2_mention}](tg://user?id={c1_id}) = ❤️

__New couple of the day may be chosen at 12AM {tomorrow}__"""
      await tbot.send_message(event.chat_id, couple_selection_message)
      couple = {
                "c1_id": c1_id,
                "c2_id": c2_id
            }
      await save_couple(chat_id, today, couple)
  elif is_selected:
            c1_id = int(is_selected['c1_id'])
            c2_id = int(is_selected['c2_id'])
            try:
              gra = await tbot.get_entity(int(c1_id))
              c1_name = gra.first_name
            except:
              c1_name = c1_id
            try:
              arg = await tbot.get_entity(int(c2_id))
              c2_name = arg.first_name
            except:
              c2_name = c2_id
            couple_selection_message = f"""Couple of the day:
[{c1_name}](tg://user?id={c1_id}) + [{c2_name}](tg://user?id={c2_id}) = ❤️


__New couple of the day may be chosen at 12AM {tomorrow}__"""
            buttons= [Button.inline('Gey🌈', data='pro'), Button.inline('Lesbo👩‍❤️‍💋‍👩', data='leb')]
            await tbot.send_message(
                event.chat_id,
                couple_selection_message,
                buttons=buttons
            )

file_help = os.path.basename(__file__)
file_help = file_help.replace(".py", "")
file_helpo = file_help.replace("_", " ")

__help__ = """
 - /ping: ping the bot
 - /music: sends the requested Music
 - /gey: get geyness
 - /shazam: gets info about the given audio
 
**Help for Karma Module:**
[UPVOTE] - Use upvote keywords like "+", "+1", "thanks" etc to upvote a message.
[DOWNVOTE] - Use downvote keywords like "-", "-1", etc to downvote a message.
Reply to a message with /karma to check a user's karma
Send /karma without replying to any message to chek karma list of top 10 users
"""
CMD_HELP.update({file_helpo: [file_helpo, __help__]})
