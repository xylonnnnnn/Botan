from __future__ import annotations

import hashlib
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import User, Meme, MemeType


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    res = await session.execute(select(User).where(User.email == email))
    return res.scalar_one_or_none()


async def verify_user(session: AsyncSession, email: str, password: str) -> bool:
    user = await get_user_by_email(session, email)
    if not user:
        return False
    return user.password_hash == hash_password(password)


async def create_user(session: AsyncSession, email: str, password: str) -> User:
    user = User(email=email, password_hash=hash_password(password))
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def create_meme(session: AsyncSession, name: str, file_path: str, caption: Optional[str], meme_type: str) -> Meme:
    mapping = {
        "photo": MemeType.photo,
        "video": MemeType.video,
        "gif": MemeType.gif,
        "sticker": MemeType.sticker,
    }
    mt = mapping.get(meme_type)
    meme = Meme(name=name, file_path = file_path, caption=caption, type=mt)
    session.add(meme)
    await session.commit()
    await session.refresh(meme)
    return meme