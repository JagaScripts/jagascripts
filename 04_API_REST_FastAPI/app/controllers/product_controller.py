from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product_schemas import ProductCreate, ProductUpdate, ProductResponse

# Logger para controladores
logger = logging.getLogger("services")

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=List[ProductResponse])
def get_products(
    skip: int = 0, 
    limit: int = 100, 
    category: str = Query(None, description="Filtrar por categoría"),
    db: Session = Depends(get_db)
):
    """Obtener lista de productos"""
    try:
        product_service = ProductService(db)
        if category:
            products = product_service.get_products_by_category(category)
        else:
            products = product_service.get_products(skip=skip, limit=limit)
        return products
    except Exception as e:
        logger.error(f"Error obteniendo productos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Obtener producto por ID"""
    try:
        product_service = ProductService(db)
        product = product_service.get_product(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        return product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo producto {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    """Crear nuevo producto"""
    try:
        product_service = ProductService(db)
        new_product = product_service.create_product(product)
        return new_product
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    """Actualizar producto existente"""
    try:
        product_service = ProductService(db)
        updated_product = product_service.update_product(product_id, product_update)
        if not updated_product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
        return updated_product
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando producto {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Eliminar producto"""
    try:
        product_service = ProductService(db)
        success = product_service.delete_product(product_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando producto {product_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )