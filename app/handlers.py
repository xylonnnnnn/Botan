from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from pathlib import Path

import app.keyboards as kb

from db.database import session_factory
from db.crud import verify_user, create_meme

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer('Привет!', reply_markup=kb.menu)


class Acc(StatesGroup):
    email = State()
    password = State()


@router.callback_query(F.data == 'reg')
async def reg(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Acc.email)
    await callback.message.edit_text('Напишите свою почту')


@router.message(Acc.email, F.text)
async def email(message: Message, state: FSMContext):
    await state.update_data(email=message.text.strip())
    await state.set_state(Acc.password)
    await message.answer('Напишите свой пароль')


@router.message(Acc.password, F.text)
async def password(message: Message, state: FSMContext):
    data = await state.get_data()
    email = (data.get("email") or "").strip()
    password = message.text.strip()

    async with session_factory()() as session:
        ok = await verify_user(session, email=email, password=password)

    if ok:
        await message.answer('Успешно! Выберите действие:', reply_markup=kb.functions)
    else:
        await message.answer(
            '❌ Аккаунт не найден или пароль неверный. '
            'Создайте аккаунт на нашем сайте.', reply_markup=kb.menu)

    await state.clear()

class mem(StatesGroup):
    type = State()
    name = State()
    file_path = State()
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

    await state.update_data(name=photo.file_id, file_path=str(dst))
    await message.answer("✅ Сохранено! Добавьте подпись (описание) к этому мему")
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

    await state.update_data(name=video.file_id, file_path=str(dst))
    await message.answer("✅ Сохранено! Добавьте подпись (описание) к этому мему")
    await state.set_state(mem.description)


@router.callback_query(F.data == 'gif')
async def gif(callback: CallbackQuery, state: FSMContext):
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

    await state.update_data(name=anim.file_id, file_path=str(dst))
    await message.answer("✅ Сохранено! Добавьте подпись (описание) к этому мему")
    await state.set_state(mem.description)


@router.callback_query(F.data == 'stickers')
async def stickers(callback: CallbackQuery, state: FSMContext):
    await state.update_data(type='sticker')
    await callback.message.edit_text('Загрузите свой стикер:')


@router.message(F.sticker)
async def get_sticker(message: Message, state: FSMContext):
    bot = message.bot
    sticker = message.sticker

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    if sticker.is_animated:
        dst = data_dir / f"{sticker.file_id}.tgs"
    elif sticker.is_video:
        dst = data_dir / f"{sticker.file_id}.webm"
    else:
        dst = data_dir / f"{sticker.file_id}.jpg"

    await bot.download(sticker, destination=dst)

    await state.update_data(name=sticker.file_id, file_path=str(dst))
    await message.answer("✅ Сохранено! Добавьте подпись (описание) к этому мему")
    await state.set_state(mem.description)


@router.message(mem.description, F.text)
async def save_meme(message: Message, state: FSMContext):
    caption = message.text.strip()
    data = await state.get_data()

    meme_type = data.get("type")
    name = data.get("name")
    file_path = data.get("file_path")

    async with session_factory()() as session:
        await create_meme(session, name=name, file_path=file_path, caption=caption, meme_type=meme_type)

    await message.answer("✅ Мем загружен и сохранён в базе!", reply_markup=kb.functions)
    await state.clear()
