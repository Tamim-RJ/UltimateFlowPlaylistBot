from sqlalchemy import text

from database.session import engine
from database.models import Base


async def alter_column_to_bigint(conn, table_name: str, column_name: str):
    result = await conn.execute(
        text(
            "SELECT data_type FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = :table_name "
            "AND column_name = :column_name"
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    row = result.first()
    if row and row[0] == "integer":
        await conn.execute(
            text(
                f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE BIGINT USING {column_name}::BIGINT"
            )
        )


async def upgrade_postgres_bigint():
    async with engine.begin() as conn:
        if engine.dialect.name != "postgresql":
            return

        await alter_column_to_bigint(conn, "users", "telegram_id")
        await alter_column_to_bigint(conn, "song_requests", "user_id")
        await alter_column_to_bigint(conn, "feedbacks", "user_id")
        await alter_column_to_bigint(conn, "ratings", "user_id")


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await upgrade_postgres_bigint()