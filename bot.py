# 1. የሚያስፈልጉ ላይብረሪዎችን ማስገባት
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from PIL import Image

# 2. የቦት ቶከን ማዋቀር (የእርስዎን ቶከን እዚህ ያስገቡ)
TOKEN = "9010960851:AAF9QQgiYhwS2WJ8wH5D51KqoWyyR4vuezg"

# 3. /start ትዕዛዝ ሲጻፍ የሚሰራ ተግባር (ፎቶ እንዲልክ መጠየቅ)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please send me your photo here")

# 4. ፎቶ ሲመጣ የሚሰራ ዋና ተግባር
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    
    # ፎቶው ማቀናበር መጀመሩን የሚገልጽ መልእክት በእንግሊዝኛ መላክ
    processing_msg = await message.reply_text("Your photo is being processed, I will send it when it's done.")
    
    # ተጠቃሚው የላከውን ትልቁን ፎቶ ማግኘት
    photo_file = await message.photo[-1].get_file()
    
    input_path = "user_photo.jpg"
    output_path = "output_photo.png"
    
    # ፎቶውን ወደ ስልካችን ማውረድ
    await photo_file.download_to_drive(input_path)
    
    try:
        # 5. ፎቶውን እና ፍሬሙን በ Pillow ማቀናበር
        user_img = Image.open(input_path).convert("RGBA")
        
        # 'frame.png' ፋይል መኖሩን ማረጋገጥ
        if not os.path.exists("frame.png"):
            await message.reply_text("Error: 'frame.png' file not found!")
            return
            
        frame = Image.open("frame.png").convert("RGBA")
        
        # የሁለቱን ምስሎች መጠን ማስተካከል
        target_size = (1080, 1080)
        user_img = user_img.resize(target_size)
        frame = frame.resize(target_size)
        
        # ፎቶውን እና ፍሬሙን ማደራረብ
        combined = Image.alpha_composite(user_img, frame)
        combined.save(output_path, "PNG")
        
        # 6. የተስተካከለውን ፎቶ ለተጠቃሚው መመለስ
        with open(output_path, "rb") as photo_to_send:
            await message.reply_photo(
                photo=photo_to_send, 
                caption="እነሆ! የጠየቁት ፎቶ ፍሬም ገብቶ ተዘጋጅቷል።"
            )
            
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

# 7. ቦቱን ማስጀመር
def main():
    application = ApplicationBuilder().token(TOKEN).build()
    
    # /start ትዕዛዝን የሚቀበል handler ማስተካከል
    application.add_handler(CommandHandler("start", start))
    
    # ፎቶዎችን ብቻ እንዲቀበል ማጣሪያ ማድረግ
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("ቦቱ በመሥራት ላይ ነው...")
    application.run_polling()

if __name__ == "__main__":
    main()