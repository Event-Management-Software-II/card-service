from flask import request, g
from functools import wraps
import uuid
from .logger import logger

def log_request():
    """Middleware para loguear requests con ID único"""
    g.request_id = str(uuid.uuid4())[:12]
    
    logger.debug(
        f"[{g.request_id}] {request.method} {request.path}",
        extra={
            'request_id': g.request_id,
            'method': request.method,
            'path': request.path,
            'ip': request.remote_addr
        }
    )

def log_response(response):
    """Loguea respuestas"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    logger.info(
        f"[{request_id}] {request.method} {request.path} - {response.status_code}",
        extra={
            'request_id': request_id,
            'method': request.method,
            'path': request.path,
            'status_code': response.status_code
        }
    )
    return response

def handle_error(error):
    """Loguea errores"""
    request_id = getattr(g, 'request_id', 'unknown')
    
    logger.error(
        f"[{request_id}] {request.method} {request.path} - Error: {str(error)}",
        extra={
            'request_id': request_id,
            'error': str(error),
        },
        exc_info=True
    )
