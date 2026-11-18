"""Carga de datos de ejemplo para poder probar el sistema al iniciarlo."""
from entidades import Usuario
from enums import FormaPago, Rol
from servicios.categoria_servicio import CategoriaServicio
from servicios.pedido_servicio import PedidoServicio
from servicios.producto_servicio import ProductoServicio
from servicios.usuario_servicio import UsuarioServicio


def cargar_datos_ejemplo(
    admin: Usuario,
    categorias: CategoriaServicio,
    productos: ProductoServicio,
    usuarios: UsuarioServicio,
    pedidos: PedidoServicio,
) -> None:
    """Crea un cliente, categorías, productos y un pedido de muestra."""
    cliente = usuarios.crear(admin, "Juan", "Gómez", "juan@foodstore.com", "2634111222", "juan123", Rol.USUARIO)
    pizzas = categorias.crear(admin, "Pizzas", "Pizzas al horno de barro")
    bebidas = categorias.crear(admin, "Bebidas", "Gaseosas, aguas y cervezas")
    postres = categorias.crear(admin, "Postres", "Dulces caseros")
    muzza = productos.crear(admin, "Pizza Muzzarella", "Clásica con salsa y queso", 8500.0, 10, "muzza.jpg", True, pizzas.id)
    productos.crear(admin, "Pizza Napolitana", "Con tomate y ajo", 9500.0, 8, "napo.jpg", True, pizzas.id)
    cola = productos.crear(admin, "Gaseosa Cola 1.5L", "Botella de 1.5 litros", 2800.0, 20, "cola.jpg", True, bebidas.id)
    productos.crear(admin, "Cerveza Rubia", "Lata 473 ml", 2200.0, 15, "rubia.jpg", True, bebidas.id)
    productos.crear(admin, "Tarta de Limón", "Porción individual (poco stock)", 3500.0, 2, "limon.jpg", True, postres.id)
    productos.crear(admin, "Flan Casero", "Con dulce de leche (no disponible)", 3000.0, 5, "flan.jpg", False, postres.id)
    pedidos.crear_pedido(admin, cliente.id, FormaPago.TARJETA, [(muzza.id, 2), (cola.id, 1)])
