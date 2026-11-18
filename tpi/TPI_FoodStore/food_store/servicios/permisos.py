"""Control de permisos por rol a nivel de servicios."""
from entidades import Usuario
from enums import Rol
from excepciones import OperacionNoPermitidaError


def exigir_admin(actor: Usuario) -> None:
    """Lanza ``OperacionNoPermitidaError`` si ``actor`` no es un ADMIN activo.

    Defensa en profundidad: aunque el menú de cliente no ofrezca opciones de
    escritura, los servicios tampoco aceptan modificaciones de otro rol.
    """
    if not isinstance(actor, Usuario) or actor.eliminado or actor.rol != Rol.ADMIN:
        raise OperacionNoPermitidaError("Solo un administrador puede crear, editar o eliminar datos")
