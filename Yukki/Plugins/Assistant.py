
from inspect import getfullargspec

from pyrogram import filters
from pyrogram.raw.functions.messages import DeleteHistory
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, InlineQueryResultArticle,
                            InlineQueryResultPhoto, InputTextMessageContent,
                            Message)

from Yukki import (ASSID, ASSISTANT_PREFIX, ASSNAME, BOT_ID, BOT_USERNAME,
                   LOG_GROUP_ID, MUSIC_BOT_NAME, SUDOERS, app, userbot)
from Yukki.Database import (approve_pmpermit, disapprove_pmpermit,
                            is_pmpermit_approved)

__MODULE__ = "Assistant"
__HELP__ = f"""

**Note:**
- Only for Sudo Users



{ASSISTANT_PREFIX[0]}block [ Reply to a User Message] 
- Blocks the User from Assistant Account.

{ASSISTANT_PREFIX[0]}unblock [ Reply to a User Message] 
- Unblocks the User from Assistant Account.

{ASSISTANT_PREFIX[0]}approve [ Reply to a User Message] 
- Approves the User for DM.

{ASSISTANT_PREFIX[0]}disapprove [ Reply to a User Message] 
- Disapproves the User for DM.

{ASSISTANT_PREFIX[0]}pfp [ Reply to a Photo] 
- Changes Assistant account PFP.

{ASSISTANT_PREFIX[0]}bio [Bio text] 
- Changes Bio of Assistant Account.

"""

flood = {}


@userbot.on_message(
    filters.private
    & filters.incoming
    & ~filters.service
    & ~filters.edited
    & ~filters.me
    & ~filters.bot
    & ~filters.via_bot
    & ~filters.user(SUDOERS)
)
async def awaiting_message(_, message):
    user_id = message.from_user.id
    if await is_pmpermit_approved(user_id):
        return
    async for m in userbot.iter_history(user_id, limit=6):
        if m.reply_markup:
            await m.delete()
    if str(user_id) in flood:
        flood[str(user_id)] += 1
    else:
        flood[str(user_id)] = 1
    if flood[str(user_id)] > 5:
        await message.reply_text("Spam Detected. User Blocked")
        await userbot.send_message(
            LOG_GROUP_ID,
            f"**Spam Detect Block On Assistant**\n\n- **Blocked User:** {message.from_user.mention}\n- **User ID:** {message.from_user.id}",
        )
        return await userbot.block_user(user_id)
    results = await userbot.get_inline_bot_results(
        BOT_ID, f"permit_to_pm {user_id}"
    )
    await userbot.send_inline_bot_result(
        user_id,
        results.query_id,
        results.results[0].id,
        hide_via=True,
    )


@userbot.on_message(
    filters.command("approve", prefixes=ASSISTANT_PREFIX)
    & filters.user(SUDOERS)
    & ~filters.via_bot
)
async def pm_approve(_, message):
    if not message.reply_to_message:
        return await eor(
            message, text="Reply to a user's message to approve."
        )
    user_id = message.reply_to_message.from_user.id
    if await is_pmpermit_approved(user_id):
        return await eor(message, text="User is already approved to pm")
    await approve_pmpermit(user_id)
    await eor(message, text="User is approved to pm")


@userbot.on_message(
    filters.command("disapprove", prefixes=ASSISTANT_PREFIX)
    & filters.user(SUDOERS)
    & ~filters.via_bot
)
async def pm_disapprove(_, message):
    if not message.reply_to_message:
        return await eor(
            message, text="Reply to a user's message to disapprove."
        )
    user_id = message.reply_to_message.from_user.id
    if not await is_pmpermit_approved(user_id):
        await eor(message, text="User is already disapproved to pm")
        async for m in userbot.iter_history(user_id, limit=6):
            if m.reply_markup:
                try:
                    await m.delete()
                except Exception:
                    pass
        return
    await disapprove_pmpermit(user_id)
    await eor(message, text="User is disapproved to pm")


@userbot.on_message(
    filters.command("block", prefixes=ASSISTANT_PREFIX)
    & filters.user(SUDOERS)
    & ~filters.via_bot
)
async def block_user_func(_, message):
    if not message.reply_to_message:
        return await eor(message, text="Reply to a user's message to block.")
    user_id = message.reply_to_message.from_user.id
    await eor(message, text="Successfully blocked the user")
    await userbot.block_user(user_id)


@userbot.on_message(
    filters.command("unblock", prefixes=ASSISTANT_PREFIX)
    & filters.user(SUDOERS)
    & ~filters.via_bot
)
async def unblock_user_func(_, message):
    if not message.reply_to_message:
        return await eor(
            message, text="Reply to a user's message to unblock."
        )
    user_id = message.reply_to_message.from_user.id
    await userbot.unblock_user(user_id)
    await eor(message, text="Successfully Unblocked the user")


    
@userbot.on_message(
    filters.command("pfp", prefixes=ASSISTANT_PREFIX)
    & filters.user(SUDOERS)
    & ~filters.via_bot
)
async def set_pfp(_, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await eor(message, text="Reply to a photo.") 
    photo = await message.reply_to_message.download()
    try: 
        await userbot.set_profile_photo(photo=photo)   
        await eor(message, text="Successfully Changed PFP.")
    except Exception as e:
        await eor(message, text=e)
    
    
@userbot.on_message(
    filters.command("bio", prefixes=ASSISTANT_PREFIX)
    & filters.user(SUDOERS)
    & ~filters.via_bot
)
async def set_bio(_, message):
    if len(message.command) == 1:
        return await eor(message , text="Give some text to set as bio.") 
    elif len(message.command) > 1:
        bio = message.text.split(None, 1)[1]
        try: 
            await userbot.update_profile(bio=bio) 
            await eor(message , text="Changed Bio.") 
        except Exception as e:
            await eor(message , text=e) 
    else:
        return await eor(message , text="Give some text to set as bio.") 

flood2 = {}

@app.on_callback_query(filters.regex("pmpermit"))
async def pmpermit_cq(_, cq):
    user_id = cq.from_user.id
    data, victim = (
        cq.data.split(None, 2)[1],
        cq.data.split(None, 2)[2],
    )
    if data == "approve":
        if user_id != ASSID:
            return await cq.answer("This Button Is Not For You")
        await approve_pmpermit(int(victim))
        return await app.edit_inline_text(
            cq.inline_message_id, "User Has Been Approved To PM."
        )

    if data == "block":
        if user_id != ASSID:
            return await cq.answer("This Button Is Not For You")
        await cq.answer()
        await app.edit_inline_text(
            cq.inline_message_id, "Successfully blocked the user."
        )
        await userbot.block_user(int(victim))
        return await userbot.send(
            DeleteHistory(
                peer=(await userbot.resolve_peer(victim)),
                max_id=0,
                revoke=False,
            )
        )

    if user_id == ASSID:
        return await cq.answer("It's For The Other Person.")

    if data == "to_scam_you":
        async for m in userbot.iter_history(user_id, limit=6):
            if m.reply_markup:
                await m.delete()
        await userbot.send_message(user_id, "Blocked, Go scam someone else.")
        await userbot.send_message(
            LOG_GROUP_ID,
            f"**Scam Block On Assistant**\n\n- **Blocked User:** {cq.from_user.mention}\n- **User ID:** {user_id}",
        )
        await userbot.block_user(user_id)
        await cq.answer()
    if data == "for_pro":
        async for m in userbot.iter_history(user_id, limit=6):
            if m.reply_markup:
                await m.delete()
        await userbot.send_message(user_id, f"Blocked, No Promotions.")
        await userbot.send_message(
            LOG_GROUP_ID,
            f"**Promotion Block On Assistant**\n\n- **Blocked User:** {cq.from_user.mention}\n- **User ID:** {user_id}",
        )
        await userbot.block_user(user_id)
        await cq.answer()
    elif data == "approve_me":
        await cq.answer()
        if str(user_id) in flood2:
            flood2[str(user_id)] += 1
        else:
            flood2[str(user_id)] = 1
        if flood2[str(user_id)] > 5:
            await userbot.send_message(
                user_id, "SPAM DETECTED, USER BLOCKED."
            )
            await userbot.send_message(
                LOG_GROUP_ID,
                f"**Spam Detect Block On Assistant**\n\n- **Blocked User:** {cq.from_user.mention}\n- **User ID:** {user_id}",
            )
            return await userbot.block_user(user_id)
        await userbot.send_message(
            user_id,
            "I'm busy right now, will approve you shortly, DO NOT SPAM.",
        )


async def pmpermit_func(answers, user_id, victim):
    if user_id != ASSID:
        return
    caption = f"Hi, I'm {ASSNAME}, What are you here for?, You'll be blocked if you send more than 5 messages."
    audio_markup2 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=f"Add {MUSIC_BOT_NAME} To Your Group",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="To Scam You",
                    callback_data=f"pmpermit to_scam_you a",
                ),
                InlineKeyboardButton(
                    text="For Promotion", callback_data=f"pmpermit for_pro a"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Approve me", callback_data=f"pmpermit approve_me a"
                ),
                InlineKeyboardButton(
                    text="Approve", callback_data=f"pmpermit approve {victim}"
                ),
            ],
            [
                InlineKeyboardButton(
                    "Block & Delete", callback_data="pmpermit block {victim}"
                )
            ],
        ]
    )
    answers.append(
        InlineQueryResultArticle(
            title="do_not_click_here",
            reply_markup=audio_markup2,
            input_message_content=InputTextMessageContent(caption),
        )
    )
    return answers


@app.on_inline_query()
async def inline_query_handler(client, query):
    try:
        text = query.query.strip().lower()
        answers = []
        if text.split()[0] == "permit_to_pm":
            user_id = query.from_user.id
            victim = text.split()[1]
            answerss = await pmpermit_func(answers, user_id, victim)
            await client.answer_inline_query(
                query.id, results=answerss, cache_time=2
            )
    except:
        return


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})

ınspect idxal getfullargspec

dan
pirograms pyrogram-dan filtrlər idxal edir.raw.funksiyaları.mesajlar
pirogram aradan qaldırılması tarixi idxal.idxal növləri (zəng sorğusu, ınlinekeyboardbutton düyməsini,
ınlinekeyboardmarkup düyməsini ınlinequeryresultarticle funksiyası,
ınlinequeryresultphoto funksiyası, mətn daxil,
mesaj)

Yukki idxal (ASSID, ASSİSTANT_PREFİX, ASSNAME, BOT_ID, istifadəçi adı,
                   LOG_GROUP_İD, MUSİC_BOT_NAME, istifadəçilər, proqramlar, istifadəçi proqramı)
Yukka ' dan.Verilənlər bazası idxal (approve_pmpermit, cansız_pmpermit,
                            ıs_pmpermit_ təsdiq)

__ Modul _ _ = "köməkçi"
__ Kömək_ _ = f"""

** Qeyd:**
- Yalnız Sudo istifadəçilər üçün



{ASSİSTANT_PREFİX [0]} [istifadəçi mesajına cavab]qarşısını almaq 
- Hesab köməkçisi istifadəçi blokları.

{ASSİSTANT_PREFİX [0]}kilidini açmaq [istifadəçi mesajına cavab] 
- Bir istifadəçi köməkçisi hesabından unlocks.

{ASSİSTANT_PREFİX [0]}Təsdiq [istifadəçi mesajına cavab] 
- DM üçün İstifadəçi təsdiq edir.

{ASSİSTANT_PREFİX [0]}rədd [istifadəçi mesajına cavab] 
- DM üçün İstifadəçi təsdiq etmir.

{ASSİSTANT_PREFİX [0]} pfp [şəkilə cavab] 
- PFP köməkçisinin hesabını dəyişir.

{ASSİSTANT_PREFİX [0]} Bio [mətn Bio] 
- Köməkçi hesabının tərcümeyi-halını dəyişir.

"""

daşqın = {}


@userbot.on_message @xüsusi mesaj(
    filters. özəl
    & filtreler.gələnlər
    & ~filtreler.xidmət
    & ~filtreler.redaktə
    &~filters.me
    & ~filtreler.bot
    & ~filtreler.via_bot
    & ~filtreler.istifadəçi (istifadəçilər)
)
asynchronous gözlənilən tərifi_masad ( _ , mesaj):
    istifadəçi id = message.from_user.ıd
    ıs_pmpermit_approved(istifadəçi identifikatoru)gözləməsi:
        qaytar
    userbot m üçün asynchronousness.iter_history (istifadəçi ID, məhdudiyyət=6):
        əgər M. reply_markup:
            gözləmə m.(sil)
    daşqın zamanı str(istifadəçi ID) varsa:
        daşqın[str (istifadəçi ID)] + = 1
    hələ:
        daşqın[str (istifadəçi ID)] = 1
    daşqın[str(istifadəçi ID)] > 5:
        mesajı gözləyir.reply_text ("spam aşkar edilmişdir. İstifadəçi bağlanacaq")
        istifadəçi gözləyir.send_message(
            LOG_GROUP_ID,
f " **köməkçisi spam aşkar kilidi**\n\n-** istifadəçi kilidli: * * {post.istifadəçi.qeyd} \ n - **istifadəçi ID: * * {message.from_user.id}",
)
        geri istifadəçi gözləyir.block_user(ıd istifadəçi)
    nəticələr userbot gözləyir . get_inline_bot_rezultat(
        BOT_ID, f " permit_to_pm {istifadəçi identifikatoru}"
    )
    istifadəçi gözləyir.send_inline_bot_rezultat(
        istifadəçi ID,
        nəticələr.
ıd sorğu nəticələri. nəticələr[0]. identifikator,
hide_via=Həqiqət,
    )


@userbot.on_message @xüsusi mesaj(
    filters.komanda ("təsdiq edilsin", prefiksləri= ASSİSTANT_PREFİX)
    & filtreler.istifadəçi (istifadəçilər)
    & ~filtreler.via_bot
)
asynchronous pm_approve tərifi ( _ , mesaj):
    heç bir mesaj yoxdur.reply_to_message:
        qaytarılması sizi gözləyir və ya(
            mesaj, mətn = "Təsdiq üçün istifadəçi mesajına cavab verin".
        )
    istifadəçi id = message.reply_to_message.from_user.ıd
    ıs_pmpermit_approved(istifadəçi identifikatoru)gözləməsi:
        geri gözləyir EOR (mesaj, mətn = "istifadəçi artıq pm üçün təsdiq edilmişdir")
    təsdiq gözləyir_pmpermit(istifadəçi ID)
    EOR (mesaj, mətn = "istifadəçi şəxsi kabinet üçün təsdiq edilmişdir")gözləyir


@userbot.on_message @xüsusi mesaj(
    filters.komanda ("Təsdiq etməyin" prefiks= ASSİSTANT_PREFİX)
    & filtreler.istifadəçi (istifadəçilər)
    & ~filtreler.via_bot
)
asynchronous pm_dısapprove tərifi ( _ , mesaj):
    heç bir mesaj yoxdur.reply_to_message:
        qaytarılması sizi gözləyir və ya(
            mesaj, mətn="cansız istifadəçi mesajına cavab verin".
        )
    istifadəçi id = message.reply_to_message.from_user.ıd
    əgər yoxsa, ıs_pmpermit_approved(istifadəçi identifikatoru)gözləyir:
        EOR gözləyir (mesaj, mətn = "istifadəçi artıq pm-də rədd edilir")
        userbot m üçün asynchronousness.iter_history (istifadəçi ID, məhdudiyyət=6):
            əgər M. reply_markup:
                nümunə:
                    gözləmə m.(sil)
                istisna olmaqla:
                    keçmək
        qaytar
    gözlənilməzlik_pmpermit (istifadəçi identifikatoru)
    EOR (mesaj, mətn = "istifadəçi pm üçün təsdiq edilmir")gözləyir


@userbot.on_message @xüsusi mesaj(
    filters.komanda ("qarşısını almaq", prefiksləri= ASSİSTANT_PREFİX)
    & filtreler.istifadəçi (istifadəçilər)
    & ~filtreler.via_bot
)
asynchronous block_ponder_functions ( _ , mesaj):
    heç bir mesaj yoxdur.reply_to_message:
        geri qaytarma gözləyir EOR (mesaj, mətn = "kilidləmək üçün istifadəçi mesajına cavab".)
    istifadəçi id = message.reply_to_message.from_user.ıd
    EOR 'u gözləyin (mesaj, mətn = "uğurla istifadəçi tərəfindən bloklandı")
    istifadəçi gözləyir.istifadəçi adı (istifadəçi identifikatoru)


@userbot.on_message @xüsusi mesaj(
    filters.komanda ("açmaq", prefiksləri= ASSİSTANT_PREFİX)
    & filtreler.istifadəçi (istifadəçilər)
    & ~filtreler.via_bot
)
asynchronous qorunması oxunuş_user_func ( _ , mesaj):
    heç bir mesaj yoxdur.reply_to_message:
        qaytarılması sizi gözləyir və ya(
            mesaj, mətn = "kilidini açmaq üçün istifadəçi mesajına cavab verin".
        )
    istifadəçi id = message.reply_to_message.from_user.ıd
    istifadəçi gözləyir.istifadəçi adı (istifadəçi identifikatoru)
    gözləmə eor (yazı, mətn= "Uğurla etmişlər istifadəçi")


    
@userbot.on_message @xüsusi mesaj(
    filters.komanda ("pfp", prefiks=ASSİSTANT_PREFİX)
    & filtreler.istifadəçi (istifadəçilər)
    & ~filtreler.via_bot
)
asynchronous set_pfp tərifi ( _ , mesaj):
    heç bir mesaj yoxdur.reply_to_message və ya heç bir mesaj.reply_to_message.şəkil:
        geri qaytarma gözləyir EOR (mesaj, mətn = "şəkilə cavab".) 
    şəkil = mesaj gözləyir.reply_to_message.Yüklə()
    nümunə: 
        istifadəçi gözləyir.set_profile_photo (foto =foto)   
        EOR (mesaj, mətn= "uğurla PFP dəyişdirildi") gözləyir.)
    e şəklində istisna olmaqla:
        gözləmə eor (yazı, mətn = e)
    
    
@userbot.on_message @xüsusi mesaj(
    filters.komanda ("bio", prefiksləri= ASSİSTANT_PREFİX)
    & filtreler.istifadəçi (istifadəçilər)
    & ~filtreler.via_bot
)
asynchronous set_bio tərifi ( _ , mesaj):
    əgər len (mesaj.komanda) == 1:
        geri gözləyir EOR (mesaj, mətn = "Bioqrafiya kimi qurmaq üçün bəzi mətn verin"). 
    elif len (mesaj.komanda) > 1:
        Bioqrafiya = mesaj.mətn.ayrılıq (No 1)[1]
        nümunə: 
            istifadəçi gözləyir.update_profile (bio=bio) 
            gözləmə eor (yazı, mətn= "Dəyişdirilmiş tərcümeyi-halı"). 
        e şəklində istisna olmaqla:
            gözləmə eor (yazı, mətn = e) 
    hələ:
        geri gözləyir EOR (mesaj, mətn = "Bioqrafiya kimi qurmaq üçün bəzi mətn verin"). 

daşqın 2 = {}

@app.on_callback_query (filtreler.Daimi ifadə ("pmpermit"))
asynchronous pmpermit_cq tərifi (_, cq):
    istifadəçi id = cq.from_user.ıd
    məlumat qurban = (
cq.data.split (xeyr, 2)[1],
cq.data.split (xeyr, 2)[2],
)
    əgər məlumat = = "Təsdiq":
        bir istifadəçi ID varsa!= ASSID:
            cq cavabını gözləyirəm. ("Bu Düyməsini Sizin Üçün Deyil")
        təsdiq gözləyir_pmpermit(int (qurban))
        bekleyen proqramı geri qaytarın.edit_inline_text(
            cq.ınline_message_id, " istifadəçi şəxsi kabinet üçün təsdiq edilmişdir."
        )

    data == "blok"əgər:
        bir istifadəçi ID varsa!= ASSID:
            cq cavabını gözləyirəm. ("Bu Düyməsini Sizin Üçün Deyil")
        suala cavab gözləyirəm ()
        ərizə gözləyir.edit_inline_text(
            cq.ınline_message_id, "İstifadəçini müvəffəqiyyətlə maneə törətdi".
        )
        istifadəçi gözləyir.block_user(int (qurban))
        geri istifadəçi gözləyir.göndər(
            Tarixi sil(
                peer-to-peer=(istifadəçi gözləyir.resolve_peer(qurban)),
max_id=0,
baxış=Yalan,
)
        )

    əgər istifadəçi id == ASSİD:
        geri qayıdın və cq cavabını gözləyin. ("Bu Başqa Bir Şəxs Üçün").

    əgər bu =="to_scam_you":
        userbot m üçün asynchronousness.iter_history (istifadəçi ID, məhdudiyyət=6):
            əgər M. reply_markup:
                gözləmə m.(sil)
        userbot gözləyirik.send_message (istifadəçi ID, "kilidli, başqa kimsə aldadıcı getmək").
        istifadəçi gözləyir.send_message(
            LOG_GROUP_ID,
f " **köməkçisi kilid scammers**\n\n- * * istifadəçi kilidli: * * {cq.from_user.qeyd}\n - * * istifadəçi ID: * * {istifadəçi ID}",
)
        istifadəçi gözləyir.istifadəçi adı (istifadəçi identifikatoru)
        suala cavab gözləyirəm ()
    əgər bu == "for_pro":
        userbot m üçün asynchronousness.iter_history (istifadəçi ID, məhdudiyyət=6):
            əgər M. reply_markup:
                gözləmə m.(sil)
        userbot gözləyir.send_message (istifadəçi ID, f "bağlanacaq, heç bir reklam payı").
        istifadəçi gözləyir.send_message(
            LOG_GROUP_ID,
f " * * köməkçisi təşviqi Lock * * \ n \ n-**istifadəçi kilidli:**{cq.from_user.qeyd}\n - * * istifadəçi ID: * * {istifadəçi ID}",
)
        istifadəçi gözləyir.istifadəçi adı (istifadəçi identifikatoru)
        suala cavab gözləyirəm ()
    məlumatlar elif = = "təsdiqlər_me":
        suala cavab gözləyirəm ()
        flood2 str(istifadəçi ID) varsa:
            flood2[str (istifadəçi ID)] + = 1
        hələ:
            flood2[str (istifadəçi ID)] = 1
        flood2[str(istifadəçi ID)] > 5:
            istifadəçi gözləyir.send_message(
                istifadəçi identifikatoru, "SPAM aşkar edilmişdir, istifadəçi bloklanır".
            )
            istifadəçi gözləyir.send_message(
                LOG_GROUP_ID,
f " * * köməkçisi spam aşkar kilidi * * \n \ n-**istifadəçi kilidli:**{cq.from_user.qeyd}\n - * * istifadəçi ID: * * {istifadəçi ID}",
)
            geri istifadəçi gözləyir.block_user(ıd istifadəçi)
        istifadəçi gözləyir.send_message(
            istifadəçi ID,
            "Mən İndi məşğulam, tezliklə sizi təsdiqləyəcəyəm, spam etməyin",
)


asynchronous pmpermit_func qorunması (cavablar, istifadəçi ID, qurban):
    bir istifadəçi ID varsa!= ASSID:
        qaytar
    imza = f " Salam, mən {adı ass}, niyə burada var? 5-dən çox mesaj göndərdiyiniz təqdirdə kilidlənəcəksiniz".
    audio_markup2 = встроенныйкейбордмаркап(
        [
[
Daxili klaviatura düyməsini(
                    mətn = f "qrupunuza {İMYA_MUZİYKİ} əlavə et",
url = f"https://t.me / {istifadəçi adı}?startgroup=true",
),
],
[
                Daxili klaviatura düyməsini(
                    text="sizi aldatmaq üçün",
callback_data = f "to_scam_you A istifadə etməyə icazə verin",
),
düyməsini ınlinekeyboardbutton(
                    mətn = "təşviqi üçün" callback_data= f "pmpermit üçün_rgo a"
                ),
],
[
Daxili klaviatura düyməsini(
                    mətn=" Məni təsdiq et", callback_data = f "mənə Bir Təsdiq edək"
                ),
daxili klaviatura düyməsini(
                    mətn=" Təsdiq", callback_data = f"pmpermit {qurban} təsdiq"
                ),
            ],
[
Daxili klaviatura düyməsini(
                    "Qarşısını almaq və aradan qaldırılması" callback_data = "pmpermit {qurban} qarşısını almaq"
                )
            ],
        ]
    )
    cavablar. əlavə(
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
