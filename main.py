from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api import provider_router, subscription_router
from app.core.database import Base, engine
from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.infra.models import provider_model, subscription_model  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="API Drift")

app.include_router(provider_router.router)
app.include_router(subscription_router.router)


@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(AlreadyExistsError)
def already_exists_handler(request: Request, exc: AlreadyExistsError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
