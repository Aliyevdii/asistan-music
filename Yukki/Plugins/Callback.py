
import asyncio
import os
import random
from asyncio import QueueEmpty

from config import get_queue
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream, InputStream

from Yukki import BOT_USERNAME, MUSIC_BOT_NAME, app, db_mem
from Yukki.Core.PyTgCalls import Queues, Yukki
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Database import (_get_playlists, delete_playlist, get_playlist,
                            get_playlist_names, is_active_chat, save_playlist)
from Yukki.Database.queue import (add_active_chat, is_active_chat,
                                  is_music_playing, music_off, music_on,
                                  remove_active_chat)
from Yukki.Decorators.admins import AdminRightsCheckCB
from Yukki.Decorators.checker import checkerCB
from Yukki.Inline import (audio_markup, audio_markup2, download_markup,
                          fetch_playlist, paste_queue_markup, primary_markup)
from Yukki.Utilities.changers import time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.paste import isPreviewUp, paste_queue
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.timer import start_timer
from Yukki.Utilities.youtube import get_yt_info_id

loop = asyncio.get_event_loop()


@app.on_callback_query(filters.regex("forceclose"))
async def forceclose(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "You're not allowed to close this.", show_alert=True
        )
    await CallbackQuery.message.delete()
    await CallbackQuery.answer()


@app.on_callback_query(
    filters.regex(pattern=r"^(pausecb|skipcb|stopcb|resumecb)$")
)
@AdminRightsCheckCB
@checkerCB
async def admin_risghts(_, CallbackQuery):
    global get_queue
    command = CallbackQuery.matches[0].group(1)
    if not await is_active_chat(CallbackQuery.message.chat.id):
        return await CallbackQuery.answer(
            "Nothing is playing on voice chat.", show_alert=True
        )
    chat_id = CallbackQuery.message.chat.id
    if command == "pausecb":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(
                "Music is already Paused", show_alert=True
            )
        await music_off(chat_id)
        await Yukki.pytgcalls.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"???? Voicechat Paused by {CallbackQuery.from_user.mention}!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Paused", show_alert=True)
    if command == "resumecb":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(
                "Music is already Resumed.", show_alert=True
            )
        await music_on(chat_id)
        await Yukki.pytgcalls.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(
            f"???? Voicechat Resumed by {CallbackQuery.from_user.mention}!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Resumed", show_alert=True)
    if command == "stopcb":
        try:
            Queues.clear(chat_id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await Yukki.pytgcalls.leave_group_call(chat_id)
        await CallbackQuery.message.reply_text(
            f"???? Voicechat End/Stopped by {CallbackQuery.from_user.mention}!",
            reply_markup=audio_markup2,
        )
        await CallbackQuery.message.delete()
        await CallbackQuery.answer("Stopped", show_alert=True)
    if command == "skipcb":
        Queues.task_done(chat_id)
        if Queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await CallbackQuery.message.reply_text(
                f"No more music in __Queue__ \n\nLeaving Voice Chat..Button Used By :- {CallbackQuery.from_user.mention}"
            )
            await Yukki.pytgcalls.leave_group_call(chat_id)
            await CallbackQuery.message.delete()
            await CallbackQuery.answer(
                "Skipped. No more music in Queue", show_alert=True
            )
            return
        else:
            videoid = Queues.get(chat_id)["file"]
            got_queue = get_queue.get(CallbackQuery.message.chat.id)
            if got_queue:
                got_queue.pop(0)
            finxx = f"{videoid[0]}{videoid[1]}{videoid[2]}"
            aud = 0
            if str(finxx) != "raw":
                await CallbackQuery.message.delete()
                await CallbackQuery.answer(
                    "Skipped! Playlist Playing....", show_alert=True
                )
                mystic = await CallbackQuery.message.reply_text(
                    f"**{MUSIC_BOT_NAME} Playlist Function**\n\n__Downloading Next Music From Playlist....__\n\nButton Used By :- {CallbackQuery.from_user.mention}"
                )
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                await mystic.edit(
                    f"**{MUSIC_BOT_NAME} Downloader**\n\n**Title:** {title[:50]}\n\n0% ???????????????????????????????????? 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                await Yukki.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            raw_path,
                        ),
                    ),
                )
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(
                    CallbackQuery.message.chat.title
                )
                thumb = await gen_thumb(
                    thumbnail,
                    title,
                    CallbackQuery.from_user.id,
                    theme,
                    chat_title,
                )
                buttons = primary_markup(
                    videoid,
                    CallbackQuery.from_user.id,
                    duration_min,
                    duration_min,
                )
                await mystic.delete()
                mention = db_mem[videoid]["username"]
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"<b>__Skipped Voice Chat__</b>\n\n????<b>__Started Playing:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n???<b>__Duration:__</b> {duration_min} Mins\n????**__Requested by:__** {mention}"
                    ),
                )
                os.remove(thumb)

            else:
                await CallbackQuery.message.delete()
                await CallbackQuery.answer("Skipped!", show_alert=True)
                await Yukki.pytgcalls.change_stream(
                    chat_id,
                    InputStream(
                        InputAudioStream(
                            videoid,
                        ),
                    ),
                )
                afk = videoid
                title = db_mem[videoid]["title"]
                duration_min = db_mem[videoid]["duration"]
                duration_sec = int(time_to_seconds(duration_min))
                mention = db_mem[videoid]["username"]
                videoid = db_mem[videoid]["videoid"]
                if str(videoid) == "smex1":
                    buttons = buttons = audio_markup(
                        videoid,
                        CallbackQuery.from_user.id,
                        duration_min,
                        duration_min,
                    )
                    thumb = "Utils/Telegram.JPEG"
                    aud = 1
                else:
                    _path_ = _path_ = (
                        (str(afk))
                        .replace("_", "", 1)
                        .replace("/", "", 1)
                        .replace(".", "", 1)
                    )
                    thumb = f"cache/{_path_}final.png"
                    buttons = primary_markup(
                        videoid,
                        CallbackQuery.from_user.id,
                        duration_min,
                        duration_min,
                    )
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"<b>__Skipped Voice Chat__</b>\n\n????<b>__Started Playing:__</b> {title} \n???<b>__Duration:__</b> {duration_min} \n????<b>__Requested by:__ </b> {mention}",
                )
            await start_timer(
                videoid,
                duration_min,
                duration_sec,
                final_output,
                CallbackQuery.message.chat.id,
                CallbackQuery.message.from_user.id,
                aud,
            )


@app.on_callback_query(filters.regex("play_playlist"))
async def play_playlist(_, CallbackQuery):
    global get_queue
    loop = asyncio.get_event_loop()
    callback_data = CallbackQuery.data.strip()
    chat_id = CallbackQuery.message.chat.id
    callback_request = callback_data.split(None, 1)[1]
    user_id, smex, type = callback_request.split("|")
    chat_title = CallbackQuery.message.chat.title
    user_id = int(user_id)
    if chat_id not in db_mem:
        db_mem[chat_id] = {}
    if smex == "third":
        _playlist = await get_playlist_names(user_id, type)
        try:
            user = await app.get_users(user_id)
            third_name = user.first_name
        except:
            third_name = "Deleted Account"
    elif smex == "Personal":
        if CallbackQuery.from_user.id != int(user_id):
            return await CallbackQuery.answer(
                "This is not for you! Play your own playlist", show_alert=True
            )
        _playlist = await get_playlist_names(user_id, type)
        third_name = CallbackQuery.from_user.first_name
    elif smex == "Group":
        _playlist = await get_playlist_names(
            CallbackQuery.message.chat.id, type
        )
        user_id = CallbackQuery.message.chat.id
        third_name = chat_title
    else:
        return await CallbackQuery.answer("Error In Playlist.")
    if not _playlist:
        return await CallbackQuery.answer(
            f"This User has no playlist on servers.", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()
        mystic = await CallbackQuery.message.reply_text(
            f"Starting Playlist Of {third_name}.\n\nRequested By:- {CallbackQuery.from_user.first_name}"
        )
        msg = f"Queued Playlist:\n\n"
        j = 0
        for_t = 0
        for_p = 0
        for shikhar in _playlist:
            _note = await get_playlist(user_id, shikhar, type)
            title = _note["title"]
            videoid = _note["videoid"]
            url = f"https://www.youtube.com/watch?v={videoid}"
            duration = _note["duration"]
            if await is_active_chat(chat_id):
                position = await Queues.put(chat_id, file=videoid)
                j += 1
                for_p = 1
                msg += f"{j}- {title[:50]}\n"
                msg += f"Queued Position- {position}\n\n"
                if videoid not in db_mem:
                    db_mem[videoid] = {}
                db_mem[videoid]["username"] = CallbackQuery.from_user.mention
                db_mem[videoid]["chat_title"] = chat_title
                db_mem[videoid]["user_id"] = user_id
                got_queue = get_queue.get(CallbackQuery.message.chat.id)
                title = title
                user = CallbackQuery.from_user.first_name
                duration = duration
                to_append = [title, user, duration]
                got_queue.append(to_append)
            else:
                loop = asyncio.get_event_loop()
                send_video = videoid
                for_t = 1
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                mystic = await mystic.edit(
                    f"**{MUSIC_BOT_NAME} Downloader**\n\n**Title:** {title[:50]}\n\n0% ???????????????????????????????????? 100%"
                )
                downloaded_file = await loop.run_in_executor(
                    None, download, videoid, mystic, title
                )
                raw_path = await convert(downloaded_file)
                try:
                    await Yukki.pytgcalls.join_group_call(
                        chat_id,
                        InputStream(
                            InputAudioStream(
                                raw_path,
                            ),
                        ),
                        stream_type=StreamType().local_stream,
                    )
                except Exception as e:
                    return await mystic.edit(
                        "Error Joining Voice Chat. Make sure Voice Chat is Enabled."
                    )
                theme = await check_theme(chat_id)
                chat_title = await specialfont_to_normal(chat_title)
                thumb = await gen_thumb(
                    thumbnail,
                    title,
                    CallbackQuery.from_user.id,
                    theme,
                    chat_title,
                )
                buttons = primary_markup(
                    videoid,
                    CallbackQuery.from_user.id,
                    duration_min,
                    duration_min,
                )
                await mystic.delete()
                get_queue[CallbackQuery.message.chat.id] = []
                got_queue = get_queue.get(CallbackQuery.message.chat.id)
                title = title
                user = CallbackQuery.from_user.first_name
                duration = duration_min
                to_append = [title, user, duration]
                got_queue.append(to_append)
                await music_on(chat_id)
                await add_active_chat(chat_id)
                cap = f"????<b>__Playing:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n????<b>__Info:__</b> [Get Additional Information](https://t.me/{BOT_USERNAME}?start=info_{videoid})\n????**__Requested by:__** {CallbackQuery.from_user.mention}"
                final_output = await CallbackQuery.message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=cap,
                )
                os.remove(thumb)
        await mystic.delete()
        if for_p == 1:
            m = await CallbackQuery.message.reply_text(
                "Pasting Queued Playlist to Bin"
            )
            link = await paste_queue(msg)
            preview = link + "/preview.png"
            url = link + "/index.txt"
            buttons = paste_queue_markup(url)
            if await isPreviewUp(preview):
                await CallbackQuery.message.reply_photo(
                    photo=preview,
                    caption=f"This is Queued Playlist of {third_name}.\n\nPlayed by :- {CallbackQuery.from_user.mention}",
                    quote=False,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                await m.delete()
            else:
                await CallbackQuery.message.reply_text(
                    text=msg, reply_markup=audio_markup2
                )
                await m.delete()
        else:
            await CallbackQuery.message.reply_text(
                "Only 1 Music in Playlist.. No more music to add in queue."
            )
        if for_t == 1:
            await start_timer(
                send_video,
                duration_min,
                duration_sec,
                final_output,
                CallbackQuery.message.chat.id,
                CallbackQuery.message.from_user.id,
                0,
            )


@app.on_callback_query(filters.regex("add_playlist"))
async def group_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    videoid, type, genre = callback_request.split("|")
    if type == "Personal":
        user_id = CallbackQuery.from_user.id
    elif type == "Group":
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "You don't have the required permission to perform this action.\nPermission: MANAGE VOICE CHATS",
                show_alert=True,
            )
        user_id = CallbackQuery.message.chat.id
    _count = await get_playlist_names(user_id, genre)
    if not _count:
        sex = await CallbackQuery.message.reply_text(
            f"Welcome To {MUSIC_BOT_NAME}'s Playlist Feature.\n\nGenerating Your  Playlist In Database...Please wait.\n\nGenre:- {genre}"
        )
        await asyncio.sleep(2)
        await sex.delete()
        count = len(_count)
    else:
        count = len(_count)
    count = int(count)
    if count == 50:
        return await CallbackQuery.answer(
            "Sorry! You can only have 50 music in a playlist.",
            show_alert=True,
        )
    loop = asyncio.get_event_loop()
    await CallbackQuery.answer()
    title, duration_min, duration_sec, thumbnail = get_yt_info_id(videoid)
    _check = await get_playlist(user_id, videoid, genre)
    title = title[:50]
    if _check:
        return await CallbackQuery.message.reply_text(
            f"{CallbackQuery.from_user.mention}, Its already in the Playlist!"
        )
    assis = {
        "videoid": videoid,
        "title": title,
        "duration": duration_min,
    }
    await save_playlist(user_id, videoid, assis, genre)
    Name = CallbackQuery.from_user.first_name
    return await CallbackQuery.message.reply_text(
        f"Added to {type}'s {genre} Playlist by {CallbackQuery.from_user.mention}"
    )


@app.on_callback_query(filters.regex("check_playlist"))
async def check_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, genre = callback_request.split("|")
    if type == "Personal":
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
    elif type == "Group":
        user_id = CallbackQuery.message.chat.id
        user_name = CallbackQuery.message.chat.title
    _playlist = await get_playlist_names(user_id, genre)
    if not _playlist:
        return await CallbackQuery.answer(
            f"No {genre} Playlist on servers. Try adding musics in playlist.",
            show_alert=True,
        )
    else:
        j = 0
        await CallbackQuery.answer()
        await CallbackQuery.message.delete()
        msg = f"Fetched Playlist:\n\n"
        for shikhar in _playlist:
            j += 1
            _note = await get_playlist(user_id, shikhar, genre)
            title = _note["title"]
            duration = _note["duration"]
            msg += f"{j}- {title[:60]}\n"
            msg += f"    Duration- {duration} Min(s)\n\n"
        m = await CallbackQuery.message.reply_text("Pasting Playlist to Bin")
        link = await paste_queue(msg)
        preview = link + "/preview.png"
        url = link + "/index.txt"
        buttons = fetch_playlist(
            user_name, type, genre, CallbackQuery.from_user.id, url
        )
        if await isPreviewUp(preview):
            await CallbackQuery.message.reply_photo(
                photo=preview,
                caption=f"This is Playlist of {user_name}.",
                quote=False,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            await m.delete()
        else:
            await CallbackQuery.message.reply_text(
                text=msg, reply_markup=audio_markup2
            )
            await m.delete()


@app.on_callback_query(filters.regex("delete_playlist"))
async def del_playlist(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    type, genre = callback_request.split("|")
    if str(type) == "Personal":
        user_id = CallbackQuery.from_user.id
        user_name = CallbackQuery.from_user.first_name
    elif str(type) == "Group":
        a = await app.get_chat_member(
            CallbackQuery.message.chat.id, CallbackQuery.from_user.id
        )
        if not a.can_manage_voice_chats:
            return await CallbackQuery.answer(
                "You don't have the required permission to perform this action.\nPermission: MANAGE VOICE CHATS",
                show_alert=True,
            )
        user_id = CallbackQuery.message.chat.id
        user_name = CallbackQuery.message.chat.title
    _playlist = await get_playlist_names(user_id, genre)
    if not _playlist:
        return await CallbackQuery.answer(
            "Group has no Playlist on Bot's Server", show_alert=True
        )
    else:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
        for shikhar in _playlist:
            await delete_playlist(user_id, shikhar, genre)
    await CallbackQuery.message.reply_text(
        f"Successfully deleted {type}'s {genre} whole playlist\n\nBy :- {CallbackQuery.from_user.mention}"
    )


@app.on_callback_query(filters.regex("audio_video_download"))
async def down_playlisyts(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"good"))
async def good(_, CallbackQuery):
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )

idxal asyncio
idxal OS
idxal t??sad??fi
asyncio olan yolu bo?? n??vb??sind?? idxal

konfiqurasiyadan get_queue-ni idxal edin
pyrogram-dan filtrl??ri idxal edin
pyrogram-dan.types idxal InlineKeyboardMarkup
pytgcalls-d??n ax??n n??v??n?? idxal edin
pytgcalls h??yata.types.??nput_stream giri?? audio ax??n??n??, giri?? ax??n??n?? idxal edir

Yukki-d??n BOT_USERNAME, MUS??C_BOT_NAME, proqram, db_mem idxal
Yukki-d??n.Core.PYTG idxal queue, Yukki ??a????r??r
Yukki-d??n.Core.Trial z??ngl??r.??evirm??k Converter idxal
Yukki-d??n.Core.Trial z??ngl??r.Y??kl??yici y??kl??m??ni idxal edir
Yukki il??.Veril??nl??r bazas?? idxal (_get_playlist, delete_playlist, get_playlist),
                            get_playl??st_names, ??s_act??ve_chat, playlist qazanc)
Yukka ' dan.Veril??nl??r bazas??.idxal n??vb?? (add_act??ve_chat, ??s_act??ve_chat,
is_music_playing, music_off, music_on,
remove_active_chat)
Yukki-d??n.Dekoratorlar.administrators AdminRightsCheckCB idxal
Yukki-d??n.Dekoratorlar.Checker idxal encoder
Yukka ' dan.Daxili idxal (audio_markup, audio_markup2, Y??kl??,
fetch_playlist, paste_queue_markup, primary_markup)
Yukka ' dan.Kommunal xidm??tl??r.decains vaxt_to_tseconds idxal
Yukka ' dan.Kommunal xidm??tl??r.chat x??susi font_to_normal idxal edir
Yukka ' dan.Kommunal xidm??tl??r.idxal ??spreviup, paste_queue daxil edin
Yukki-d??n.Kommunal xidm??tl??r.check_theme idxal m??vzusu
Yukki-d??n.Kommunal xidm??tl??r.ki??ik idxal gen_thumb
Yukki-d??n.Kommunal xidm??tl??r.timer start_timer idxal
Yukki-d??n.Kommunal xidm??tl??r.idxal youtube get_yt_info_id

loop = asyncio.get_event_loop()


@app.on_callback_query (filtreler.Daimi ifad?? ("m??cburi ba??lanma"))
m??cburi asynchronous qorunmas?? aradan qald??r??lmas?? (_, callback sor??u):
    callback_data = z??ng sor??usu.m??lumat.zolaq()
    callback_request = callback_data.split (he?? bir, 1)[1]
    sor??u, istifad????i identifikatoru = t??rs z??ng_request.split("|")
    ??g??r CallbackQuery.from_user.??d != ??nt(istifad????i ID):
        geri ??a????rma???? g??zl??y??n qaytar??n.cavab(
            "Bunu ba??laman??za icaz?? verilmir"., g??st??r_alert=h??qiq??t
        )
    z??ng g??zl??yirik.mesaj.(sil)
    z??ng g??zl??yirik.cavab()


@ app .on_callback_ sor??u(
    filters.Daimi ifad??(??ablon=r"^(fasil??|atlama|Stop|Resume)$")
)
@ adminrightscheckcb - admin
@checkercb
asynchronous administrator h??quqlar??n??n qorunmas?? ( _ , geri ??a????rma sor??usu):
    qlobal get_queue
    command = z??ng sor??u.uy??un[0].qrup(1)
    ??g??r yoxsa, ??s_active_chat g??zl??yin (CallbackQuery.message.chat.id):
        geri ??a????rma???? g??zl??y??n qaytar??n.cavab(
            "S??sli s??hb??td?? he?? bir ??ey t??krarlanm??r"., g??st??r_alert=h??qiq??t
        )
    ??d chat = CallbackQuery.message.chat.??d
    komanda = = "fasil??":
        ??g??r yoxsa, ??s_music_playing (chat ID)g??zl??yin:
            geri ??a????rma???? g??zl??y??n qaytar??n.cavab(
                "Musiqi art??q dayand??r??l??b", ??ou=h??qiq??t
            )
        music_off (chat ID)g??zl??yir
        Yukki g??zl??yir.pytgcalls.pause_stream(??d chat)
        z??ng g??zl??yirik.mesaj.cavab_text(
            F " The Voice Chat {??ks-sor??u dayand??r??l??b.istifad????i.qeyd}!",
reply_markup=audio_markup2,
        )
        z??ng g??zl??yirik.mesaj.(sil)
        z??ng g??zl??yirik.cavab ("dayand??r??l??b", g??st??rm??=h??qiq??t)
    ??g??r komanda = = "i???? davam et":
        ??s_music_playing (chat ID)g??zl??yir:
            geri ??a????rma???? g??zl??y??n qaytar??n.cavab(
                "Musiqi art??q b??rpa olunub"., g??st??r_alert=h??qiq??t
            )
        music_on(chat ID)g??zl??yir
        Yukki g??zl??yir.pytgcalls.resume_stream(??d chat)
        z??ng g??zl??yirik.mesaj.cavab_text(
            f " The Voice Chat {??ks-sor??u il?? b??rpa olunur.istifad????i.qeyd}!",
reply_markup=audio_markup2,
        )
        z??ng g??zl??yirik.mesaj.(sil)
        z??ng g??zl??yirik.cavab ("b??rpa", g??st??rm??=h??qiq??t)
    komanda =="stopcb":
        n??mun??:
            N??vb??.clear (chat ID)
        bo?? n??vb?? istisna olmaqla:
            ke??m??k
        g??zl??m?? silinm??_aktiv_cat (??at identifikatoru)
        Yukki g??zl??yin.pytgcalls.burax??n_group_caler (chat ID)
        z??ng g??zl??yirik.mesaj.cavab_text(
            f " the s??sli s??hb??t tamamland??/dayand??r??ld?? {??ks-sor??u.istifad????i.qeyd}!",
reply_markup=audio_markup2,
        )
        z??ng g??zl??yirik.mesaj.(sil)
        z??ng g??zl??yirik.cavab ("dayand??r??l??b", g??st??rm??=h??qiq??t)
    komanda =="skipcb":
        N??vb??.task_done(??d chat)
        n??vb?? varsa. is_empty (chat ID):
            g??zl??m?? silinm??_aktiv_cat (??at identifikatoru)
            z??ng g??zl??yirik.mesaj.cavab_text(
                f " __Queue _ \n\n s??s chat t??rk art??q musiqi..Istifad?? button: - {??ks sor??u.istifad????i.yada sal}"
            )
            Yukki g??zl??yin.pytgcalls.burax??n_group_caler (chat ID)
            z??ng g??zl??yirik.mesaj.(sil)
            z??ng g??zl??yirik.cavab(
                "Burax??lm????. N??vb?? No daha ??ox musiqi", g??st??r_alert = h??qiq??t
            )
            qaytar
        h??l??:
            Videoid = n??vb??.al??n (chat ID) ["fayl"]
            got_queue = get_queue. almaq(CallbackQuery.message.chat.id)
            got_queue ??g??r:
                got_queue.pop(0)
            finxx = f " {video??d[0]}{video??d [1]}{video??d[2]}"
            aud = 0
            ??g??r str(finxx)! = "i??l??nm??mi??":
                z??ng g??zl??yirik.mesaj.(sil)
                z??ng g??zl??yirik.cavab(
                    "Burax??lm????! Playlist playback....", g??st??r=h??qiq??t
                )
                Mystic = callback g??zl??yir.mesaj.cavab_text(
                    f " * * {MUS??Q??_MUSE_BOTA} oxutma funksiyas?? * * \n \ n__ _ n??vb??ti musiqini ??al???? siyah??s??ndan Y??kl??yin...._Istifad?? _ \n \ pbutton: - {callback sor??u.istifad????i.yada sal}"
                )
                (
ad??,
m??dd??ti_min,
uzunluq_sek,
                    miniat??r,
) = get_yt_info_id(??????????????)
                mistisizmi g??zl??yin.Sinaqoqlar f??sil??sinin
                    f " **{ADI_MUSES} Uploader**\n\n * * Title: * * {ad??[:50]} \ n \ n0% ???????????????????????????????????? 100%"
                )
                y??kl??nmi?? fayl = g??zl??m?? d??vr??.run_in_executor(
                    Xeyr, Y??kl??, Video, mistisizm, ad??
                )
                = g??zl??m?? d??n??????m (nazil fayl)
                Yukki g??zl??yir.pytgcalls.d??yi??iklik_potok(
                    identifikator
chat, giri?? stream(
                        Input audio stream(
                            raw_path,
),
),
)
                m??vzu = g??zl??m?? yoxlamalar_teml??r (chat ID)
                chat_title = x??susi font_to_normal ??????n g??zl??m??(
                    Z??ng sor??usu.mesaj.chat.ba??l??q
                )
                thumb = gen_thumb g??zl??yir ( 
                    miniat??r,
ba??l??q,
CallbackQuery.from_user.id,
m??vzu,
                    s??hb??t ba??l??????,
)
                d??ym??l??r = ilkin qeyd(
                    azeri porno,
CallbackQuery.from_user.id,
m??dd??ti_min,
m??dd??ti_min,
)
                mistisizm g??zl??yir.(sil)
                qeyd = db_mem[video] ["istifad????i ad??"]
                final_output = callback g??zl??yir.mesaj.cavab_photo(
                    ????kil = thumb,
                    reply_markup= ??nlinekeyboardmarkup(d??ym??l??ri),
imza=(
                        f " <b>__s??s chat burax??lm????__ _ < /b > \ n\n<b>____oynama??a ba??lad??: _ _ _ < /b>[{ad?? [:25]}] (https://www.youtube.com/watch?v = {videoid}) \n<b>_duration:__ _ < / b> {davamiyy??t_min} d??qiq??\n** _ t??l??b: _ _ * * {qeyd}"
                    ),
                )
                os.sil (thumb)

            h??l??:
                z??ng g??zl??yirik.mesaj.(sil)
                g??zl??m?? sor??u geri z??ng.cavab ("burax??lm????!"g??st??r_alert=h??qiq??t)
                Yukki g??zl??yir.pytgcalls.d??yi??iklik_potok(
                    identifikator
chat, giri?? stream(
                        Input audio stream(
                            azeri porno,
),
),
)
                AFK = videoid
                title = db_mem[video??d] ["title"]
                duration_min = db_mem[video??d]["duration"]
                durat??on_sec = ??nt(vaxt_to_tecunds (uzunluq_min))
                qeyd = db_mem[video] ["istifad????i ad??"]
                video??d = db_mem[video??d] ["video??d"]
                ??g??r str(video)=="smex1":
                    d??ym??l??r = d??ym??l??r = Audio markalanma(
                        azeri porno,
CallbackQuery.from_user.id,
m??dd??ti_min,
m??dd??ti_min,
)
                    thumb = "Utils/Telegram.JPEG "
                    aud = 1
                h??l??:
                    _pat_ = _pat_ = (
(str(afc))
                        .d??yi??dirin("_", "", 1)
                        .d??yi??dirin("/", "", 1)
                        .d??yi??dirin(".", "", 1)
                    )
                    thumb = f"cache/{_path_}Ultimate . png"
                    d??ym??l??r = ilkin qeyd(
                        azeri porno,
CallbackQuery.from_user.id,
m??dd??ti_min,
m??dd??ti_min,
)
                final_output = callback g??zl??yir.mesaj.cavab_photo(
                    ????kil = thumb,
                    reply_markup = x??tti etiketl??m?? (d??ym??l??r),
                    imza = e " < b>__ _ s??s chat burax??lm????</b><b>________oynama??a ba??lad??:__ _ _ </b> {ad??} \n<B> _ _ _ duration_min} \n <b> _ _ _ _ _ _ _ _ _ _ _ _ t??l??b: _ _ _ _ < /b > {dan????an}",
 )
            g??zl??m?? start_timer(
                azeri porno,
m??dd??ti_min,
uzunluq_sek,
                yekun n??tic??,
CallbackQuery.message.chat.id,
CallbackQuery.message.from_user.id,
aglayan,
)


@app.on_callback_query (filtreler.Daimi ifad?? ("playlist"))
asynchronous playlist ( _ , callback sor??u):
    qlobal get_queue
    loop = asyncio.get_event_loop()
    callback_data = z??ng sor??usu.m??lumat.zolaq()
    ??d chat = CallbackQuery.message.chat.??d
    callback_request = callback_data.split (he?? bir, 1)[1]
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
