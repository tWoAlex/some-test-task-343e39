from contextlib import asynccontextmanager

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis as AsyncRedis

from app.auth import auth
from app.config import config
from app.containers import Container

from app.api.orders import router as orders_router
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
app.include_router(orders_router, prefix='/orders')


RATE_LIMIT_KEY_TEMPLATE = 'rate_limit: <{host}>'


@app.middleware('http')
@inject
async def rate_limit(
    request: Request,
    call_next,
    redis_client: AsyncRedis = Provide[Container.redis_client]
):
    """ Ограничение частоты запросов """

    key = RATE_LIMIT_KEY_TEMPLATE.format(host=request.client.host)
    current_value = await redis_client.get(key)

    if current_value is None:
        await redis_client.set(
            key,
            config.REQUESTS_PER_MINUTE_FOR_IP - 1,
            ex=60
        )
    elif int(current_value) == 0:
        return JSONResponse(
            content={'detail': {'message': f"Only {config.REQUESTS_PER_MINUTE_FOR_IP} requests per minute allowed"}},
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    else:
        await redis_client.decr(key)

    return await call_next(request)
