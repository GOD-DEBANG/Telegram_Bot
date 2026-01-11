import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
from services.booking_service import create_booking, search_transport
from pdf.pdf_generator import generate_ticket_pdf

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8272704484:AAHEJRxCkHigR-kgcVaxqkN4M4MNDxjkCOE"

# Conversation states
SOURCE, DESTINATION, MODE, SELECT_OPTION, PASSENGER_NAME, PASSENGER_AGE, SEAT_SELECTION = range(7)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the bot."""
    await update.message.reply_text(
        "Welcome to GoRoute 🌍\n\nUse /book to start booking your journey!"
    )

async def start_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Starts the booking process."""
    await update.message.reply_text(
        "📍 From which city are you traveling? (e.g. Delhi)"
    )
    return SOURCE

async def get_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets source city."""
    context.user_data["source"] = update.message.text
    await update.message.reply_text(
        f"✅ From: {update.message.text}\n\n📍 To which city are you traveling? (e.g. Mumbai)"
    )
    return DESTINATION

async def get_destination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets destination city."""
    context.user_data["destination"] = update.message.text
    
    buttons = [
        [InlineKeyboardButton("🚌 Bus", callback_data="mode_Bus")],
        [InlineKeyboardButton("🚆 Train", callback_data="mode_Train")],
        [InlineKeyboardButton("✈ Flight", callback_data="mode_Flight")]
    ]
    await update.message.reply_text(
        f"✅ Route: {context.user_data['source']} → {context.user_data['destination']}\n\n"
        "🚦 Select your travel mode:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return MODE

async def get_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets travel mode and shows options."""
    query = update.callback_query
    await query.answer()
    
    mode = query.data.split("_")[1]
    context.user_data["mode"] = mode
    
    source = context.user_data["source"]
    dest = context.user_data["destination"]
    
    await query.edit_message_text(f"🔍 Searching for {mode}s from {source} to {dest}...")
    
    # Get mock options
    options = search_transport(source, dest, mode)
    context.user_data["options"] = options
    
    # Create buttons for options
    keyboard = []
    for idx, opt in enumerate(options):
        text = f"{opt['operator']} ({opt['departure']}-{opt['arrival']}) - ₹{opt['price']}"
        keyboard.append([InlineKeyboardButton(text, callback_data=f"opt_{idx}")])
        
    await query.edit_message_text(
        f"📋 Available {mode}s:\nSelect one to proceed:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return SELECT_OPTION

async def select_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles option selection."""
    query = update.callback_query
    await query.answer()
    
    idx = int(query.data.split("_")[1])
    selected_opt = context.user_data["options"][idx]
    context.user_data["selected_option"] = selected_opt
    
    await query.edit_message_text(
        f"✅ Selected: {selected_opt['operator']}\n"
        f"🕒 Time: {selected_opt['departure']} - {selected_opt['arrival']}\n"
        f"💰 Price: ₹{selected_opt['price']}\n\n"
        "👤 Please enter Passenger Name:"
    )
    return PASSENGER_NAME

async def get_passenger_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets passenger name."""
    context.user_data["passenger_name"] = update.message.text
    await update.message.reply_text("🎂 Please enter Passenger Age:")
    return PASSENGER_AGE

async def get_passenger_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets age and asks for seat number."""
    age = update.message.text
    if not age.isdigit():
        await update.message.reply_text("❌ Please enter a valid number for age.")
        return PASSENGER_AGE
        
    context.user_data["passenger_age"] = age
    await update.message.reply_text("💺 Please enter your preferred Seat Number (e.g., 12A, S5, 4):")
    return SEAT_SELECTION

async def get_seat_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Gets seat number and generates ticket."""
    seat_num = update.message.text
    context.user_data["seat_number"] = seat_num
    
    # Generate ticket
    await update.message.reply_text("🎫 Generating your ticket... Please wait.")
    
    try:
        user_data = context.user_data
        opt = user_data["selected_option"]
        
        # Override create_booking to use selected option details
        booking = create_booking(
            user={"name": user_data["passenger_name"], "email": "demo@mail.com"},
            mode=user_data["mode"],
            source=user_data["source"],
            destination=user_data["destination"],
            operator=opt["operator"],
            seat_count=1,
            specific_seats=[seat_num]
        )
        
        # Update booking with specific time/price from selection
        booking["departure_time"] = opt["departure"]
        booking["arrival_time"] = opt["arrival"]
        booking["fare"] = opt["price"]

        pdf_file = f"ticket_{booking['ticket_id']}.pdf"
        generate_ticket_pdf(pdf_file, booking)
        
        # Send PDF
        with open(pdf_file, 'rb') as pdf:
            await update.message.reply_document(
                document=pdf,
                filename=f"GoRoute_Ticket_{booking['ticket_id']}.pdf",
                caption=(
                    f"✅ **Booking Confirmed!**\n\n"
                    f"🆔 Ticket ID: `{booking['ticket_id']}`\n"
                    f"👤 Passenger: {booking['name']} ({user_data['passenger_age']})\n"
                    f"🚀 Mode: {booking['mode']} - {booking['operator']}\n"
                    f"📍 Route: {booking['from']} → {booking['to']}\n"
                    f"🕒 Time: {booking['departure_time']} - {booking['arrival_time']}\n"
                    f"💺 Seat: {booking['seats'][0]}\n"
                    f"💰 Fare: ₹{booking['fare']}\n\n"
                    f"✨ Have a safe journey!"
                ),
                parse_mode='Markdown'
            )
            
        if os.path.exists(pdf_file):
            os.remove(pdf_file)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error generating ticket. Please try again.")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the conversation."""
    await update.message.reply_text("🚫 Booking cancelled. Use /book to start again.")
    return ConversationHandler.END

def main():
    """Start the bot."""
    application = Application.builder().token(TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("book", start_booking)],
        states={
            SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_source)],
            DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_destination)],
            MODE: [CallbackQueryHandler(get_mode, pattern="^mode_")],
            SELECT_OPTION: [CallbackQueryHandler(select_option, pattern="^opt_")],
            PASSENGER_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_passenger_name)],
            PASSENGER_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_passenger_age)],
            SEAT_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_seat_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)

    print("🤖 Bot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()