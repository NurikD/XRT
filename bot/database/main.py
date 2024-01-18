from os import getenv
import asyncpg


async def connect_pg() -> asyncpg.Connection:
    connection = await asyncpg.connect(
        user=getenv('PG_USER'),
        password=getenv('PG_PASSWORD'),
        database=getenv('PG_NAME'),
        host=getenv('PG_HOST')
        )

    return connection
