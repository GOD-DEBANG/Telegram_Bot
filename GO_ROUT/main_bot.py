from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from services.booking_service import create_booking
from services.hotel_service import get_hotels
from pdf.pdf_generator import generate_ticket_pdf

TOKEN = "8272704484:AAHEJRxCkHigR-kgcVaxqkN4M4MNDxjkCOE"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to GoRoute 🌍\n\nUse /book to start booking."
    )

async def book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [InlineKeyboardButton("🚌 Bus", callback_data="mode_Bus")],
        [InlineKeyboardButton("🚆 Train", callback_data="mode_Train")],
        [InlineKeyboardButton("✈ Flight", callback_data="mode_Flight")]
    ]
    await update.message.reply_text(
        "Select Travel Mode:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def mode_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    mode = query.data.split("_")[1]
    context.user_data["mode"] = mode

    booking = create_booking(
        user={"name": query.from_user.first_name, "email": "demo@mail.com"},
        mode=mode,
        source="Delhi",
        destination="Lucknow",
        operator="Demo Operator",
        seat_count=2
    )

    pdf_file = f"ticket_{booking['ticket_id']}.pdf"
    generate_ticket_pdf(pdf_file, booking)

    await query.edit_message_text(
        f"🎫 Booking Confirmed!\n\n"
        f"🆔 Ticket ID: {booking['ticket_id']}\n"
        f"👤 Passenger: {booking['name']}\n")