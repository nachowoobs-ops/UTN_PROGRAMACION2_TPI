from __future__ import annotations
from typing import TYPE_CHECKING
from entidades.base import Base
from entidades.validaciones import texto_no_vacio
if TYPE_CHECKING:
    from entidades.producto import Producto
class Categoria(Base):
    """
    Es una *agregación*: la categoría conoce a sus productos, pero los
    productos tienen vida propia.
    """

    def __init__(self, nombre: str, descripcion: str) -> None:
        # Se valida primero y se llama a Base.__init__ al final para que un alta fallida no consuma un id.
        self.nombre = nombre
        self.descripcion = descripcion
        self.__productos: list[Producto] = []
        super().__init__()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre: str = texto_no_vacio(valor, "El nombre de la categoría")

    @property
    def descripcion(self) -> str:
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, valor: str) -> None:
        self.__descripcion: str = texto_no_vacio(valor, "La descripción de la categoría")

    @property
    def productos(self) -> tuple[Producto, ...]:
        return tuple(self.__productos)

    @property
    def productos_activos(self) -> tuple[Producto, ...]:
        return tuple(p for p in self.__productos if not p.eliminado)
    def _agregar_producto(self, producto: Producto) -> None:
        self.__productos.append(producto)

    def _quitar_producto(self, producto: Producto) -> None:
        self.__productos = [p for p in self.__productos if p is not producto]

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} - {self.descripcion}"
