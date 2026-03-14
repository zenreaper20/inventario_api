from fastapi import FastAPI
from app.database import Base,engine
from app.routers import productos
from app.routers import auth
from app.routers import users
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi.exceptions import HTTPException as FastAPIHTTPException

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(productos.router)

app.include_router(auth.router)

app.include_router(users.router)

@app.exception_handler(FastAPIHTTPException)
async def custom_http_exception_handler(request: Request, exc: FastAPIHTTPException):

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "code": exc.status_code
        }
    )

@app.get("/health")
def health_check():

    return {"status": "ok"}