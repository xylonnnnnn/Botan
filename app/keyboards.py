from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = 'Зайти в аккаунт', callback_data='reg')]
])

functions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text = 'Загрузка фото', callback_data='photo')],
    [InlineKeyboardButton(text = 'Загрузка видео', callback_data='video')],
    [InlineKeyboardButton(text = 'Загрузка GIF', callback_data='gif')],
    [InlineKeyboardButton(text = 'Загрузка стикера', callback_data='stickers')]
])