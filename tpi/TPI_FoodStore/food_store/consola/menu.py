"""Clases abstractas de la consola"""
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence

from consola.entrada import leer_entero
from consola.vistas import ejecutar_seguro
from entidades import Usuario

Accion = Callable[[], None]
Opcion = tuple[str, Accion]


def ejecutar_submenu(titulo: str, opciones: Sequence[Opcion]) -> None:
    while True:
        print(f"\n--- {titulo} ---")
        for i, (texto, _) in enumerate(opciones, start=1):
            print(f"{i}. {texto}")
        print("0. Volver")
        eleccion = leer_entero("Seleccione: ", 0, len(opciones))
        if eleccion == 0:
            return
        ejecutar_seguro(opciones[eleccion - 1][1])


class Menu(ABC):
    def __init__(self, usuario: Usuario) -> None:
        self._usuario: Usuario = usuario

    @abstractmethod
    def mostrar(self) -> bool:
        ...

    def _bucle_principal(self, titulo: str, opciones: dict[int, Opcion]) -> bool:
        while True:
            print(f"\n=== FOOD STORE - {titulo} ({self._usuario.nombre_completo}) ===")
            for numero, (texto, _) in opciones.items():
                print(f"{numero}. {texto}")
            print("9. Cerrar sesión")
            print("0. Salir")
            eleccion = leer_entero("Seleccione: ", 0, 9)
            if eleccion == 9:
                return True
            if eleccion == 0:
                return False
            if eleccion in opciones:
                ejecutar_seguro(opciones[eleccion][1])
            else:
                print("[ERROR] Opción inexistente.")


class Seccion(ABC):
    """Submenú de gestión (Listar / Crear / Editar / Eliminar) de una entidad."""
    @property
    @abstractmethod
    def titulo(self) -> str: ...

    @abstractmethod
    def opciones(self) -> list[Opcion]: ...

    def mostrar(self) -> None:
        ejecutar_submenu(self.titulo, self.opciones())
