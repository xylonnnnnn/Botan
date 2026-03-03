from aiogram import F, Router
from aiogram.filters import CommandStart, Command, state
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from pathlib import Path

import app.keyboards as kb

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет!', reply_markup = kb.menu)

################################################################
################################################################
class Acc(StatesGroup):
    email = State()
    password = State()

@router.callback_query(F.data == 'reg')
async def reg(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Acc.email)
    await callback.message.edit_text('Напишите свою почту')

@router.message(Acc.email, F.text)
async def email(message: Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await state.set_state(Acc.password)
    await message.answer('Напишите свой пароль')

@router.message(Acc.password, F.text)
async def password(message: Message, state: FSMContext):
    password = message.text
    await state.update_data(password=password)
    # здесь проверяем почту и пароль в базе данных
    '''
    if ...:
        await message.answer('Успешно! Выберите действие:', reply_markup=kb.menu)
        
    else:
        await message.answer('Создайте аккаунт на нашем сайте - ...')
    '''
    await message.answer('Успешно! Выберите действие:', reply_markup=kb.functions)
################################################################
################################################################

class mem(StatesGroup):
    type = State()
    description = State()

@router.callback_query(F.data == 'photo')
async def photo(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type='photo')
    await callback.message.edit_text('Загрузите свое фото:')


@router.message(F.photo)
async def get_photo(message: Message, state: FSMContext):
    bot = message.bot
    photo = message.photo[-1]
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    dst = data_dir / f"{photo.file_id}.jpg"
    await bot.download(photo, destination=dst)
    await message.answer(f"✅ Сохранено! Добавьте описание к этой фотографии")
    await state.set_state(mem.description)


@router.callback_query(F.data == 'video')
async def video(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type='video')
    await callback.message.edit_text('Загрузите свое видео:')

@router.message(F.video)
async def get_video(message: Message, state: FSMContext):
    bot = message.bot
    video = message.video
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    dst = data_dir / f"{video.file_id}.mp4"
    await bot.download(video, destination=dst)
    await message.answer("✅ Сохранено! Добавьте описание к этому видео")
    await state.set_state(mem.description)


@router.callback_query(F.data == 'gif')
async def video(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type='gif')
    await callback.message.edit_text('Загрузите свою гифку:')


@router.message(F.animation)
async def get_gif(message: Message, state: FSMContext):
    bot = message.bot
    anim = message.animation
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    dst = data_dir / f"{anim.file_id}.mp4"
    await bot.download(anim, destination=dst)
    await message.answer("✅ Сохранено! Добавьте описание к этой гифке")
    await state.set_state(mem.description)


@router.callback_query(F.data == 'stickers')
async def video(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type='stickers')
    await callback.message.edit_text('Загрузите свой стикер:')

@router.message(F.sticker)
async def get_sticker(message: Message, state: FSMContext):
    bot = message.bot
    sticker = message.sticker

    if sticker.is_animated or sticker.is_video:
        await message.answer("⚠️ Пришлите, пожалуйста, обычный статичный стикер (не анимированный).")
        return

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    dst = data_dir / f"{sticker.file_id}.jpg"
    await bot.download(sticker, destination=dst)
    await message.answer("✅ Сохранено! Добавьте описание к этому стикеру")
    await state.set_state(mem.description)


@router.message(mem.description, F.text)
async def description_photo(message: Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)
    await message.answer(f"✅ Мем загружен")