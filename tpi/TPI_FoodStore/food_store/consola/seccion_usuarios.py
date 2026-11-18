"""Submenú de administración de usuarios."""
from consola.entrada import (
    elegir_enum, elegir_enum_opcional, leer_contrasenia, leer_entero,
    leer_si_no, leer_texto, leer_texto_opcional,
)
from consola.menu import Opcion, Seccion
from consola.vistas import error, imprimir_lista, ok
from entidades import Usuario
from enums import Rol
from excepciones import DuplicadoError, MailInvalidoError
from servicios import UsuarioServicio


class SeccionUsuarios(Seccion):
    def __init__(self, actor: Usuario, usuarios: UsuarioServicio) -> None:
        self.__actor: Usuario = actor
        self.__usuarios: UsuarioServicio = usuarios

    @property
    def titulo(self) -> str:
        return "USUARIOS"

    def opciones(self) -> list[Opcion]:
        return [("Listar", self.listar), ("Crear", self.crear),
                ("Editar", self.editar), ("Eliminar", self.eliminar)]

    def listar(self) -> None:
        imprimir_lista(self.__usuarios.listar(), "No hay usuarios cargados")

    def crear(self) -> None:
        nombre = leer_texto("Nombre: ")
        apellido = leer_texto("Apellido: ")
        celular = leer_texto("Celular: ")
        contrasenia = leer_contrasenia("Contraseña: ")
        rol = elegir_enum(Rol, "Rol")
        assert contrasenia is not None
        while True:  # si el mail es inválido o ya existe, se informa y se pide otro
            mail = leer_texto("Mail: ")
            try:
                usuario = self.__usuarios.crear(
                    self.__actor, nombre, apellido, mail, celular, contrasenia, rol
                )
                break
            except (DuplicadoError, MailInvalidoError) as e:
                error(f"{e}. Ingrese otro mail.")
        ok(f"Usuario creado con id {usuario.id}.")

    def editar(self) -> None:
        self.listar()
        actual = self.__usuarios.obtener(leer_entero("Id del usuario a editar: ", 1))
        nombre = leer_texto_opcional(f"Nombre [{actual.nombre}] (Enter conserva): ")
        apellido = leer_texto_opcional(f"Apellido [{actual.apellido}] (Enter conserva): ")
        mail = leer_texto_opcional(f"Mail [{actual.mail}] (Enter conserva): ")
        celular = leer_texto_opcional(f"Celular [{actual.celular}] (Enter conserva): ")
        contrasenia = leer_contrasenia("Nueva contraseña (Enter conserva): ", opcional=True)
        rol = elegir_enum_opcional(Rol, f"Rol actual: {actual.rol.name}. Nuevo rol")
        self.__usuarios.editar(self.__actor, actual.id, nombre, apellido, mail, celular, contrasenia, rol)
        ok("Usuario actualizado.")

    def eliminar(self) -> None:
        self.listar()
        usuario = self.__usuarios.obtener(leer_entero("Id del usuario a eliminar: ", 1))
        if not leer_si_no(f"¿Confirma eliminar a '{usuario.nombre_completo}'? (S/N): "):
            print("Operación cancelada.")
            return
        self.__usuarios.eliminar(self.__actor, usuario.id)
        ok("Usuario eliminado.")
