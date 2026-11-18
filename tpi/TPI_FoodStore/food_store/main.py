"""Food Store - Sistema de gestión de pedidos de comida (consola).

Crea los servicios, carga el administrador inicial y arranca el ciclo
inicio de sesión -> menú del rol. No contiene reglas de negocio.
"""
from consola import crear_menu, iniciar_sesion
from servicios import (
    CategoriaServicio, PedidoServicio, ProductoServicio, UsuarioServicio,
    cargar_datos_ejemplo,
)


def main() -> None:
    categorias = CategoriaServicio()
    productos = ProductoServicio(categorias)
    usuarios = UsuarioServicio()
    pedidos = PedidoServicio(usuarios, productos)

    # Sin un administrador inicial nadie podría ingresar al sistema.
    admin = usuarios.crear_administrador_inicial(
        "Ana", "Pérez", "admin@foodstore.com", "2634000000", "admin123"
    )
    cargar_datos_ejemplo(admin, categorias, productos, usuarios, pedidos)

    try:
        while True:
            usuario = iniciar_sesion(usuarios)  # la sesión es una variable local
            if usuario is None:
                break
            menu = crear_menu(usuario, categorias, productos, usuarios, pedidos)
            if not menu.mostrar():  # False = salir del programa
                break
    except (EOFError, KeyboardInterrupt):
        print("\nEntrada finalizada.")
    print("¡Hasta luego!")


if __name__ == "__main__":
    main()
