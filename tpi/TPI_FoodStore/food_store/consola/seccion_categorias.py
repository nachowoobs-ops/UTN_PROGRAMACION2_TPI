"""Submenú de administración de categorías."""
from consola.entrada import leer_entero, leer_si_no, leer_texto, leer_texto_opcional
from consola.menu import Opcion, Seccion
from consola.vistas import imprimir_lista, ok
from entidades import Usuario
from servicios import CategoriaServicio


class SeccionCategorias(Seccion):
    def __init__(self, actor: Usuario, categorias: CategoriaServicio) -> None:
        self.__actor: Usuario = actor
        self.__categorias: CategoriaServicio = categorias

    @property
    def titulo(self) -> str:
        return "CATEGORÍAS"

    def opciones(self) -> list[Opcion]:
        return [("Listar", self.listar), ("Crear", self.crear),
                ("Editar", self.editar), ("Eliminar", self.eliminar)]

    def listar(self) -> None:
        imprimir_lista(self.__categorias.listar(), "No hay categorías cargadas")

    def crear(self) -> None:
        nombre = leer_texto("Nombre: ")
        descripcion = leer_texto("Descripción: ")
        categoria = self.__categorias.crear(self.__actor, nombre, descripcion)
        ok(f"Categoría creada con id {categoria.id}.")

    def editar(self) -> None:
        self.listar()
        actual = self.__categorias.obtener(leer_entero("Id de la categoría a editar: ", 1))
        nombre = leer_texto_opcional(f"Nombre [{actual.nombre}] (Enter conserva): ")
        descripcion = leer_texto_opcional(f"Descripción [{actual.descripcion}] (Enter conserva): ")
        self.__categorias.editar(self.__actor, actual.id, nombre, descripcion)
        ok("Categoría actualizada.")

    def eliminar(self) -> None:
        self.listar()
        categoria = self.__categorias.obtener(leer_entero("Id de la categoría a eliminar: ", 1))
        if not leer_si_no(f"¿Confirma eliminar '{categoria.nombre}'? (S/N): "):
            print("Operación cancelada.")
            return
        self.__categorias.eliminar(self.__actor, categoria.id)
        ok("Categoría eliminada.")
