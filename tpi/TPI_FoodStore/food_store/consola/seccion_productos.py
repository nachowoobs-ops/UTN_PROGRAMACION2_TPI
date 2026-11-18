"""Submenú de administración de productos."""
from consola.entrada import (
    leer_entero, leer_entero_opcional, leer_flotante, leer_flotante_opcional,
    leer_si_no, leer_si_no_opcional, leer_texto, leer_texto_opcional,
)
from consola.menu import Opcion, Seccion
from consola.vistas import imprimir_lista, ok
from entidades import Usuario
from servicios import CategoriaServicio, ProductoServicio


class SeccionProductos(Seccion):
    def __init__(self, actor: Usuario, categorias: CategoriaServicio, productos: ProductoServicio) -> None:
        self.__actor: Usuario = actor
        self.__categorias: CategoriaServicio = categorias
        self.__productos: ProductoServicio = productos

    @property
    def titulo(self) -> str:
        return "PRODUCTOS"

    def opciones(self) -> list[Opcion]:
        return [("Listar", self.listar), ("Crear", self.crear),
                ("Editar", self.editar), ("Eliminar", self.eliminar)]

    def listar(self) -> None:
        categoria_id = leer_entero_opcional("Filtrar por id de categoría (Enter = todas): ", 1)
        imprimir_lista(self.__productos.listar(categoria_id=categoria_id), "No hay productos cargados")

    def _listar_todos(self) -> None:
        imprimir_lista(self.__productos.listar(), "No hay productos cargados")

    def crear(self) -> None:
        imprimir_lista(self.__categorias.listar(), "No hay categorías cargadas")
        nombre = leer_texto("Nombre: ")
        descripcion = leer_texto_opcional("Descripción: ") or ""
        precio = leer_flotante("Precio: ")
        stock = leer_entero("Stock: ")
        imagen = leer_texto_opcional("Imagen (archivo o URL): ") or ""
        disponible = leer_si_no("¿Disponible? (S/N): ")
        categoria_id = leer_entero("Id de la categoría: ", 1)
        producto = self.__productos.crear(
            self.__actor, nombre, descripcion, precio, stock, imagen, disponible, categoria_id
        )
        ok(f"Producto creado con id {producto.id}.")

    def editar(self) -> None:
        self._listar_todos()
        actual = self.__productos.obtener(leer_entero("Id del producto a editar: ", 1))
        nombre = leer_texto_opcional(f"Nombre [{actual.nombre}] (Enter conserva): ")
        descripcion = leer_texto_opcional(f"Descripción [{actual.descripcion}] (Enter conserva): ")
        precio = leer_flotante_opcional(f"Precio [{actual.precio:.2f}] (Enter conserva): ")
        stock = leer_entero_opcional(f"Stock [{actual.stock}] (Enter conserva): ")
        imagen = leer_texto_opcional(f"Imagen [{actual.imagen}] (Enter conserva): ")
        disponible = leer_si_no_opcional(
            f"¿Disponible? [{'S' if actual.disponible else 'N'}] (S/N, Enter conserva): "
        )
        categoria_id = leer_entero_opcional(
            f"Id de categoría [{actual.categoria.id} - {actual.categoria.nombre}] (Enter conserva): ", 1
        )
        self.__productos.editar(
            self.__actor, actual.id, nombre, descripcion, precio, stock, imagen, disponible, categoria_id
        )
        ok("Producto actualizado.")

    def eliminar(self) -> None:
        self._listar_todos()
        producto = self.__productos.obtener(leer_entero("Id del producto a eliminar: ", 1))
        if not leer_si_no(f"¿Confirma eliminar '{producto.nombre}'? (S/N): "):
            print("Operación cancelada.")
            return
        self.__productos.eliminar(self.__actor, producto.id)
        ok("Producto eliminado.")
