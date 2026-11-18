"""Excepciones propias del dominio de Food Store.

Todas heredan de ``FoodStoreError`` para que la consola pueda capturar
"cualquier error de negocio" con un único ``except FoodStoreError``.
"""
class FoodStoreError(Exception):
    """Excepción base de la aplicación."""
    
class EntidadNoEncontradaError(FoodStoreError):
    """El id buscado no existe o corresponde a una entidad eliminada."""


class DatoInvalidoError(FoodStoreError):
    """Dato de entrada vacío, con formato incorrecto o de tipo erróneo."""


class PrecioInvalidoError(DatoInvalidoError):
    """El precio no es un número válido o es negativo."""


class StockInvalidoError(DatoInvalidoError):
    """El stock no es un entero válido o es negativo."""


class CantidadInvalidaError(DatoInvalidoError):
    """La cantidad no es un entero mayor que cero."""


class MailInvalidoError(DatoInvalidoError):
    """El mail está vacío o no tiene un formato básico válido."""


class StockInsuficienteError(FoodStoreError):
    """Se pidió una cantidad mayor al stock disponible del producto."""


class DuplicadoError(FoodStoreError):
    """Mail de usuario o nombre de categoría repetido."""


class OperacionNoPermitidaError(FoodStoreError):
    """Operación prohibida por una regla de negocio.

    Ejemplos: transición de estado inválida, categoría con productos
    activos, administrador que intenta eliminarse, rol sin permisos.
    """


class CredencialesInvalidasError(FoodStoreError):
    """Mail o contraseña incorrectos, o usuario eliminado."""
