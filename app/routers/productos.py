from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import csv
import io
from sqlalchemy.orm import Session
from app import crud
from app.database import get_db
from app.schemas import ProductoCreate, ProductoResponse, StatsResponse
from app.dependencies import require_role, get_current_user
from app.models import ProductoDB, UsuarioDB
from app.models import AuditLog
router = APIRouter(
    prefix="/productos",
    tags=["Productos"]
)

@router.post("/", response_model=ProductoResponse)
def crear_producto( producto: ProductoCreate, db: Session = Depends(get_db),user: UsuarioDB = Depends(get_current_user),username = Depends(require_role("admin"))):

    nuevo,prod = crud.crear_producto(db, producto,user)

    crud.crear_log(
        db,
        username=user.username,
        action="crear_producto",
        resource="producto",
        resource_id=prod.id,
        description=f"producto {prod.nombre} creado"
    )

    return nuevo

@router.put("/{id}", response_model=ProductoResponse)
def actualizar(id: int,datos: ProductoCreate,db: Session = Depends(get_db),user: UsuarioDB = Depends(get_current_user),username: dict = Depends(require_role("admin"))):

    actualizado = crud.actualizar_producto(id,datos,db)

    if actualizado is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    crud.crear_log(
        db,
        username=user.username,
        action="actualizar",
        resource="producto",
        resource_id=id,
        description=f"Producto {datos.nombre} actualizado"
    )

    return actualizado

@router.delete("/{id}")
def eliminar(id:int,db: Session = Depends(get_db),user: UsuarioDB = Depends(get_current_user),username: dict= Depends(require_role("admin"))):

    eliminado = crud.eliminar_producto(id,db)

    if eliminado is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    crud.crear_log(
        db,
        username=user.username,
        action="eliminar",
        resource="producto",
        resource_id=id,
        description=f"Producto {eliminado} eliminado"
    )

    return {"mensaje": "Producto eliminado correctamente"}

@router.get("/")
def listar_productos(
    buscar: str = None,
    skip: int = 0,
    limit: int = 10,
    orden: str = None,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):

    return crud.obtener_productos(db, buscar, skip, limit, orden)

@router.get("/logs")
def listar_logs(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: UsuarioDB = Depends(get_current_user)
):

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    return crud.obtener_logs(db, skip, limit)

@router.get("/logs/export")
def exportar_logs(
    db: Session = Depends(get_db),
    user: UsuarioDB = Depends(get_current_user)
):

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "username",
        "action",
        "resource",
        "resource_id",
        "description",
        "timestamp"
    ])

    for log in logs:
        writer.writerow([
            log.id,
            log.username,
            log.action,
            log.resource,
            log.resource_id,
            log.description,
            log.timestamp
        ])

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logs.csv"}
    )

@router.get("/stats", response_model=StatsResponse)
def stats(
    db: Session = Depends(get_db),
    user: UsuarioDB= Depends(get_current_user)
):

    if user.role!= "admin":
        raise HTTPException(status_code=403, detail="No autorizado")

    return crud.obtener_stats(db)