"""Pantalla de inicio de sesión."""
from consola.entrada import leer_contrasenia
from entidades import Usuario
from excepciones import CredencialesInvalidasError
from servicios import UsuarioServicio

MAX_INTENTOS: int = 3


def iniciar_sesion(usuarios: UsuarioServicio) -> Usuario | None:
    print("\n=== FOOD STORE - INICIO DE SESIÓN ===")
    for intento in range(1, MAX_INTENTOS + 1):
        mail = input("Mail: ").strip()
        contrasenia = leer_contrasenia("Contraseña: ", opcional=True) or ""
        try:
            usuario = usuarios.autenticar(mail, contrasenia)
        except CredencialesInvalidasError as e:
            print(f"[ERROR] {e} (intento {intento} de {MAX_INTENTOS})")
            continue
        print(f"\nBienvenido/a, {usuario.nombre_completo} [{usuario.rol.name}]")
        return usuario
    print("Se agotaron los intentos de inicio de sesión. El programa finaliza.")
    return None
