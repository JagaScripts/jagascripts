from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.services.cart_service import CartService
from app.schemas.cart_schemas import CartCreate, CartUpdate, CartResponse

# Logger para controladores
logger = logging.getLogger("services")

router = APIRouter(prefix="/carts", tags=["carts"])

@router.get("/", response_model=List[CartResponse])
def get_carts(
    skip: int = 0, 
    limit: int = 100,
    user_id: int = Query(None, description="Filtrar por ID de usuario"),
    db: Session = Depends(get_db)
):
    """Obtener lista de carritos"""
    try:
        cart_service = CartService(db)
        if user_id:
            carts = cart_service.get_carts_by_user(user_id)
        else:
            carts = cart_service.get_all_carts(skip=skip, limit=limit)
        return carts
    except Exception as e:
        logger.error(f"Error obteniendo carritos: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{cart_id}", response_model=CartResponse)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    """Obtener carrito por ID"""
    try:
        cart_service = CartService(db)
        cart = cart_service.get_cart(cart_id)
        if not cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrito no encontrado"
            )
        return cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo carrito {cart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
def create_cart(cart: CartCreate, db: Session = Depends(get_db)):
    """Crear nuevo carrito"""
    try:
        cart_service = CartService(db)
        new_cart = cart_service.create_cart(cart)
        return new_cart
    except Exception as e:
        logger.error(f"Error creando carrito: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{cart_id}", response_model=CartResponse)
def update_cart(cart_id: int, cart_update: CartUpdate, db: Session = Depends(get_db)):
    """Actualizar carrito existente"""
    try:
        cart_service = CartService(db)
        updated_cart = cart_service.update_cart(cart_id, cart_update)
        if not updated_cart:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrito no encontrado"
            )
        return updated_cart
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando carrito {cart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    """Eliminar carrito"""
    try:
        cart_service = CartService(db)
        success = cart_service.delete_cart(cart_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Carrito no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando carrito {cart_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )