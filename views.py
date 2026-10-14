from abc import ABC, abstractmethod

# Ahora importamos Vendedor en lugar de Pago
from models import Cliente, Vendedor, Producto, Venta
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


# =====================================================================
# CLASE BASE (ABSTRACTA)
# =====================================================================
class CrudBase(ABC):
    @abstractmethod
    def leer(self): pass
    @abstractmethod
    def obtener(self, id_registro): pass
    @abstractmethod
    def buscar(self, texto): pass
    @abstractmethod
    def siguiente(self): pass
    @abstractmethod
    def crear(self, datos): pass
    @abstractmethod
    def actualizar(self, id_registro, datos): pass
    @abstractmethod
    def eliminar(self, id_registro): pass


# =====================================================================
# CONTROLADOR DE CLIENTES
# =====================================================================
class ClienteController(CrudBase):

    def __init__(self, archivo="data/clientes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Cliente.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for cliente in self.lista:
            datos.append(cliente.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            usados = {c.email for c in self.lista if c.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"

        telefono = str(datos.get("telefono", "")).strip()
        if telefono != "" and not telefono.isdigit():
            return "El teléfono solo puede tener números"
        return None

    def leer(self): return self.lista
    def obtener(self, id_cliente):
        for cliente in self.lista:
            if cliente.id == id_cliente:
                return cliente
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "": return encontrados
        for cliente in self.lista:
            if (texto in cliente.nombre.lower() or texto in cliente.apellido.lower()
                    or texto in cliente.email or texto in cliente.telefono
                    or texto in cliente.ciudad.lower()):
                encontrados.append(cliente)
        return encontrados

    def siguiente(self):
        mayor = 0
        for cliente in self.lista:
            if cliente.id > mayor: mayor = cliente.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error: return False, error

        cliente = Cliente(self.siguiente(),
                          str(datos["nombre"]).strip().title(),
                          str(datos["apellido"]).strip().title(),
                          str(datos["email"]).strip().lower(),
                          str(datos.get("telefono", "")).strip(),
                          str(datos.get("ciudad", "")).strip().title())
        self.lista.append(cliente)
        self.guardar()
        return True, f"Cliente creado: {cliente.etiqueta()}"

    def actualizar(self, id_cliente, datos):
        cliente = self.obtener(id_cliente)
        if cliente is None: return False, f"No existe un cliente con id {id_cliente}"
        if not datos: return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "apellido", "email", "telefono", "ciudad"}
        if desconocidos: return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_cliente)
        if error: return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "ciudad"): valor = valor.title()
            elif campo == "email": valor = valor.lower()
            setattr(cliente, campo, valor)

        self.guardar()
        return True, f"Cliente {id_cliente} actualizado"

    def eliminar(self, id_cliente):
        cliente = self.obtener(id_cliente)
        if cliente is None: return False, f"No existe un cliente con id {id_cliente}"
        self.lista.remove(cliente)
        self.guardar()
        return True, f"Cliente {id_cliente} eliminado"


# =====================================================================
# CONTROLADOR DE VENDEDORES (NUEVO)
# =====================================================================
class VendedorController(CrudBase):

    def __init__(self, archivo="data/vendedores.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Vendedor.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for vendedor in self.lista:
            datos.append(vendedor.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            usados = {v.email for v in self.lista if v.id != id_actual}
            if email in usados:
                return "Ese email ya está registrado"
        return None

    def leer(self): return self.lista
    
    def obtener(self, id_vendedor):
        for vendedor in self.lista:
            if vendedor.id == id_vendedor:
                return vendedor
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "": return encontrados
        for vendedor in self.lista:
            if (texto in vendedor.nombre.lower() or texto in vendedor.apellido.lower()
                    or texto in vendedor.email or texto in vendedor.sucursal.lower()):
                encontrados.append(vendedor)
        return encontrados

    def siguiente(self):
        mayor = 0
        for vendedor in self.lista:
            if vendedor.id > mayor: mayor = vendedor.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error: return False, error

        sucursal = str(datos.get("sucursal", "")).strip().title()
        vendedor = Vendedor(self.siguiente(),
                            str(datos["nombre"]).strip().title(),
                            str(datos["apellido"]).strip().title(),
                            str(datos["email"]).strip().lower(),
                            sucursal if sucursal else "Principal")
        self.lista.append(vendedor)
        self.guardar()
        return True, f"Vendedor creado: {vendedor.etiqueta()}"

    def actualizar(self, id_vendedor, datos):
        vendedor = self.obtener(id_vendedor)
        if vendedor is None: return False, f"No existe un vendedor con id {id_vendedor}"
        if not datos: return False, "No se indicó ningún cambio"

        desconocidos = set(datos) - {"nombre", "apellido", "email", "sucursal"}
        if desconocidos: return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_vendedor)
        if error: return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "sucursal"): valor = valor.title()
            elif campo == "email": valor = valor.lower()
            setattr(vendedor, campo, valor)

        self.guardar()
        return True, f"Vendedor {id_vendedor} actualizado"

    def eliminar(self, id_vendedor):
        vendedor = self.obtener(id_vendedor)
        if vendedor is None: return False, f"No existe un vendedor con id {id_vendedor}"
        self.lista.remove(vendedor)
        self.guardar()
        return True, f"Vendedor {id_vendedor} eliminado"


# =====================================================================
# CONTROLADOR DE PRODUCTOS
# =====================================================================
class ProductoController(CrudBase):
    # (El código del ProductoController queda exactamente igual al original. 
    # Lo abrevio aquí visualmente para enfocarnos en los cambios, pero en tu 
    # archivo debe ir completo).
    
    def __init__(self, archivo="data/productos.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Producto.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for producto in self.lista:
            datos.append(producto.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "precio"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"
        if "precio" in datos and not Producto.es_precio_valido(datos["precio"]):
            return f"Precio inválido: '{datos['precio']}'"
        stock = str(datos.get("stock", "")).strip()
        if stock != "" and not stock.isdigit():
            return "El stock debe ser un número entero positivo"
        if "nombre" in datos:
            nombre = str(datos["nombre"]).strip().title()
            for otro in self.lista:
                if otro.nombre == nombre and otro.id != id_actual:
                    return f"Ya existe un producto llamado {nombre}"
        return None

    def leer(self): return self.lista
    def obtener(self, id_producto):
        for producto in self.lista:
            if producto.id == id_producto: return producto
        return None
    def buscar(self, texto):
        texto = texto.strip().lower()
        if texto == "": return []
        return [p for p in self.lista if texto in p.nombre.lower()]
    def siguiente(self):
        mayor = 0
        for producto in self.lista:
            if producto.id > mayor: mayor = producto.id
        return mayor + 1
    def crear(self, datos):
        error = self.validar(datos)
        if error: return False, error
        stock = str(datos.get("stock", "")).strip()
        producto = Producto(self.siguiente(), str(datos["nombre"]).strip().title(),
                            float(datos["precio"]), int(stock) if stock != "" else 0)
        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"
    def actualizar(self, id_producto, datos):
        producto = self.obtener(id_producto)
        if producto is None: return False, "No existe el producto"
        if not datos: return False, "Sin cambios"
        error = self.validar(datos, id_producto)
        if error: return False, error
        if "nombre" in datos: producto.nombre = str(datos["nombre"]).strip().title()
        if "precio" in datos: producto.precio = float(datos["precio"])
        if "stock" in datos: producto.stock = int(datos["stock"])
        self.guardar()
        return True, "Producto actualizado"
    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None: return False, "No existe"
        self.lista.remove(producto)
        self.guardar()
        return True, "Eliminado"


# =====================================================================
# CONTROLADOR DE VENTAS (MODIFICADO PARA INTEGRAR VENDEDOR)
# =====================================================================
class VentaController(CrudBase):

    # 1. Ahora recibe a los Vendedores en el constructor
    def __init__(self, clientes, vendedores, productos, archivo="data/ventas.json"):
        self.clientes = clientes
        self.vendedores = vendedores # <--- NUEVA DEPENDENCIA
        self.productos = productos
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for venta in self.lista:
            datos.append(venta.a_diccionario())
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            vendedor_id = int(datos.get("vendedor_id", 0)) # <--- VALIDAMOS QUE LO MANDEN
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "IDs y cantidad deben ser números enteros"

        if cantidad <= 0:
            return "La cantidad debe ser mayor a 0"
            
        if self.clientes.obtener(cliente_id) is None:
            return f"No existe un cliente con id {cliente_id}"
            
        # 2. Validamos que el vendedor exista en el sistema
        if self.vendedores.obtener(vendedor_id) is None:
            return f"No existe un vendedor con id {vendedor_id}"

        producto = self.productos.obtener(producto_id)
        if producto is None:
            return f"No existe un producto con id {producto_id}"
        if not producto.hay_stock(cantidad):
            return (f"Stock insuficiente de {producto.nombre}: "
                    f"hay {producto.stock}, piden {cantidad}")
        return None

    def leer(self): return self.lista
    
    def obtener(self, id_venta):
        for venta in self.lista:
            if venta.id == id_venta:
                return venta
        return None

    def buscar(self, texto):
        texto = texto.strip()
        encontradas = []
        if texto == "": return encontradas
        for venta in self.lista:
            if texto in venta.fecha:
                encontradas.append(venta)
        return encontradas

    def siguiente(self):
        mayor = 0
        for venta in self.lista:
            if venta.id > mayor: mayor = venta.id
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        producto = self.productos.obtener(int(datos["producto_id"]))
        
        # 3. Le pasamos el vendedor_id al crear la instancia
        venta = Venta(self.siguiente(),
                      int(datos["cliente_id"]),
                      int(datos["vendedor_id"]), # <--- NUEVO CAMPO
                      producto.id,
                      int(datos["cantidad"]),
                      producto.precio)

        producto.descontar_stock(venta.cantidad)
        self.productos.guardar()
        self.lista.append(venta)
        self.guardar()
        return True, f"Venta {venta.id} registrada por ${venta.calcular_total():.2f}"

    def actualizar(self, id_venta, datos):
        return False, "Las ventas no se pueden modificar: anúlela y registre otra"

    def eliminar(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None:
            return False, f"No existe la venta {id_venta}"

        producto = self.productos.obtener(venta.producto_id)
        if producto is not None:
            producto.devolver_stock(venta.cantidad)
            self.productos.guardar()

        self.lista.remove(venta)
        self.guardar()
        return True, f"Venta {id_venta} anulada y stock devuelto"

    def comprobante(self, id_venta):
        venta = self.obtener(id_venta)
        if venta is None: return None

        cliente = self.clientes.obtener(venta.cliente_id)
        vendedor = self.vendedores.obtener(venta.vendedor_id) # <--- OBTENEMOS AL VENDEDOR
        producto = self.productos.obtener(venta.producto_id)
        total = venta.calcular_total()

        # 4. Imprimimos el nombre del vendedor en el ticket
        texto = f"COMPROBANTE #{venta.id}   fecha: {venta.fecha}\n"
        texto += f"Atendido por: {vendedor.nombre_completo() if vendedor else 'eliminado'}\n"
        texto += "-" * 42 + "\n"
        texto += f"Cliente : {cliente.nombre_completo() if cliente else 'eliminado'}\n"
        texto += f"Producto: {producto.nombre if producto else 'eliminado'}\n"
        texto += f"Cantidad: {venta.cantidad} x ${venta.precio_unitario:.2f}\n"
        texto += "-" * 42 + "\n"
        texto += f"SUBTOTAL: ${total:.2f}\n"
        texto += f"TOTAL con IVA: ${Producto.con_iva(total):.2f}"
        return texto