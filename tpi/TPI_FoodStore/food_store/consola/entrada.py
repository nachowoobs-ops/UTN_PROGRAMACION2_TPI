import math
from enum import Enum
from typing import TypeVar

E = TypeVar("E", bound=Enum)


def leer_texto(mensaje: str) -> str:
    """Pide un texto no vacío, repitiendo hasta que se ingrese uno."""
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("[ERROR] El texto no puede estar vacío.")


def leer_texto_opcional(mensaje: str) -> str | None:
    """Devuelve el texto ingresado o ``None`` si se presionó Enter (conservar)."""
    valor = input(mensaje).strip()
    return valor or None


def leer_contrasenia(mensaje: str, opcional: bool = False) -> str | None:
    """Lee una contraseña sin mostrarla en pantalla (getpass)."""
    while True:
        valor = input(mensaje)
        if valor:
            return valor
        if opcional:
            return None
        print("[ERROR] La contraseña no puede estar vacía.")


def _a_entero(texto: str) -> int | None:
    try:
        return int(texto)
    except ValueError:
        print("[ERROR] Ingrese un número entero válido.")
        return None


def _a_flotante(texto: str) -> float | None:
    try:
        valor = float(texto.replace(",", "."))
    except ValueError:
        print("[ERROR] Ingrese un número válido (ej.: 1500 o 1500.50).")
        return None
    if not math.isfinite(valor):
        print("[ERROR] Ingrese un número válido.")
        return None
    return valor


def _en_rango(valor: int, minimo: int | None, maximo: int | None) -> bool:
    if minimo is not None and valor < minimo:
        print(f"[ERROR] El valor mínimo permitido es {minimo}.")
        return False
    if maximo is not None and valor > maximo:
        print(f"[ERROR] El valor máximo permitido es {maximo}.")
        return False
    return True


def leer_entero(mensaje: str, minimo: int | None = None, maximo: int | None = None) -> int:
    """Pide un entero (opcionalmente dentro de un rango), repitiendo ante errores."""
    while True:
        valor = _a_entero(input(mensaje).strip())
        if valor is not None and _en_rango(valor, minimo, maximo):
            return valor


def leer_entero_opcional(mensaje: str, minimo: int | None = None) -> int | None:
    """Como ``leer_entero`` pero Enter devuelve ``None`` (conservar / sin filtro)."""
    while True:
        texto = input(mensaje).strip()
        if not texto:
            return None
        valor = _a_entero(texto)
        if valor is not None and _en_rango(valor, minimo, None):
            return valor


def leer_flotante(mensaje: str) -> float:
    """Pide un número decimal (acepta coma o punto)."""
    while True:
        valor = _a_flotante(input(mensaje).strip())
        if valor is not None:
            return valor


def leer_flotante_opcional(mensaje: str) -> float | None:
    while True:
        texto = input(mensaje).strip()
        if not texto:
            return None
        valor = _a_flotante(texto)
        if valor is not None:
            return valor


def leer_si_no(mensaje: str) -> bool:
    """Pide S/N y devuelve True para sí."""
    while True:
        r = input(mensaje).strip().casefold()
        if r in ("s", "si", "sí"):
            return True
        if r in ("n", "no"):
            return False
        print("[ERROR] Responda S o N.")


def leer_si_no_opcional(mensaje: str) -> bool | None:
    while True:
        r = input(mensaje).strip().casefold()
        if not r:
            return None
        if r in ("s", "si", "sí"):
            return True
        if r in ("n", "no"):
            return False
        print("[ERROR] Responda S, N o Enter para conservar.")


def elegir_enum(enum_cls: type[E], titulo: str) -> E:
    """Muestra las opciones numeradas del enumerado y devuelve la elegida."""
    miembros = list(enum_cls)
    print(f"{titulo}:")
    for i, m in enumerate(miembros, start=1):
        print(f"  {i}. {m.name}")
    return miembros[leer_entero("Seleccione: ", 1, len(miembros)) - 1]


def elegir_enum_opcional(enum_cls: type[E], titulo: str) -> E | None:
    """Como ``elegir_enum`` pero Enter devuelve ``None`` (conservar valor)."""
    miembros = list(enum_cls)
    print(f"{titulo} (Enter conserva):")
    for i, m in enumerate(miembros, start=1):
        print(f"  {i}. {m.name}")
    while True:
        n = leer_entero_opcional("Seleccione: ", 1)
        if n is None:
            return None
        if n <= len(miembros):
            return miembros[n - 1]
        print(f"[ERROR] El valor máximo permitido es {len(miembros)}.")
