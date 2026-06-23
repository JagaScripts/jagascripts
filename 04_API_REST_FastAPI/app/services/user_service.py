from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.user_model import User
from app.schemas.user_schemas import UserCreate, UserUpdate
import logging

# Logger específico para servicios
logger = logging.getLogger("services")

class UserService:
    def __init__(self, db: Session):
        self.db = db
        logger.debug("UserService inicializado")
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        logger.debug(f"Buscando usuario por ID: {user_id}")
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            logger.info(f"Usuario encontrado: {user.email} (ID: {user_id})")
        else:
            logger.warning(f"Usuario no encontrado: ID {user_id}")
        return user
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        logger.debug(f"Buscando usuario por email: {email}")
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            logger.info(f"Usuario encontrado por email: {email}")
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Obtener lista de usuarios con paginación"""
        logger.debug(f"Obteniendo lista de usuarios - skip: {skip}, limit: {limit}")
        users = self.db.query(User).offset(skip).limit(limit).all()
        logger.info(f"Se obtuvieron {len(users)} usuarios")
        return users
    
    def create_user(self, user: UserCreate) -> User:
        """Crear nuevo usuario con validación de email único"""
        logger.debug(f"Intentando crear usuario: {user.email}")
        
        # Verificar si el email ya existe
        if self.get_user_by_email(user.email):
            logger.error(f"Email ya registrado: {user.email}")
            raise ValueError(f"El email {user.email} ya está registrado")
        
        # Crear instancia del usuario
        db_user = User(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Usuario creado exitosamente: {db_user.email} (ID: {db_user.id})")
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Actualizar usuario existente"""
        logger.debug(f"Intentando actualizar usuario ID: {user_id}")
        
        db_user = self.get_user(user_id)
        if not db_user:
            logger.warning(f"Usuario no encontrado para actualizar: ID {user_id}")
            return None
        
        # Actualizar solo los campos proporcionados
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
            logger.debug(f"Campo actualizado {field} para usuario ID {user_id}")
        
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Usuario actualizado exitosamente: {db_user.email} (ID: {user_id})")
        return db_user
    
    def delete_user(self, user_id: int) -> bool:
        """Eliminar usuario"""
        logger.debug(f"Intentando eliminar usuario ID: {user_id}")
        
        db_user = self.get_user(user_id)
        if not db_user:
            logger.warning(f"Usuario no encontrado para eliminar: ID {user_id}")
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        logger.info(f"Usuario eliminado exitosamente: {db_user.email} (ID: {user_id})")
        return True