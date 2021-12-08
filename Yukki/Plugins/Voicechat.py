import asyncio
import os
import shutil
import subprocess
from sys import version as pyver

from config import get_queue
from pyrogram import Client, filters
from pyrogram.types import Message

from Yukki import SUDOERS, app, db_mem, userbot
from Yukki.Database import get_active_chats, is_active_chat
from Yukki.Decorators.checker import checker, checkerCB
from Yukki.Inline import primary_markup

from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)

loop = asyncio.get_event_loop()

__MODULE__ = "Join/Leave"
__HELP__ = """

**Note:**
Only for Sudo Users


/joinassistant [Chat Username or Chat ID]
- Qrupa köməkçiyə qoşulun.

/leaveassistant [Chat Username or Chat ID]
- Assistent xüsusi qrupdan ayrılacaq.

/leavebot [Chat Username or Chat ID]
- Bot xüsusi söhbəti tərk edəcək.

"""



@app.on_callback_query(filters.regex("pr_go_back_timer"))
async def pr_go_back_timer(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, user_id = callback_request.split("|")
    if await is_active_chat(CallbackQuery.message.chat.id):
        if db_mem[CallbackQuery.message.chat.id]["videoid"] == videoid:
            dur_left = db_mem[CallbackQuery.message.chat.id]["left"]
            duration_min = db_mem[CallbackQuery.message.chat.id]["total"]
            buttons = primary_markup(videoid, user_id, dur_left, duration_min)
            await CallbackQuery.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(buttons))
             
    
    

@app.on_callback_query(filters.regex("timer_checkup_markup"))
async def timer_checkup_markup(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, user_id = callback_request.split("|")
    if await is_active_chat(CallbackQuery.message.chat.id):
        if db_mem[CallbackQuery.message.chat.id]["videoid"] == videoid:
            dur_left = db_mem[CallbackQuery.message.chat.id]["left"]
            duration_min = db_mem[CallbackQuery.message.chat.id]["total"]
            return await CallbackQuery.answer(
                f"Remaining {dur_left} out of {duration_min} Mins.",
                show_alert=True,
            )
        return await CallbackQuery.answer(f"Oynamır.", show_alert=True)
    else:
        return await CallbackQuery.answer(
            f"Aktiv Səsli Söhbət yoxdur", show_alert=True
        )


@app.on_message(filters.command("queue"))
async def activevc(_, message: Message):
    global get_queue
    if await is_active_chat(message.chat.id):
        mystic = await message.reply_text("Zəhmət olmasa gözləyin... Növbə əldə edilir..")
        dur_left = db_mem[message.chat.id]["left"]
        duration_min = db_mem[message.chat.id]["total"]
        got_queue = get_queue.get(message.chat.id)
        if not got_queue:
            await mystic.edit(f"Növbədə heç nə yoxdur")
        fetched = []
        for get in got_queue:
            fetched.append(get)

        ### Results
        current_playing = fetched[0][0]
        user_name = fetched[0][1]

        msg = "**Queued List**\n\n"
        msg += "**Currently Oynayan:**"
        msg += "\n▶️" + cari_oyun[:30]
        msg += f"\n   ╚By:- {user_name}"
        msg += f"\n   ╚Duration:- Remaining `{dur_left}` out of `{duration_min}` Mins."
        fetched.pop(0)
        if fetched:
            msg += "\n\n"
            msg += "**Növbəti Növbədə:**"
            for song in fetched:
                name = song[0][:30]
                usr = song[1]
                dur = song[2]
                msg += f"\n⏸️{ad}"
                msg += f"\n   ╠Duration : {dur}"
                msg += f"\n   ╚Requested by : {usr}\n"
        if len(msg) > 4096:
            await mystic.delete()
            filename = "queue.txt"
            with open(filename, "w+", encoding="utf8") as out_file:
                out_file.write(str(msg.strip()))
            await message.reply_document(
                document=filename,
                caption=f"**ÇIXIŞ:**\n\n`Növbəyə qoyulmuş Siyahı`",
                quote=False,
            )
            os.remove(filename)
        else:
            await mystic.edit(msg)
    else:
        await message.reply_text(f"Növbədə heç nə yoxdur")


@app.on_message(filters.command("activevc") & filters.user(SUDOERS))
async def activevc(_, message: Message):
    served_chats = []
    try:
        chats = await get_active_chats()
        for chat in chats:
            served_chats.append(int(chat["chat_id"]))
    except Exception as e:
        await message.reply_text(f"**Xəta:-** {e}")
    text = ""
    j = 0
    for x in served_chats:
        try:
            title = (await app.get_chat(x)).title
        except Exception:
            title = "Private Group"
        if (await app.get_chat(x)).username:
            user = (await app.get_chat(x)).username
            text += (
                f"<b>{j + 1}.</b>  [{title}](https://t.me/{user})[`{x}`]\n"
            )
        else:
            text += f"<b>{j + 1}. {title}</b> [`{x}`]\n"
        j += 1
    if not text:
        await message.reply_text("Aktiv Səsli Söhbət yoxdur")
    else:
        await message.reply_text(
            f"**Aktiv səsli söhbətlər:-**\n\n{text}",
            disable_web_page_preview=True,
        )


@app.on_message(filters.command("joinassistant") & filters.user(SUDOERS))
async def basffy(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**İstifadəsi:**\n/joinassistant [Söhbət İstifadəçi adı və ya Söhbət ID-si]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        userbot.join_cha-nı gözləyint(chat)
    except Exception as e:
        await message.reply_text(f"Uğursuz\n**Mümkün səbəb** ola bilər:{e}")
        return
    await message.reply_text("qoşuldu.")


@app.on_message(filters.command("leavebot") & filters.user(SUDOERS))
async def baaaf(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**İstifadə:**\n/leavebot [Söhbət İstifadəçi adı və ya Söhbət ID-si]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        await app.leave_chat(chat)
    except Exception as e:
        await message.reply_text(f"Uğursuz oldu\n**Mümkün səbəb ola bilər**:{e}")
        print(e)
        return
    await message.reply_text("Bot çatı uğurla tərk etdi")


@app.on_message(filters.command("leaveassistant") & filters.user(SUDOERS))
async def baujaf(_, message):
    if len(message.command) != 2:
        await message.reply_text(
            "**İstifadəsi:**\n/buraxmaq [Chat Username or Chat ID]"
        )
        return
    chat = message.text.split(None, 2)[1]
    try:
        await userbot.leave_chat(chat)
    except Exception as e:
        await message.reply_text(f"Failed\n**Mümkün səbəb ola bilər**:{e}")
        return
    await message.reply_text("Left.")
