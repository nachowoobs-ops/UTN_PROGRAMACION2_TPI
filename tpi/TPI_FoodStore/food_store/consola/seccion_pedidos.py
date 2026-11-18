"""Submenú de administración de pedidos."""
from consola.entrada import (
    elegir_enum, elegir_enum_opcional, leer_entero, leer_entero_opcional, leer_si_no,
)
from consola.menu import Opcion, Seccion
from consola.vistas import error, imprimir_lista, imprimir_pedido_detallado, ok
from entidades import Usuario
from enums import Estado, FormaPago
from excepciones import FoodStoreError
from servicios import PedidoServicio, ProductoServicio, UsuarioServicio


class SeccionPedidos(Seccion):
    def __init__(
        self, actor: Usuario, usuarios: UsuarioServicio,
        productos: ProductoServicio, pedidos: PedidoServicio,
    ) -> None:
        self.__actor: Usuario = actor
        self.__usuarios: UsuarioServicio = usuarios
        self.__productos: ProductoServicio = productos
        self.__pedidos: PedidoServicio = pedidos

    @property
    def titulo(self) -> str:
        return "PEDIDOS"

    def opciones(self) -> list[Opcion]:
        return [("Listar", self.listar), ("Ver detalle de un pedido", self.ver_detalle),
                ("Crear", self.crear), ("Cambiar estado / forma de pago", self.actualizar),
                ("Eliminar", self.eliminar)]

    def listar(self) -> None:
        usuario_id = leer_entero_opcional("Filtrar por id de usuario (Enter = todos): ", 1)
        imprimir_lista(self.__pedidos.listar(usuario_id), "No hay pedidos cargados")

    def _listar_todos(self) -> None:
        imprimir_lista(self.__pedidos.listar(), "No hay pedidos cargados")

    def ver_detalle(self) -> None:
        self._listar_todos()
        pedido = self.__pedidos.obtener(leer_entero("Id del pedido: ", 1))
        imprimir_pedido_detallado(pedido)

    def crear(self) -> None:
        imprimir_lista(self.__usuarios.listar(), "No hay usuarios cargados")
        usuario_id = leer_entero("Id del usuario: ", 1)
        forma_pago = elegir_enum(FormaPago, "Forma de pago")
        pedido = self.__pedidos.iniciar_pedido(self.__actor, usuario_id, forma_pago)
        imprimir_lista(self.__productos.listar(solo_vendibles=True), "No hay productos disponibles")
        try:
            while True:
                producto_id = leer_entero("Id del producto: ", 1)
                cantidad = leer_entero("Cantidad: ")
                self.__pedidos.agregar_item(self.__actor, pedido, producto_id, cantidad)
                ok("Detalle agregado.")
                if not leer_si_no("¿Agregar otro producto? (S/N): "):
                    break
            pedido = self.__pedidos.confirmar_creacion(self.__actor, pedido)
        except FoodStoreError as e:
            error(str(e))
            print("Creación del pedido cancelada: no se agregó el pedido ni se modificó ningún stock.")
            return
        ok(f"Pedido creado con id {pedido.id}. Total: ${pedido.total:.2f}")

    def actualizar(self) -> None:
        self._listar_todos()
        pedido = self.__pedidos.obtener(leer_entero("Id del pedido: ", 1))
        print(f"Estado actual: {pedido.estado.name} | Forma de pago actual: {pedido.forma_pago.name}")
        estado = elegir_enum_opcional(Estado, "Nuevo estado")
        forma_pago = elegir_enum_opcional(FormaPago, "Nueva forma de pago")
        self.__pedidos.actualizar(self.__actor, pedido.id, estado, forma_pago)
        ok("Pedido actualizado.")

    def eliminar(self) -> None:
        self._listar_todos()
        pedido = self.__pedidos.obtener(leer_entero("Id del pedido a eliminar: ", 1))
        if not leer_si_no(f"¿Confirma eliminar el pedido {pedido.id}? (S/N): "):
            print("Operación cancelada.")
            return
        self.__pedidos.eliminar(self.__actor, pedido.id)
        ok("Pedido eliminado.")
