"""
DataService - Servicio de carga y acceso a datos
=================================================
Versión SIN pandas - usa csv nativo de Python
"""

import csv
import os

class DataService:
    """Servicio para cargar y acceder a los datos del sistema"""
    
    def __init__(self, data_path='data'):
        self.data_path = data_path
        self.clientes = []
        self.productos = []
        self.contratos = []
        
        self._cargar_datos()
    
    def _cargar_datos(self):
        """Carga todos los archivos CSV"""
        try:
            # Cargar clientes
            clientes_path = os.path.join(self.data_path, 'tabla_clientes.csv')
            if os.path.exists(clientes_path):
                self.clientes = self._leer_csv(clientes_path)
                print(f"✅ Clientes cargados: {len(self.clientes)}")
            
            # Cargar productos
            productos_path = os.path.join(self.data_path, 'productos.csv')
            if os.path.exists(productos_path):
                self.productos = self._leer_csv(productos_path)
                print(f"✅ Productos cargados: {len(self.productos)}")
            
            # Cargar contratos
            contratos_path = os.path.join(self.data_path, 'contratos_clientes.csv')
            if os.path.exists(contratos_path):
                self.contratos = self._leer_csv(contratos_path)
                print(f"✅ Contratos cargados: {len(self.contratos)}")
                
        except Exception as e:
            print(f"❌ Error cargando datos: {e}")
    
    def _leer_csv(self, filepath):
        """Lee un archivo CSV y devuelve lista de diccionarios"""
        datos = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convertir valores numéricos
                fila = {}
                for key, value in row.items():
                    # Intentar convertir a int
                    try:
                        fila[key] = int(value)
                    except (ValueError, TypeError):
                        # Intentar convertir a float
                        try:
                            fila[key] = float(value)
                        except (ValueError, TypeError):
                            fila[key] = value  # Mantener como string
                datos.append(fila)
        return datos
    
    # ============================================================
    # MÉTODOS DE CLIENTES
    # ============================================================
    
    def obtener_clientes(self):
        """Obtiene lista de todos los clientes"""
        return [{'id': c['id'], 'name': c['name']} for c in self.clientes]
    
    def obtener_cliente(self, cliente_id):
        """Obtiene un cliente por su ID"""
        for cliente in self.clientes:
            if cliente['id'] == cliente_id:
                return cliente.copy()
        return None
    
    def obtener_nombre_cliente(self, cliente_id):
        """Obtiene solo el nombre de un cliente"""
        cliente = self.obtener_cliente(cliente_id)
        return cliente['name'] if cliente else 'Desconocido'
    
    # ============================================================
    # MÉTODOS DE PRODUCTOS
    # ============================================================
    
    def obtener_productos(self):
        """Obtiene lista de todos los productos"""
        return [p.copy() for p in self.productos]
    
    def obtener_producto(self, producto_id):
        """Obtiene un producto por su ID"""
        for producto in self.productos:
            if producto['id'] == producto_id:
                return producto.copy()
        return None
    
    def obtener_nombre_producto(self, producto_id):
        """Obtiene solo el nombre de un producto"""
        producto = self.obtener_producto(producto_id)
        return producto['name'] if producto else 'Desconocido'
    
    def obtener_stock_producto(self, producto_id):
        """Obtiene el stock actual de un producto"""
        producto = self.obtener_producto(producto_id)
        if producto:
            # Intentar ambas columnas posibles
            return int(producto.get('stock_current', producto.get('stock_actual', 0)))
        return 0
    
    def actualizar_stock_producto(self, producto_id, cantidad_a_restar):
        """Actualiza el stock de un producto después de un pedido"""
        for producto in self.productos:
            if producto['id'] == producto_id:
                # Determinar columna de stock
                stock_key = 'stock_current' if 'stock_current' in producto else 'stock_actual'
                stock_actual = int(producto.get(stock_key, 0))
                nuevo_stock = max(0, stock_actual - cantidad_a_restar)
                producto[stock_key] = nuevo_stock
                print(f"📦 Stock actualizado: Producto {producto_id} -> {nuevo_stock} (restado {cantidad_a_restar})")
                return True
        return False
    
    # ============================================================
    # MÉTODOS DE CONTRATOS
    # ============================================================
    
    def obtener_contrato(self, cliente_id, producto_id):
        """Obtiene un contrato específico cliente-producto"""
        for contrato in self.contratos:
            cid = contrato.get('client_id', contrato.get('cliente_id'))
            pid = contrato.get('product_id', contrato.get('producto_id'))
            if cid == cliente_id and pid == producto_id:
                return contrato.copy()
        return None
    
    def obtener_contratos_cliente(self, cliente_id):
        """Obtiene todos los contratos de un cliente"""
        resultado = []
        for contrato in self.contratos:
            cid = contrato.get('client_id', contrato.get('cliente_id'))
            if cid == cliente_id:
                resultado.append(contrato.copy())
        return resultado
    
    def obtener_todos_contratos(self):
        """Obtiene todos los contratos"""
        return [c.copy() for c in self.contratos]
    
    def actualizar_contrato_despues_pedido(self, cliente_id, producto_id, cantidad_aprobada):
        """
        Actualiza el contrato después de confirmar un pedido
        - Incrementa card_current_amount
        """
        for contrato in self.contratos:
            cid = contrato.get('client_id', contrato.get('cliente_id'))
            pid = contrato.get('product_id', contrato.get('producto_id'))
            if cid == cliente_id and pid == producto_id:
                # Determinar columna de tarjetas actuales
                key = 'card_current_amount' if 'card_current_amount' in contrato else 'tarjetas_actuales'
                tarjetas_actuales = int(contrato.get(key, 0))
                nuevas_tarjetas = tarjetas_actuales + cantidad_aprobada
                contrato[key] = nuevas_tarjetas
                print(f"📄 Contrato actualizado: Cliente {cliente_id}, Producto {producto_id} -> {nuevas_tarjetas} tarjetas (+{cantidad_aprobada})")
                return True
        return False
