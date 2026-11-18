from enum import Enum
class Estado(Enum):
    """Estado del ciclo de vida de un pedido."""

    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    TERMINADO = "TERMINADO"
    CANCELADO = "CANCELADO"
