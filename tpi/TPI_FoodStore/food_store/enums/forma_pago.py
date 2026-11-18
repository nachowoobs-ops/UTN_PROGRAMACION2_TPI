from enum import Enum
class FormaPago(Enum):
    """Forma de pago elegida para un pedido."""

    TARJETA = "TARJETA"
    TRANSFERENCIA = "TRANSFERENCIA"
    EFECTIVO = "EFECTIVO"
