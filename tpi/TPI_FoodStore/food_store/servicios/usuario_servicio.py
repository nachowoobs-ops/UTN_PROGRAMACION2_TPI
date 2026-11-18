"""Servicio de usuarios y autenticación."""
from entidades import Usuario
from enums import Rol
from excepciones import (
    CredencialesInvalidasError,
    DuplicadoError,
    EntidadNoEncontradaError,
    FoodStoreError,
    OperacionNoPermitidaError,
)
from servicios.permisos import exigir_admin


class UsuarioServicio:
    """Colección de usuarios en memoria, reglas de negocio y login."""

    def __init__(self) -> None:
        self.__usuarios: list[Usuario] = []

    def listar(self) -> list[Usuario]:
        return [u for u in self.__usuarios if not u.eliminado]

    def obtener(self, usuario_id: int) -> Usuario:
        for u in self.__usuarios:
            if u.id == usuario_id and not u.eliminado:
                return u
        raise EntidadNoEncontradaError(f"No existe un usuario con id {usuario_id}")

    def _buscar_por_mail(self, mail: str) -> Usuario | None:
        """Busca recorriendo TODA la colección (incluye eliminados), sin distinguir mayúsculas."""
        buscado = mail.strip().casefold() if isinstance(mail, str) else ""
        for u in self.__usuarios:
            if u.mail.casefold() == buscado:
                return u
        return None

    def _validar_mail_unico(self, mail: str, excluir: Usuario | None = None) -> None:
        existente = self._buscar_por_mail(mail)
        if existente is not None and existente is not excluir:
            raise DuplicadoError(f"Ya existe un usuario con el mail '{existente.mail}'")

    def autenticar(self, mail: str, contrasenia: str) -> Usuario:
        """Devuelve el usuario activo o lanza ``CredencialesInvalidasError``.

        El mensaje es idéntico en los tres casos (mail inexistente, usuario
        eliminado, contraseña incorrecta) para no revelar qué dato falló.
        """
        usuario = self._buscar_por_mail(mail)
        if usuario is None or usuario.eliminado or not usuario.verificar_contrasenia(contrasenia):
            raise CredencialesInvalidasError("Mail o contraseña incorrectos")
        return usuario

    def crear_administrador_inicial(
        self, nombre: str, apellido: str, mail: str, celular: str, contrasenia: str
    ) -> Usuario:
        """Crea el primer ADMIN (sin él nadie podría ingresar). Solo con la colección vacía."""
        if self.__usuarios:
            raise OperacionNoPermitidaError("El administrador inicial solo se crea con el sistema vacío")
        admin = Usuario(nombre, apellido, mail, celular, contrasenia, Rol.ADMIN)
        self.__usuarios.append(admin)
        return admin

    def crear(
        self, actor: Usuario, nombre: str, apellido: str, mail: str,
        celular: str, contrasenia: str, rol: Rol,
    ) -> Usuario:
        exigir_admin(actor)
        self._validar_mail_unico(mail)
        usuario = Usuario(nombre, apellido, mail, celular, contrasenia, rol)
        self.__usuarios.append(usuario)
        return usuario

    def _admins_activos(self) -> list[Usuario]:
        return [u for u in self.listar() if u.rol == Rol.ADMIN]

    def editar(
        self,
        actor: Usuario,
        usuario_id: int,
        nombre: str | None = None,
        apellido: str | None = None,
        mail: str | None = None,
        celular: str | None = None,
        contrasenia: str | None = None,
        rol: Rol | None = None,
    ) -> Usuario:
        """Modifica los campos recibidos (``None`` = conservar). Es todo o nada."""
        exigir_admin(actor)
        usuario = self.obtener(usuario_id)
        if mail is not None:
            self._validar_mail_unico(mail, excluir=usuario)
        if (rol is not None and rol != Rol.ADMIN and usuario.rol == Rol.ADMIN
                and len(self._admins_activos()) == 1):
            raise OperacionNoPermitidaError("No se puede quitar el rol al único administrador activo")
        anterior = (usuario.nombre, usuario.apellido, usuario.mail, usuario.celular, usuario.rol)
        try:
            if nombre is not None:
                usuario.nombre = nombre
            if apellido is not None:
                usuario.apellido = apellido
            if mail is not None:
                usuario.mail = mail
            if celular is not None:
                usuario.celular = celular
            if rol is not None:
                usuario.rol = rol
            if contrasenia is not None:
                usuario.contrasenia = contrasenia
        except FoodStoreError:
            usuario.nombre, usuario.apellido, usuario.mail, usuario.celular, usuario.rol = anterior
            raise
        return usuario

    def eliminar(self, actor: Usuario, usuario_id: int) -> None:
        """Baja lógica. Un administrador no puede eliminarse a sí mismo."""
        exigir_admin(actor)
        usuario = self.obtener(usuario_id)
        if usuario == actor:
            raise OperacionNoPermitidaError("Un administrador no puede eliminarse a sí mismo")
        usuario.eliminar()
