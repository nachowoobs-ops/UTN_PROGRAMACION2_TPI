"""Servicio de categorías."""
from entidades import Categoria, Usuario
from entidades.validaciones import texto_no_vacio
from excepciones import DuplicadoError, EntidadNoEncontradaError, FoodStoreError, OperacionNoPermitidaError
from servicios.permisos import exigir_admin


class CategoriaServicio:
    """Colección de categorías en memoria y sus reglas de negocio."""

    def __init__(self) -> None:
        self.__categorias: list[Categoria] = []

    def listar(self) -> list[Categoria]:
        """Categorías no eliminadas."""
        return [c for c in self.__categorias if not c.eliminado]

    def obtener(self, categoria_id: int) -> Categoria:
        """Busca por id; falla si no existe o está eliminada."""
        for c in self.__categorias:
            if c.id == categoria_id and not c.eliminado:
                return c
        raise EntidadNoEncontradaError(f"No existe una categoría con id {categoria_id}")

    def _validar_nombre_unico(self, nombre: str, excluir: Categoria | None = None) -> None:
        """El nombre es único entre las categorías activas, sin distinguir mayúsculas."""
        buscado = texto_no_vacio(nombre, "El nombre de la categoría").casefold()
        for c in self.listar():
            if c is not excluir and c.nombre.casefold() == buscado:
                raise DuplicadoError(f"Ya existe una categoría llamada '{c.nombre}'")

    def crear(self, actor: Usuario, nombre: str, descripcion: str) -> Categoria:
        exigir_admin(actor)
        self._validar_nombre_unico(nombre)
        categoria = Categoria(nombre, descripcion)
        self.__categorias.append(categoria)
        return categoria

    def editar(
        self,
        actor: Usuario,
        categoria_id: int,
        nombre: str | None = None,
        descripcion: str | None = None,
    ) -> Categoria:
        """Modifica los campos recibidos; ``None`` conserva el valor anterior."""
        exigir_admin(actor)
        categoria = self.obtener(categoria_id)
        nombre_ant, descripcion_ant = categoria.nombre, categoria.descripcion
        try:
            if nombre is not None:
                self._validar_nombre_unico(nombre, excluir=categoria)
                categoria.nombre = nombre
            if descripcion is not None:
                categoria.descripcion = descripcion
        except FoodStoreError:
            categoria.nombre, categoria.descripcion = nombre_ant, descripcion_ant
            raise
        return categoria

    def eliminar(self, actor: Usuario, categoria_id: int) -> None:
        """Baja lógica; no se permite si la categoría tiene productos activos."""
        exigir_admin(actor)
        categoria = self.obtener(categoria_id)
        cantidad = len(categoria.productos_activos)
        if cantidad > 0:
            raise OperacionNoPermitidaError(
                f"No se puede eliminar la categoría: tiene {cantidad} producto(s) activo(s)"
            )
        categoria.eliminar()
