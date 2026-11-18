"""Entidad DetallePedido."""
from __future__ import annotations

from entidades.base import Base
from entidades.producto import Producto
from entidades.validaciones import es_entero
from excepciones import CantidadInvalidaError, DatoInvalidoError


def validar_cantidad(cantidad: object) -> int:
    """Devuelve la cantidad si es un entero > 0; si no, lanza ``CantidadInvalidaError``."""
    if not es_entero(cantidad) or cantidad <= 0:  # type: ignore[operator]
        raise CantidadInvalidaError("La cantidad debe ser un entero mayor que cero")
    return cantidad  # type: ignore[return-value]

class DetallePedido(Base):
    def __init__(self, cantidad: int, producto: Producto) -> None:
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("El detalle requiere un producto válido")
        self.__cantidad: int = validar_cantidad(cantidad)
        self.__producto: Producto = producto
        self.__subtotal: float = round(self.__cantidad * producto.precio, 2)
        super().__init__()

    @property
    def cantidad(self) -> int:
        return self.__cantidad

    @property
    def subtotal(self) -> float:
        return self.__subtotal

    @property
    def producto(self) -> Producto:
        return self.__producto

    def sumar_cantidad(self, extra: int) -> None:
        """Suma unidades al detalle (mismo producto agregado de nuevo).

        Las unidades nuevas se valorizan con el precio vigente del producto.
        """
        extra = validar_cantidad(extra)
        self.__cantidad += extra
        self.__subtotal = round(self.__subtotal + extra * self.__producto.precio, 2)

    def __str__(self) -> str:
        return f"{self.producto.nombre} x{self.cantidad} = ${self.subtotal:.2f}"
