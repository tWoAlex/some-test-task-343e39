from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.auth import auth
from app.containers import Container

from app.api.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    container = Container()
    container.init_resources()

    # Задаём структуру БД без миграции
    async with container.db_engine().begin() as conn:
        await conn.run_sync(container.db_metadata().create_all)

    yield
    container.shutdown_resources()


app = FastAPI(lifespan=lifespan)
auth.handle_errors(app)
app.include_router(users_router)
