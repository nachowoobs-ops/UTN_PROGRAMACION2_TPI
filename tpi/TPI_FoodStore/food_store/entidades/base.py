"""Clase abstracta Base: superclase de todas las entidades."""
from abc import ABC, abstractmethod
from datetime import datetime


class Base(ABC):
    __contadores: dict[type, int] = {}

    def __init__(self) -> None:
        clase: type = type(self)
        Base.__contadores[clase] = Base.__contadores.get(clase, 0) + 1
        self.__id: int = Base.__contadores[clase]
        self.__eliminado: bool = False
        self.__creado_en: datetime = datetime.now()

    @property
    def id(self) -> int:
        return self.__id

    @property
    def eliminado(self) -> bool:
        return self.__eliminado

    @property
    def creado_en(self) -> datetime:
        return self.__creado_en

    def eliminar(self) -> None:
        """Baja lógica: marca ``eliminado = True``; el objeto no se destruye."""
        self.__eliminado = True

    def __eq__(self, otro: object) -> bool:
        """Dos entidades son iguales si son del mismo tipo y tienen el mismo id."""
        if not isinstance(otro, Base):
            return NotImplemented
        return type(self) is type(otro) and self.id == otro.id

    def __hash__(self) -> int:
        return hash((type(self), self.id))

    @abstractmethod
    def __str__(self) -> str:
        """Línea de texto para listados de consola (la define cada entidad)."""
        ...
