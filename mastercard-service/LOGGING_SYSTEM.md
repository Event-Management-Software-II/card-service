# Sistema de Logging - Card Service

## Características Implementadas

Este servicio implementa logging completo con:

### Logger (Python)
- **Archivo:** `service-mastercard/app/logger.py`
- **Librería:** `logging` (stdlib)
- **Rotación de archivos:** 5MB por archivo, máximo 10 archivos

### Middleware de Logging
- **Archivo:** `service-mastercard/app/middleware.py`
- **Características:**
  - Request IDs únicos (12 caracteres) para trazabilidad
  - Logging de requests y responses
  - Manejo de excepciones

### Archivos de Log Generados

```
logs/
├── combined.log      # Todos los eventos (DEBUG y superior)
├── error.log         # Solo errores (ERROR y superior)
└── transactions.log  # Detalles de transacciones de tarjetas
```

## Configuración

### Habilitar logs en consola

En `.env`:
```env
FLASK_DEBUG=true
```

## Ejemplo de Logs

### Validación de tarjeta
```
[2026-05-19 14:23:45] DEBUG - card-service - [abc123def4] Validating card (last 4: 0123)
[2026-05-19 14:23:45] INFO - card-service - [abc123def4] Card validated successfully
```

### Procesamiento de cargo
```
[2026-05-19 14:23:46] INFO - card-service - [abc123def4] Processing charge: 100.00 (card: 0123)
[2026-05-19 14:23:46] INFO - card-service.transactions - [abc123def4] CHARGE | Amount: 100.00 | Status: approved | Reference: ORDER-123
```

## Request IDs para Trazabilidad

Cada request obtiene un ID único que aparece en todos los logs:

```
Frontend Request: abc123def4
  └─> event-management [abc123def4]
      └─> payment-orchestrator [abc123def4]
          └─> card-service [abc123def4]
```

Esto permite rastrear una transacción completa a través de todos los servicios.

## Ver Logs

```bash
# Logs en tiempo real
tail -f logs/combined.log
tail -f logs/error.log
tail -f logs/transactions.log

# O en otra terminal mientras se ejecuta el servicio
python run.py
```
