from sqlalchemy import Column, Integer, String, Float, ForeignKey
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    resource_id = Column(Integer)
    description = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ProductoDB(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    precio = Column(Float)
    stock = Column(Integer)

    user_id = Column(Integer, ForeignKey("usuarios.id"))

    owner = relationship("UsuarioDB")

class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="user")

    productos = relationship("ProductoDB", back_populates="owner")