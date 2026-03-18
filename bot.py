from datetime import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)

import config
import storage

Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10, Q11, Q12, Q13, Q14, Q15 = range(15)

questions = [
       "Не был ли я в течение дня раздражительным, злобным?",
    "По каким поводам я испытывал беспокойство и жалость к себе?",
    "В чем я был эгоистичным?",
    "В чем был нечестным?",
    "По какому поводу испытывал страх?",
    "Не думал ли я опять в основном только о себе?",
    "Думал ли я и делал ли что-то для других?",
    "Был ли я честен перед собой и другими людьми?",
    "Не совершил ли корыстные и бесчестные поступки?",
    "Не нанес ли я ущерб или обиду людям?",
    "Не нужно ли мне завтра извиниться или возместить ущерб?",
    "Не затаил ли я что-то про себя, есть ли ситуация для обсуждения со спонсором?",
    "Проявлял ли я любовь и доброту ко всем окружающим?",
    "Что я мог бы сделать лучше?"

    "Оцени день от 1 до 10"
]

user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    users = context.bot_data.get("users", set())
    users.add(user_id)
    context.bot_data["users"] = users

    await update.message.reply_text(
        "Привет 🙏\nЯ буду писать тебе каждый вечер.\nНажми кнопку ниже 👇",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Начать", callback_data="start_evening")]
        ])
    )

async def start_evening(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_answers[user_id] = []

    await update.message.reply_text(questions[0])
    return Q1

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "start_evening":
        user_answers[query.from_user.id] = []
        await query.message.reply_text(questions[0])
        return Q1

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_answers[user_id].append(update.message.text)

    step = len(user_answers[user_id])

    if step < len(questions):
        await update.message.reply_text(questions[step])
        return step
    else:
        answers = user_answers[user_id]
        storage.add_entry(user_id, answers)

        await update.message.reply_text("✅ Сохранено. Спасибо 🙏")
        return ConversationHandler.END

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = storage.load_data()
    user_id = str(update.effective_user.id)

    if user_id not in data:
        await update.message.reply_text("Нет данных")
        return

    moods = [int(x["mood"]) for x in data[user_id] if x.get("mood")]
    avg = sum(moods) / len(moods)

    await update.message.reply_text(f"📊 Средняя оценка: {avg:.2f}")

async def reminder(context: ContextTypes.DEFAULT_TYPE):
    users = context.bot_data.get("users", set())

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Начать", callback_data="start_evening")]
    ])

    for user_id in users:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text="🌙 Время вечернего самоанализа",
                reply_markup=keyboard
            )
        except:
            pass

app = ApplicationBuilder().token(config.TOKEN).build()

conv = ConversationHandler(
    entry_points=[
        CommandHandler("evening", start_evening),
        CallbackQueryHandler(button_handler)
    ],
  states = {
    Q1: [MessageHandler(filters.TEXT, handle_answer)],
    Q2: [MessageHandler(filters.TEXT, handle_answer)],
    Q3: [MessageHandler(filters.TEXT, handle_answer)],
    Q4: [MessageHandler(filters.TEXT, handle_answer)],
    Q5: [MessageHandler(filters.TEXT, handle_answer)],
    Q6: [MessageHandler(filters.TEXT, handle_answer)],
    Q7: [MessageHandler(filters.TEXT, handle_answer)],
    Q8: [MessageHandler(filters.TEXT, handle_answer)],
    Q9: [MessageHandler(filters.TEXT, handle_answer)],
    Q10: [MessageHandler(filters.TEXT, handle_answer)],
    Q11: [MessageHandler(filters.TEXT, handle_answer)],
    Q12: [MessageHandler(filters.TEXT, handle_answer)],
    Q13: [MessageHandler(filters.TEXT, handle_answer)],
    Q14: [MessageHandler(filters.TEXT, handle_answer)],
    Q15: [MessageHandler(filters.TEXT, handle_answer)]
},
    fallbacks=[]
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(conv)

app.job_queue.run_daily(
    reminder,
    time=time(hour=config.REMINDER_HOUR)
)

import asyncio

async def main():
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())