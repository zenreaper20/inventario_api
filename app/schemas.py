from pydantic import BaseModel

class ProductoCreate(BaseModel):
    nombre: str
    precio: float
    stock: int

class StatsResponse(BaseModel):
    total_productos: int
    productos_sin_stock: int
    valor_total_inventario: float | None

class ProductoResponse(ProductoCreate):
    id: int

    class Config:
        from_attributes = True

class UsuarioCreate(BaseModel):
    username: str
    password: str

class UsuarioLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str