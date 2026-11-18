"""Servicio de pedidos."""
from entidades import Pedido, Usuario
from enums import Estado, FormaPago
from excepciones import DatoInvalidoError, EntidadNoEncontradaError, OperacionNoPermitidaError
from servicios.permisos import exigir_admin
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio


class PedidoServicio:
    """Colección de pedidos en memoria y sus reglas de negocio.

    La creación es un proceso de tres pasos que garantiza que, si algo falla,
    no queda ningún rastro (ni pedido en la colección ni stock modificado):

    1. ``iniciar_pedido``: crea un pedido *borrador* (todavía fuera de la colección).
    2. ``agregar_item``: lo completa usando ``Pedido.agregar_detalle``.
    3. ``confirmar_creacion``: calcula el total, descuenta el stock y lo guarda.
    """

    def __init__(self, usuarios: UsuarioServicio, productos: ProductoServicio) -> None:
        self.__pedidos: list[Pedido] = []
        self.__usuarios: UsuarioServicio = usuarios
        self.__productos: ProductoServicio = productos

    # ---------- consultas ----------
    def listar(self, usuario_id: int | None = None) -> list[Pedido]:
        """Pedidos no eliminados; opcionalmente solo los del usuario indicado (vista admin)."""
        pedidos = [p for p in self.__pedidos if not p.eliminado]
        if usuario_id is not None:
            pedidos = [p for p in pedidos if p.usuario.id == usuario_id]
        return pedidos

    def listar_de_usuario(self, usuario: Usuario) -> list[Pedido]:
        """Pedidos no eliminados del usuario con sesión iniciada (vista cliente)."""
        return [p for p in self.__pedidos if not p.eliminado and p.usuario == usuario]

    def obtener(self, pedido_id: int) -> Pedido:
        for p in self.__pedidos:
            if p.id == pedido_id and not p.eliminado:
                return p
        raise EntidadNoEncontradaError(f"No existe un pedido con id {pedido_id}")

    def obtener_de_usuario(self, pedido_id: int, usuario: Usuario) -> Pedido:
        """Como ``obtener``, pero un pedido ajeno se informa como inexistente."""
        pedido = self.obtener(pedido_id)
        if pedido.usuario != usuario:
            raise EntidadNoEncontradaError(f"No existe un pedido con id {pedido_id}")
        return pedido

    # ---------- creación ----------
    def iniciar_pedido(self, actor: Usuario, usuario_id: int, forma_pago: FormaPago) -> Pedido:
        exigir_admin(actor)
        usuario = self.__usuarios.obtener(usuario_id)  # existe y no está eliminado
        return Pedido(usuario, forma_pago)

    def agregar_item(self, actor: Usuario, pedido: Pedido, producto_id: int, cantidad: int) -> None:
        exigir_admin(actor)
        producto = self.__productos.obtener(producto_id)  # existe y no está eliminado
        pedido.agregar_detalle(cantidad, producto)

    def confirmar_creacion(self, actor: Usuario, pedido: Pedido) -> Pedido:
        exigir_admin(actor)
        if pedido in self.__pedidos:
            raise OperacionNoPermitidaError("El pedido ya fue creado")
        if not pedido.detalles:
            raise DatoInvalidoError("El pedido debe tener al menos un detalle")
        pedido.calcular_total()
        pedido.reservar_stock()
        self.__pedidos.append(pedido)
        return pedido

    def crear_pedido(
        self, actor: Usuario, usuario_id: int, forma_pago: FormaPago,
        items: list[tuple[int, int]],
    ) -> Pedido:
        """Atajo que encadena los tres pasos. ``items`` = [(producto_id, cantidad), ...]."""
        pedido = self.iniciar_pedido(actor, usuario_id, forma_pago)
        for producto_id, cantidad in items:
            self.agregar_item(actor, pedido, producto_id, cantidad)
        return self.confirmar_creacion(actor, pedido)

    # ---------- modificación ----------
    def actualizar(
        self, actor: Usuario, pedido_id: int,
        estado: Estado | None = None, forma_pago: FormaPago | None = None,
    ) -> Pedido:
        """Cambia estado y/o forma de pago (``None`` = conservar). Si el estado
        no es válido no cambia nada; al pasar a CANCELADO se devuelve el stock."""
        exigir_admin(actor)
        pedido = self.obtener(pedido_id)
        if estado is None and forma_pago is None:
            raise DatoInvalidoError("No se indicó ningún cambio")
        if pedido.es_final:
            raise OperacionNoPermitidaError(
                f"Un pedido {pedido.estado.name} no puede modificarse"
            )
        if estado is not None and estado != pedido.estado:
            pedido.cambiar_estado(estado)  # si es inválida lanza antes de tocar nada
            if estado == Estado.CANCELADO:
                pedido.liberar_stock()
        if forma_pago is not None:
            pedido.forma_pago = forma_pago
        return pedido

    def eliminar(self, actor: Usuario, pedido_id: int) -> None:
        """Baja lógica del pedido y sus detalles; devuelve el stock si no estaba cerrado."""
        exigir_admin(actor)
        pedido = self.obtener(pedido_id)
        if pedido.estado not in (Estado.TERMINADO, Estado.CANCELADO):
            pedido.liberar_stock()
        pedido.eliminar()
