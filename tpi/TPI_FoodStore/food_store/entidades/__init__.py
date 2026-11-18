"""Paquete de entidades (modelo) según el UML."""
from entidades.base import Base
from entidades.calculable import Calculable
from entidades.categoria import Categoria
from entidades.producto import Producto
from entidades.usuario import Usuario
from entidades.detalle_pedido import DetallePedido
from entidades.pedido import Pedido

__all__ = [
    "Base", "Calculable", "Categoria", "Producto",
    "Usuario", "DetallePedido", "Pedido",
]
