"""Menú del rol ADMIN: gestión completa."""
from consola.menu import Menu
from consola.seccion_categorias import SeccionCategorias
from consola.seccion_pedidos import SeccionPedidos
from consola.seccion_productos import SeccionProductos
from consola.seccion_usuarios import SeccionUsuarios
from entidades import Usuario
from servicios import CategoriaServicio, PedidoServicio, ProductoServicio, UsuarioServicio


class MenuAdministrador(Menu):
    def __init__(
        self, usuario: Usuario, categorias: CategoriaServicio, productos: ProductoServicio,
        usuarios: UsuarioServicio, pedidos: PedidoServicio,
    ) -> None:
        super().__init__(usuario)
        self.__secciones: dict[int, tuple[str, SeccionCategorias | SeccionProductos | SeccionUsuarios | SeccionPedidos]] = {
            1: ("Categorías", SeccionCategorias(usuario, categorias)),
            2: ("Productos", SeccionProductos(usuario, categorias, productos)),
            3: ("Usuarios", SeccionUsuarios(usuario, usuarios)),
            4: ("Pedidos", SeccionPedidos(usuario, usuarios, productos, pedidos)),
        }

    def mostrar(self) -> bool:
        opciones = {n: (texto, seccion.mostrar) for n, (texto, seccion) in self.__secciones.items()}
        return self._bucle_principal(f"ADMINISTRADOR", opciones)
