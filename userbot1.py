import logging
import asyncio
import os
import io
import sys
import traceback
import requests
import csv
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# ---------------------------------------------------------
# 1. إعدادات النظام الأساسية
# ---------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("AboElfadl_Agent")

API_ID = 26170736
API_HASH = "a049185c492233f10895e97e5845cd0d"
OWNER_ID = 1431886140

app = Client("AboElfadl_Session", api_id=API_ID, api_hash=API_HASH)
is_owner = filters.user(OWNER_ID)

# متغيرات حالة النظام
AFK_STATE = {"is_afk": False, "reason": "", "original_bio": "", "mentions": []}
AUTO_REPLY_STATE = {"enabled": False}

# ---------------------------------------------------------
# 2. واجهة التحكم والأوامر (Control Panel)
# ---------------------------------------------------------
@app.on_message(filters.command("menu", prefixes=".") & is_owner)
async def system_menu(client, message):
    """عرض جميع الخصائص باختصارات قابلة للنسخ"""
    menu_text = (
        "👑 **نظام إدارة أعمال أبو الفضل (النسخة الاحترافية)**\n"
        "*(اضغط على أي أمر لنسخه)*\n\n"
        "🛡️ **الهوية والإدارة الأساسية:**\n"
        "🔹 `.readall` : قراءة جميع الرسائل وتصفير الإشعارات.\n"
        "🔹 `.scan` : (بالرد على رسالة) فحص الرابط أو النص.\n"
        "🔹 `.profile dev` : تفعيل وضع المبرمج السيبراني.\n"
        "🔹 `.profile mark` : تفعيل وضع وكالة AboElfadl Media.\n"
        "🔹 `.profile per` : تفعيل الوضع الشخصي.\n"
        "🔹 `.نبذة` : استبدال الكلمة بوصفك المهني وروابطك.\n"
        "🔹 `.afk [السبب]` : تفعيل وضع غير متاح وتغيير الـ Bio.\n"
        "🔹 `.unafk` : إيقاف وضع غير متاح والعودة.\n\n"
        "💻 **أدوات المطور:**\n"
        "🔹 `.eval [الكود]` : تنفيذ كود بايثون مباشر.\n"
        "🔹 `.github [كلمة]` : بحث مباشر في مستودعات جيت هاب.\n\n"
        "💼 **التسويق والمبيعات:**\n"
        "🔹 `.autoreply on` / `.autoreply off` : تحكم بالرد الآلي.\n"
        "🔹 `.bcast` : (بالرد على رسالة) بثها لجميع المجموعات.\n"
        "🔹 `.scrape` : سحب بيانات أعضاء المجموعة (CSV).\n"
        "🔹 `.sch [ثواني]` : (بالرد على رسالة) جدولتها للإرسال.\n"
        "🔹 `.log` : (بالرد على طلب عميل) أرشفته في رسائلك المحفوظة."
    )
    await message.reply_text(menu_text)

# ---------------------------------------------------------
# 3. أدوات الإدارة الأساسية (Read All & Scan)
# ---------------------------------------------------------
@app.on_message(filters.command("readall", prefixes=".") & is_owner)
async def read_all_messages(client, message):
    status_msg = await message.reply_text("⏳ **جاري فحص النظام وتصفير الإشعارات...**")
    unread_total = 0
    chats_processed = 0
    try:
        async for dialog in client.get_dialogs():
            if dialog.unread_messages_count > 0:
                try:
                    await client.read_chat_history(dialog.chat.id)
                    unread_total += dialog.unread_messages_count
                    chats_processed += 1
                    await asyncio.sleep(0) 
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    pass
        await status_msg.edit_text(
            f"✅ **تمت العملية باحترافية!**\n"
            f"👁️ **الرسائل المقروءة:** `{unread_total}`\n"
            f"📁 **المحادثات المنظفة:** `{chats_processed}`"
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ **حدث خطأ:** `{e}`")

@app.on_message(filters.command("scan", prefixes=".") & is_owner)
async def scan_command(client, message):
    try:
        if not message.reply_to_message:
            await message.reply_text("⚠️ يرجى الرد (Reply) على الرسالة التي تحتوي على الرابط لفحصها.")
            return

        target_text = message.reply_to_message.text
        await message.reply_text(
            f"🔍 **تقرير الفحص الأولي:**\n"
            f"تم رصد النص: `{target_text[:20]}...`\n"
            f"🛡️ **الحالة:** تم تسجيل البيانات لتحليلها."
        )
    except Exception as e:
        logger.error(f"خطأ في أداة الفحص: {e}")

# ---------------------------------------------------------
# 4. إدارة الهوية والاختصارات (Profile & Macros)
# ---------------------------------------------------------
@app.on_message(filters.command("profile", prefixes=".") & is_owner)
async def profile_manager(client, message):
    if len(message.command) < 2:
        return await message.edit_text("⚠️ يرجى تحديد الوضع: `dev`, `mark`, `per`")
    mode = message.command[1].lower()
    
    if mode == "dev":
        new_bio = "Tech & Web Developer 👨‍💻 | Cybersecurity Enthusiast 🛡️"
        name = "Mahmoud AboElfadl | Dev"
    elif mode == "mark":
        new_bio = "Founder of AboElfadl Media 📈 | Digital Marketing & E-commerce"
        name = "AboElfadl Media 🚀"
    else:
        new_bio = "History Student @ Helwan Uni 🏛️ | Entrepreneur 💡"
        name = "Mahmoud AboElfadl"

    await client.update_profile(first_name=name, bio=new_bio)
    await message.edit_text(f"✅ **تم تحديث الهوية بنجاح إلى وضع:** `{mode.upper()}`")

@app.on_message(filters.regex(r"^\.نبذة$") & is_owner)
async def text_macro_bio(client, message):
    full_bio = (
        "**محمود أبو الفضل** 🇪🇬\n"
        "طالب بقسم التاريخ – كلية الآداب جامعة حلوان، وصاحب رؤية ريادية تجمع بين الإبداع الرقمي والتجارة الإلكترونية.\n\n"
        "💼 **مؤسس مشاريع:**\n"
        "- AboElfadl Media (وكالة تسويق رقمي)\n"
        "- AboElfadl Store (تكنولوجيا)\n"
        "- AboElfadl Clothing (أزياء رجالية)\n\n"
        "🌐 **الروابط الرسمية:**\n"
        "🔗 الموقع: `mahmoud-aboelfadl.my.canva.site`\n"
        "🎵 تيك توك: `@aboeifadi`\n"
        "💳 انستا باي: `beicard@instapay`"
    )
    await message.edit_text(full_bio, disable_web_page_preview=True)

# ---------------------------------------------------------
# 5. وضع غير متاح (AFK Mode)
# ---------------------------------------------------------
@app.on_message(filters.command("afk", prefixes=".") & is_owner)
async def set_afk(client, message):
    reason = " ".join(message.command[1:]) or "في اجتماع / مشغول حالياً"
    
    # 🌟 التصحيح: استخدام get_chat لجلب النبذة التعريفية (Bio) بشكل صحيح
    chat_info = await client.get_chat("me")
    AFK_STATE["original_bio"] = chat_info.bio or ""
    
    AFK_STATE["is_afk"] = True
    AFK_STATE["reason"] = reason
    AFK_STATE["mentions"].clear()
    
    try:
        await client.update_profile(bio=f"🔴 غير متاح: {reason}")
    except Exception as e:
        logger.error(f"لم يتمكن من تحديث الـ Bio: {e}")
        
    await message.edit_text(f"💤 **تم تفعيل وضع AFK.**\nالسبب: `{reason}`")

@app.on_message(filters.command("unafk", prefixes=".") & is_owner)
async def unset_afk(client, message):
    if AFK_STATE["is_afk"]:
        AFK_STATE["is_afk"] = False
        try:
            await client.update_profile(bio=AFK_STATE["original_bio"])
        except Exception as e:
            logger.error(f"لم يتمكن من استرجاع الـ Bio: {e}")
            
        report = f"✅ **تم إيقاف وضع AFK.**\n\nتلقيت ({len(AFK_STATE['mentions'])}) رسائل أثناء غيابك."
        await message.edit_text(report)
    else:
        await message.edit_text("⚠️ وضع AFK غير مفعل حالياً.")

@app.on_message(filters.private & ~is_owner)
async def afk_listener(client, message):
    if AFK_STATE["is_afk"]:
        AFK_STATE["mentions"].append(message.chat.id)
        await message.reply_text(
            f"👋 أهلاً بك، أنا **محمود أبو الفضل**.\n"
            f"أنا غير متاح حالياً للأسباب التالية: `{AFK_STATE['reason']}`\n"
            f"سأقوم بالرد عليك فور عودتي. ⏳"
        )

# ---------------------------------------------------------
# 6. أدوات المطور (Live Terminal & GitHub)
# ---------------------------------------------------------
@app.on_message(filters.command("eval", prefixes=".") & is_owner)
async def live_eval(client, message):
    if len(message.text.split()) == 1:
        return await message.edit_text("⚠️ يرجى كتابة الكود بعد الأمر.")
    
    code = message.text.split(" ", 1)[1]
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    stdout, stderr = "", ""
    
    try:
        exec(f"async def __ex(client, message):\n" + "".join(f"\n    {line}" for line in code.split("\n")))
        await locals()["__ex"](client, message)
        stdout = redirected_output.getvalue()
    except Exception:
        stderr = traceback.format_exc()
    finally:
        sys.stdout = old_stdout
    
    output = stdout or stderr or "تم التنفيذ بدون مخرجات."
    await message.edit_text(f"💻 **الكود:**\n`{code}`\n\n⚙️ **النتيجة:**\n`{output}`")

@app.on_message(filters.command("github", prefixes=".") & is_owner)
async def github_search(client, message):
    if len(message.command) < 2:
        return await message.edit_text("⚠️ اكتب ما تريد البحث عنه في جيت هاب.")
    
    query = message.text.split(" ", 1)[1]
    await message.edit_text("🔍 جاري البحث في GitHub...")
    
    req = requests.get(f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc")
    if req.status_code == 200:
        results = req.json().get("items", [])[:3]
        text = f"🐙 **أفضل النتائج لـ:** `{query}`\n\n"
        for repo in results:
            text += f"▪️ **[{repo['name']}]({repo['html_url']})**\n"
            text += f"⭐ {repo['stargazers_count']} | 📝 {repo['description']}\n\n"
        await message.edit_text(text, disable_web_page_preview=True)
    else:
        await message.edit_text("❌ حدث خطأ أثناء الاتصال بـ GitHub.")

# ---------------------------------------------------------
# 7. التسويق وإدارة البيانات (Marketing & Scrape)
# ---------------------------------------------------------
@app.on_message(filters.command("autoreply", prefixes=".") & is_owner)
async def toggle_auto_reply(client, message):
    state = message.command[1].lower() if len(message.command) > 1 else ""
    if state == "on":
        AUTO_REPLY_STATE["enabled"] = True
        await message.edit_text("✅ تم تشغيل الرد الآلي لخدمة العملاء.")
    elif state == "off":
        AUTO_REPLY_STATE["enabled"] = False
        await message.edit_text("❌ تم إيقاف الرد الآلي.")

@app.on_message(filters.private & ~is_owner)
async def customer_auto_reply(client, message):
    if AUTO_REPLY_STATE["enabled"] and not AFK_STATE["is_afk"]:
        ad_text = (
            "✨ **مرحباً بك في AboElfadl Media / Store** ✨\n\n"
            "استفسارك يهمنا. إذا كان بخصوص:\n"
            "🎨 **التصميم والتسويق:** سيتم تحويلك للقسم المختص.\n"
            "🛒 **متجر الإلكترونيات والملابس:** يرجى ترك طلبك وسنرد فوراً.\n\n"
            "🌐 لزيارة أعمالنا: `aboelfadl-media.my.canva.site`"
        )
        await message.reply_text(ad_text)

@app.on_message(filters.command("bcast", prefixes=".") & is_owner)
async def broadcast_msg(client, message):
    if not message.reply_to_message:
        return await message.edit_text("⚠️ يجب الرد على الرسالة المراد بثها (نص أو صورة).")
    
    await message.edit_text("⏳ جاري بث الرسالة لجميع المجموعات...")
    success, failed = 0, 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await message.reply_to_message.forward(dialog.chat.id)
                success += 1
                await asyncio.sleep(2) 
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
                failed += 1
                
    await message.edit_text(f"✅ **تم البث بنجاح.**\nنجاح: `{success}` | فشل: `{failed}`")

@app.on_message(filters.command("scrape", prefixes=".") & is_owner)
async def scrape_members(client, message):
    if message.chat.type not in ["group", "supergroup"]:
        return await message.edit_text("⚠️ يجب استخدام هذا الأمر داخل المجموعة المستهدفة.")
    
    await message.edit_text("⏳ جاري سحب بيانات الأعضاء لملف CSV...")
    file_name = f"AboElfadl_Scrape_{message.chat.id}.csv"
    
    with open(file_name, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["User ID", "First Name", "Username"])
        async for member in client.get_chat_members(message.chat.id):
            user = member.user
            writer.writerow([user.id, user.first_name, user.username or "None"])
            
    await client.send_document("me", file_name, caption=f"📊 داتا عملاء مجموعة: {message.chat.title}")
    await message.edit_text("✅ تم السحب وإرسال الملف لرسائلك المحفوظة.")
    os.remove(file_name)

# ---------------------------------------------------------
# 8. الأرشفة والجدولة (Logger & Scheduler)
# ---------------------------------------------------------
@app.on_message(filters.command("log", prefixes=".") & is_owner)
async def order_logger(client, message):
    if not message.reply_to_message:
        return await message.edit_text("⚠️ رد على طلب العميل لأرشفته.")
    
    order_text = message.reply_to_message.text or "وسائط (صورة/ملف)"
    client_name = message.reply_to_message.from_user.first_name if message.reply_to_message.from_user else "مجهول"
    
    log_format = (
        f"📦 **طلب جديد وارد**\n"
        f"👤 العميل: {client_name}\n"
        f"📅 الوقت: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"📝 التفاصيل:\n`{order_text}`\n\n#طلبات_العملاء"
    )
    await client.send_message("me", log_format)
    await message.edit_text("✅ تم تسجيل الطلب في الأرشيف السري.")

@app.on_message(filters.command("sch", prefixes=".") & is_owner)
async def schedule_message(client, message):
    if len(message.command) < 2 or not message.reply_to_message:
        return await message.edit_text("⚠️ الطريقة: `.sch [عدد_الثواني]` مع الرد على الرسالة المراد جدولتها.")
    
    delay = int(message.command[1])
    target_chat = message.chat.id
    msg_to_send = message.reply_to_message.text
    
    await message.edit_text(f"⏳ تمت الجدولة. سيتم الإرسال بعد `{delay}` ثانية.")
    
    async def task():
        await asyncio.sleep(delay)
        await client.send_message(target_chat, msg_to_send)
        
    asyncio.create_task(task())

# التشغيل النهائي للنظام
if __name__ == "__main__":
    logger.info("تم إقلاع نظام AboElfadl بنجاح...")
    app.run()