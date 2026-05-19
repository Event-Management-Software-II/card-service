import atexit

from prisma import Prisma

db = Prisma()
_connected = False


def connect_db():
    global _connected
    if not _connected:
        db.connect()
        _connected = True


def disconnect_db():
    global _connected
    if _connected:
        db.disconnect()
        _connected = False


atexit.register(disconnect_db)
