import asyncio
from os import path

from pyrogram import filters
from pyrogram.types import (InlineKeyboardMarkup, InputMediaPhoto, Message,
                            Voice)
from youtube_search import YoutubeSearch

from Yukki import (BOT_USERNAME, DURATION_LIMIT, DURATION_LIMIT_MIN,
                   MUSIC_BOT_NAME, app, db_mem)
from Yukki.Decorators.permission import PermissionCheck
from Yukki.Inline import song_download_markup, song_markup
from Yukki.Utilities.url import get_url
from Yukki.Utilities.youtube import (get_yt_info_query,
                                     get_yt_info_query_slider)

loop = asyncio.get_event_loop()

__MODULE__ = "Song"
__HELP__ = """


/song [Youtube URL və ya Axtarış Sorğu] 
- Xüsusi sorğunu audio və ya video formatında yükləyin.



"""


@app.on_message(
    filters.command(["song", f"song@{BOT_USERNAME}"]) & filters.group
)
@PermissionCheck
async def play(_, message: Message):
    if message.sender_chat:
        return await message.reply_text(
            "Siz bu Çat Qrupunda __Anonim Adminsiniz__!\nAdmin Sağdan İstifadəçi Hesabına qayıdıns."
        )
    await message.delete()
    url = get_url(message)
    if url:
        mystic = await message.reply_text("🔄 URL emal olunur... Lütfən gözləyin!")
        query = message.text.split(None, 1)[1]
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(None, get_yt_info_query, query)
        if str(duration_min) == "None":
            return await mystic.edit("Sorry! Its a Live Video")
        await mystic.delete()
        buttons = song_download_markup(videoid, message.from_user.id)
        return await message.reply_photo(
            photo=thumb,
            caption=f"📎Başlıq: **{title}\n\n⏳Müddət:** {duration_min} Saniyə\n\n__[Video Haqqında Əlavə Məlumat Alın](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    else:
        if len(message.command) < 2:
            await message.reply_text(
                "**Usage:**\n\n/song [Youtube Url və ya Musiqi Adı]\n\nXüsusi Sorğunu yükləyir."
            )
            return
        mystic = await message.reply_text("🔍 Sorğunuz Axtarılır...")
        query = message.text.split(None, 1)[1]
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(None, get_yt_info_query, query)
        if str(duration_min) == "None":
            return await mystic.edit("Sorry! Its a Live Video")
        await mystic.delete()
        buttons = song_markup(
            videoid, duration_min, message.from_user.id, query, 0
        )
        return await message.reply_photo(
            photo=thumb,
            caption=f"📎Başlıq: **{title}\n\n⏳Müddət:** {duration_min} Saniyə\n\n__[Video Haqqında Əlavə Məlumat Alın](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_callback_query(filters.regex("qwertyuiopasdfghjkl"))
async def qwertyuiopasdfghjkl(_, CallbackQuery):
    print("234")
    await CallbackQuery.answer()
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    userid = CallbackQuery.from_user.id
    videoid, user_id = callback_request.split("|")
    buttons = song_download_markup(videoid, user_id)
    await CallbackQuery.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex(pattern=r"song_right"))
async def song_right(_, CallbackQuery):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, type, query, user_id = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        return await CallbackQuery.answer(
            "Öz Musiqini Axtar. Bu düymədən istifadə etməyə icazəniz yoxdur.",
            show_alert=True,
        )
    what = str(what)
    type = int(type)
    if what == "F":
        if type == 9:
            query_type = 0
        else:
            query_type = int(type + 1)
        await CallbackQuery.answer("Növbəti Nəticənin Alınması", show_alert=True)
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(
            None, get_yt_info_query_slider, query, query_type
        )
        buttons = song_markup(
            videoid, duration_min, user_id, query, query_type
        )
        med = InputMediaPhoto(
            media=thumb,
            caption=f"📎Başlıq: **{title}\n\n⏳Müddət:** {duration_min} Saniyə\n\n__[Video Haqqında Əlavə Məlumat Alın](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
    if what == "B":
        if type == 0:
            query_type = 9
        else:
            query_type = int(type - 1)
        await CallbackQuery.answer("Getting Previous Result", show_alert=True)
        (
            title,
            duration_min,
            duration_sec,
            thumb,
            videoid,
        ) = await loop.run_in_executor(
            None, get_yt_info_query_slider, query, query_type
        )
        buttons = song_markup(
            videoid, duration_min, user_id, query, query_type
        )
        med = InputMediaPhoto(
            media=thumb,
            caption=f"📎Başlıq: **{title}\n\n⏳Müddət:** {duration_min} Saniyə\n\n__[Video Haqqında Əlavə Məlumat Alın](https://t.me/{BOT_USERNAME}?start=info_{videoid})__",
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
