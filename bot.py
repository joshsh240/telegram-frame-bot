import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image

# Enter your bot token from @BotFather here
TOKEN = "9252895759:AAGm5kuefSmyecwUXFV3LH1nf5-O-CjVMPs"

# 1. /start command handler with interactive buttons
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼 Send Photo for Frame", callback_data="send_photo_info")],
        [InlineKeyboardButton("ℹ️ About Bot", callback_data="about_bot")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "Hello! Welcome to the Photo Framing Bot.\n\n"
        "Please send me your photo here, and I will apply a nice design frame to it!"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        await update.callback_query.message.edit_text(welcome_text, reply_markup=reply_markup)

# 2. Handle button clicks (Inline Keyboard callbacks)
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "send_photo_info":
        await query.message.reply_text("Please upload or send your photo directly in our chat now!")
    elif query.data == "about_bot":
        await query.message.reply_text("This bot automatically adds a custom design frame to your photos instantly!")

# 3. Handle incoming photos and process them
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # Send a processing status message in English
    await message.reply_text("Your photo is being processed, I will send it when it's done.")
    
    # Get the highest resolution photo file
    photo_file = await message.photo[-1].get_file()
    
    input_path = "user_photo.jpg"
    output_path = "output_photo.png"
    
    # Download the photo locally
    await photo_file.download_to_drive(input_path)
    
    try:
        # Open user image and convert to RGBA
        user_img = Image.open(input_path).convert("RGBA")
        
        # Check if frame.png exists in the same folder
        if not os.path.exists("frame.png"):
            await message.reply_text("Error: 'frame.png' file not found in the directory!")
            return
            
        # Open the design frame image
        frame = Image.open("frame.png").convert("RGBA")
        
        # Resize both images to target resolution
        target_size = (1080, 1080)
        user_img = user_img.resize(target_size)
        frame = frame.resize(target_size)
        
        # Overlay user image with the frame
        combined = Image.alpha_composite(user_img, frame)
        combined.save(output_path, "PNG")
        
        # Send the final framed photo back to the user with buttons
        keyboard = [[InlineKeyboardButton("🔄 Frame Another Photo", callback_data="send_photo_info")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        with open(output_path, "rb") as photo_to_send:
            await message.reply_photo(
                photo=photo_to_send, 
                caption="Here is your framed photo! Enjoy!",
                reply_markup=reply_markup
            )
            
    except Exception as e:
        await message.reply_text(f"An error occurred during processing: {str(e)}")

# 4. Main function to start the bot
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Handlers configuration
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Bot is up and running successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()
