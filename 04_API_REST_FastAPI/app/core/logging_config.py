import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Crear carpeta logs si no existe
    log_dir = "app/logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handlers para diferentes niveles
    debug_handler = RotatingFileHandler(
        f"{log_dir}/debug.log", maxBytes=10485760, backupCount=5
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)
    
    info_handler = RotatingFileHandler(
        f"{log_dir}/info.log", maxBytes=10485760, backupCount=5  
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)
    
    error_handler = RotatingFileHandler(
        f"{log_dir}/error.log", maxBytes=10485760, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    all_handler = RotatingFileHandler(
        f"{log_dir}/all.log", maxBytes=10485760, backupCount=5
    )
    all_handler.setLevel(logging.DEBUG)
    all_handler.setFormatter(formatter)
    
    # Logger principal
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(debug_handler)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)
    logger.addHandler(all_handler)

    # Logger para servicios
    service_logger = logging.getLogger("services")
    service_logger.setLevel(logging.DEBUG)
    service_logger.addHandler(debug_handler)
    service_logger.addHandler(info_handler) 
    service_logger.addHandler(error_handler)
    service_logger.addHandler(all_handler)