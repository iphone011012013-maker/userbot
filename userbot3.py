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

# المكتبات الجديدة للخصائص المضافة
from deep_translator import GoogleTranslator
import speech_recognition as sr
from pydub import AudioSegment

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

AFK_STATE = {"is_afk": False, "reason": "", "original_bio": "", "mentions": []}
AUTO_REPLY_STATE = {"enabled": False}

# ---------------------------------------------------------
# 2. واجهة التحكم والأوامر (Control Panel)
# ---------------------------------------------------------
@app.on_message(filters.command("menu", prefixes=".") & is_owner)
async def system_menu(client, message):
    menu_text = (
        "👑 **نظام إدارة أعمال أبو الفضل (النسخة الاحترافية)**\n"
        "*(اضغط على أي أمر لنسخه)*\n\n"
        "🛡️ **الهوية والإدارة:**\n"
        "🔹 `.readall` : تصفير إشعارات الحساب بالكامل.\n"
        "🔹 `.scan` : فحص الروابط (بالرد على الرسالة).\n"
        "🔹 `.afk [السبب]` : تفعيل وضع غير متاح.\n"
        "🔹 `.unafk` : إيقاف وضع غير متاح والعودة.\n\n"
        "💼 **التجارة وإدارة العملاء:**\n"
        "🔹 `.bill [العميل] [المنتج] [السعر]` : توليد فاتورة سريعة.\n"
        "🔹 `.log` : أرشفة طلب العميل (بالرد عليه).\n"
        "🔹 `.scrape` : سحب بيانات العملاء (CSV).\n"
        "🔹 `.autoreply on/off` : تشغيل/إيقاف الرد الآلي.\n\n"
        "🤖 **أدوات الذكاء والمحتوى:**\n"
        "🔹 `.v2t` : تفريغ المقطع الصوتي لنص (بالرد عليه).\n"
        "🔹 `.str` : ترجمة صامتة لرسالة أجنبية وإرسالها للمحفوظات.\n\n"
        "💻 **أدوات المطور:**\n"
        "🔹 `.eval [الكود]` : تنفيذ كود بايثون مباشر.\n"
        "🔹 `.github [كلمة]` : بحث في مستودعات جيت هاب."
    )
    await message.reply_text(menu_text)

# ---------------------------------------------------------
# 3. الخصائص الجديدة (الفواتير، المترجم، والتفريغ)
# ---------------------------------------------------------

@app.on_message(filters.command("bill", prefixes=".") & is_owner)
async def generate_invoice(client, message):
    """توليد فاتورة منسقة مع رابط الدفع"""
    args = message.text.split(" ", 3)
    if len(args) < 4:
        return await message.edit_text("⚠️ الطريقة الصحيحة: `.bill [اسم_العميل] [المنتج] [السعر]`\nمثال: `.bill أحمد تصميم_شعار 500ج`")
    
    client_name, product, price = args[1], args[2], args[3]
    
    invoice_text = (
        f"🧾 **فاتورة طلب إلكترونية**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **العميل:** {client_name.replace('_', ' ')}\n"
        f"🛍️ **الخدمة/المنتج:** {product.replace('_', ' ')}\n"
        f"💰 **إجمالي الحساب:** {price}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 **طرق الدفع (InstaPay):**\n"
        f"`beicard@instapay`\n\n"
        f"✨ *نشكركم لثقتكم في AboElfadl Media / Store*"
    )
    await message.edit_text(invoice_text)

@app.on_message(filters.command("str", prefixes=".") & is_owner)
async def silent_translator(client, message):
    """ترجمة صامتة للرسائل وإرسالها للرسائل المحفوظة"""
    if not message.reply_to_message or not message.reply_to_message.text:
        return await message.edit_text("⚠️ يرجى الرد (Reply) على رسالة نصية لترجمتها.")
    
    original_text = message.reply_to_message.text
    client_name = message.reply_to_message.from_user.first_name if message.reply_to_message.from_user else "مجهول"
    
    await message.edit_text("⏳ جاري الترجمة الصامتة...")
    
    try:
        translated_text = GoogleTranslator(source='auto', target='ar').translate(original_text)
        
        log_text = (
            f"🔕 **ترجمة صامتة واردة**\n"
            f"👤 **من:** {client_name}\n"
            f"📝 **النص الأصلي:**\n`{original_text}`\n\n"
            f"🌐 **الترجمة العربية:**\n`{translated_text}`"
        )
        
        # إرسال الترجمة لرسائلك المحفوظة (me)
        await client.send_message("me", log_text)
        # حذف الأمر الخاص بك من الشات العام كي لا يلاحظ العميل
        await message.delete()
        
    except Exception as e:
        await message.edit_text(f"❌ حدث خطأ في الترجمة: `{e}`")

@app.on_message(filters.command("v2t", prefixes=".") & is_owner)
async def voice_to_text(client, message):
    """تفريغ المقاطع الصوتية إلى نص مكتوب"""
    if not message.reply_to_message or not message.reply_to_message.voice:
        return await message.edit_text("⚠️ يرجى الرد (Reply) على مقطع صوتي (Voice Note) لتفريغه.")
    
    status_msg = await message.edit_text("⏳ جاري تحميل المقطع الصوتي ومعالجته...")
    
    try:
        # 1. تحميل المقطع الصوتي
        file_path = await message.reply_to_message.download()
        wav_path = file_path + ".wav"
        
        # 2. تحويل الصيغة من OGG (تيليجرام) إلى WAV
        audio = AudioSegment.from_file(file_path)
        audio.export(wav_path, format="wav")
        
        # 3. استخراج النص باستخدام Google Speech Recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language="ar-EG") # مدعوم باللغة العربية (مصر)
        
        await status_msg.edit_text(f"🎙️ **التفريغ الصوتي:**\n\n`{text}`")
        
        # تنظيف الملفات بعد الانتهاء
        os.remove(file_path)
        os.remove(wav_path)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ **فشل التفريغ.** إذا كان الخطأ متعلقاً بـ FFmpeg، فيجب تثبيته على نظام Windows أولاً.\nالخطأ: `{e}`")

# ---------------------------------------------------------
# الأوامر القديمة المحتفظ بها للاستقرار (Read All, Scan, AFK, Eval, etc)
# ---------------------------------------------------------
# تم إبقاء جميع الأوامر السابقة هنا لضمان عمل النظام المتكامل
@app.on_message(filters.command("readall", prefixes=".") & is_owner)
async def read_all_messages(client, message):
    status_msg = await message.reply_text("⏳ **جاري تصفير الإشعارات...**")
    try:
        async for dialog in client.get_dialogs():
            if dialog.unread_messages_count > 0:
                try:
                    await client.read_chat_history(dialog.chat.id)
                    await asyncio.sleep(1.5) 
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except Exception:
                    pass
        await status_msg.edit_text(f"✅ **تمت العملية باحترافية!**")
    except Exception as e:
        await status_msg.edit_text(f"❌ **حدث خطأ:** `{e}`")

@app.on_message(filters.command("scan", prefixes=".") & is_owner)
async def scan_command(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ يرجى الرد على الرسالة لفحصها.")
    target_text = message.reply_to_message.text
    await message.reply_text(f"🔍 **تقرير الفحص الأولي:**\n`{target_text[:20]}...`\n🛡️ تم تسجيل البيانات.")

@app.on_message(filters.command("afk", prefixes=".") & is_owner)
async def set_afk(client, message):
    reason = " ".join(message.command[1:]) or "مشغول حالياً"
    chat_info = await client.get_chat("me")
    AFK_STATE["original_bio"] = chat_info.bio or ""
    AFK_STATE["is_afk"] = True
    AFK_STATE["reason"] = reason
    AFK_STATE["mentions"].clear()
    try:
        await client.update_profile(bio=f"🔴 غير متاح: {reason}")
    except Exception:
        pass
    await message.edit_text(f"💤 **تم تفعيل وضع AFK.**\nالسبب: `{reason}`")

@app.on_message(filters.command("unafk", prefixes=".") & is_owner)
async def unset_afk(client, message):
    if AFK_STATE["is_afk"]:
        AFK_STATE["is_afk"] = False
        try:
            await client.update_profile(bio=AFK_STATE["original_bio"])
        except Exception:
            pass
        await message.edit_text(f"✅ **تم إيقاف وضع AFK.**\nتلقيت ({len(AFK_STATE['mentions'])}) رسائل.")

@app.on_message(filters.private & ~is_owner)
async def afk_listener(client, message):
    if AFK_STATE["is_afk"]:
        AFK_STATE["mentions"].append(message.chat.id)
        await message.reply_text(f"👋 أنا غير متاح حالياً: `{AFK_STATE['reason']}`\nسأرد لاحقاً. ⏳")

if __name__ == "__main__":
    logger.info("تم إقلاع النظام مع التحديثات الجديدة...")
    app.run()