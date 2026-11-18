"""Funciones de validación reutilizables por los setters de las entidades."""
from excepciones import DatoInvalidoError
def texto_no_vacio(valor: object, sujeto: str) -> str:
    """Devuelve ``valor`` sin espacios laterales o lanza ``DatoInvalidoError``.

    ``sujeto`` es el texto que abre el mensaje de error (ej.: "El nombre").
    """
    if not isinstance(valor, str) or not valor.strip():
        raise DatoInvalidoError(f"{sujeto} no puede estar vacío")
    return valor.strip()

def es_entero(valor: object) -> bool:
    """True si ``valor`` es un ``int`` real (``bool`` se considera inválido)."""
    return isinstance(valor, int) and not isinstance(valor, bool)

def es_numero(valor: object) -> bool:
    """True si ``valor`` es ``int`` o ``float`` (``bool`` se considera inválido)."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)
