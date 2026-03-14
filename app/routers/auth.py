from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import UsuarioDB
from app.schemas import UsuarioCreate, UsuarioLogin, Token
from passlib.context import CryptContext
from jose import jwt
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth", tags=["Auth"])
SECRET_KEY = "supersecreto"
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):

    return pwd_context.hash(password)

def verify_password(password, hash):

    return pwd_context.verify(password, hash)

@router.post("/register")
def register(user: UsuarioCreate,db: Session = Depends(get_db)):

    existe = db.query(UsuarioDB).filter(UsuarioDB.username == user.username).first()

    if existe:
        raise HTTPException(status_code=400, detail="Usuario ya existe")

    nuevo = UsuarioDB(
    username=user.username,
    password_hash=hash_password(user.password),
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    return {"mensaje": "Usuario registrado correctamente"}

@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    usuario = db.query(UsuarioDB).filter(
        UsuarioDB.username == form_data.username
    ).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not verify_password(form_data.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = jwt.encode(
        {
            "sub": usuario.username,
            "role": usuario.role
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": token, "token_type": "bearer"}
