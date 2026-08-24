from fastapi import FastAPI
from order_service.presentation.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title='Order Service')
    app.include_router(router)

    @app.get('/api/health', tags=['health'])
    async def health() -> dict[str, str]:
        return {'status': 'ok'}

    return app


app = create_app()
