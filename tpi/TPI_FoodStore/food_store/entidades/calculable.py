"""Interfaz Calculable."""
from abc import ABC, abstractmethod
class Calculable(ABC):
    """Contrato de los objetos que pueden recalcular su propio total.

    No tiene atributos: solo define el comportamiento común.
    """
    @abstractmethod
    def calcular_total(self) -> None:
        """Actualiza el total del objeto que implementa la interfaz."""
        ...
