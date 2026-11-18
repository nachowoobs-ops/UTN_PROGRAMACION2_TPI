"""Menú del rol USUARIO (cliente): solo consulta."""
from consola.entrada import leer_entero_opcional
from consola.menu import Menu
from consola.vistas import imprimir_lista, imprimir_pedido_detallado
from entidades import Usuario
from servicios import CategoriaServicio, PedidoServicio, ProductoServicio


class MenuCliente(Menu):
    def __init__(
        self, usuario: Usuario, categorias: CategoriaServicio,
        productos: ProductoServicio, pedidos: PedidoServicio,
    ) -> None:
        super().__init__(usuario)
        self.__categorias: CategoriaServicio = categorias
        self.__productos: ProductoServicio = productos
        self.__pedidos: PedidoServicio = pedidos

    def mostrar(self) -> bool:
        opciones = {
            1: ("Ver categorías", self._ver_categorias),
            2: ("Ver productos disponibles", self._ver_productos),
            3: ("Mis pedidos", self._mis_pedidos),
            4: ("Mis datos", self._mis_datos),
        }
        return self._bucle_principal("CLIENTE", opciones)

    def _ver_categorias(self) -> None:
        imprimir_lista(self.__categorias.listar(), "No hay categorías cargadas")

    def _ver_productos(self) -> None:
        categoria_id = leer_entero_opcional("Filtrar por id de categoría (Enter = todas): ", 1)
        imprimir_lista(
            self.__productos.listar(solo_vendibles=True, categoria_id=categoria_id),
            "No hay productos disponibles",
        )

    def _mis_pedidos(self) -> None:
        mios = self.__pedidos.listar_de_usuario(self._usuario)
        imprimir_lista(mios, "Todavía no tiene pedidos")
        if not mios:
            return
        pedido_id = leer_entero_opcional("Id de un pedido para ver su detalle (Enter = volver): ", 1)
        if pedido_id is not None:
            imprimir_pedido_detallado(self.__pedidos.obtener_de_usuario(pedido_id, self._usuario))

    def _mis_datos(self) -> None:
        u = self._usuario
        print(f"  Nombre:   {u.nombre}\n  Apellido: {u.apellido}\n  Mail:     {u.mail}\n"
              f"  Celular:  {u.celular}\n  Rol:      {u.rol.name}")
