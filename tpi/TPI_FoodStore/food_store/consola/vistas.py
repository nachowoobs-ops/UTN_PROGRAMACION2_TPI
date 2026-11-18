"""Funciones de presentación (mensajes y listados) compartidas por los menús."""
from collections.abc import Callable, Iterable

from entidades import Base, Pedido
from excepciones import FoodStoreError


def ok(mensaje: str) -> None:
    print(f"[OK] {mensaje}")


def error(mensaje: str) -> None:
    print(f"[ERROR] {mensaje}")


def imprimir_lista(elementos: Iterable[Base], mensaje_vacio: str) -> None:
    """Imprime un elemento por línea (usa ``__str__``) o el mensaje si no hay ninguno."""
    lista = list(elementos)
    if not lista:
        print(mensaje_vacio)
        return
    for e in lista:
        print(f"  {e}")


def imprimir_pedido_detallado(pedido: Pedido) -> None:
    """Cabecera del pedido, sus detalles (producto, cantidad, subtotal) y el total."""
    print(f"  {pedido}")
    for detalle in pedido.detalles:
        print(f"      - {detalle}")
    print(f"      TOTAL: ${pedido.total:.2f}")


def ejecutar_seguro(accion: Callable[[], None]) -> None:
    """Ejecuta una acción de menú: un error informa y vuelve al menú, nunca cierra el programa."""
    try:
        accion()
    except FoodStoreError as e:
        error(str(e))
    except ValueError as e:
        error(f"Dato inválido: {e}")
