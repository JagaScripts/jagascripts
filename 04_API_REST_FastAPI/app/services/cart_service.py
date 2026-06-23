from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.cart_model import CartItem
from app.schemas.cart_schemas import CartCreate, CartUpdate
import logging

# Logger específico para servicios
logger = logging.getLogger("services")

class CartService:
    def __init__(self, db: Session):
        self.db = db
        logger.debug("CartService inicializado")
    
    def get_cart(self, cart_id: int) -> Optional[CartItem]:
        """Obtener carrito por ID"""
        logger.debug(f"Buscando carrito por ID: {cart_id}")
        cart = self.db.query(CartItem).filter(CartItem.id == cart_id).first()
        if cart:
            logger.info(f"Carrito encontrado: ID {cart_id}")
        else:
            logger.warning(f"Carrito no encontrado: ID {cart_id}")
        return cart
    
    def get_carts_by_user(self, user_id: int) -> List[CartItem]:
        """Obtener carritos por usuario"""
        logger.debug(f"Buscando carritos del usuario ID: {user_id}")
        carts = self.db.query(CartItem).filter(CartItem.user_id == user_id).all()
        logger.info(f"Se encontraron {len(carts)} carritos para el usuario ID {user_id}")
        return carts
    
    def get_all_carts(self, skip: int = 0, limit: int = 100) -> List[CartItem]:
        """Obtener todos los carritos con paginación"""
        logger.debug(f"Obteniendo lista de carritos - skip: {skip}, limit: {limit}")
        carts = self.db.query(CartItem).offset(skip).limit(limit).all()
        logger.info(f"Se obtuvieron {len(carts)} carritos")
        return carts
    
    def create_cart(self, cart: CartCreate) -> CartItem:
        """Crear nuevo carrito"""
        logger.debug(f"Intentando crear carrito para usuario ID: {cart.user_id}")
        
        # Crear instancia del carrito
        db_cart = CartItem(**cart.dict())
        self.db.add(db_cart)
        self.db.commit()
        self.db.refresh(db_cart)
        logger.info(f"Carrito creado exitosamente: ID {db_cart.id} para usuario ID {cart.user_id}")
        return db_cart
    
    def update_cart(self, cart_id: int, cart_update: CartUpdate) -> Optional[CartItem]:
        """Actualizar carrito existente"""
        logger.debug(f"Intentando actualizar carrito ID: {cart_id}")
        
        db_cart = self.get_cart(cart_id)
        if not db_cart:
            logger.warning(f"Carrito no encontrado para actualizar: ID {cart_id}")
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = cart_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_cart, field, value)
            logger.debug(f"Campo actualizado {field} para carrito ID {cart_id}")
        
        self.db.commit()
        self.db.refresh(db_cart)
        logger.info(f"Carrito actualizado exitosamente: ID {cart_id}")
        return db_cart
    
    def delete_cart(self, cart_id: int) -> bool:
        """Eliminar carrito"""
        logger.debug(f"Intentando eliminar carrito ID: {cart_id}")
        
        db_cart = self.get_cart(cart_id)
        if not db_cart:
            logger.warning(f"Carrito no encontrado para eliminar: ID {cart_id}")
            return False
        
        self.db.delete(db_cart)
        self.db.commit()
        logger.info(f"Carrito eliminado exitosamente: ID {cart_id}")
        return True