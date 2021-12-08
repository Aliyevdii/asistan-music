
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
            msg += f"{j}➤ {user}[`{user_id}`]\n"
            msg += f"    ┗ Added By:- {admin_name}[`{admin_id}`]\n\n"
        await m.edit_text(msg)

müştəri idxal Tortlar, filtreler
pirogramdan.idxal mesaj növləri

Yukki 'den SUDOERS' i idxal edin, ərizə
Yukka ' dan.Verilənlər bazası idxal (_get_authusers, silinmə_authuser, get_authuser,
get_authuser_count, get_authuser_names,
saxlanma_touser)
Yukka ' dan.Dekoratorlar.administratorlar İnzibati məlumatları idxal edirlər
Yukki-dən.Kommunal xidmətlər.idxal dəyişikliklər (alpha_to_ınt, ınt_to_alpha,
time_to_seconds)

__ Modul _ _ _ = "istifadəçilərin avtorizasiyası"
__ Yardım__="""

** Qeyd:**
- Authentication istifadəçilər hətta administrator hüquqları olmadan səs sohbetler davam dayandırmaq, fasilə, atlayabilir.


/ avtorizasiya [istifadəçi adı və ya mesaj cavab] 
- Əlavə etmək üçün istifadəçi SİYAHISI GİRİŞ qruplar.

/ icazəsiz [istifadəçi adı və ya mesaj cavab] 
- Aradan qaldırılması istifadəçi SİYAHISI GİRİŞ qruplar.

/ avtorizatorlar 
- Yoxlayın SİYAHISI GİRİŞ qruplar.
"""


@app.on_message (komanda filters.("avtorizasiya") və filters qrupu.)
@Adminactual
asynchronous identifikasiyası ( _ , mesaj: mesaj):
    heç bir mesaj yoxdur.reply_to_message:
        əgər len (mesaj.komanda)!= 2:
            mesajı gözləyir.reply_text(
                "İstifadəçi mesajına cavab verin və ya istifadəçi adı/istifadəçi identifikatorunu göstərin."
            )
            qaytar
        istifadəçi = mesaj.mətn.ayrılıq (No 1)[1]
        əgər " @ " istifadəçi:
            user = istifadəçi.əvəz("@", "")
        istifadəçi = app gözləyir . get_users(istifadəçi)
        istifadəçi id = message.from_user.ıd
        Token = ınt_to_alpha gözləyir(user.id)
        istifadəçi adı = mesajı.istifadəçi adı.adya_fail
        istifadəçi adı_ıd= message.from_user.id
        _check = ad_torlaşdırılmış istifadəçilərin alınmasını gözləyin(message.chat.id)
        sayı = 0
        _check da smex üçün:
            sayı += 1
        ınt(miqdarı) == 20 varsa:
            gözləyən mesajı qaytarın.reply_text(
                "Qruplarınızın Səlahiyyətli istifadəçiləri siyahısında (AUL) yalnız 20 istifadəçi ola bilər"
            )
        mö ' cüzə _check deyilsə:
            Assis = {
                "auth_user_ıd istifadəçi identifikatoru": user.id,
"istifadəçi adı": istifadəçi.istifadəçi adı,
                "admin ID": istifadəçi ID,
"Admin Adı": istifadəçi adı,
            }
            saxlanmanın gözlənilməsi istifadəçi_avtobusu(message.chat.id, Token, Assis)
            mesajı gözləyir.reply_text(
                f "bu qrupun Səlahiyyətli istifadəçilərinin siyahısına əlavə edildi".
            )
            qaytar
        hələ:
            mesajı gözləyir.reply_text (F "artıq səlahiyyətli istifadəçilər siyahısında".)
        qaytar
    istifadəçi adı_ıd= message.from_user.id
    istifadəçi id = message.reply_to_message.from_user.ıd
    istifadəçi adı = mesajı.reply_to_message.istifadəçi.adya_fail
    Token = ınt_to_alpha (istifadəçi identifikatoru)
    istifadəçi adı = mesajı.istifadəçi adı.adya_fail
    _check = ad_torlaşdırılmış istifadəçilərin alınmasını gözləyin(message.chat.id)
    sayı = 0
    _check da smex üçün:
        sayı += 1
    ınt(miqdarı) == 20 varsa:
        gözləyən mesajı qaytarın.reply_text(
            "Qruplarınızın Səlahiyyətli istifadəçiləri siyahısında (AUL) yalnız 20 istifadəçi ola bilər"
        )
    mö ' cüzə _check deyilsə:
        Assis = {
            "auth_user_id": istifadəçi ıd,
"istifadəçi adı": istifadəçi adı,
            "admin ID": istifadəçi ID,
"Admin Adı": istifadəçi adı,
        }
        saxlanmanın gözlənilməsi istifadəçi_avtobusu(message.chat.id, Token, Assis)
        mesajı gözləyir.reply_text(
            f "bu qrupun Səlahiyyətli istifadəçilərinin siyahısına əlavə edildi".
        )
        qaytar
    hələ:
        mesajı gözləyir.reply_text (F "artıq səlahiyyətli istifadəçilər siyahısında".)


@app.on_message (komanda filters.("icazəsiz") və filters.group)
@Adminactual
asynchronous ağ siyahı qorunması_chat_func ( _ , mesaj: mesaj):
    heç bir mesaj yoxdur.reply_to_message:
        əgər len (mesaj.komanda)!= 2:
            mesajı gözləyir.reply_text(
                "İstifadəçi mesajına cavab verin və ya istifadəçi adı/istifadəçi identifikatorunu göstərin."
            )
            qaytar
        istifadəçi = mesaj.mətn.ayrılıq (No 1)[1]
        əgər " @ " istifadəçi:
            user = istifadəçi.əvəz("@", "")
        istifadəçi = app gözləyir . get_users(istifadəçi)
        Token = ınt_to_alpha gözləyir(user.id)
        silindi = silmə gözləyir_avtobuser istifadəçi(message.chat.id, Token)
        silindi varsa:
            gözləyən mesajı qaytarın.reply_text(
                f "bu qrupun Səlahiyyətli istifadəçilərinin siyahısından silindi".
            )
        hələ:
            gözləyən mesajı qaytarın.reply_text (f "qeyri-səlahiyyətli istifadəçi".)
    istifadəçi id = message.reply_to_message.from_user.ıd
    Token = ınt_to_alpha (istifadəçi identifikatoru)
    silindi = silmə gözləyir_avtobuser istifadəçi(message.chat.id, Token)
    silindi varsa:
        gözləyən mesajı qaytarın.reply_text(
            f "bu qrupun Səlahiyyətli istifadəçilərinin siyahısından silindi".
        )
    hələ:
        gözləyən mesajı qaytarın.reply_text (f "qeyri-səlahiyyətli istifadəçi".)


@app.on_message (filters.komanda ("istifadəçilər") və filters.group)
asynchronous istifadəçi tərifi ( _ , mesaj: mesaj):
    _playlist = ad_torlaşdırılmış istifadəçilərin alınmasını gözləyir(message.chat.id)
    _pleylist yoxsa:
        gözləyən mesajı qaytarın.reply_text(
            f " bu qrupda səlahiyyətli istifadəçilər yoxdur.\ N \ NADD / icazə istifadə edərək, istifadəçilər authenticate və /unauthenticated istifadə edərək aradan qaldırılması ."
        )
    hələ:
        j = 0
        m = mesaj gözləyir.reply_text(
            "Səlahiyyətli İstifadəçilərin Seçimi... Xahiş Edirik Gözləyin"
        )
        msg = f "səlahiyyətli istifadəçilərin * * siyahısı[AUL]: * * \ n \ n"
        _playlist qeydlər üçün:
            _ qeyd = get_authuser gözləyir(message.chat.id, qeyd)
            istifadəçi id = _ qeyd["istifadəçi id"]
            istifadəçi adı = _ qeyd["istifadəçi adı"]
            admin_ıd = _ qeyd["admin ID"]
            nazir müavini imya_ad = _ qeyd ["nazir müavini imya_ad"]
            nümunə:
                istifadəçi = app gözləyir . get_users(ıd istifadəçi)
                user = istifadəçi.adya_fail
                j+= 1
            istisna olmaqla:
                davam
            msg + = f"{j} {istifadəçi}[`{istifadəçi identifikatoru}`]\n"
            msg + = f " əlavə edildi: - {Admin Adı} ['{admin ID}'] \ n \ n"
        gözləmə m.edit_text(yazı)
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
