from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from menu_data import MENU
from orders import OrderManager
import logging
import os

API_TOKEN = os.getenv("BOT_TOKEN")
HUSBAND_CHAT_ID = int(os.getenv("HUSBAND_ID"))

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
order_manager = OrderManager()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=1)
    for key, item in MENU.items():
        markup.add(InlineKeyboardButton(item['title'], callback_data=f"menu_{key}"))
    await message.answer("🍽 Доброе утро! Выберите завтрак:", reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data.startswith("menu_"))
async def show_item(callback_query: types.CallbackQuery):
    item_key = callback_query.data.split("_", 1)[1]
    item = MENU[item_key]
    buttons = InlineKeyboardMarkup()
    buttons.add(
        InlineKeyboardButton("➕ Добавить в заказ", callback_data=f"add_{item_key}"),
        InlineKeyboardButton("🔙 Назад", callback_data="back_to_menu")
    )
    await bot.send_photo(
        chat_id=callback_query.from_user.id,
        photo=item['photo'],
        caption=f"<b>{item['title']}</b>\n{item['description']}\nЦена: {item['price']}₽",
        parse_mode="HTML",
        reply_markup=buttons
    )

@dp.callback_query_handler(lambda c: c.data.startswith("add_"))
async def add_item(callback_query: types.CallbackQuery):
    item_key = callback_query.data.split("_", 1)[1]
    order_manager.add_item(callback_query.from_user.id, item_key, MENU)
    await callback_query.answer("✅ Добавлено в заказ")

@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    await send_welcome(callback_query.message)

@dp.message_handler(commands=['order'])
async def show_order(message: types.Message):
    summary = order_manager.get_order_summary(message.from_user.id)
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("✅ Оформить заказ", callback_data="submit_order"),
        InlineKeyboardButton("🗑 Очистить", callback_data="clear_order")
    )
    await message.answer(summary, reply_markup=markup)

@dp.callback_query_handler(lambda c: c.data == "clear_order")
async def clear_order(callback_query: types.CallbackQuery):
    order_manager.clear_order(callback_query.from_user.id)
    await callback_query.message.answer("🗑 Корзина очищена.")
    await send_welcome(callback_query.message)

@dp.callback_query_handler(lambda c: c.data == "submit_order")
async def submit_order(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    summary = order_manager.get_order_summary(user_id)
    order_manager.clear_order(user_id)
    await callback_query.message.answer("🎉 Заказ оформлен! Муж уже шуршит над завтраком 😎")
    await bot.send_message(HUSBAND_CHAT_ID,
        f"📦 Новый заказ от {callback_query.from_user.first_name}:\n\n{summary}"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)