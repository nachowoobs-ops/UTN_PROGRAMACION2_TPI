"""Servicio de productos."""
from entidades import Producto, Usuario
from excepciones import EntidadNoEncontradaError, FoodStoreError
from servicios.categoria_servicio import CategoriaServicio
from servicios.permisos import exigir_admin


class ProductoServicio:
    """Colección de productos en memoria y sus reglas de negocio."""

    def __init__(self, categorias: CategoriaServicio) -> None:
        self.__productos: list[Producto] = []
        self.__categorias: CategoriaServicio = categorias

    def listar(
        self, solo_vendibles: bool = False, categoria_id: int | None = None
    ) -> list[Producto]:
        """Productos no eliminados.

        ``solo_vendibles=True`` deja los disponibles y con stock > 0 (vista del
        cliente). ``categoria_id`` filtra por categoría (que debe existir).
        """
        categoria = self.__categorias.obtener(categoria_id) if categoria_id is not None else None
        resultado = [p for p in self.__productos if not p.eliminado]
        if solo_vendibles:
            resultado = [p for p in resultado if p.vendible]
        if categoria is not None:
            resultado = [p for p in resultado if p.categoria == categoria]
        return resultado

    def obtener(self, producto_id: int) -> Producto:
        for p in self.__productos:
            if p.id == producto_id and not p.eliminado:
                return p
        raise EntidadNoEncontradaError(f"No existe un producto con id {producto_id}")

    def crear(
        self,
        actor: Usuario,
        nombre: str,
        descripcion: str,
        precio: float,
        stock: int,
        imagen: str,
        disponible: bool,
        categoria_id: int,
    ) -> Producto:
        exigir_admin(actor)
        categoria = self.__categorias.obtener(categoria_id)
        producto = Producto(nombre, precio, descripcion, stock, imagen, disponible, categoria)
        self.__productos.append(producto)
        return producto

    def editar(
        self,
        actor: Usuario,
        producto_id: int,
        nombre: str | None = None,
        descripcion: str | None = None,
        precio: float | None = None,
        stock: int | None = None,
        imagen: str | None = None,
        disponible: bool | None = None,
        categoria_id: int | None = None,
    ) -> Producto:
        """Modifica los campos recibidos (``None`` = conservar). Es todo o nada."""
        exigir_admin(actor)
        producto = self.obtener(producto_id)
        categoria = self.__categorias.obtener(categoria_id) if categoria_id is not None else None
        anterior = (
            producto.nombre, producto.descripcion, producto.precio,
            producto.stock, producto.imagen, producto.disponible, producto.categoria,
        )
        try:
            if nombre is not None:
                producto.nombre = nombre
            if descripcion is not None:
                producto.descripcion = descripcion
            if precio is not None:
                producto.precio = precio
            if stock is not None:
                producto.stock = stock
            if imagen is not None:
                producto.imagen = imagen
            if disponible is not None:
                producto.disponible = disponible
            if categoria is not None:
                producto.categoria = categoria
        except FoodStoreError:
            (producto.nombre, producto.descripcion, producto.precio, producto.stock,
             producto.imagen, producto.disponible, producto.categoria) = anterior
            raise
        return producto

    def eliminar(self, actor: Usuario, producto_id: int) -> None:
        """Baja lógica: sale de los listados y no puede agregarse a pedidos nuevos."""
        exigir_admin(actor)
        self.obtener(producto_id).eliminar()
