
from pyrogram import Client, filters
from pyrogram.types import Message

from Yukki import SUDOERS, app
from Yukki.Database import (_get_authusers, delete_authuser, get_authuser,
                            get_authuser_count, get_authuser_names,
                            save_authuser)
from Yukki.Decorators.admins import AdminActual
from Yukki.Utilities.changers import (alpha_to_int, int_to_alpha,
                                      time_to_seconds)

__MODULE__ = "Auth Users"
__HELP__ = """

**Note:**
-Auth users can skip, pause, stop, resume Voice Chats even without Admin Rights.


/auth [Username or Reply to a Message] 
- Add a user to AUTH LIST of the group.

/unauth [Username or Reply to a Message] 
- Remove a user from AUTH LIST of the group.

/authusers 
- Check AUTH LIST of the group.
"""


@app.on_message(filters.command("auth") & filters.group)
@AdminActual
async def auth(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "Reply to a user's message or give username/user_id."
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        user_id = message.from_user.id
        token = await int_to_alpha(user.id)
        from_user_name = message.from_user.first_name
        from_user_id = message.from_user.id
        _check = await get_authuser_names(message.chat.id)
        count = 0
        for smex in _check:
            count += 1
        if int(count) == 20:
            return await message.reply_text(
                "You can only have 20 Users In Your Groups Authorised Users List (AUL)"
            )
        if token not in _check:
            assis = {
                "auth_user_id": user.id,
                "auth_name": user.first_name,
                "admin_id": from_user_id,
                "admin_name": from_user_name,
            }
            await save_authuser(message.chat.id, token, assis)
            await message.reply_text(
                f"Added to Authorised Users List of this group."
            )
            return
        else:
            await message.reply_text(f"Already in the Authorised Users List.")
        return
    from_user_id = message.from_user.id
    user_id = message.reply_to_message.from_user.id
    user_name = message.reply_to_message.from_user.first_name
    token = await int_to_alpha(user_id)
    from_user_name = message.from_user.first_name
    _check = await get_authuser_names(message.chat.id)
    count = 0
    for smex in _check:
        count += 1
    if int(count) == 20:
        return await message.reply_text(
            "You can only have 20 Users In Your Groups Authorised Users List (AUL)"
        )
    if token not in _check:
        assis = {
            "auth_user_id": user_id,
            "auth_name": user_name,
            "admin_id": from_user_id,
            "admin_name": from_user_name,
        }
        await save_authuser(message.chat.id, token, assis)
        await message.reply_text(
            f"Added to Authorised Users List of this group."
        )
        return
    else:
        await message.reply_text(f"Already in the Authorised Users List.")


@app.on_message(filters.command("unauth") & filters.group)
@AdminActual
async def whitelist_chat_func(_, message: Message):
    if not message.reply_to_message:
        if len(message.command) != 2:
            await message.reply_text(
                "Reply to a user's message or give username/user_id."
            )
            return
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        token = await int_to_alpha(user.id)
        deleted = await delete_authuser(message.chat.id, token)
        if deleted:
            return await message.reply_text(
                f"Removed from Authorised Users List of this Group."
            )
        else:
            return await message.reply_text(f"Not an Authorised User.")
    user_id = message.reply_to_message.from_user.id
    token = await int_to_alpha(user_id)
    deleted = await delete_authuser(message.chat.id, token)
    if deleted:
        return await message.reply_text(
            f"Removed from Authorised Users List of this Group."
        )
    else:
        return await message.reply_text(f"Not an Authorised User.")


@app.on_message(filters.command("authusers") & filters.group)
async def authusers(_, message: Message):
    _playlist = await get_authuser_names(message.chat.id)
    if not _playlist:
        return await message.reply_text(
            f"No Authorised Users in this Group.\n\nAdd Auth users by /auth and remove by /unauth."
        )
    else:
        j = 0
        m = await message.reply_text(
            "Fetching Authorised Users... Please Wait"
        )
        msg = f"**Authorised Users List[AUL]:**\n\n"
        for note in _playlist:
            _note = await get_authuser(message.chat.id, note)
            user_id = _note["auth_user_id"]
            user_name = _note["auth_name"]
            admin_id = _note["admin_id"]
            admin_name = _note["admin_name"]
            try:
                user = await app.get_users(user_id)
                user = user.first_name
                j += 1
            except Exception:
                continue
            msg += f"{j}??? {user}[`{user_id}`]\n"
            msg += f"    ??? Added By:- {admin_name}[`{admin_id}`]\n\n"
        await m.edit_text(msg)

m????t??ri idxal Tortlar, filtreler
pirogramdan.idxal mesaj n??vl??ri

Yukki 'den SUDOERS' i idxal edin, ??riz??
Yukka ' dan.Veril??nl??r bazas?? idxal (_get_authusers, silinm??_authuser, get_authuser,
get_authuser_count, get_authuser_names,
saxlanma_touser)
Yukka ' dan.Dekoratorlar.administratorlar ??nzibati m??lumatlar?? idxal edirl??r
Yukki-d??n.Kommunal xidm??tl??r.idxal d??yi??iklikl??r (alpha_to_??nt, ??nt_to_alpha,
time_to_seconds)

__ Modul _ _ _ = "istifad????il??rin avtorizasiyas??"
__ Yard??m__="""

** Qeyd:**
- Authentication istifad????il??r h??tta administrator h??quqlar?? olmadan s??s sohbetler davam dayand??rmaq, fasil??, atlayabilir.


/ avtorizasiya [istifad????i ad?? v?? ya mesaj cavab] 
- ??lav?? etm??k ??????n istifad????i S??YAHISI G??R???? qruplar.

/ icaz??siz [istifad????i ad?? v?? ya mesaj cavab] 
- Aradan qald??r??lmas?? istifad????i S??YAHISI G??R???? qruplar.

/ avtorizatorlar 
- Yoxlay??n S??YAHISI G??R???? qruplar.
"""


@app.on_message (komanda filters.("avtorizasiya") v?? filters qrupu.)
@Adminactual
asynchronous identifikasiyas?? ( _ , mesaj: mesaj):
    he?? bir mesaj yoxdur.reply_to_message:
        ??g??r len (mesaj.komanda)!= 2:
            mesaj?? g??zl??yir.reply_text(
                "??stifad????i mesaj??na cavab verin v?? ya istifad????i ad??/istifad????i identifikatorunu g??st??rin."
            )
            qaytar
        istifad????i = mesaj.m??tn.ayr??l??q (No 1)[1]
        ??g??r " @ " istifad????i:
            user = istifad????i.??v??z("@", "")
        istifad????i = app g??zl??yir . get_users(istifad????i)
        istifad????i id = message.from_user.??d
        Token = ??nt_to_alpha g??zl??yir(user.id)
        istifad????i ad?? = mesaj??.istifad????i ad??.adya_fail
        istifad????i ad??_??d= message.from_user.id
        _check = ad_torla??d??r??lm???? istifad????il??rin al??nmas??n?? g??zl??yin(message.chat.id)
        say?? = 0
        _check da smex ??????n:
            say?? += 1
        ??nt(miqdar??) == 20 varsa:
            g??zl??y??n mesaj?? qaytar??n.reply_text(
                "Qruplar??n??z??n S??lahiyy??tli istifad????il??ri siyah??s??nda (AUL) yaln??z 20 istifad????i ola bil??r"
            )
        m?? ' c??z?? _check deyils??:
            Assis = {
                "auth_user_??d istifad????i identifikatoru": user.id,
"istifad????i ad??": istifad????i.istifad????i ad??,
                "admin ID": istifad????i ID,
"Admin Ad??": istifad????i ad??,
            }
            saxlanman??n g??zl??nilm??si istifad????i_avtobusu(message.chat.id, Token, Assis)
            mesaj?? g??zl??yir.reply_text(
                f "bu qrupun S??lahiyy??tli istifad????il??rinin siyah??s??na ??lav?? edildi".
            )
            qaytar
        h??l??:
            mesaj?? g??zl??yir.reply_text (F "art??q s??lahiyy??tli istifad????il??r siyah??s??nda".)
        qaytar
    istifad????i ad??_??d= message.from_user.id
    istifad????i id = message.reply_to_message.from_user.??d
    istifad????i ad?? = mesaj??.reply_to_message.istifad????i.adya_fail
    Token = ??nt_to_alpha (istifad????i identifikatoru)
    istifad????i ad?? = mesaj??.istifad????i ad??.adya_fail
    _check = ad_torla??d??r??lm???? istifad????il??rin al??nmas??n?? g??zl??yin(message.chat.id)
    say?? = 0
    _check da smex ??????n:
        say?? += 1
    ??nt(miqdar??) == 20 varsa:
        g??zl??y??n mesaj?? qaytar??n.reply_text(
            "Qruplar??n??z??n S??lahiyy??tli istifad????il??ri siyah??s??nda (AUL) yaln??z 20 istifad????i ola bil??r"
        )
    m?? ' c??z?? _check deyils??:
        Assis = {
            "auth_user_id": istifad????i ??d,
"istifad????i ad??": istifad????i ad??,
            "admin ID": istifad????i ID,
"Admin Ad??": istifad????i ad??,
        }
        saxlanman??n g??zl??nilm??si istifad????i_avtobusu(message.chat.id, Token, Assis)
        mesaj?? g??zl??yir.reply_text(
            f "bu qrupun S??lahiyy??tli istifad????il??rinin siyah??s??na ??lav?? edildi".
        )
        qaytar
    h??l??:
        mesaj?? g??zl??yir.reply_text (F "art??q s??lahiyy??tli istifad????il??r siyah??s??nda".)


@app.on_message (komanda filters.("icaz??siz") v?? filters.group)
@Adminactual
asynchronous a?? siyah?? qorunmas??_chat_func ( _ , mesaj: mesaj):
    he?? bir mesaj yoxdur.reply_to_message:
        ??g??r len (mesaj.komanda)!= 2:
            mesaj?? g??zl??yir.reply_text(
                "??stifad????i mesaj??na cavab verin v?? ya istifad????i ad??/istifad????i identifikatorunu g??st??rin."
            )
            qaytar
        istifad????i = mesaj.m??tn.ayr??l??q (No 1)[1]
        ??g??r " @ " istifad????i:
            user = istifad????i.??v??z("@", "")
        istifad????i = app g??zl??yir . get_users(istifad????i)
        Token = ??nt_to_alpha g??zl??yir(user.id)
        silindi = silm?? g??zl??yir_avtobuser istifad????i(message.chat.id, Token)
        silindi varsa:
            g??zl??y??n mesaj?? qaytar??n.reply_text(
                f "bu qrupun S??lahiyy??tli istifad????il??rinin siyah??s??ndan silindi".
            )
        h??l??:
            g??zl??y??n mesaj?? qaytar??n.reply_text (f "qeyri-s??lahiyy??tli istifad????i".)
    istifad????i id = message.reply_to_message.from_user.??d
    Token = ??nt_to_alpha (istifad????i identifikatoru)
    silindi = silm?? g??zl??yir_avtobuser istifad????i(message.chat.id, Token)
    silindi varsa:
        g??zl??y??n mesaj?? qaytar??n.reply_text(
            f "bu qrupun S??lahiyy??tli istifad????il??rinin siyah??s??ndan silindi".
        )
    h??l??:
        g??zl??y??n mesaj?? qaytar??n.reply_text (f "qeyri-s??lahiyy??tli istifad????i".)


@app.on_message (filters.komanda ("istifad????il??r") v?? filters.group)
asynchronous istifad????i t??rifi ( _ , mesaj: mesaj):
    _playlist = ad_torla??d??r??lm???? istifad????il??rin al??nmas??n?? g??zl??yir(message.chat.id)
    _pleylist yoxsa:
        g??zl??y??n mesaj?? qaytar??n.reply_text(
            f " bu qrupda s??lahiyy??tli istifad????il??r yoxdur.\ N \ NADD / icaz?? istifad?? ed??r??k, istifad????il??r authenticate v?? /unauthenticated istifad?? ed??r??k aradan qald??r??lmas?? ."
        )
    h??l??:
        j = 0
        m = mesaj g??zl??yir.reply_text(
            "S??lahiyy??tli ??stifad????il??rin Se??imi... Xahi?? Edirik G??zl??yin"
        )
        msg = f "s??lahiyy??tli istifad????il??rin * * siyah??s??[AUL]: * * \ n \ n"
        _playlist qeydl??r ??????n:
            _ qeyd = get_authuser g??zl??yir(message.chat.id, qeyd)
            istifad????i id = _ qeyd["istifad????i id"]
            istifad????i ad?? = _ qeyd["istifad????i ad??"]
            admin_??d = _ qeyd["admin ID"]
            nazir m??avini imya_ad = _ qeyd ["nazir m??avini imya_ad"]
            n??mun??:
                istifad????i = app g??zl??yir . get_users(??d istifad????i)
                user = istifad????i.adya_fail
                j+= 1
            istisna olmaqla:
                davam
            msg + = f"{j} {istifad????i}[`{istifad????i identifikatoru}`]\n"
            msg + = f " ??lav?? edildi: - {Admin Ad??} ['{admin ID}'] \ n \ n"
        g??zl??m?? m.edit_text(yaz??)
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
