
import os
import re
import subprocess
import sys
import traceback
from asyncio import create_subprocess_shell, sleep, subprocess
from html import escape
from inspect import getfullargspec
from io import StringIO
from time import time

from pyrogram import filters
from pyrogram.errors import MessageNotModified
from pyrogram.types import Message, ReplyKeyboardMarkup

from Yukki import SUDOERS, userbot
from Yukki.Utilities.tasks import add_task, rm_task

# Eval and Sh module from WBB

__MODULE__ = "Broadcast"
__HELP__ = """

**Note:**
Only for Sudo Users.


/broadcast [Message or Reply to a Message] 
- Broadcast any message to Bot's Served Chats.

/broadcast_pin [Message or Reply to a Message] 
- Broadcast any message to Bot's Served Chats with message getting Pinned in chat [Disabled Notifications].

/broadcast_pin_loud [Message or Reply to a Message] 
- Broadcast any message to Bot's Served Chats with message getting Pinned in chat [Enabled Notifications].

"""

m = None
p = print
r = None
arrow = lambda x: (x.text if isinstance(x, Message) else "") + "\n`→`"


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


async def iter_edit(message: Message, text: str):
    async for m in userbot.iter_history(message.chat.id):

        # If no replies found, reply
        if m.message_id == message.message_id:
            return 0

        if not m.from_user or not m.text or not m.reply_to_message:
            continue

        if (
            (m.reply_to_message.message_id == message.message_id)
            and (m.from_user.id == message.from_user.id)
            and ("→" in m.text)
        ):
            try:
                return await m.edit(text)
            except MessageNotModified:
                return


@userbot.on_message(
    filters.user(SUDOERS)
    & ~filters.forwarded
    & ~filters.via_bot
    & ~filters.edited
    & filters.command("eval"),
)
async def executor(client, message: Message):
    global m, p, r
    if len(message.command) < 2:
        return await eor(message, text="Command needed to execute")

    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()

    if message.chat.type == "channel":
        return

    m = message
    p = print

    # To prevent keyboard input attacks
    if m.reply_to_message:
        r = m.reply_to_message
        if r.reply_markup and isinstance(r.reply_markup, ReplyKeyboardMarkup):
            return await eor(m, text="INSECURE!")
    status = None
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        task, task_id = await add_task(
            aexec,
            "Eval",
            cmd,
            client,
            m,
        )

        text = f"{arrow('')} Pending Task `{task_id}`"
        if not message.edit_date:
            status = await m.reply(text, quote=True)

        await task
    except Exception as e:
        e = traceback.format_exc()
        print(e)
        exc = e.splitlines()[-1]

    await rm_task()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = f"**→**\n`{escape(evaluation.strip())}`"

    if len(final_output) > 4096:
        filename = "output.txt"
        with open(filename, "w+", encoding="utf8") as out_file:
            out_file.write(str(evaluation.strip()))
        await message.reply_document(
            document=filename,
            caption="`→`\n  **Attached Document**",
            quote=False,
        )
        os.remove(filename)
        if status:
            await status.delete()
        return

    # Edit the output if input is edited
    if message.edit_date:
        status_ = await iter_edit(message, final_output)
        if status_ == 0:
            return await message.reply(final_output, quote=True)
        return
    if not status.from_user:
        status = await userbot.get_messages(status.chat.id, status.message_id)
    await eor(status, text=final_output, quote=True)


@userbot.on_message(
    filters.user(SUDOERS)
    & ~filters.forwarded
    & ~filters.via_bot
    & ~filters.edited
    & filters.command("sh"),
)
async def shellrunner(_, message: Message):
    if len(message.command) < 2:
        return await eor(message, text="**Usage:**\n/sh git pull")

    if message.reply_to_message:
        r = message.reply_to_message
        if r.reply_markup and isinstance(
            r.reply_markup,
            ReplyKeyboardMarkup,
        ):
            return await eor(message, text="INSECURE!")
    output = ""
    text = message.text.split(None, 1)[1]
    if "\n" in text:
        code = text.split("\n")
        shell = " ".join(code)
    else:
        shell = text
    process = await create_subprocess_shell(
        shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, errorz = await process.communicate()
    if errorz:
        error = f"**INPUT:**\n```{escape(text)}```\n\n**ERROR:**\n```{errorz.decode('utf-8')}```"
        return await eor(message, text=error)
    output += out.decode("utf-8")
    output += "\n"
    if str(output) == "\n":
        output = None
    if output:
        if len(output) > 4096:
            with open("output.txt", "w+") as file:
                file.write(output)
            await message.reply_document(
                "output.txt", caption=f"{escape(text)}"
            )
            return os.remove("output.txt")
        await eor(
            message,
            text=f"**INPUT:**\n```{escape(text)}```\n\n**OUTPUT:**\n```{(output)}```",
        )
    else:
        return await eor(
            message,
            text=f"**INPUT:**\n```{escape(text)}```\n\n**OUTPUT: **\n`No output`",
        )

os idxal
təkrar idxal
idxal subprocess
sys idxal
idxal iz
asyncio Import create_subprocess_shell, yuxu, subprocess
html idxal escape
ınspect idxal getfullargspec from
I-çıxış idxal StringİO
vaxt idxal

pirogramdan filtrləri idxal edin
pirogramdan.səhvlər dəyişdirilməmiş mesajı idxal et
pirogramdan.idxal mesaj növləri, ReplyKeyboardMarkup

Yukki ' den SUDOERS, userbot idxal edin
Yukka ' dan.Kommunal xidmətlər.idxal add_task vəzifələri, rm_task

# Qiymətləndirilməsi modulu və SH

__MODULU__ = "Yayım"
__ Yardım__="""

** Qeyd:**
Yalnız Sudo istifadəçilər üçün.


/ yayım [mesaj və ya mesaj cavab] 
- Xidmət Bot sohbetler hər hansı bir mesaj yayımlanacaq.

/ broadcast_pin [mesaj və ya mesaj cavab] 
- Chat mesaj pinning [reports aradan] ilə Bot Xidmət sohbetler hər hansı bir mesaj yayımlanacaq.

/ broadcast_pin_loud [mesaj və ya mesaj cavab] 
- Chat mesaj pinning [bildirişlərin daxil] ilə Bot Xidmət sohbetler hər hansı bir mesaj yayımlanacaq.

"""

m = Yox
p = çap
r = Yox
ox = Lambda x: (x.mətn, əgər dəyər varsa (x, mesaj) başqa cür") + " \`n`'"


asynchronous definition (mesaj: mesaj, **kvargi):
    funksiyası = (
        (msg.edit_text əgər MSG.from_user.is_self digər msg.cavab)
        mesaj varsa.ot_poluser
        daha mesaj.cavab
    )
    dəqiqləşdirilməsi = getfullargspec(funksiyası.__bükülmüş__).arqumentlər
    geri qaytarma (**{k: k üçün v, v kuvargs-də.ıtems () əgər k dəqiqləşdirilməsi})


asynchronous aexec qorunması (kod, müştəri, mesaj):
    icraçı direktor(
        "asinxron tərif _ _ aexec (müştəri, mesaj):"
        + "".qoşulmaq(f"\n {a}" üçün bir kod.split("\n"))
    )
    qaytarılması gözləyir yerli sakinləri()["__aexec"] (müştəri, mesaj)


asynchronous iter_edit tərifi (mesaj: mesaj, mətn: str):
    userbot.iter_history m üçün asinxron(message.chat.id):

        # Cavablar tapılmazsa, cavab verin
        əgər m. message_id = = mesaj.message_id:
            0 qaytarılması

        m.from_user yoxsa m.mətn və ya m.reply_to_message yoxdur:
            davam

        əgər (
(m.reply_to_message.message_id==mesajı.mesaj id)
            və (m.from_user.id == message.from_user.ıd)
            və (m mətnində" tərcümə")
        ):
            nümunə:
                geri gözləyir m. redaktə etmək (mətn)
            dəyişdirilməmiş mesajlar istisna olmaqla:
                qaytar


@userbot.on_message @xüsusi mesaj(
    filters.istifadəçi (istifadəçilər)
    & ~filtreler.yönlendirileceksiniz
    & ~filtreler.via_bot
    & ~filtreler.redaktə
    &filtreler.komanda ("qiymətləndirmə"),
)
artist asynchronous qorunması (müştəri, mesaj: mesaj):
    qlobal m, p, r
 əgər len (mesaj.komanda) < 2:
        qaytarma gözləyir EOR (mesaj, mətn = "yerinə yetirmək üçün lazım olan komanda")

    nümunə:
        cmd = mesaj.mətn.split ("", maxsplit=1)[1]
    index səhv istisna olmaqla:
        gözləyən mesajı geri qaytarın.(sil)

    mesaj varsa.chat.type = = "kanal":
        qaytar

    m = mesajı
    p = çap

    # Klaviatura giriş hücumları qarşısını almaq üçün
    əgər M. reply_to_message:
        r = m.cavab mesaj
        əgər r.reply_markup və isinstance (r.reply_markup, ReplyKeyboardMarkup):
            geri gözləyir eor (m, mətn= "TƏHLÜKƏLİDİR!")
    status = Xeyr
old_stderr = sys.stderr
    old_stdout = sys.standart
çıxış yönləndirilmiş çıxış = sys.standart nəticə = StringİO()
    yönlendirilen_error = sys.stderr = StringIO()
    stdout, stderr, exc = Xeyr, yox
cəhdlər:
        tapşırıq, task_ıd = tapşırıq əlavə etməyi gözləyir(
            aexec,
            "Qiymətləndirmə",
cmd,
müştəri,
m,
)

        mətn = f " {ox(")} gözləyən vəzifə " {tapşırıq identifikatoru}"
        heç bir mesaj yoxdur.edit_date:
            status = gözləmə m. cavab (mətn, sitat = həqiqət)

        vəzifə gözləyir
 e kimi istisna istisna olmaqla:
        e = geri izləmə.format_exs()
        çap (e)
        exc = e.ayırıcı xətləri () [-1]

    gözləmə rm_task()

    standart çıxış = yönləndirilmiş çıxış . getvalue()
    stderr = yönləndirilmiş səhv.getvalue()
    sys.stdout = old_stdout
sys.stderr = old_stderr
    qiymətləndirmə = ""
    əgər:
        qiymətləndirmə = istisna
    Elif stderr:
        qiymətləndirmə = stderr
    standart nəticə elif:
        qiymətləndirmə = standart
hələ nəticə:
        qiymətləndirmə = "Uğur"

    final_output = f"** * * * \ n ' {escape(hesab.zolaq ()}`"

    əgər len(son nəticə) > 4096:
        fayl adı = "çıxış.txt "
        out_file kimi açıq (fayl adı, "L+", encoding="utf8") ilə:
            giden fayl.yazmaq(str(qiymətdir.zolaq ())
        mesajı gözləyir.reply_document(
            sənəd= fayl adı,
            imza="`→`\n**əlavə sənəd**",
            quote= Yalan,
)
        os.sil (faylın adı)
        əgər status:
            gözləmə vəziyyəti.(sil)
        qaytar

     Giriş redaktə əgər # edit çıxış
    mesaj varsa.edit_date:
        status_ = ıter_edit ' i gözləyin (mesaj, son nəticə)
        əgər status_ = = 0:
            gözləyən mesajı qaytarın.cavab (yekun_otter, sitat = həqiqət)
        qaytarın
 heç bir status əgər . from_user:
        status = istifadəçi gözləyir. get_messages(status.chat.id, status. mesaj ID)
    gözləmə eor (status, mətn = yekun nəticə quote=True)


@userbot.on_message @xüsusi mesaj(
    filters.istifadəçi (istifadəçilər)
    & ~filtreler.yönlendirileceksiniz
    & ~filtreler.via_bot
    & ~filtreler.redaktə
    &filtreler.komanda ("sh"),
)
asynchronous shell qoruyucu ( _ , mesaj: mesaj):
    əgər len (mesaj.komanda) < 2:
        geri EOR gözləyir (mesaj, mətn="**istifadə:**\n/sh git pull")

    mesaj varsa.reply_to_message:
        r = bir mesaj.cavab_to_mession
        əgər r.reply_markup və isinstance(
            r.reply_markup,
ReplyKeyboardMarkup,
):
            geri gözləyir eor (yazı, mətn= "TƏHLÜKƏLİDİR!")
    nəticə = ""
    mətn = mesaj.mətn.ayrılıq (No 1)[1]
    mətn "\n" əgər:
        kod = mətn.split("\n")
        shell = " ".qoşulmaq (kod)
    hələ:
        shell = mətn
    proses = gözləyir create_subprocess_shell(
        qabıq,
standart nəticə = subprocess.boru,
        stderr = subprocess.boru,
    )
    çıxış, səhv = prosesi gözləyir.əlaqə()
    səhv varsa:
        bug = f "* * Input: * * \ n " {escape (mətn)}`\n\n**Bug:**\n`{səhv.decoding ('utf-8')}`"
        geri gözləyir eor (yazı, mətn = səhv)
    çıxış + = çıxış.decoding ("utf-8")
    nəticə += "\n"
    əgər str(nəticə)== "\n":
        nəticə = Yox
 əgər nəticə:
        əgər len(çıxış) > 4096:
            açıq ("çıxış.txt", " l+") bir fayl olaraq:
                fayl.qeyd (çıxış)
            mesajı gözləyir.reply_document(
                "output.txt", imza=f"{escape(mətn)}"
            )
            OS qaytarın.sil ("çıxış.txt ")
        gözləyin və ya(
            mesaj,
            mətn = f "* * giriş: * * \ n "{escape(mətn)} " \ n \ n * * nəticə: * * \ n`{(nəticə)}`",
)
    hələ:
        qaytarılması sizi gözləyir və ya(
            mesaj,
            mətn=f "* * Input: * * \ n "{escape(mətn)} "\ n \ n * * nəticə: * * \ N 'No çıxış'",
)
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
