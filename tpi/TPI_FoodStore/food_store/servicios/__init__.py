"""Paquete de servicios (lógica de negocio y colecciones en memoria)."""
from servicios.categoria_servicio import CategoriaServicio
from servicios.datos_ejemplo import cargar_datos_ejemplo
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio

__all__ = [
    "CategoriaServicio", "ProductoServicio", "UsuarioServicio",
    "PedidoServicio", "cargar_datos_ejemplo",
]
