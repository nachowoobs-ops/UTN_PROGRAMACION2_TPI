"""Entidad Pedido."""
from __future__ import annotations

from datetime import date
from typing import ClassVar

from entidades.base import Base
from entidades.calculable import Calculable
from entidades.detalle_pedido import DetallePedido, validar_cantidad
from entidades.producto import Producto
from entidades.usuario import Usuario
from enums import Estado, FormaPago
from excepciones import (
    DatoInvalidoError,
    EntidadNoEncontradaError,
    OperacionNoPermitidaError,
    StockInsuficienteError,
)


class Pedido(Base, Calculable):

    _TRANSICIONES: ClassVar[dict[Estado, frozenset[Estado]]] = {
        Estado.PENDIENTE: frozenset({Estado.CONFIRMADO, Estado.CANCELADO}),
        Estado.CONFIRMADO: frozenset({Estado.TERMINADO, Estado.CANCELADO}),
        Estado.TERMINADO: frozenset(),
        Estado.CANCELADO: frozenset(),
    }

    def __init__(self, usuario: Usuario, forma_pago: FormaPago) -> None:
        if not isinstance(usuario, Usuario):
            raise DatoInvalidoError("El pedido requiere un usuario")
        if usuario.eliminado:
            raise OperacionNoPermitidaError("No se puede crear un pedido para un usuario eliminado")
        self.__usuario: Usuario = usuario
        self.forma_pago = forma_pago
        self.__fecha: date = date.today()
        self.__estado: Estado = Estado.PENDIENTE
        self.__total: float = 0.0
        self.__detalles: list[DetallePedido] = []
        self.__stock_reservado: bool = False
        super().__init__()

    # ---------- propiedades ----------
    @property
    def usuario(self) -> Usuario:
        return self.__usuario

    @property
    def fecha(self) -> date:
        return self.__fecha

    @property
    def estado(self) -> Estado:
        return self.__estado

    @property
    def total(self) -> float:
        return self.__total

    @property
    def forma_pago(self) -> FormaPago:
        return self.__forma_pago

    @forma_pago.setter
    def forma_pago(self, valor: FormaPago) -> None:
        if not isinstance(valor, FormaPago):
            raise DatoInvalidoError("La forma de pago debe ser un valor del enumerado FormaPago")
        self.__forma_pago: FormaPago = valor

    @property
    def detalles(self) -> tuple[DetallePedido, ...]:
        """Copia inmutable de los detalles: no permite modificar el pedido desde afuera."""
        return tuple(self.__detalles)

    @property
    def stock_reservado(self) -> bool:
        return self.__stock_reservado

    @property
    def es_final(self) -> bool:
        """True si el estado ya no puede cambiar (TERMINADO o CANCELADO)."""
        return not self._TRANSICIONES[self.__estado]

    # ---------- detalles (composición) ----------
    def agregar_detalle(self, cantidad: int, producto: Producto) -> None:
        """Agrega un producto; si ya estaba, suma la cantidad al detalle existente.
        No descuenta stock (eso ocurre al confirmar la creación), pero sí
        verifica que lo pedido en total no supere el stock actual.
        """
        self._exigir_edicion_abierta()
        validar_cantidad(cantidad)
        if not isinstance(producto, Producto):
            raise DatoInvalidoError("El detalle requiere un producto válido")
        if producto.eliminado:
            raise OperacionNoPermitidaError(f"El producto '{producto.nombre}' fue eliminado del catálogo")
        if not producto.disponible:
            raise OperacionNoPermitidaError(f"El producto '{producto.nombre}' no está disponible")
        existente = self.buscar_detalle_por_producto(producto)
        pedido_total = cantidad + (existente.cantidad if existente else 0)
        if pedido_total > producto.stock:
            raise StockInsuficienteError(
                f"Stock insuficiente de '{producto.nombre}': "
                f"disponible {producto.stock}, solicitado {pedido_total}"
            )
        if existente is not None:
            existente.sumar_cantidad(cantidad)
        else:
            self.__detalles.append(DetallePedido(cantidad, producto))
        self.calcular_total()

    def buscar_detalle_por_producto(self, producto: Producto) -> DetallePedido | None:
        """Devuelve el detalle de ese producto o ``None`` si no está en el pedido."""
        for detalle in self.__detalles:
            if detalle.producto == producto:
                return detalle
        return None

    def eliminar_detalle_por_producto(self, producto: Producto) -> None:
        """Quita el detalle del producto; falla si el producto no está en el pedido."""
        self._exigir_edicion_abierta()
        detalle = self.buscar_detalle_por_producto(producto)
        if detalle is None:
            raise EntidadNoEncontradaError("El producto no está en el pedido")
        self.__detalles.remove(detalle)
        self.calcular_total()

    def calcular_total(self) -> None:
        """Implementación de ``Calculable``: total = suma de subtotales."""
        self.__total = round(sum(d.subtotal for d in self.__detalles), 2)

    def _exigir_edicion_abierta(self) -> None:
        if self.__stock_reservado or self.__estado is not Estado.PENDIENTE:
            raise OperacionNoPermitidaError(
                "El pedido ya fue confirmado en el sistema; no se pueden modificar sus detalles"
            )

    # ---------- estado ----------
    def cambiar_estado(self, nuevo: Estado) -> None:
        """Aplica una transición válida o lanza ``OperacionNoPermitidaError``.

        Válidas: PENDIENTE→CONFIRMADO→TERMINADO; PENDIENTE|CONFIRMADO→CANCELADO.
        """
        if not isinstance(nuevo, Estado):
            raise DatoInvalidoError("El estado debe ser un valor del enumerado Estado")
        if nuevo not in self._TRANSICIONES[self.__estado]:
            raise OperacionNoPermitidaError(
                f"Transición de estado inválida: {self.__estado.name} -> {nuevo.name}"
            )
        self.__estado = nuevo

    # ---------- stock ----------
    def reservar_stock(self) -> None:
        """Descuenta del stock de cada producto lo pedido (todo o nada)."""
        if self.__stock_reservado:
            raise OperacionNoPermitidaError("El stock de este pedido ya fue reservado")
        if not self.__detalles:
            raise DatoInvalidoError("El pedido debe tener al menos un detalle")
        for d in self.__detalles:  # primero se verifica todo...
            if d.cantidad > d.producto.stock:
                raise StockInsuficienteError(
                    f"Stock insuficiente de '{d.producto.nombre}': "
                    f"disponible {d.producto.stock}, solicitado {d.cantidad}"
                )
        for d in self.__detalles:  # ...y recién después se descuenta
            d.producto.descontar_stock(d.cantidad)
        self.__stock_reservado = True

    def liberar_stock(self) -> None:
        """Devuelve el stock reservado. Es idempotente: no devuelve dos veces."""
        if not self.__stock_reservado:
            return
        for d in self.__detalles:
            d.producto.reponer_stock(d.cantidad)
        self.__stock_reservado = False

    # ---------- baja lógica ----------
    def eliminar(self) -> None:
        """Baja lógica del pedido y de sus detalles (el detalle muere con su pedido)."""
        super().eliminar()
        for detalle in self.__detalles:
            detalle.eliminar()

    def __str__(self) -> str:
        return (
            f"[{self.id}] {self.usuario.nombre_completo} | {self.estado.name} | "
            f"{self.forma_pago.name} | Total: ${self.total:.2f} | "
            f"Fecha: {self.fecha.strftime('%d/%m/%Y')}"
        )
