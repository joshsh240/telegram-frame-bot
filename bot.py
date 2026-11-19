import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, CallbackQueryHandler, filters, ContextTypes
from PIL import Image, ImageOps

TOKEN = "9252895759:AAFsdO3SIeo84XnCaFvW3tletLJIPC0lFwc"
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

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "send_photo_info":
        await query.message.reply_text("Please upload or send your photo directly in our chat now!")
    elif query.data == "about_bot":
        await query.message.reply_text("This bot automatically adds a custom design frame to your photos instantly!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    await message.reply_text("Your photo is being processed, I will send it when it's done.")

    photo_file = await message.photo[-1].get_file()
    input_path = "user_photo.jpg"
    output_path = "output_photo.png"

    await photo_file.download_to_drive(input_path)

    try:
        user_img = Image.open(input_path)
        user_img = ImageOps.exif_transpose(user_img).convert("RGBA")

        if not os.path.exists("frame.png"):
            await message.reply_text("Error: 'frame.png' file not found in the directory!")
            return

        frame = Image.open("frame.png").convert("RGBA")

        # Keep frame's original size and fit user photo without stretching or cropping
        fitted_photo = ImageOps.contain(user_img, frame.size, method=Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", frame.size, (255, 255, 255, 255))
        x = (frame.width - fitted_photo.width) // 2
        y = (frame.height - fitted_photo.height) // 2
        canvas.paste(fitted_photo, (x, y))

        combined = Image.alpha_composite(canvas, frame)
        combined.save(output_path, "PNG")

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

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is up and running successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()
