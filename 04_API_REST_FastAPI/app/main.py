from fastapi import FastAPI
import os
import subprocess
import sys
from app.core.logging_config import setup_logging
from app.controllers import user_controller, product_controller, cart_controller
import logging

# Configurar logging
setup_logging()
logger = logging.getLogger("app")

# Crear aplicación FastAPI
app = FastAPI(
    title="JaGaStore API",
    description="API para ecommerce basada en Fake Store API",
    version="1.0.0"
)

def check_and_populate_database():
    """Verificar si la base de datos existe y poblarla si es necesario"""
    db_path = "app/core/jagastore.db"
    
    if not os.path.exists(db_path):
        logger.info("Base de datos no encontrada. Poblando con datos iniciales...")
        try:
            # Ejecutar el script fill_db.py
            result = subprocess.run(
                [sys.executable, "app/scripts/fill_db.py"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(__file__))  # Ir a la raíz del proyecto
            )
            
            if result.returncode == 0:
                logger.info("✅ Base de datos poblada exitosamente")
            else:
                logger.error(f"❌ Error poblando base de datos: {result.stderr}")
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando fill_db.py: {e}")
    else:
        logger.info("✅ Base de datos encontrada")

@app.on_event("startup")
async def startup_event():
    """Evento al iniciar la aplicación"""
    check_and_populate_database()
    logger.info("🚀 JaGaStore API iniciada")

@app.on_event("shutdown")
async def shutdown_event():
    """Evento al cerrar la aplicación"""
    logger.info("🛑 JaGaStore API detenida")

# Incluir routers
app.include_router(user_controller.router)
app.include_router(product_controller.router)
app.include_router(cart_controller.router)

@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a JaGaStore API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Endpoint de salud"""
    return {"status": "healthy"}