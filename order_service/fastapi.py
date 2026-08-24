from contextlib import asynccontextmanager

from fastapi import FastAPI
from order_service.presentation.api.dependencies import close_http_clients
from order_service.presentation.api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_http_clients()


def create_app() -> FastAPI:
    app = FastAPI(title='Order Service', lifespan=lifespan)
    app.include_router(router)

    @app.get('/api/health', tags=['health'])
    async def health() -> dict[str, str]:
        return {'status': 'ok'}

    return app


app = create_app()
