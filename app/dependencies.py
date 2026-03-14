from fastapi import Depends, HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from app.models import UsuarioDB
from sqlalchemy.orm import Session
from app.database import get_db

SECRET_KEY = "supersecreto"
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        usuario = db.query(UsuarioDB).filter(
            UsuarioDB.username == username
        ).first()

        if usuario is None:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        return usuario

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def require_role(required_role: str):
    def role_checker(user: UsuarioDB= Depends(get_current_user)):

        if user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos"
            )

        return

    return role_checker
