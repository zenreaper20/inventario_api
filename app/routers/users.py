from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.models import UsuarioDB
router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
def get_me(user: UsuarioDB = Depends(get_current_user)):

    return {
        "mensaje": "Usuario autenticado correctamente",
        "username": user.username,
        "role": user.role
    }