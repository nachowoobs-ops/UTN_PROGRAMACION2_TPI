from __future__ import annotations
from entidades.base import Base
from entidades.categoria import Categoria
from entidades.validaciones import es_entero, es_numero, texto_no_vacio
from excepciones import (
    CantidadInvalidaError,
    DatoInvalidoError,
    OperacionNoPermitidaError,
    PrecioInvalidoError,
    StockInsuficienteError,
    StockInvalidoError,
)
class Producto(Base):
    def __init__(
        self,
        nombre: str,
        precio: float,
        descripcion: str,
        stock: int,
        imagen: str,
        disponible: bool,
        categoria: Categoria,
    ) -> None:
        self.__categoria: Categoria | None = None
        self.nombre = nombre
        self.precio = precio
        self.descripcion = descripcion
        self.stock = stock
        self.imagen = imagen
        self.disponible = disponible
        super().__init__()
        # La categoría se asigna al final: recién ahí el objeto está completo y
        # puede registrarse en la agregación de la categoría.
        self.categoria = categoria

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre: str = texto_no_vacio(valor, "El nombre del producto")

    @property
    def precio(self) -> float:
        return self.__precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if not es_numero(valor):
            raise PrecioInvalidoError("El precio debe ser un número")
        if valor < 0:
            raise PrecioInvalidoError("El precio no puede ser negativo")
        self.__precio: float = float(valor)

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise DatoInvalidoError("La descripción debe ser un texto")
        self.__descripcion: str = valor.strip()

    @property
    def stock(self) -> int:
        return self.__stock

    @stock.setter
    def stock(self, valor: int) -> None:
        if not es_entero(valor):
            raise StockInvalidoError("El stock debe ser un número entero")
        if valor < 0:
            raise StockInvalidoError("El stock no puede ser negativo")
        self.__stock: int = valor

    @property
    def imagen(self) -> str:
        return self.__imagen

    @imagen.setter
    def imagen(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise DatoInvalidoError("La imagen debe ser un texto")
        self.__imagen: str = valor.strip()

    @property
    def disponible(self) -> bool:
        return self.__disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise DatoInvalidoError("La disponibilidad debe ser verdadero o falso")
        self.__disponible: bool = valor

    @property
    def categoria(self) -> Categoria:
        assert self.__categoria is not None
        return self.__categoria

    @categoria.setter
    def categoria(self, valor: Categoria) -> None:
        if not isinstance(valor, Categoria):
            raise DatoInvalidoError("El producto debe pertenecer a una categoría")
        if valor.eliminado:
            raise OperacionNoPermitidaError("No se puede usar una categoría eliminada")
        if self.__categoria is not None:
            self.__categoria._quitar_producto(self)
        valor._agregar_producto(self)
        self.__categoria = valor

    @property
    def vendible(self) -> bool:
        """True si un cliente puede verlo: no eliminado, disponible y con stock."""
        return (not self.eliminado) and self.disponible and self.stock > 0

    def descontar_stock(self, cantidad: int) -> None:
        """Resta ``cantidad`` al stock; falla si no alcanza."""
        if not es_entero(cantidad) or cantidad <= 0:
            raise CantidadInvalidaError("La cantidad debe ser un entero mayor que cero")
        if cantidad > self.__stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de '{self.nombre}': "
                f"disponible {self.__stock}, solicitado {cantidad}"
            )
        self.__stock -= cantidad

    def reponer_stock(self, cantidad: int) -> None:
        """Suma ``cantidad`` al stock (por ejemplo, al cancelar un pedido)."""
        if not es_entero(cantidad) or cantidad <= 0:
            raise CantidadInvalidaError("La cantidad debe ser un entero mayor que cero")
        self.__stock += cantidad

    def __str__(self) -> str:
        extra = "" if self.disponible else " | NO DISPONIBLE"
        return (
            f"[{self.id}] {self.nombre} | ${self.precio:.2f} | "
            f"Stock: {self.stock} | Categoría: {self.categoria.nombre}{extra}"
        )
