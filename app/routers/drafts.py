from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.invoice_models import Borrador, BorradorBase, BorradorResponse, BorradorCreate
from app.db import get_db
from typing import List
from pprint import pprint
from datetime import datetime

router = APIRouter()

@router.get("/consultar-borrador/", tags=['Consulta Borrador'])
async def comprobar_borrador(
    codigo_galac: str,
    fecha: str,  # Supongo que la fecha se pasa como string. Puedes ajustarla si usas formato específico.
    observaciones: str,
    total_facturas: float,
    base_imp_d_desc: float,
    db: Session = Depends(get_db)
):
    # Construir la consulta para buscar el borrador con los parámetros proporcionados
    borrador = db.query(Borrador).filter(
        and_(
            Borrador.codigo_galac == codigo_galac,
            Borrador.fecha == fecha,  # Considera convertir 'fecha' a tipo Date si lo guardas así
            Borrador.observaciones == observaciones,
            Borrador.total_facturas == total_facturas,
            Borrador.base_imp_d_des == base_imp_d_desc
        )
    ).first()  # Usar .first() para obtener un único resultado o None

    # Retornar True si el borrador fue encontrado, False de lo contrario
    return {"exists": borrador is not None}  # Devuelve True/False como un diccionario


@router.post("/borradores/", response_model=BorradorCreate, tags=['Agregar Borrador'])
async def agregar_borrador(borrador: BorradorCreate, db: Session = Depends(get_db)):
    # Verificar si el borrador ya existe antes de agregar
    existing_borrador = db.query(Borrador).filter(
        Borrador.codigo_galac == borrador.codigo_galac,
        Borrador.fecha == borrador.fecha,
        Borrador.observaciones == borrador.observaciones,
        Borrador.total_facturas == borrador.total_facturas,
        #Borrador.codigo_articulo == borrador.codigo_articulo
    ).first()

    if existing_borrador:
        raise HTTPException(status_code=400, detail="El borrador ya existe.")

    # Crear una instancia del modelo Borrador
    nuevo_borrador = Borrador(**borrador.dict())

    # Agregar el borrador a la sesión de la base de datos
    db.add(nuevo_borrador)
    db.commit()  # Confirmar los cambios en la base de datos
    db.refresh(nuevo_borrador)  # Refrescar la instancia para obtener el UUID generado

    # Convierte el UUID a string
    return BorradorResponse(
        uuid=str(nuevo_borrador.uuid),  # Convertimos el UUID a string
        codigo_borrador=nuevo_borrador.codigo_borrador,
        fecha=nuevo_borrador.fecha.isoformat(),  # Convertimos a formato de fecha ISO
        codigo_galac=nuevo_borrador.codigo_galac,
        vendedor=nuevo_borrador.vendedor,
        observaciones=nuevo_borrador.observaciones,
        monto_exento_descuento=nuevo_borrador.monto_exento_descuento,
        base_imp_d_des=nuevo_borrador.base_imp_d_des,
        total_renglones=nuevo_borrador.total_renglones,
        total_iva=nuevo_borrador.total_iva,
        total_facturas=nuevo_borrador.total_facturas,
        por_desc=nuevo_borrador.por_desc,
        status_factura=nuevo_borrador.status_factura,
        tipo_documento=nuevo_borrador.tipo_documento,
        usar_dir_fiscal=nuevo_borrador.usar_dir_fiscal,
        
        # Detalles del artículo
        descripcion=nuevo_borrador.descripcion,
        cantidad=nuevo_borrador.cantidad,
        precio_sin_iva=nuevo_borrador.precio_sin_iva,
        precio_con_iva=nuevo_borrador.precio_con_iva,
        
        # Porcentaje de base
        porcentaje_base=nuevo_borrador.porcentaje_base
    )