from sqlalchemy.orm import Session
from app.models import ProductoDB
from app.schemas import ProductoCreate
from app.models import UsuarioDB
from app.models import AuditLog
from sqlalchemy import func

def obtener_stats(db: Session):

    total_productos = db.query(func.count(ProductoDB.id)).scalar()

    sin_stock = db.query(func.count(ProductoDB.id)).filter(ProductoDB.stock == 0).scalar()

    valor_inventario = db.query(func.sum(ProductoDB.precio * ProductoDB.stock)).scalar()

    return {
        "total_productos": total_productos,
        "productos_sin_stock": sin_stock,
        "valor_total_inventario": valor_inventario
    }

def crear_log(db, username, action, resource, resource_id=None, description=None):

    log = AuditLog(
        username=username,
        action=action,
        resource=resource,
        resource_id=resource_id,
        description=description
    )

    db.add(log)
    db.commit()

def obtener_logs(db, skip=0, limit=50):

    return db.query(AuditLog).order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

def obtener_stats(db: Session):

    total_productos = db.query(func.count(ProductoDB.id)).scalar()

    sin_stock = db.query(func.count(ProductoDB.id)).filter(ProductoDB.stock == 0).scalar()

    valor_inventario = db.query(func.sum(ProductoDB.precio * ProductoDB.stock)).scalar()

    return {
        "total_productos": total_productos,
        "productos_sin_stock": sin_stock,
        "valor_total_inventario": valor_inventario
    }

def crear_producto(db: Session, producto: ProductoCreate,user: UsuarioDB):

    nuevo = ProductoDB(
        nombre=producto.nombre,
        precio=producto.precio,
        stock=producto.stock,
        user_id=user.id
    )

    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)

    prod: ProductoDB = db.query(ProductoDB).filter(ProductoDB.nombre == producto.nombre).first()

    return nuevo,prod

def actualizar_producto(id: int,datos: ProductoCreate,db: Session):

    producto = db.query(ProductoDB).filter(ProductoDB.id == id).first()

    if producto is None:
        return None

    producto.nombre = datos.nombre
    producto.precio = datos.precio
    producto.stock = datos.stock

    db.commit()
    db.refresh(producto)

    return producto

def eliminar_producto(id,db: Session):

    producto = db.query(ProductoDB).filter(ProductoDB.id == id).first()

    if not producto:
        return None

    nombre_producto = producto.nombre


    db.delete(producto)
    db.commit()

    return nombre_producto

def obtener_productos(db: Session, buscar=None, skip=0, limit=10, orden=None):

    query = db.query(ProductoDB)

    if buscar:
        query = query.filter(ProductoDB.nombre.contains(buscar))

    if orden:
        if orden.startswith("-"):
            campo = orden[1:]
            query = query.order_by(getattr(ProductoDB, campo).desc())
        else:
            query = query.order_by(getattr(ProductoDB, orden))

    productos = query.offset(skip).limit(limit).all()

    return productos