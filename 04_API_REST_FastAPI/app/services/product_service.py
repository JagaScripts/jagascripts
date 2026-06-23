from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.product_model import Product
from app.schemas.product_schemas import ProductCreate, ProductUpdate
import logging

# Logger específico para servicios
logger = logging.getLogger("services")

class ProductService:
    def __init__(self, db: Session):
        self.db = db
        logger.debug("ProductService inicializado")
    
    def get_product(self, product_id: int) -> Optional[Product]:
        """Obtener producto por ID"""
        logger.debug(f"Buscando producto por ID: {product_id}")
        product = self.db.query(Product).filter(Product.id == product_id).first()
        if product:
            logger.info(f"Producto encontrado: {product.title} (ID: {product_id})")
        else:
            logger.warning(f"Producto no encontrado: ID {product_id}")
        return product
    
    def get_products(self, skip: int = 0, limit: int = 100) -> List[Product]:
        """Obtener lista de productos con paginación"""
        logger.debug(f"Obteniendo lista de productos - skip: {skip}, limit: {limit}")
        products = self.db.query(Product).offset(skip).limit(limit).all()
        logger.info(f"Se obtuvieron {len(products)} productos")
        return products
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Obtener productos por categoría"""
        logger.debug(f"Buscando productos por categoría: {category}")
        products = self.db.query(Product).filter(Product.category == category).all()
        logger.info(f"Se encontraron {len(products)} productos en la categoría {category}")
        return products
    
    def create_product(self, product: ProductCreate) -> Product:
        """Crear nuevo producto"""
        logger.debug(f"Intentando crear producto: {product.title}")
        
        # Crear instancia del producto
        db_product = Product(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        logger.info(f"Producto creado exitosamente: {db_product.title} (ID: {db_product.id})")
        return db_product
    
    def update_product(self, product_id: int, product_update: ProductUpdate) -> Optional[Product]:
        """Actualizar producto existente"""
        logger.debug(f"Intentando actualizar producto ID: {product_id}")
        
        db_product = self.get_product(product_id)
        if not db_product:
            logger.warning(f"Producto no encontrado para actualizar: ID {product_id}")
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = product_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
            logger.debug(f"Campo actualizado {field} para producto ID {product_id}")
        
        self.db.commit()
        self.db.refresh(db_product)
        logger.info(f"Producto actualizado exitosamente: {db_product.title} (ID: {product_id})")
        return db_product
    
    def delete_product(self, product_id: int) -> bool:
        """Eliminar producto"""
        logger.debug(f"Intentando eliminar producto ID: {product_id}")
        
        db_product = self.get_product(product_id)
        if not db_product:
            logger.warning(f"Producto no encontrado para eliminar: ID {product_id}")
            return False
        
        self.db.delete(db_product)
        self.db.commit()
        logger.info(f"Producto eliminado exitosamente: {db_product.title} (ID: {product_id})")
        return True