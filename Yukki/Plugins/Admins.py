
import asyncio
import os
import random
from asyncio import QueueEmpty

from config import get_queue
from pyrogram import filters
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, KeyboardButton, Message,
                            ReplyKeyboardMarkup, ReplyKeyboardRemove)
from pytgcalls import StreamType
from pytgcalls.types.input_stream import InputAudioStream, InputStream

from Yukki import BOT_USERNAME, MUSIC_BOT_NAME, app, db_mem
from Yukki.Core.PyTgCalls import Queues, Yukki
from Yukki.Core.PyTgCalls.Converter import convert
from Yukki.Core.PyTgCalls.Downloader import download
from Yukki.Database import (is_active_chat, is_music_playing, music_off,
                            music_on, remove_active_chat)
from Yukki.Decorators.admins import AdminRightsCheck
from Yukki.Decorators.checker import checker, checkerCB
from Yukki.Inline import audio_markup, primary_markup
from Yukki.Utilities.changers import time_to_seconds
from Yukki.Utilities.chat import specialfont_to_normal
from Yukki.Utilities.theme import check_theme
from Yukki.Utilities.thumbnails import gen_thumb
from Yukki.Utilities.timer import start_timer
from Yukki.Utilities.youtube import get_yt_info_id

loop = asyncio.get_event_loop()


__MODULE__ = "Voice Chat"
__HELP__ = """


/pause
- Pause the playing music on voice chat.

/resume
- Resume the paused music on voice chat.

/skip
- Skip the current playing music on voice chat

/end or /stop
- Stop the playout.

/queue
- Check queue list.


**Note:**
Only for Sudo Users

/activevc
- Check active voice chats on bot.

"""


@app.on_message(
    filters.command(["pause", "skip", "resume", "stop", "end"])
    & filters.group
)
@AdminRightsCheck
@checker
async def admins(_, message: Message):
    global get_queue
    if not len(message.command) == 1:
        return await message.reply_text("Error! Wrong Usage of Command.")
    if not await is_active_chat(message.chat.id):
        return await message.reply_text("Nothing is playing on voice chat.")
    chat_id = message.chat.id
    if message.command[0][1] == "a":
        if not await is_music_playing(message.chat.id):
            return await message.reply_text("Music is already Paused.")
        await music_off(chat_id)
        await Yukki.pytgcalls.pause_stream(chat_id)
        await message.reply_text(
            f"🎧 Voicechat Paused by {message.from_user.mention}!"
        )
    if message.command[0][1] == "e":
        if await is_music_playing(message.chat.id):
            return await message.reply_text("Music is already Playing.")
        await music_on(chat_id)
        await Yukki.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text(
            f"🎧 Voicechat Resumed by {message.from_user.mention}!"
        )
    if message.command[0][1] == "t" or message.command[0][1] == "n":
        try:
            Queues.clear(message.chat.id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await Yukki.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text(
            f"🎧 Voicechat End/Stopped by {message.from_user.mention}!"
        )
    if message.command[0][1] == "k":
        Queues.task_done(chat_id)
        if Queues.is_empty(chat_id):
            await remove_active_chat(chat_id)
            await message.reply_text(
                "No more music in __Queue__ \n\nLeaving Voice Chat"
            )
            await Yukki.pytgcalls.leave_group_call(message.chat.id)
            return
        else:
            videoid = Queues.get(chat_id)["file"]
            got_queue = get_queue.get(chat_id)
            if got_queue:
                got_queue.pop(0)
            finxx = f"{videoid[0]}{videoid[1]}{videoid[2]}"
            aud = 0
            if str(finxx) != "raw":
                mystic = await message.reply_text(
                    f"**{MUSIC_BOT_NAME} Playlist Function**\n\n__Downloading Next Music From Playlist....__"
                )
                (
                    title,
                    duration_min,
                    duration_sec,
                    thumbnail,
                ) = get_yt_info_id(videoid)
                await mystic.edit(
                    f"**{MUSIC_BOT_NAME} Downloader**\n\n**Title:** {title[:50]}\n\n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
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
                chat_title = await specialfont_to_normal(message.chat.title)
                thumb = await gen_thumb(
                    thumbnail, title, message.from_user.id, theme, chat_title
                )
                buttons = primary_markup(
                    videoid, message.from_user.id, duration_min, duration_min
                )
                await mystic.delete()
                mention = db_mem[videoid]["username"]
                final_output = await message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=(
                        f"<b>__Skipped Voice Chat__</b>\n\n🎥<b>__Started Playing:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n⏳<b>__Duration:__</b> {duration_min} Mins\n👤**__Requested by:__** {mention}"
                    ),
                )
                os.remove(thumb)
            else:
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
                        message.from_user.id,
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
                        message.from_user.id,
                        duration_min,
                        duration_min,
                    )
                final_output = await message.reply_photo(
                    photo=thumb,
                    reply_markup=InlineKeyboardMarkup(buttons),
                    caption=f"<b>__Skipped Voice Chat__</b>\n\n🎥<b>__Started Playing:__</b> {title} \n⏳<b>__Duration:__</b> {duration_min} \n👤<b>__Requested by:__ </b> {mention}",
                )
            await start_timer(
                videoid,
                duration_min,
                duration_sec,
                final_output,
                message.chat.id,
                message.from_user.id,
                aud,
            )

idxal asyncio
idxal OS
idxal təsadüfi
asyncio olan yolu boş növbəsində idxal

get_queue konfiqurasiya idxal
pies idxal filtreler
pirogramdan.növləri idxal (
zəng sorğusu, ınlinekeyboardbutton düyməsi, ınlinekeyboardmarkup düyməsi, klaviatura düyməsi, mesaj,
                            Replykeyboardmarkap, replykeyboardperehod)
pytgcalls idxal növü
pytgcalls dən stream.types.ınput_stream giriş audio axınını, giriş axınını idxal edir

Yukki-dən BOT_USERNAME, MUSİC_BOT_NAME, proqram, db_mem idxal
Yukki-dən.Core.PyTgCalls idxal queue, Yuki
Yukka ' dan.Core.Trial zənglər.Çevirmək Converter idxal
Yukki-dən.Core.Trial zənglər.Yükləyici yükləməni idxal edir
Yukki ilə.Verilənlər bazası idxal (ıs_actıve_chat, ıs_music_playing, music_off,
music_on, remove_active_chat)
Yukki-dən.Dekoratorlar.administrators admin doğrulama idxal
Yukki-dən.Dekoratorlar.Checker bir checker idxal
Yukka ' dan.Daxili audio_markup, primary_markup idxal
Yukki-dən.Kommunal xidmətlər.xəyanətçilər time_to_seconds ' u idxal edirlər
Yukki-dən.Kommunal xidmətlər.chat xüsusi font_to_normal idxal edir
Yukka ' dan.Kommunal xidmətlər.check_theme idxal mövzusu
Yukka ' dan.Kommunal xidmətlər.kiçik idxal gen_thumb
Yukki-dən.Kommunal xidmətlər.timer start_timer idxal
Yukki-dən.Kommunal xidmətlər.idxal youtube get_yt_info_id

loop = asyncio.get_event_loop()


__MODULU__ = "Səsli chat"
__ Yardım__="""


/ fasilə
- Səsli söhbətdə musiqi çalmasını dayandırın.

/ xülasə
- Səsli söhbətdə durdurulmuş musiqini davam etdirin.

/ keçmək
- Səs chat cari oynatılamayabilir musiqi skip

/son və ya /stop
- Playback dayandırmaq.

/ növbə
- Yoxlayın siyahısı növbələrin.


** Qeyd:**
Yalnız Sudo istifadəçilər üçün

/aktiv
- Bot üzrə aktiv səs sohbetler yoxlayın.

"""


@app.on_message(@proqram.on_message)(
    filters.komanda (["dayandırmaq", "skip", "davam et", "Stop", "tam"])
    & filtreler.qrup
)
@adminrightscheck
@ yoxlamaq
asynchronous administratorları qorunması ( _ , mesaj: mesaj):
    qlobal get_queue
    heç bir len(mesaj.komanda) == 1:
        gözləyən mesajı qaytarır.reply_text("Error! Sui-istifadə komanda".)
    əgər yoxsa, ıs_active_chat gözləyin (message.chat.id):
        gözləyən mesajı geri qaytarın.reply_text ("səsli söhbətdə heç bir şey təkrarlanmır").
    ıd chat = message.chat.ıd
    mesaj varsa.komanda[0][1]== "a":
        gözləyin deyilsə, sonra ıs_music_playing(message.chat.id):
            gözləyən mesajı qaytarın.reply_text ("Musiqi artıq dayandırılıb".)
        music_off (chat ID)gözləyir
        Yukki gözləyir.pytgcalls.pause_stream(ıd chat)
        mesajı gözləyir.reply_text(
            F " The səs chat dayandırılıb {post.istifadəçi.qeyd}!"
        )
    mesaj varsa.komanda[0][1]== "e":
        gözləmə-bu_muzyaka_games (message.chat.id):
            gözləyən mesajı qaytarın.reply_text ("Musiqi artıq oynayır".)
        music_on(chat ID)gözləyir
        Yukki gözləyir.pytgcalls.bərpa axını(message.chat.ıd)
        mesajı gözləyir.reply_text(
            f " The Voice Chat bərpa {post.istifadəçi.qeyd}!"
        )
    mesaj varsa.komanda[0] [1] = = " t " və ya mesaj.komanda[0][1]=="n":
        nümunə:
            Növbə. təmizləmək(message.chat.ıd)
        boş növbə istisna olmaqla:
            keçmək
        gözləmə silinmə_aktiv_cat (çat identifikatoru)
        Yukki.pytgcalls gözləyin. tərk_group_dcall(message.chat.id)
        mesajı gözləyir.reply_text(
            F " The Voice Chat başa/dayandırılıb {post.istifadəçi.qeyd}!"
        )
    mesaj varsa.komanda[0] [1] = = "k":
        Növbə.task_done(ıd chat)
        növbə varsa. is_empty (chat ID):
            gözləmə silinmə_aktiv_cat (çat identifikatoru)
            mesajı gözləyir.reply_text(
                "__Növbə__\n\n səs chat tərk No daha çox musiqi"
            )
            Yukki.pytgcalls gözləyin. tərk_group_dcall(message.chat.id)
            qaytar
        hələ:
            Videoid = növbə.alın (chat ID) ["fayl"]
            got_queue = get_queue.get(ıd chat)
            got_queue əgər:
                got_queue.pop(0)
            finxx = f " {videoıd[0]}{videoıd [1]}{videoıd[2]}"
            aud = 0
            əgər str(finxx)! = "işlənməmiş":
                Mystic = mesaj gözləyir.reply_text(
                    f " **{MUSİQİLƏR} oxutma funksiyası * * \n\n__ _ növbəti musiqini çalğı siyahısından Yükləyin....__"
                )
                (
adı,
müddəti_min,
uzunluq_sek,
                    miniatür,
) = get_yt_info_id(видеоид)
                mistisizmi gözləyin.Sinaqoqlar fəsiləsinin
                    f " **{ADI_MUSES} Uploader**\n\n * * Title: * * {adı[:50]} \ n \ n0% ▓▓▓▓▓▓▓▓▓▓▓▓ 100%"
                )
                yüklənmiş fayl = gözləmə dövrü.run_in_executor(
                    Xeyr, Yüklə, Video, mistisizm, adı
                )
                = gözləmə dönüşüm (nazil fayl)
                Yukki gözləyir.pytgcalls.dəyişiklik_potok(
                    identifikator
chat, giriş stream(
                        Input audio stream(
                            raw_path,
),
),
)
                mövzu = gözləmə yoxlamalar_temlər (chat ID)
                chat_title = xüsusi font_to_normal (mesaj) üçün gözləmə.chat.Başlıq)
                thumb = gen_thumb gözləyir ( 
                    miniatür, başlığını, message.from_user.ıd, mövzu, mövzu chat
                )
                düymələr = ilkin qeyd(
                    videoid, message.from_user.id, müddəti_min, müddəti_min
                )
                mistisizm gözləyir.(sil)
                qeyd = db_mem[video] ["istifadəçi adı"]
                final_output = gözləyir mesajları.reply_photo(
                    şəkil = thumb,
                    reply_markup= ınlinekeyboardmarkup(düymələri),
imza=(
                        f " <b>__səs chat buraxılmış__ _ < /b > \ n\n<b>____oynamağa başladı: _ _ _ < /b>[{adı [:25]}] (https://www.youtube.com/watch?v = {videoid}) \n<b>_duration:__ _ < / b> {davamiyyət_min} dəqiqə\n** _ tələb: _ _ * * {qeyd}"
                    ),
                )
                os.sil (thumb)
            hələ:
                Yukki gözləyir.pytgcalls.dəyişiklik_potok(
                    identifikator
chat, giriş stream(
                        Input audio stream(
                            azeri porno,
),
),
)
                AFK = videoid
                title = db_mem[videoıd] ["title"]
                duration_min = db_mem[videoıd]["duration"]
                duratıon_sec = ınt(vaxt_to_tecunds (uzunluq_min))
                qeyd = db_mem[video] ["istifadəçi adı"]
                videoıd = db_mem[videoıd] ["videoıd"]
                əgər str(video)=="smex1":
                    düymələr = düymələr = Audio markalanma(
                        azeri porno,
message.from_user.id,
müddəti_min,
müddəti_min,
)
                    thumb = "Utils/Telegram.JPEG "
                    aud = 1
                hələ:
                    _pat_ = _pat_ = (
(str(afc))
                        .dəyişdirin("_", "", 1)
                        .dəyişdirin("/", "", 1)
                        .dəyişdirin(".", "", 1)
                    )
                    thumb = f"cache/{_path_}Ultimate . png"
                    düymələr = ilkin qeyd(
                        azeri porno,
message.from_user.id,
müddəti_min,
müddəti_min,
                    )
                final_output = gözləyir mesajları.reply_photo(
                    şəkil = thumb,
                    reply_markup=InlineKeyboardMarkup(düymələri),
 imza = e " < b>__ _ səs chat buraxılmış</b><b>________oynamağa başladı:__ _ _ </b> {adı} \n<B> _ _ _ duration_min} \n <b> _ _ _ _ _ _ _ _ _ _ _ _ tələb: _ _ _ _ < /b > {danışan}",
 )
            gözləmə start_timer(
                azeri porno,
müddəti_min,
uzunluq_sek,
                son nəticə,
message.chat.id,
message.from_user.id,
                aglayan,
)
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
