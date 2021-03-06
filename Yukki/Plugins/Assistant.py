
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

??nspect idxal getfullargspec

dan
pirograms pyrogram-dan filtrl??r idxal edir.raw.funksiyalar??.mesajlar
pirogram aradan qald??r??lmas?? tarixi idxal.idxal n??vl??ri (z??ng sor??usu, ??nlinekeyboardbutton d??ym??sini,
??nlinekeyboardmarkup d??ym??sini ??nlinequeryresultarticle funksiyas??,
??nlinequeryresultphoto funksiyas??, m??tn daxil,
mesaj)

Yukki idxal (ASSID, ASS??STANT_PREF??X, ASSNAME, BOT_ID, istifad????i ad??,
                   LOG_GROUP_??D, MUS??C_BOT_NAME, istifad????il??r, proqramlar, istifad????i proqram??)
Yukka ' dan.Veril??nl??r bazas?? idxal (approve_pmpermit, cans??z_pmpermit,
                            ??s_pmpermit_ t??sdiq)

__ Modul _ _ = "k??m??k??i"
__ K??m??k_ _ = f"""

** Qeyd:**
- Yaln??z Sudo istifad????il??r ??????n



{ASS??STANT_PREF??X [0]} [istifad????i mesaj??na cavab]qar????s??n?? almaq 
- Hesab k??m??k??isi istifad????i bloklar??.

{ASS??STANT_PREF??X [0]}kilidini a??maq [istifad????i mesaj??na cavab] 
- Bir istifad????i k??m??k??isi hesab??ndan unlocks.

{ASS??STANT_PREF??X [0]}T??sdiq [istifad????i mesaj??na cavab] 
- DM ??????n ??stifad????i t??sdiq edir.

{ASS??STANT_PREF??X [0]}r??dd [istifad????i mesaj??na cavab] 
- DM ??????n ??stifad????i t??sdiq etmir.

{ASS??STANT_PREF??X [0]} pfp [????kil?? cavab] 
- PFP k??m??k??isinin hesab??n?? d??yi??ir.

{ASS??STANT_PREF??X [0]} Bio [m??tn Bio] 
- K??m??k??i hesab??n??n t??rc??meyi-hal??n?? d??yi??ir.

"""

da??q??n = {}


@userbot.on_message @x??susi mesaj(
    filters. ??z??l
    & filtreler.g??l??nl??r
    & ~filtreler.xidm??t
    & ~filtreler.redakt??
    &~filters.me
    & ~filtreler.bot
    & ~filtreler.via_bot
    & ~filtreler.istifad????i (istifad????il??r)
)
asynchronous g??zl??nil??n t??rifi_masad ( _ , mesaj):
    istifad????i id = message.from_user.??d
    ??s_pmpermit_approved(istifad????i identifikatoru)g??zl??m??si:
        qaytar
    userbot m ??????n asynchronousness.iter_history (istifad????i ID, m??hdudiyy??t=6):
        ??g??r M. reply_markup:
            g??zl??m?? m.(sil)
    da??q??n zaman?? str(istifad????i ID) varsa:
        da??q??n[str (istifad????i ID)] + = 1
    h??l??:
        da??q??n[str (istifad????i ID)] = 1
    da??q??n[str(istifad????i ID)] > 5:
        mesaj?? g??zl??yir.reply_text ("spam a??kar edilmi??dir. ??stifad????i ba??lanacaq")
        istifad????i g??zl??yir.send_message(
            LOG_GROUP_ID,
f " **k??m??k??isi spam a??kar kilidi**\n\n-** istifad????i kilidli: * * {post.istifad????i.qeyd} \ n - **istifad????i ID: * * {message.from_user.id}",
)
        geri istifad????i g??zl??yir.block_user(??d istifad????i)
    n??tic??l??r userbot g??zl??yir . get_inline_bot_rezultat(
        BOT_ID, f " permit_to_pm {istifad????i identifikatoru}"
    )
    istifad????i g??zl??yir.send_inline_bot_rezultat(
        istifad????i ID,
        n??tic??l??r.
??d sor??u n??tic??l??ri. n??tic??l??r[0]. identifikator,
hide_via=H??qiq??t,
    )


@userbot.on_message @x??susi mesaj(
    filters.komanda ("t??sdiq edilsin", prefiksl??ri= ASS??STANT_PREF??X)
    & filtreler.istifad????i (istifad????il??r)
    & ~filtreler.via_bot
)
asynchronous pm_approve t??rifi ( _ , mesaj):
    he?? bir mesaj yoxdur.reply_to_message:
        qaytar??lmas?? sizi g??zl??yir v?? ya(
            mesaj, m??tn = "T??sdiq ??????n istifad????i mesaj??na cavab verin".
        )
    istifad????i id = message.reply_to_message.from_user.??d
    ??s_pmpermit_approved(istifad????i identifikatoru)g??zl??m??si:
        geri g??zl??yir EOR (mesaj, m??tn = "istifad????i art??q pm ??????n t??sdiq edilmi??dir")
    t??sdiq g??zl??yir_pmpermit(istifad????i ID)
    EOR (mesaj, m??tn = "istifad????i ????xsi kabinet ??????n t??sdiq edilmi??dir")g??zl??yir


@userbot.on_message @x??susi mesaj(
    filters.komanda ("T??sdiq etm??yin" prefiks= ASS??STANT_PREF??X)
    & filtreler.istifad????i (istifad????il??r)
    & ~filtreler.via_bot
)
asynchronous pm_d??sapprove t??rifi ( _ , mesaj):
    he?? bir mesaj yoxdur.reply_to_message:
        qaytar??lmas?? sizi g??zl??yir v?? ya(
            mesaj, m??tn="cans??z istifad????i mesaj??na cavab verin".
        )
    istifad????i id = message.reply_to_message.from_user.??d
    ??g??r yoxsa, ??s_pmpermit_approved(istifad????i identifikatoru)g??zl??yir:
        EOR g??zl??yir (mesaj, m??tn = "istifad????i art??q pm-d?? r??dd edilir")
        userbot m ??????n asynchronousness.iter_history (istifad????i ID, m??hdudiyy??t=6):
            ??g??r M. reply_markup:
                n??mun??:
                    g??zl??m?? m.(sil)
                istisna olmaqla:
                    ke??m??k
        qaytar
    g??zl??nilm??zlik_pmpermit (istifad????i identifikatoru)
    EOR (mesaj, m??tn = "istifad????i pm ??????n t??sdiq edilmir")g??zl??yir


@userbot.on_message @x??susi mesaj(
    filters.komanda ("qar????s??n?? almaq", prefiksl??ri= ASS??STANT_PREF??X)
    & filtreler.istifad????i (istifad????il??r)
    & ~filtreler.via_bot
)
asynchronous block_ponder_functions ( _ , mesaj):
    he?? bir mesaj yoxdur.reply_to_message:
        geri qaytarma g??zl??yir EOR (mesaj, m??tn = "kilidl??m??k ??????n istifad????i mesaj??na cavab".)
    istifad????i id = message.reply_to_message.from_user.??d
    EOR 'u g??zl??yin (mesaj, m??tn = "u??urla istifad????i t??r??find??n blokland??")
    istifad????i g??zl??yir.istifad????i ad?? (istifad????i identifikatoru)


@userbot.on_message @x??susi mesaj(
    filters.komanda ("a??maq", prefiksl??ri= ASS??STANT_PREF??X)
    & filtreler.istifad????i (istifad????il??r)
    & ~filtreler.via_bot
)
asynchronous qorunmas?? oxunu??_user_func ( _ , mesaj):
    he?? bir mesaj yoxdur.reply_to_message:
        qaytar??lmas?? sizi g??zl??yir v?? ya(
            mesaj, m??tn = "kilidini a??maq ??????n istifad????i mesaj??na cavab verin".
        )
    istifad????i id = message.reply_to_message.from_user.??d
    istifad????i g??zl??yir.istifad????i ad?? (istifad????i identifikatoru)
    g??zl??m?? eor (yaz??, m??tn= "U??urla etmi??l??r istifad????i")


    
@userbot.on_message @x??susi mesaj(
    filters.komanda ("pfp", prefiks=ASS??STANT_PREF??X)
    & filtreler.istifad????i (istifad????il??r)
    & ~filtreler.via_bot
)
asynchronous set_pfp t??rifi ( _ , mesaj):
    he?? bir mesaj yoxdur.reply_to_message v?? ya he?? bir mesaj.reply_to_message.????kil:
        geri qaytarma g??zl??yir EOR (mesaj, m??tn = "????kil?? cavab".) 
    ????kil = mesaj g??zl??yir.reply_to_message.Y??kl??()
    n??mun??: 
        istifad????i g??zl??yir.set_profile_photo (foto =foto)   
        EOR (mesaj, m??tn= "u??urla PFP d??yi??dirildi") g??zl??yir.)
    e ????klind?? istisna olmaqla:
        g??zl??m?? eor (yaz??, m??tn = e)
    
    
@userbot.on_message @x??susi mesaj(
    filters.komanda ("bio", prefiksl??ri= ASS??STANT_PREF??X)
    & filtreler.istifad????i (istifad????il??r)
    & ~filtreler.via_bot
)
asynchronous set_bio t??rifi ( _ , mesaj):
    ??g??r len (mesaj.komanda) == 1:
        geri g??zl??yir EOR (mesaj, m??tn = "Bioqrafiya kimi qurmaq ??????n b??zi m??tn verin"). 
    elif len (mesaj.komanda) > 1:
        Bioqrafiya = mesaj.m??tn.ayr??l??q (No 1)[1]
        n??mun??: 
            istifad????i g??zl??yir.update_profile (bio=bio) 
            g??zl??m?? eor (yaz??, m??tn= "D??yi??dirilmi?? t??rc??meyi-hal??"). 
        e ????klind?? istisna olmaqla:
            g??zl??m?? eor (yaz??, m??tn = e) 
    h??l??:
        geri g??zl??yir EOR (mesaj, m??tn = "Bioqrafiya kimi qurmaq ??????n b??zi m??tn verin"). 

da??q??n 2 = {}

@app.on_callback_query (filtreler.Daimi ifad?? ("pmpermit"))
asynchronous pmpermit_cq t??rifi (_, cq):
    istifad????i id = cq.from_user.??d
    m??lumat qurban = (
cq.data.split (xeyr, 2)[1],
cq.data.split (xeyr, 2)[2],
)
    ??g??r m??lumat = = "T??sdiq":
        bir istifad????i ID varsa!= ASSID:
            cq cavab??n?? g??zl??yir??m. ("Bu D??ym??sini Sizin ??????n Deyil")
        t??sdiq g??zl??yir_pmpermit(int (qurban))
        bekleyen proqram?? geri qaytar??n.edit_inline_text(
            cq.??nline_message_id, " istifad????i ????xsi kabinet ??????n t??sdiq edilmi??dir."
        )

    data == "blok"??g??r:
        bir istifad????i ID varsa!= ASSID:
            cq cavab??n?? g??zl??yir??m. ("Bu D??ym??sini Sizin ??????n Deyil")
        suala cavab g??zl??yir??m ()
        ??riz?? g??zl??yir.edit_inline_text(
            cq.??nline_message_id, "??stifad????ini m??v??ff??qiyy??tl?? mane?? t??r??tdi".
        )
        istifad????i g??zl??yir.block_user(int (qurban))
        geri istifad????i g??zl??yir.g??nd??r(
            Tarixi sil(
                peer-to-peer=(istifad????i g??zl??yir.resolve_peer(qurban)),
max_id=0,
bax????=Yalan,
)
        )

    ??g??r istifad????i id == ASS??D:
        geri qay??d??n v?? cq cavab??n?? g??zl??yin. ("Bu Ba??qa Bir ????xs ??????n").

    ??g??r bu =="to_scam_you":
        userbot m ??????n asynchronousness.iter_history (istifad????i ID, m??hdudiyy??t=6):
            ??g??r M. reply_markup:
                g??zl??m?? m.(sil)
        userbot g??zl??yirik.send_message (istifad????i ID, "kilidli, ba??qa kims?? aldad??c?? getm??k").
        istifad????i g??zl??yir.send_message(
            LOG_GROUP_ID,
f " **k??m??k??isi kilid scammers**\n\n- * * istifad????i kilidli: * * {cq.from_user.qeyd}\n - * * istifad????i ID: * * {istifad????i ID}",
)
        istifad????i g??zl??yir.istifad????i ad?? (istifad????i identifikatoru)
        suala cavab g??zl??yir??m ()
    ??g??r bu == "for_pro":
        userbot m ??????n asynchronousness.iter_history (istifad????i ID, m??hdudiyy??t=6):
            ??g??r M. reply_markup:
                g??zl??m?? m.(sil)
        userbot g??zl??yir.send_message (istifad????i ID, f "ba??lanacaq, he?? bir reklam pay??").
        istifad????i g??zl??yir.send_message(
            LOG_GROUP_ID,
f " * * k??m??k??isi t????viqi Lock * * \ n \ n-**istifad????i kilidli:**{cq.from_user.qeyd}\n - * * istifad????i ID: * * {istifad????i ID}",
)
        istifad????i g??zl??yir.istifad????i ad?? (istifad????i identifikatoru)
        suala cavab g??zl??yir??m ()
    m??lumatlar elif = = "t??sdiql??r_me":
        suala cavab g??zl??yir??m ()
        flood2 str(istifad????i ID) varsa:
            flood2[str (istifad????i ID)] + = 1
        h??l??:
            flood2[str (istifad????i ID)] = 1
        flood2[str(istifad????i ID)] > 5:
            istifad????i g??zl??yir.send_message(
                istifad????i identifikatoru, "SPAM a??kar edilmi??dir, istifad????i bloklan??r".
            )
            istifad????i g??zl??yir.send_message(
                LOG_GROUP_ID,
f " * * k??m??k??isi spam a??kar kilidi * * \n \ n-**istifad????i kilidli:**{cq.from_user.qeyd}\n - * * istifad????i ID: * * {istifad????i ID}",
)
            geri istifad????i g??zl??yir.block_user(??d istifad????i)
        istifad????i g??zl??yir.send_message(
            istifad????i ID,
            "M??n ??ndi m??????ulam, tezlikl?? sizi t??sdiql??y??c??y??m, spam etm??yin",
)


asynchronous pmpermit_func qorunmas?? (cavablar, istifad????i ID, qurban):
    bir istifad????i ID varsa!= ASSID:
        qaytar
    imza = f " Salam, m??n {ad?? ass}, niy?? burada var? 5-d??n ??ox mesaj g??nd??rdiyiniz t??qdird?? kilidl??n??c??ksiniz".
    audio_markup2 = ??????????????????????????????????????????????(
        [
[
Daxili klaviatura d??ym??sini(
                    m??tn = f "qrupunuza {??MYA_MUZ??YK??} ??lav?? et",
url = f"https://t.me / {istifad????i ad??}?startgroup=true",
),
],
[
                Daxili klaviatura d??ym??sini(
                    text="sizi aldatmaq ??????n",
callback_data = f "to_scam_you A istifad?? etm??y?? icaz?? verin",
),
d??ym??sini ??nlinekeyboardbutton(
                    m??tn = "t????viqi ??????n" callback_data= f "pmpermit ??????n_rgo a"
                ),
],
[
Daxili klaviatura d??ym??sini(
                    m??tn=" M??ni t??sdiq et", callback_data = f "m??n?? Bir T??sdiq ed??k"
                ),
daxili klaviatura d??ym??sini(
                    m??tn=" T??sdiq", callback_data = f"pmpermit {qurban} t??sdiq"
                ),
            ],
[
Daxili klaviatura d??ym??sini(
                    "Qar????s??n?? almaq v?? aradan qald??r??lmas??" callback_data = "pmpermit {qurban} qar????s??n?? almaq"
                )
            ],
        ]
    )
    cavablar. ??lav??(
Yandex uses essential, analytical, marketing and other cookies. These files are necessary to ensure smooth operation of all Yandex sites and services, they help us remember you and your personal settings. For details, please read our Cookie Policy.
View my options
Accept
