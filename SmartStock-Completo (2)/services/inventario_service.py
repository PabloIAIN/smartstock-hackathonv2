"""
InventarioService - Servicio de control de inventario
======================================================
Versión SIN pandas
"""


class InventarioService:
    """Servicio para gestionar el inventario de productos"""
    
    def __init__(self, data_service):
        self.data = data_service
    
    def _calcular_nivel(self, stock_actual, stock_alerta):
        """
        Calcula el nivel de stock:
        - critico: < 50% del nivel de alerta
        - bajo: 50% - 100% del nivel de alerta
        - normal: 100% - 200% del nivel de alerta
        - optimo: > 200% del nivel de alerta
        """
        if stock_alerta <= 0:
            return 'optimo'
        
        ratio = stock_actual / stock_alerta
        
        if ratio < 0.5:
            return 'critico'
        elif ratio < 1:
            return 'bajo'
        elif ratio < 2:
            return 'normal'
        else:
            return 'optimo'
    
    def obtener_estado_inventario(self):
        """Obtiene el estado completo del inventario"""
        productos = self.data.productos
        
        if not productos:
            return {
                'productos': [],
                'resumen': {'criticos': 0, 'bajos': 0, 'normales': 0, 'optimos': 0},
                'alertas': []
            }
        
        resultado = []
        resumen = {'criticos': 0, 'bajos': 0, 'normales': 0, 'optimos': 0}
        alertas = []
        
        for p in productos:
            stock_actual = int(p.get('stock_current', p.get('stock_actual', 0)))
            stock_alerta = int(p.get('stock_alert', p.get('stock_minimo', 50)))
            nivel = self._calcular_nivel(stock_actual, stock_alerta)
            
            # Calcular porcentaje
            porcentaje = round((stock_actual / (stock_alerta * 2)) * 100) if stock_alerta > 0 else 100
            
            producto_info = {
                'id': int(p['id']),
                'nombre': p['name'],
                'stock_actual': stock_actual,
                'stock_minimo': stock_alerta,
                'stock_alerta': stock_alerta,
                'nivel': nivel,
                'porcentaje_stock': min(porcentaje, 100)
            }
            resultado.append(producto_info)
            
            # Contar por nivel
            if nivel == 'critico':
                resumen['criticos'] += 1
                alertas.append({
                    'tipo': 'critico',
                    'producto_id': int(p['id']),
                    'producto': p['name'],
                    'stock_actual': stock_actual,
                    'stock_alerta': stock_alerta,
                    'mensaje': f'Stock crítico: solo {stock_actual:,} unidades (alerta en {stock_alerta:,})'
                })
            elif nivel == 'bajo':
                resumen['bajos'] += 1
                alertas.append({
                    'tipo': 'bajo',
                    'producto_id': int(p['id']),
                    'producto': p['name'],
                    'stock_actual': stock_actual,
                    'stock_alerta': stock_alerta,
                    'mensaje': f'Stock bajo: {stock_actual:,} unidades (alerta en {stock_alerta:,})'
                })
            elif nivel == 'normal':
                resumen['normales'] += 1
            else:
                resumen['optimos'] += 1
        
        return {
            'productos': resultado,
            'resumen': resumen,
            'alertas': alertas
        }
    
    def obtener_alertas(self):
        """Obtiene solo las alertas activas"""
        estado = self.obtener_estado_inventario()
        return estado['alertas']
    
    def verificar_stock(self, producto_id, cantidad):
        """Verifica si hay stock suficiente para un pedido"""
        producto = self.data.obtener_producto(producto_id)
        
        if not producto:
            return {
                'disponible': False,
                'stock_actual': 0,
                'cantidad_solicitada': cantidad,
                'mensaje': 'Producto no encontrado'
            }
        
        stock_actual = int(producto.get('stock_current', producto.get('stock_actual', 0)))
        disponible = stock_actual >= cantidad
        
        return {
            'disponible': disponible,
            'stock_actual': stock_actual,
            'cantidad_solicitada': cantidad,
            'faltante': max(0, cantidad - stock_actual),
            'mensaje': 'Stock disponible' if disponible else f'Stock insuficiente. Disponible: {stock_actual:,}'
        }
