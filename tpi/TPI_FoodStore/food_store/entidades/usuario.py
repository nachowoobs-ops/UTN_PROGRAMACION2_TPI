from __future__ import annotations
import hashlib
import hmac
import os
from entidades.base import Base
from entidades.validaciones import texto_no_vacio
from enums import Rol
from excepciones import DatoInvalidoError, MailInvalidoError

_ITERACIONES: int = 50_000


def _derivar(contrasenia: str, sal: bytes) -> bytes:
    """Deriva un hash PBKDF2-HMAC-SHA256 de la contraseña con la sal dada."""
    return hashlib.pbkdf2_hmac("sha256", contrasenia.encode("utf-8"), sal, _ITERACIONES)

class Usuario(Base):
    """Usuario del sistema (cliente o administrador).

    La contraseña **nunca sale del objeto**: no existe una property de lectura
    y, además, no se guarda en texto plano sino como hash con sal. La única
    forma de comprobarla es ``verificar_contrasenia``.
    """

    def __init__(
        self,
        nombre: str,
        apellido: str,
        mail: str,
        celular: str,
        contrasenia: str,
        rol: Rol,
    ) -> None:
        self.nombre = nombre
        self.apellido = apellido
        self.mail = mail
        self.celular = celular
        self.contrasenia = contrasenia
        self.rol = rol
        super().__init__()

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        self.__nombre: str = texto_no_vacio(valor, "El nombre")

    @property
    def apellido(self) -> str:
        return self.__apellido

    @apellido.setter
    def apellido(self, valor: str) -> None:
        self.__apellido: str = texto_no_vacio(valor, "El apellido")

    @property
    def mail(self) -> str:
        return self.__mail

    @mail.setter
    def mail(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise MailInvalidoError("El mail no puede estar vacío")
        limpio = valor.strip()
        partes = limpio.split("@")
        formato_ok = (
            len(partes) == 2
            and all(partes)
            and "." in partes[1]
            and not any(c.isspace() for c in limpio)
        )
        if not formato_ok:
            raise MailInvalidoError("El mail no tiene un formato válido (ej.: nombre@dominio.com)")
        self.__mail: str = limpio

    @property
    def celular(self) -> str:
        return self.__celular

    @celular.setter
    def celular(self, valor: str) -> None:
        self.__celular: str = texto_no_vacio(valor, "El celular")

    def _escribir_contrasenia(self, valor: str) -> None:
        if not isinstance(valor, str) or valor == "":
            raise DatoInvalidoError("La contraseña no puede estar vacía")
        self.__sal: bytes = os.urandom(16)
        self.__hash: bytes = _derivar(valor, self.__sal)

    # Property de solo escritura: leer ``usuario.contrasenia`` lanza AttributeError.
    contrasenia = property(fset=_escribir_contrasenia, doc="Solo escritura (se guarda como hash).")

    @property
    def rol(self) -> Rol:
        return self.__rol

    @rol.setter
    def rol(self, valor: Rol) -> None:
        if not isinstance(valor, Rol):
            raise DatoInvalidoError("El rol debe ser un valor del enumerado Rol")
        self.__rol: Rol = valor

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"

    def verificar_contrasenia(self, contrasenia: str) -> bool:
        """True si ``contrasenia`` coincide con la guardada (comparación segura)."""
        if not isinstance(contrasenia, str):
            return False
        return hmac.compare_digest(_derivar(contrasenia, self.__sal), self.__hash)

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre_completo} | {self.mail} | {self.rol.name}"
