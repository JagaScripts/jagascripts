from datetime import datetime
import requests
import logging
from sqlalchemy.orm import Session 
from app.models.cart_model import CartItem
from app.models.user_model import User
from app.models.product_model import Product
from app.models.dec_base import DecBase
from app.core.database import engine, get_db

# Constantes para la Fake Store API
FAKE_STORE_API_BASE_URL = "https://fakestoreapi.com"


# Definir los endpoints y sus modelos correspondientes
ENDPOINTS_CONFIG = [
    {
        "url": f"{FAKE_STORE_API_BASE_URL}/products",
        "model": Product,
        "name": "products"
    },
    {
        "url": f"{FAKE_STORE_API_BASE_URL}/users" , 
        "model": User,
        "name": "users"
    },
    {
        "url": f"{FAKE_STORE_API_BASE_URL}/carts",
        "model": CartItem,
        "name": "carts"
    }
]

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("jagastore")

def get_items_model(model_url):
    try:
        response = requests.get(model_url)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"Error al obtener datos de {model_url}: {e}")
        return None
    except requests.RequestException as e:
        logger.error(f"Error de conexión con {model_url}: {e}")
        return None

def insert_data_generic(db: Session, data_list: list, model_class):
    try:
        # Convertir fechas strings a objetos datetime
        for data in data_list:
            if 'date' in data and isinstance(data['date'], str):
                data['date'] = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        
        db.bulk_insert_mappings(model_class, data_list)
        db.commit()
        logger.info(f"Datos insertados en {model_class.__tablename__}: {len(data_list)} registros")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error al insertar datos en {model_class.__tablename__}: {e}")
        return False

if __name__ == "__main__":
    # Crear tablas
    DecBase.metadata.create_all(bind=engine)
    
     # Usar get_db() como generador
    db_generator = get_db()
    db = next(db_generator)
    try:
        for config in ENDPOINTS_CONFIG:
            data = get_items_model(config["url"])
            if data:
                success = insert_data_generic(db, data, config["model"])
                if success:
                    logger.info(f"✅ {config['name']} insertados correctamente")
                else:
                    logger.error(f"❌ Error insertando {config['name']}")
            else:
                logger.error(f"❌ No se pudieron obtener {config['name']}")
                
    finally:
        try:
            next(db_generator)  
        except StopIteration:
            pass