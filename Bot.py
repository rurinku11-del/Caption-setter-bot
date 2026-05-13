from flask import Flask
from threading import Thread

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "I am alive!"


def run():
    # Render provides the port via environment variable
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()
  
import os
import json
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8648928771:AAHbd7KdYYC-HZR-5gIO9GUASLGZ7Yaey74"  # Apna Token yahan daalein
ADMIN_HANDLE = "@Shadow_atomic_21"
STYLE_FILE = "user_styles.json"
THUMB_DIR = "thumbnails"

if not os.path.exists(THUMB_DIR):
    os.makedirs(THUMB_DIR)

# --- DATA PERSISTENCE ---
def load_styles():
    if os.path.exists(STYLE_FILE):
        with open(STYLE_FILE, "r") as f: return json.load(f)
    return {}

def save_styles(data):
    with open(STYLE_FILE, "w") as f: json.dump(data, f)

user_styles = load_styles()

# --- CAPTION ENGINE (30 PREMIUM STYLES) ---
def get_caption(anime, season, ep, quality, audio, power, style_choice):
    ep_str = f"{ep:02d}"
    sn_str = f"{int(season):02d}"
    
    styles = [
        # Style 1: Premium Request 1
        f"<b>{anime} ━━━━━━━━━━━━━━━━━━━━━━━━\n° Season : {sn_str} ° Episode : {ep_str}\n° Quality : {quality}\n° Audio : {audio}\n━━━━━━━━━━━━━━━━━━━━━━━━\n<blockquote>➳ᴘᴏᴡᴇʀᴇᴅ ʙʏ:- {power}</blockquote></b>",
        
        # Style 2: Cleaned (No Anime Name, No Upload Text)
        f"<b>❖  ᴇᴘɪsᴏᴅᴇ: {ep_str}\n✧  ʟᴀɴɢᴜᴀɢᴇ: {audio}\n➠  ǫᴜᴀʟɪᴛʏ: {quality} \n━━━━━━━━━━━━━━\n<blockquote>➳ᴘᴏᴡᴇʀᴇᴅ ʙʏ:- \n{power}</blockquote></b>",

        # Style 3: Elegant Box
        f"<b>╔═══════════════════╗\n  {anime} [S{sn_str}]\n╚═══════════════════╝\n◈ Episode: {ep_str}\n◈ Audio: {audio}\n◈ Quality: {quality}\n<blockquote>🚀 {power}</blockquote></b>",

        # Style 4: Modern Minimal
        f"<b>『 {anime} 』\n────────────────\nSeason: {sn_str} ⚡️ Episode: {ep_str}\nQuality: {quality}\nAudio: {audio}\n<blockquote>🔗 Join: {power}</blockquote></b>",

        # Style 5: Fire Theme
        f"<b>🔥 {anime} 🔥\n━━━━━━━━━━━━━━━\n💥 Season: {sn_str}\n💥 Episode: {ep_str}\n💥 Audio: {audio}\n💥 Quality: {quality}\n<blockquote>✨ Credits: {power}</blockquote></b>",

        # Style 6: Cyberpunk
        f"<b>[ ʟᴏᴀᴅɪɴɢ {anime}... ]\n\n■ ᴇᴘɪsᴏᴅᴇ : {ep_str}\n■ ǫᴜᴀʟɪᴛʏ : {quality}\n■ ᴀᴜᴅɪᴏ : {audio}\n<blockquote>⚡️ sʏsᴛᴇᴍ: {power}</blockquote></b>",

        # Style 7: Diamond Style
        f"<b>💠 {anime} 💠\n\n🔹 Episode : {ep_str}\n🔹 Quality : {quality}\n🔹 Language: {audio}\n<blockquote>💎 {power}</blockquote></b>",

        # Style 8: Heart/Kawaii
        f"<b>🌸 {anime} 🌸\n━━━━━━━━━━━━━━━\n✿ Episode: {ep_str}\n✿ Quality: {quality}\n✿ Audio  : {audio}\n<blockquote>💌 {power}</blockquote></b>",

        # Style 9: Dotted Frame
        f"<b>╭┈─────── ೄྀ࿐ ˊˎ-\n╰┈➤ ❝ {anime} ❞\n\n📍 Ep: {ep_str} | Sn: {sn_str}\n📍 Quality: {quality}\n📍 Audio: {audio}\n<blockquote>🕊️ {power}</blockquote></b>",

        # Style 10: Japanese Look
        f"<b>⛩️ {anime} ⛩️\n🏮 Season: {sn_str}\n🏮 Episode: {ep_str}\n🏮 Audio: {audio}\n<blockquote>🎴 {power}</blockquote></b>",

        # Style 11: Arrow List
        f"<b>➠ {anime} S{sn_str}\n\n➠ Episode : {ep_str}\n➠ Resolution: {quality}\n➠ Language : {audio}\n<blockquote>➠ Join: {power}</blockquote></b>",

        # Style 12: Glass Border
        f"<b>┎┈┈┈┈┈┈┈┈┈┈┈┈┈┒\n  {anime}\n┖┈┈┈┈┈┈┈┈┈┈┈┈┈┚\n◈ Ep: {ep_str} | Q: {quality}\n◈ Audio: {audio}\n<blockquote>🛡️ {power}</blockquote></b>",

        # Style 13: Star Premium
        f"<b>🌟 {anime} 🌟\n\n⭐ Episode: {ep_str}\n⭐ Quality: {quality}\n⭐ Audio: {audio}\n<blockquote>🌟 Uploaded By: {power}</blockquote></b>",

        # Style 14: Simple Clean
        f"<b>● {anime} S{sn_str} ●\n\n◦ Ep: {ep_str}\n◦ Res: {quality}\n◦ Lang: {audio}\n<blockquote>🔗 {power}</blockquote></b>",

        # Style 15: Thunder Bolt
        f"<b>⚡️ {anime} ⚡️\n────────────────\n⚡️ Ep: {ep_str}\n⚡️ Qual: {quality}\n⚡️ Audio: {audio}\n<blockquote>⚡️ Link: {power}</blockquote></b>",

        # Style 16: Ghost Dark
        f"<b>💀 {anime} [S{sn_str}]\n────────────────\n👻 Episode: {ep_str}\n👻 Quality: {quality}\n👻 Audio: {audio}\n<blockquote>🌑 {power}</blockquote></b>",

        # Style 17: Crown Royal
        f"<b>👑 {anime} 👑\n━━━━━━━━━━━━━━━\n🔱 Ep: {ep_str}\n🔱 Res: {quality}\n🔱 Audio: {audio}\n<blockquote>🏰 {power}</blockquote></b>",

        # Style 18: Bubble Tech
        f"<b>🫧 {anime} 🫧\n◌ Ep: {ep_str}\n◌ Res: {quality}\n◌ Lang: {audio}\n<blockquote>🫧 Credit: {power}</blockquote></b>",

        # Style 19: Nature
        f"<b>🍃 {anime} 🍃\n━━━━━━━━━━━━━━━\n🌿 Episode: {ep_str}\n🌿 Quality: {quality}\n🌿 Audio: {audio}\n<blockquote>🍀 {power}</blockquote></b>",

        # Style 20: Cyber Grid
        f"<b>网 {anime} 网\n\n格 Ep: {ep_str}\n格 Res: {quality}\n格 Lang: {audio}\n<blockquote>🌐 {power}</blockquote></b>",

        # Style 21: Sharp Angle
        f"<b>◤ {anime} ◢\n\n➤ Ep: {ep_str}\n➤ Qual: {quality}\n➤ Lang: {audio}\n<blockquote>◢ {power} ◣</blockquote></b>",

        # Style 22: Double Line
        f"<b>═ {anime} ═\n\n║ Season: {sn_str}\n║ Episode: {ep_str}\n║ Audio: {audio}\n<blockquote>═ {power} ═</blockquote></b>",

        # Style 23: Shield Theme
        f"<b>🛡️ {anime} 🛡️\n\n⚔️ Episode: {ep_str}\n⚔️ Quality: {quality}\n⚔️ Language: {audio}\n<blockquote>🛡️ Powered by: {power}</blockquote></b>",

        # Style 24: Square Bullet
        f"<b>▣ {anime} S{sn_str}\n\n▣ Ep: {ep_str}\n▣ Res: {quality}\n▣ Lang: {audio}\n<blockquote>▣ Link: {power}</blockquote></b>",

        # Style 25: Sparkle Mix
        f"<b>✨ {anime} ✨\n━━━━━━━━━━━━━━━\n💎 Ep: {ep_str}\n💎 Q: {quality}\n💎 A: {audio}\n<blockquote>💠 {power}</blockquote></b>",

        # Style 26: Music/Vibe
        f"<b>🎶 {anime} 🎶\n\n🎵 Ep: {ep_str}\n🎵 Qual: {quality}\n🎵 Audio: {audio}\n<blockquote>🎧 {power}</blockquote></b>",

        # Style 27: Cross Theme
        f"<b>☩ {anime} ☩\n\n☩ Ep: {ep_str}\n☩ Qual: {quality}\n☩ Audio: {audio}\n<blockquote>☩ {power} ☩</blockquote></b>",

        # Style 28: Bold Slash
        f"<b>// {anime} //\n\n// Ep: {ep_str}\n// Res: {quality}\n// Lang: {audio}\n<blockquote>// {power} //</blockquote></b>",

        # Style 29: Galaxy/Night
        f"<b>🌌 {anime} 🌌\n━━━━━━━━━━━━━━━\n🌠 Ep: {ep_str}\n🌠 Quality: {quality}\n🌠 Audio: {audio}\n<blockquote>🪐 {power}</blockquote></b>",

        # Style 30: Tech/Robot
        f"<b>🤖 {anime} 🤖\n\n⚙️ Episode: {ep_str}\n⚙️ Quality: {quality}\n⚙️ Audio: {audio}\n<blockquote>⚙️ Powered by {power}</blockquote></b>"
    ]
    
    try:
        idx = int(style_choice) - 1
        return styles[idx] if 0 <= idx < 30 else styles[0]
    except:
        return styles[0]

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "<b>🤖 Welcome to Anime Uploader Bot!</b>\n\n"
        "I can upload videos with custom premium captions.\n\n"
        "<b>Commands:</b>\n"
        "/usage - How to use me\n"
        "/help - Contact Admin\n"
        "/setstyle [1-30] - Set caption style\n"
        "/mystyle - Check current style\n"
        "/preview - Preview current style\n"
        "/see_all - See all 30 styles\n"
        "/thumb - Set custom thumbnail\n"
        "/del_thumb - Delete thumbnail\n"
        "And many more..."
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

async def usage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide = (
        "<b>📖 How to use:</b>\n\n"
        "1. Send your video(s) to the bot.\n"
        "2. Type /done after sending all videos.\n"
        "3. Send details in this format:\n"
        "<code>Anime Name | Season | Quality | Audio | @Channel | StartEP</code>\n\n"
        "Bot will automatically start uploading!"
    )
    await update.message.reply_text(guide, parse_mode="HTML")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆘 For support, contact Admin: {ADMIN_HANDLE}")

async def setstyle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Use: /setstyle 1-30")
        return
    val = context.args[0]
    user_id = str(update.effective_user.id)
    user_styles[user_id] = int(val)
    save_styles(user_styles)
    await update.message.reply_text(f"✅ Style {val} set successfully!")

async def mystyle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = user_styles.get(str(update.effective_user.id), 1)
    await update.message.reply_text(f"🎨 Your current style is: {style}")

async def preview(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    choice = user_styles.get(user_id, 1)
    cap = get_caption("Solo Leveling", "01", 5, "1080p", "Hindi", "@MyChannel", choice)
    await update.message.reply_text(f"<b>Preview Style {choice}:</b>\n\n{cap}", parse_mode="HTML")

async def see_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Generating all 30 styles... please wait.")
    for i in range(1, 31):
        cap = get_caption("Anime Name", "01", i, "720p", "Jap/Eng", "@Channel", i)
        await update.message.reply_text(f"<b>Style {i}:</b>\n\n{cap}", parse_mode="HTML")
        await asyncio.sleep(0.5)

# Thumbnail Management
async def thumb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["waiting_thumb"] = True
    await update.message.reply_text("📸 Now send the photo you want to set as Thumbnail.")

async def show_thumb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = f"{THUMB_DIR}/{update.effective_user.id}.jpg"
    if os.path.exists(path):
        await update.message.reply_photo(photo=open(path, "rb"), caption="🖼️ Your current thumbnail")
    else:
        await update.message.reply_text("❌ No thumbnail set!")

async def del_thumb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = f"{THUMB_DIR}/{update.effective_user.id}.jpg"
    if os.path.exists(path):
        os.remove(path)
        await update.message.reply_text("🗑️ Thumbnail deleted.")
    else:
        await update.message.reply_text("❌ No thumbnail to delete.")

# Video Handling
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If waiting for thumbnail
    if context.user_data.get("waiting_thumb"):
        if update.message.photo:
            file = await update.message.photo[-1].get_file()
            await file.download_to_drive(f"{THUMB_DIR}/{update.effective_user.id}.jpg")
            context.user_data["waiting_thumb"] = False
            await update.message.reply_text("✅ Thumbnail saved successfully!")
            return

    # Normal video saving
    file = update.message.video or update.message.document
    if file:
        context.user_data.setdefault("videos", []).append(file.file_id)
        await update.message.reply_text(f"📥 Video Saved ({len(context.user_data['videos'])})")

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("videos"):
        await update.message.reply_text("❌ Please send videos first!")
        return
    context.user_data["ask_details"] = True
    await update.message.reply_text("✅ Send details in format:\n<code>Anime | Season | Quality | Audio | @channel | StartEP</code>", parse_mode="HTML")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("ask_details"): return
    
    try:
        data = [x.strip() for x in update.message.text.split("|")]
        anime, season, quality, audio, power, start_ep = data
        start_ep = int(start_ep)
    except:
        await update.message.reply_text("❌ Invalid Format! Use:\nAnime | Season | Quality | Audio | @channel | StartEP")
        return

    videos = context.user_data.get("videos", [])
    user_id = str(update.effective_user.id)
    choice = user_styles.get(user_id, 1)
    thumb_path = f"{THUMB_DIR}/{user_id}.jpg"
    actual_thumb = open(thumb_path, "rb") if os.path.exists(thumb_path) else None

    await update.message.reply_text(f"🚀 Starting Upload of {len(videos)} videos...")

    for i, vid in enumerate(videos):
        caption = get_caption(anime, season, start_ep + i, quality, audio, power, choice)
        try:
            if actual_thumb:
                actual_thumb.seek(0) # Reset file pointer for re-use
                await update.message.reply_video(video=vid, caption=caption, thumbnail=actual_thumb, parse_mode="HTML")
            else:
                await update.message.reply_video(video=vid, caption=caption, parse_mode="HTML")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error: {e}")

    await update.message.reply_text("✅ All videos uploaded successfully!")
    context.user_data.clear()

# --- RUN BOT ---
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Commands
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("usage", usage))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(CommandHandler("setstyle", setstyle))
app.add_handler(CommandHandler("mystyle", mystyle))
app.add_handler(CommandHandler("preview", preview))
app.add_handler(CommandHandler("see_all", see_all))
app.add_handler(CommandHandler("reset_cap", setstyle)) # Shortcut
app.add_handler(CommandHandler("del_cap", setstyle))   # Shortcut
app.add_handler(CommandHandler("thumb", thumb))
app.add_handler(CommandHandler("show_thumb", show_thumb))
app.add_handler(CommandHandler("del_thumb", del_thumb))
app.add_handler(CommandHandler("done", done))

# Messages
app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL | filters.PHOTO, handle_video))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

print("⚡ Bot is Running...")
app.run_polling()
