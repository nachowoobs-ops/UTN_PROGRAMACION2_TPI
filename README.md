# Food Store – Sistema de Gestión de Pedidos de Comida (Consola)

Trabajo Práctico Integrador – **Programación II**
Tecnicatura Universitaria en Programación a Distancia – UTN

Aplicación de consola en **Python** con Programación Orientada a Objetos: gestiona
categorías, productos, usuarios y pedidos con inicio de sesión por rol
(ADMIN / USUARIO). Toda la información vive en memoria (colecciones); al cerrar el
programa los datos se pierden, tal como pide el enunciado.

## Cómo ejecutar

Requisitos: **Python 3.12 o superior**. Solo usa la biblioteca estándar (sin instalar nada).

```bash
cd food_store
python main.py        # inicia la aplicación
python pruebas.py     # corre las pruebas del modelo y los servicios (sin menú)
```

En algunos sistemas el comando es `python3`.

## Credenciales

| Rol     | Mail                  | Contraseña |
|---------|-----------------------|------------|
| ADMIN   | admin@foodstore.com   | admin123   |
| USUARIO | juan@foodstore.com    | juan123    |

El administrador inicial se crea en `main()` (sin él nadie podría ingresar). Además se
cargan datos de ejemplo: 3 categorías, 6 productos (uno con poco stock y otro no
disponible, útiles para probar errores) y un pedido del cliente.

## Estructura del proyecto

```
food_store/
├── main.py           # crea los servicios, el admin inicial y arranca el menú
├── pruebas.py        # pruebas del modelo y servicios, sin menú
├── entidades/        # modelo del UML: Base, Calculable, Categoria, Producto,
│                     #   Usuario, Pedido, DetallePedido
├── enums/            # Rol, Estado, FormaPago
├── excepciones/      # FoodStoreError y sus subclases
├── servicios/        # un servicio por entidad + permisos + datos de ejemplo
└── consola/          # Menu (abstracta), MenuAdministrador, MenuCliente,
                      #   secciones CRUD, lectura validada, inicio de sesión
```

La dependencia va en un solo sentido: **consola → servicios → entidades**.

## Decisiones principales

* `Base` es abstracta (declara `__str__` abstracto) y asigna el `id` con un contador **por clase**;
  `__eq__` compara tipo + id.
* Atributos privados con `@property`; `Usuario.contrasenia` es de solo escritura, se guarda como
  hash PBKDF2 con sal y se verifica con `verificar_contrasenia`.
* `Pedido` implementa `Calculable` y es el único que crea `DetallePedido` (composición).
* Menú por rol con polimorfismo: `Menu` → `MenuAdministrador` / `MenuCliente`; el `if` por rol
  existe en un único lugar (`consola/fabrica_menu.py`).
* Los servicios exigen rol ADMIN para crear/editar/eliminar (defensa en profundidad).
* Sin variables globales: servicios y sesión se crean en `main()` y se pasan a los menús.
* Type hints en todo el código (verificado con `mypy --strict`).

## Entregables

* Informe PDF: `Informe_TPI_FoodStore.pdf` (en la raíz del repositorio).
* Video demostración: _<completar con el enlace con permisos públicos de visualización>_
* Repositorio: _<completar con el enlace de GitHub>_
