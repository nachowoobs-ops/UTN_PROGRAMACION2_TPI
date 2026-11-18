"""Pruebas del modelo y los servicios (sin menú).

Ejecutar con:  python pruebas.py
Muestra en pantalla los casos válidos ([OK]) y los errores esperados ([ERROR ESPERADO]).
"""
from collections.abc import Callable

from entidades import Base, Calculable, Categoria, DetallePedido, Pedido, Producto, Usuario
from enums import Estado, FormaPago, Rol
from excepciones import (
    CantidadInvalidaError, CredencialesInvalidasError, DatoInvalidoError, DuplicadoError,
    EntidadNoEncontradaError, FoodStoreError, MailInvalidoError, OperacionNoPermitidaError,
    PrecioInvalidoError, StockInsuficienteError, StockInvalidoError,
)
from servicios import CategoriaServicio, PedidoServicio, ProductoServicio, UsuarioServicio

resultados: list[bool] = []


def verificar(descripcion: str, condicion: bool) -> None:
    """Caso válido: la condición debe cumplirse."""
    resultados.append(condicion)
    print(f"  [{'OK' if condicion else 'FALLO'}] {descripcion}")


def esperar_error(descripcion: str, accion: Callable[[], object], tipo: type[BaseException]) -> None:
    """Caso inválido: la acción debe lanzar ``tipo``."""
    try:
        accion()
    except tipo as e:
        resultados.append(True)
        print(f"  [ERROR ESPERADO] {descripcion} -> {type(e).__name__}: {e}")
    except Exception as e:  # tipo de error equivocado
        resultados.append(False)
        print(f"  [FALLO] {descripcion} -> lanzó {type(e).__name__} en vez de {tipo.__name__}")
    else:
        resultados.append(False)
        print(f"  [FALLO] {descripcion} -> no lanzó ninguna excepción")


def titulo(texto: str) -> None:
    print(f"\n=== {texto} ===")


def armar_escenario() -> tuple[CategoriaServicio, ProductoServicio, UsuarioServicio, PedidoServicio, Usuario, Usuario]:
    categorias = CategoriaServicio()
    productos = ProductoServicio(categorias)
    usuarios = UsuarioServicio()
    pedidos = PedidoServicio(usuarios, productos)
    admin = usuarios.crear_administrador_inicial("Ana", "Pérez", "admin@foodstore.com", "111", "admin123")
    cliente = usuarios.crear(admin, "Juan", "Gómez", "juan@foodstore.com", "222", "juan123", Rol.USUARIO)
    return categorias, productos, usuarios, pedidos, admin, cliente


def pruebas_modelo() -> None:
    titulo("MODELO: Base, herencia y encapsulamiento")
    esperar_error("Base no se puede instanciar", lambda: Base(), TypeError)  # type: ignore[abstract]
    esperar_error("Calculable no se puede instanciar", lambda: Calculable(), TypeError)  # type: ignore[abstract]
    c1, c2 = Categoria("Pizzas", "Al horno"), Categoria("Bebidas", "Frías")
    verificar("ids automáticos y consecutivos por clase", c2.id == c1.id + 1)
    verificar("__eq__ compara por id (y tipo)", c1 == c1 and c1 != c2)
    verificar("creado_en se asigna solo", c1.creado_en is not None)
    verificar("__str__ útil en Categoria", "Pizzas" in str(c1))
    p = Producto("Muzza", 100.0, "", 5, "", True, c1)
    verificar("Producto se registra en la agregación de su categoría", p in c1.productos_activos)
    p.categoria = c2
    verificar("Al cambiar de categoría se actualiza la agregación",
              p not in c1.productos and p in c2.productos)
    esperar_error("Precio negativo", lambda: Producto("X", -1, "", 1, "", True, c1), PrecioInvalidoError)
    esperar_error("Precio no numérico", lambda: setattr(p, "precio", "caro"), PrecioInvalidoError)
    esperar_error("Stock negativo", lambda: Producto("X", 1, "", -1, "", True, c1), StockInvalidoError)
    esperar_error("Nombre vacío", lambda: Producto("  ", 1, "", 1, "", True, c1), DatoInvalidoError)
    esperar_error("Categoría con nombre vacío", lambda: Categoria("", "x"), DatoInvalidoError)
    esperar_error("Descontar más que el stock", lambda: p.descontar_stock(99), StockInsuficienteError)
    esperar_error("Reponer cantidad cero", lambda: p.reponer_stock(0), CantidadInvalidaError)

    titulo("MODELO: Usuario y contraseña")
    u = Usuario("Ana", "Pérez", "ana@x.com", "123", "secreta", Rol.ADMIN)
    verificar("verificar_contrasenia correcta", u.verificar_contrasenia("secreta"))
    verificar("verificar_contrasenia incorrecta", not u.verificar_contrasenia("otra"))
    esperar_error("La contraseña no se puede leer", lambda: u.contrasenia, AttributeError)
    verificar("__str__ de Usuario no incluye la contraseña", "secreta" not in str(u))
    esperar_error("Mail sin @", lambda: Usuario("A", "B", "ana.com", "1", "x", Rol.ADMIN), MailInvalidoError)
    esperar_error("Mail sin punto", lambda: Usuario("A", "B", "ana@com", "1", "x", Rol.ADMIN), MailInvalidoError)
    esperar_error("Mail vacío", lambda: Usuario("A", "B", "", "1", "x", Rol.ADMIN), MailInvalidoError)
    esperar_error("Rol inválido", lambda: Usuario("A", "B", "a@b.com", "1", "x", "ADMIN"), DatoInvalidoError)  # type: ignore[arg-type]

    titulo("MODELO: Pedido, composición y Calculable")
    cat = Categoria("Comidas", "x")
    cola = Producto("Cola", 2800.0, "", 10, "", True, cat)
    pizza = Producto("Pizza", 8500.0, "", 3, "", True, cat)
    cli = Usuario("Juan", "Gómez", "j@x.com", "1", "x", Rol.USUARIO)
    ped = Pedido(cli, FormaPago.EFECTIVO)
    verificar("Pedido implementa Calculable", isinstance(ped, Calculable))
    verificar("Pedido nace PENDIENTE y con total 0", ped.estado == Estado.PENDIENTE and ped.total == 0)
    ped.agregar_detalle(2, cola)
    ped.agregar_detalle(1, pizza)
    verificar("subtotal = cantidad x precio", ped.buscar_detalle_por_producto(cola).subtotal == 5600.0)  # type: ignore[union-attr]
    verificar("total calculado = 14100", ped.total == 14100.0)
    ped.agregar_detalle(3, cola)
    verificar("mismo producto: se suma al detalle existente (sin duplicar)",
              len(ped.detalles) == 2 and ped.buscar_detalle_por_producto(cola).cantidad == 5)  # type: ignore[union-attr]
    esperar_error("Cantidad 0", lambda: ped.agregar_detalle(0, cola), CantidadInvalidaError)
    esperar_error("Cantidad mayor al stock (acumulada)", lambda: ped.agregar_detalle(6, cola), StockInsuficienteError)
    esperar_error("detalles es una tupla: no se puede modificar desde afuera",
                  lambda: ped.detalles.append(None), AttributeError)  # type: ignore[attr-defined]
    ped.eliminar_detalle_por_producto(pizza)
    verificar("eliminar detalle recalcula el total", ped.total == 14000.0)
    esperar_error("Eliminar un producto que no está en el pedido",
                  lambda: ped.eliminar_detalle_por_producto(pizza), EntidadNoEncontradaError)
    esperar_error("Pedido sin usuario", lambda: Pedido(None, FormaPago.TARJETA), DatoInvalidoError)  # type: ignore[arg-type]
    eliminado = Usuario("Z", "Z", "z@x.com", "1", "x", Rol.USUARIO)
    eliminado.eliminar()
    esperar_error("Pedido con usuario eliminado", lambda: Pedido(eliminado, FormaPago.TARJETA), OperacionNoPermitidaError)
    gone = Producto("Viejo", 1.0, "", 5, "", True, cat)
    gone.eliminar()
    esperar_error("Agregar un producto eliminado", lambda: ped.agregar_detalle(1, gone), OperacionNoPermitidaError)
    esperar_error("Detalle con cantidad inválida", lambda: DetallePedido(-1, cola), CantidadInvalidaError)

    titulo("MODELO: transiciones de estado")
    p2 = Pedido(cli, FormaPago.TARJETA)
    esperar_error("PENDIENTE -> TERMINADO no es válida", lambda: p2.cambiar_estado(Estado.TERMINADO), OperacionNoPermitidaError)
    p2.cambiar_estado(Estado.CONFIRMADO)
    p2.cambiar_estado(Estado.TERMINADO)
    verificar("PENDIENTE -> CONFIRMADO -> TERMINADO", p2.estado == Estado.TERMINADO)
    esperar_error("TERMINADO no cambia más", lambda: p2.cambiar_estado(Estado.CANCELADO), OperacionNoPermitidaError)


def pruebas_servicios() -> None:
    titulo("SERVICIOS: autenticación y usuarios")
    categorias, productos, usuarios, pedidos, admin, cliente = armar_escenario()
    verificar("autenticar con credenciales correctas", usuarios.autenticar("admin@foodstore.com", "admin123") == admin)
    verificar("el mail no distingue mayúsculas", usuarios.autenticar("ADMIN@foodstore.com", "admin123") == admin)
    esperar_error("Contraseña incorrecta", lambda: usuarios.autenticar("admin@foodstore.com", "mala"), CredencialesInvalidasError)
    esperar_error("Mail inexistente", lambda: usuarios.autenticar("nadie@x.com", "x"), CredencialesInvalidasError)
    esperar_error("Mail duplicado", lambda: usuarios.crear(admin, "O", "T", "JUAN@foodstore.com", "1", "x", Rol.USUARIO), DuplicadoError)
    esperar_error("Cliente no puede crear usuarios", lambda: usuarios.crear(cliente, "O", "T", "o@x.com", "1", "x", Rol.USUARIO), OperacionNoPermitidaError)
    esperar_error("Admin no puede eliminarse a sí mismo", lambda: usuarios.eliminar(admin, admin.id), OperacionNoPermitidaError)
    esperar_error("No se quita el rol al único admin", lambda: usuarios.editar(admin, admin.id, rol=Rol.USUARIO), OperacionNoPermitidaError)
    esperar_error("Mail inválido al editar (no cambia nada)", lambda: usuarios.editar(admin, cliente.id, nombre="Otro", mail="malo"), MailInvalidoError)
    verificar("edición fallida hace rollback", cliente.nombre == "Juan")
    usuarios.editar(admin, cliente.id, celular="999")
    verificar("editar celular", cliente.celular == "999")
    extra = usuarios.crear(admin, "Eli", "Mina", "eli@x.com", "1", "x", Rol.USUARIO)
    usuarios.eliminar(admin, extra.id)
    verificar("usuario eliminado sigue en la colección pero no en listados", extra.eliminado and extra not in usuarios.listar())
    esperar_error("Usuario eliminado no puede iniciar sesión", lambda: usuarios.autenticar("eli@x.com", "x"), CredencialesInvalidasError)
    esperar_error("Usuario eliminado no se obtiene por id", lambda: usuarios.obtener(extra.id), EntidadNoEncontradaError)

    titulo("SERVICIOS: categorías y productos")
    pizzas = categorias.crear(admin, "Pizzas", "Al horno")
    esperar_error("Nombre de categoría repetido (sin distinguir mayúsculas)", lambda: categorias.crear(admin, "pIZZAS", "otra"), DuplicadoError)
    esperar_error("Cliente no puede crear categorías", lambda: categorias.crear(cliente, "X", "Y"), OperacionNoPermitidaError)
    muzza = productos.crear(admin, "Muzza", "", 8500, 5, "", True, pizzas.id)
    esperar_error("Producto con categoría inexistente", lambda: productos.crear(admin, "X", "", 1, 1, "", True, 999), EntidadNoEncontradaError)
    esperar_error("Eliminar categoría con productos activos", lambda: categorias.eliminar(admin, pizzas.id), OperacionNoPermitidaError)
    esperar_error("Editar con precio negativo", lambda: productos.editar(admin, muzza.id, nombre="Nueva", precio=-5), PrecioInvalidoError)
    verificar("edición fallida de producto hace rollback", muzza.nombre == "Muzza" and muzza.precio == 8500.0)
    productos.editar(admin, muzza.id, precio=9000)
    verificar("editar precio", muzza.precio == 9000.0)
    vacia = categorias.crear(admin, "Vacía", "sin productos")
    categorias.eliminar(admin, vacia.id)
    verificar("categoría sin productos activos se elimina (baja lógica)", vacia.eliminado and vacia not in categorias.listar())
    agotado = productos.crear(admin, "Agotado", "", 1, 0, "", True, pizzas.id)
    oculto = productos.crear(admin, "Oculto", "", 1, 5, "", False, pizzas.id)
    visibles = productos.listar(solo_vendibles=True)
    verificar("el cliente solo ve productos disponibles y con stock", muzza in visibles and agotado not in visibles and oculto not in visibles)

    titulo("SERVICIOS: pedidos, stock y baja lógica")
    ped = pedidos.crear_pedido(admin, cliente.id, FormaPago.TARJETA, [(muzza.id, 2)])
    verificar("crear pedido descuenta stock (5 -> 3)", muzza.stock == 3)
    verificar("total = 2 x 9000", ped.total == 18000.0 and ped.estado == Estado.PENDIENTE)
    esperar_error("Pedido cancelado por falta de stock", lambda: pedidos.crear_pedido(admin, cliente.id, FormaPago.EFECTIVO, [(muzza.id, 4)]), StockInsuficienteError)
    verificar("pedido fallido: no se guarda ni toca el stock", len(pedidos.listar()) == 1 and muzza.stock == 3)
    esperar_error("Pedido para usuario eliminado", lambda: pedidos.crear_pedido(admin, extra.id, FormaPago.EFECTIVO, [(muzza.id, 1)]), EntidadNoEncontradaError)
    esperar_error("Pedido sin detalles", lambda: pedidos.crear_pedido(admin, cliente.id, FormaPago.EFECTIVO, []), DatoInvalidoError)
    esperar_error("Cliente no puede crear pedidos", lambda: pedidos.crear_pedido(cliente, cliente.id, FormaPago.EFECTIVO, [(muzza.id, 1)]), OperacionNoPermitidaError)
    esperar_error("Transición inválida no cambia nada", lambda: pedidos.actualizar(admin, ped.id, Estado.TERMINADO, FormaPago.EFECTIVO), OperacionNoPermitidaError)
    verificar("...ni siquiera la forma de pago", ped.forma_pago == FormaPago.TARJETA)
    pedidos.actualizar(admin, ped.id, Estado.CONFIRMADO, FormaPago.TRANSFERENCIA)
    verificar("PENDIENTE -> CONFIRMADO y cambio de forma de pago", ped.estado == Estado.CONFIRMADO and ped.forma_pago == FormaPago.TRANSFERENCIA)
    pedidos.actualizar(admin, ped.id, Estado.CANCELADO)
    verificar("cancelar devuelve el stock (3 -> 5)", muzza.stock == 5)
    esperar_error("Pedido CANCELADO no cambia más", lambda: pedidos.actualizar(admin, ped.id, forma_pago=FormaPago.EFECTIVO), OperacionNoPermitidaError)
    pedidos.eliminar(admin, ped.id)
    verificar("eliminar un pedido ya cancelado no devuelve el stock dos veces", muzza.stock == 5 and ped.eliminado)

    ped2 = pedidos.crear_pedido(admin, cliente.id, FormaPago.EFECTIVO, [(muzza.id, 3)])
    verificar("segundo pedido: stock 5 -> 2", muzza.stock == 2)
    pedidos.eliminar(admin, ped2.id)
    verificar("eliminar pedido no terminado devuelve el stock", muzza.stock == 5)
    verificar("baja lógica marca también los detalles", all(d.eliminado for d in ped2.detalles))
    verificar("el pedido eliminado no aparece en los listados", ped2 not in pedidos.listar())

    titulo("SERVICIOS: visibilidad del cliente y baja de productos")
    otro = usuarios.crear(admin, "Eva", "Sol", "eva@x.com", "3", "x", Rol.USUARIO)
    mio = pedidos.crear_pedido(admin, cliente.id, FormaPago.TARJETA, [(muzza.id, 1)])
    ajeno = pedidos.crear_pedido(admin, otro.id, FormaPago.TARJETA, [(muzza.id, 1)])
    verificar("el cliente solo ve sus pedidos", pedidos.listar_de_usuario(cliente) == [mio])
    esperar_error("Pedido de otro usuario se informa como inexistente", lambda: pedidos.obtener_de_usuario(ajeno.id, cliente), EntidadNoEncontradaError)
    productos.eliminar(admin, muzza.id)
    verificar("producto eliminado no aparece en listados", muzza not in productos.listar())
    verificar("...pero los pedidos existentes lo siguen mostrando", "Muzza" in str(mio.detalles[0]))
    esperar_error("Producto eliminado no se agrega a pedidos nuevos", lambda: pedidos.crear_pedido(admin, cliente.id, FormaPago.TARJETA, [(muzza.id, 1)]), EntidadNoEncontradaError)
    usuarios.eliminar(admin, otro.id)
    verificar("pedidos de un usuario eliminado siguen consultables", ajeno in pedidos.listar())


def main() -> None:
    pruebas_modelo()
    pruebas_servicios()
    total, ok = len(resultados), sum(resultados)
    print(f"\n=== RESUMEN: {ok}/{total} pruebas correctas ===")
    if ok != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
