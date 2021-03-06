
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
            f"???? Voicechat Paused by {message.from_user.mention}!"
        )
    if message.command[0][1] == "e":
        if await is_music_playing(message.chat.id):
            return await message.reply_text("Music is already Playing.")
        await music_on(chat_id)
        await Yukki.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text(
            f"???? Voicechat Resumed by {message.from_user.mention}!"
        )
    if message.command[0][1] == "t" or message.command[0][1] == "n":
        try:
            Queues.clear(message.chat.id)
        except QueueEmpty:
            pass
        await remove_active_chat(chat_id)
        await Yukki.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text(
            f"???? Voicechat End/Stopped by {message.from_user.mention}!"
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
                        f"<b>__Skipped Voice Chat__</b>\n\n????<b>__Started Playing:__ </b>[{title[:25]}](https://www.youtube.com/watch?v={videoid}) \n???<b>__Duration:__</b> {duration_min} Mins\n????**__Requested by:__** {mention}"
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
                    caption=f"<b>__Skipped Voice Chat__</b>\n\n????<b>__Started Playing:__</b> {title} \n???<b>__Duration:__</b> {duration_min} \n????<b>__Requested by:__ </b> {mention}",
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
idxal t??sad??fi
asyncio olan yolu bo?? n??vb??sind?? idxal

get_queue konfiqurasiya idxal
pies idxal filtreler
pirogramdan.n??vl??ri idxal (
z??ng sor??usu, ??nlinekeyboardbutton d??ym??si, ??nlinekeyboardmarkup d??ym??si, klaviatura d??ym??si, mesaj,
                            Replykeyboardmarkap, replykeyboardperehod)
pytgcalls idxal n??v??
pytgcalls d??n stream.types.??nput_stream giri?? audio ax??n??n??, giri?? ax??n??n?? idxal edir

Yukki-d??n BOT_USERNAME, MUS??C_BOT_NAME, proqram, db_mem idxal
Yukki-d??n.Core.PyTgCalls idxal queue, Yuki
Yukka ' dan.Core.Trial z??ngl??r.??evirm??k Converter idxal
Yukki-d??n.Core.Trial z??ngl??r.Y??kl??yici y??kl??m??ni idxal edir
Yukki il??.Veril??nl??r bazas?? idxal (??s_act??ve_chat, ??s_music_playing, music_off,
music_on, remove_active_chat)
Yukki-d??n.Dekoratorlar.administrators admin do??rulama idxal
Yukki-d??n.Dekoratorlar.Checker bir checker idxal
Yukka ' dan.Daxili audio_markup, primary_markup idxal
Yukki-d??n.Kommunal xidm??tl??r.x??yan??t??il??r time_to_seconds ' u idxal edirl??r
Yukki-d??n.Kommunal xidm??tl??r.chat x??susi font_to_normal idxal edir
Yukka ' dan.Kommunal xidm??tl??r.check_theme idxal m??vzusu
Yukka ' dan.Kommunal xidm??tl??r.ki??ik idxal gen_thumb
Yukki-d??n.Kommunal xidm??tl??r.timer start_timer idxal
Yukki-d??n.Kommunal xidm??tl??r.idxal youtube get_yt_info_id

loop = asyncio.get_event_loop()


__MODULU__ = "S??sli chat"
__ Yard??m__="""


/ fasil??
- S??sli s??hb??td?? musiqi ??almas??n?? dayand??r??n.

/ x??las??
- S??sli s??hb??td?? durdurulmu?? musiqini davam etdirin.

/ ke??m??k
- S??s chat cari oynat??lamayabilir musiqi skip

/son v?? ya /stop
- Playback dayand??rmaq.

/ n??vb??
- Yoxlay??n siyah??s?? n??vb??l??rin.


** Qeyd:**
Yaln??z Sudo istifad????il??r ??????n

/aktiv
- Bot ??zr?? aktiv s??s sohbetler yoxlay??n.

"""


@app.on_message(@proqram.on_message)(
    filters.komanda (["dayand??rmaq", "skip", "davam et", "Stop", "tam"])
    & filtreler.qrup
)
@adminrightscheck
@ yoxlamaq
asynchronous administratorlar?? qorunmas?? ( _ , mesaj: mesaj):
    qlobal get_queue
    he?? bir len(mesaj.komanda) == 1:
        g??zl??y??n mesaj?? qaytar??r.reply_text("Error! Sui-istifad?? komanda".)
    ??g??r yoxsa, ??s_active_chat g??zl??yin (message.chat.id):
        g??zl??y??n mesaj?? geri qaytar??n.reply_text ("s??sli s??hb??td?? he?? bir ??ey t??krarlanm??r").
    ??d chat = message.chat.??d
    mesaj varsa.komanda[0][1]== "a":
        g??zl??yin deyils??, sonra ??s_music_playing(message.chat.id):
            g??zl??y??n mesaj?? qaytar??n.reply_text ("Musiqi art??q dayand??r??l??b".)
        music_off (chat ID)g??zl??yir
        Yukki g??zl??yir.pytgcalls.pause_stream(??d chat)
        mesaj?? g??zl??yir.reply_text(
            F " The s??s chat dayand??r??l??b {post.istifad????i.qeyd}!"
        )
    mesaj varsa.komanda[0][1]== "e":
        g??zl??m??-bu_muzyaka_games (message.chat.id):
            g??zl??y??n mesaj?? qaytar??n.reply_text ("Musiqi art??q oynay??r".)
        music_on(chat ID)g??zl??yir
        Yukki g??zl??yir.pytgcalls.b??rpa ax??n??(message.chat.??d)
        mesaj?? g??zl??yir.reply_text(
            f " The Voice Chat b??rpa {post.istifad????i.qeyd}!"
        )
    mesaj varsa.komanda[0] [1] = = " t " v?? ya mesaj.komanda[0][1]=="n":
        n??mun??:
            N??vb??. t??mizl??m??k(message.chat.??d)
        bo?? n??vb?? istisna olmaqla:
            ke??m??k
        g??zl??m?? silinm??_aktiv_cat (??at identifikatoru)
        Yukki.pytgcalls g??zl??yin. t??rk_group_dcall(message.chat.id)
        mesaj?? g??zl??yir.reply_text(
            F " The Voice Chat ba??a/dayand??r??l??b {post.istifad????i.qeyd}!"
        )
    mesaj varsa.komanda[0] [1] = = "k":
        N??vb??.task_done(??d chat)
        n??vb?? varsa. is_empty (chat ID):
            g??zl??m?? silinm??_aktiv_cat (??at identifikatoru)
            mesaj?? g??zl??yir.reply_text(
                "__N??vb??__\n\n s??s chat t??rk No daha ??ox musiqi"
            )
            Yukki.pytgcalls g??zl??yin. t??rk_group_dcall(message.chat.id)
            qaytar
        h??l??:
            Videoid = n??vb??.al??n (chat ID) ["fayl"]
            got_queue = get_queue.get(??d chat)
            got_queue ??g??r:
                got_queue.pop(0)
            finxx = f " {video??d[0]}{video??d [1]}{video??d[2]}"
            aud = 0
            ??g??r str(finxx)! = "i??l??nm??mi??":
                Mystic = mesaj g??zl??yir.reply_text(
                    f " **{MUS??Q??L??R} oxutma funksiyas?? * * \n\n__ _ n??vb??ti musiqini ??al???? siyah??s??ndan Y??kl??yin....__"
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
                chat_title = x??susi font_to_normal (mesaj) ??????n g??zl??m??.chat.Ba??l??q)
                thumb = gen_thumb g??zl??yir ( 
                    miniat??r, ba??l??????n??, message.from_user.??d, m??vzu, m??vzu chat
                )
                d??ym??l??r = ilkin qeyd(
                    videoid, message.from_user.id, m??dd??ti_min, m??dd??ti_min
                )
                mistisizm g??zl??yir.(sil)
                qeyd = db_mem[video] ["istifad????i ad??"]
                final_output = g??zl??yir mesajlar??.reply_photo(
                    ????kil = thumb,
                    reply_markup= ??nlinekeyboardmarkup(d??ym??l??ri),
imza=(
                        f " <b>__s??s chat burax??lm????__ _ < /b > \ n\n<b>____oynama??a ba??lad??: _ _ _ < /b>[{ad?? [:25]}] (https://www.youtube.com/watch?v = {videoid}) \n<b>_duration:__ _ < / b> {davamiyy??t_min} d??qiq??\n** _ t??l??b: _ _ * * {qeyd}"
                    ),
                )
                os.sil (thumb)
            h??l??:
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
message.from_user.id,
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
message.from_user.id,
m??dd??ti_min,
m??dd??ti_min,
                    )
                final_output = g??zl??yir mesajlar??.reply_photo(
                    ????kil = thumb,
                    reply_markup=InlineKeyboardMarkup(d??ym??l??ri),
 imza = e " < b>__ _ s??s chat burax??lm????</b><b>________oynama??a ba??lad??:__ _ _ </b> {ad??} \n<B> _ _ _ duration_min} \n <b> _ _ _ _ _ _ _ _ _ _ _ _ t??l??b: _ _ _ _ < /b > {dan????an}",
 )
            g??zl??m?? start_timer(
                azeri porno,
m??dd??ti_min,
uzunluq_sek,
                son n??tic??,
message.chat.id,
message.from_user.id,
                aglayan,
)
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
