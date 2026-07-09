from sqlalchemy import select, update

from database.models import Feedback, Rating, SongRequest, User
from database.session import async_session


async def get_or_create_user(telegram_id, username):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

        if username and user.username != username:
            user.username = username
            await session.commit()

        return user


async def get_user(user_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


async def get_user_by_telegram_id(telegram_id):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()


async def add_song_request(user_id, song):
    async with async_session() as session:
        request = SongRequest(user_id=user_id, song=song)
        session.add(request)
        await session.commit()
        await session.refresh(request)
        return request


async def get_song_request(request_id):
    async with async_session() as session:
        result = await session.execute(select(SongRequest).where(SongRequest.id == request_id))
        return result.scalar_one_or_none()


async def list_pending_requests():
    async with async_session() as session:
        result = await session.execute(
            select(SongRequest)
            .where(SongRequest.status == "pending")
            .order_by(SongRequest.id.desc())
        )
        return result.scalars().all()


async def update_song_request_status(request_id, status):
    async with async_session() as session:
        await session.execute(update(SongRequest).where(SongRequest.id == request_id).values(status=status))
        await session.commit()


async def block_user(user_id):
    async with async_session() as session:
        user = await session.get(User, user_id)
        if user is not None:
            user.blocked = True
            await session.commit()


async def add_feedback(user_id, message):
    async with async_session() as session:
        feedback = Feedback(user_id=user_id, message=message)
        session.add(feedback)
        await session.commit()
        await session.refresh(feedback)
        return feedback


async def list_feedbacks(limit=10):
    async with async_session() as session:
        result = await session.execute(select(Feedback).order_by(Feedback.id.desc()).limit(limit))
        return result.scalars().all()


async def add_rating(user_id, score):
    async with async_session() as session:
        rating = Rating(user_id=user_id, score=score)
        session.add(rating)
        await session.commit()
        await session.refresh(rating)
        return rating


async def get_rating_stats():
    async with async_session() as session:
        result = await session.execute(select(Rating.score))
        scores = [row[0] for row in result.all()]
        if not scores:
            return {"average": 0, "total_votes": 0}
        return {"average": round(sum(scores) / len(scores), 2), "total_votes": len(scores)}


async def count_users():
    async with async_session() as session:
        result = await session.execute(select(User))
        return len(result.scalars().all())


async def count_requests():
    async with async_session() as session:
        result = await session.execute(select(SongRequest))
        return len(result.scalars().all())