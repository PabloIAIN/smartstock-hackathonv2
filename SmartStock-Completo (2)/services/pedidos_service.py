"""
PedidosService - Servicio de gestión de pedidos
================================================
IMPORTANTE: Cuando se confirma un pedido:
1. Se actualiza el contrato (aumenta card_current_amount)
2. Se actualiza el inventario (disminuye stock_current)
"""

from datetime import datetime


class PedidosService:
    """Servicio para gestionar pedidos con contabilización"""
    
    def __init__(self, data_service, motor_reglas):
        self.data = data_service
        self.motor = motor_reglas
        
        # Almacenamiento en memoria
        self.pedidos = []
        self.contador = 0
    
    def _generar_tracking(self):
        """Genera un número de tracking único"""
        self.contador += 1
        fecha = datetime.now().strftime('%Y%m%d')
        return f'SS-{fecha}-{self.contador:04d}'
    
    def confirmar_pedido(self, cliente_id, producto_id, cantidad):
        """
        Confirma un pedido y ACTUALIZA los datos:
        1. Valida el pedido
        2. Actualiza el contrato (más tarjetas)
        3. Actualiza el inventario (menos stock)
        4. Registra el pedido
        """
        # 1. Validar primero
        validacion = self.motor.validar_pedido(cliente_id, producto_id, cantidad)
        
        if validacion['cantidad_aprobada'] <= 0:
            return {
                'success': False,
                'mensaje': 'Pedido rechazado',
                'resultado': validacion
            }
        
        cantidad_aprobada = validacion['cantidad_aprobada']
        
        # 2. ACTUALIZAR CONTRATO (agregar tarjetas al cliente)
        self.data.actualizar_contrato_despues_pedido(cliente_id, producto_id, cantidad_aprobada)
        
        # 3. ACTUALIZAR INVENTARIO (restar stock)
        self.data.actualizar_stock_producto(producto_id, cantidad_aprobada)
        
        # 4. Crear registro del pedido
        tracking = self._generar_tracking()
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        pedido = {
            'id': self.contador,
            'tracking': tracking,
            'fecha': fecha_actual,
            'cliente_id': cliente_id,
            'cliente_nombre': self.data.obtener_nombre_cliente(cliente_id),
            'producto_id': producto_id,
            'producto_nombre': self.data.obtener_nombre_producto(producto_id),
            'cantidad_solicitada': cantidad,
            'cantidad_aprobada': cantidad_aprobada,
            'estado': validacion['estado'],
            'mensaje': validacion['mensaje'],
            'estado_envio': 'aprobado',
            'ubicacion_actual': 'Almacén Central',
            'historial_envio': [
                {
                    'estado': 'solicitado',
                    'fecha': fecha_actual,
                    'comentario': 'Pedido recibido en el sistema'
                },
                {
                    'estado': 'aprobado',
                    'fecha': fecha_actual,
                    'comentario': f'Pedido aprobado: {cantidad_aprobada:,} tarjetas'
                }
            ]
        }
        
        self.pedidos.append(pedido)
        
        print(f"✅ Pedido confirmado: {tracking} - {cantidad_aprobada} tarjetas para {self.data.obtener_nombre_cliente(cliente_id)}")
        
        return {
            'success': True,
            'mensaje': f'Pedido confirmado con tracking {tracking}',
            'pedido': pedido
        }
    
    def obtener_historial(self):
        """Obtiene el historial completo de pedidos"""
        return sorted(self.pedidos, key=lambda x: x['id'], reverse=True)
    
    def obtener_pedidos_en_proceso(self):
        """Obtiene pedidos que aún no han sido entregados"""
        en_proceso = [p for p in self.pedidos if p['estado_envio'] != 'entregado']
        return sorted(en_proceso, key=lambda x: x['id'], reverse=True)
    
    def obtener_pedido(self, pedido_id):
        """Obtiene un pedido por su ID"""
        for pedido in self.pedidos:
            if pedido['id'] == pedido_id:
                return pedido
        return None
    
    def obtener_pedido_por_tracking(self, tracking):
        """Obtiene un pedido por su número de tracking"""
        tracking_upper = tracking.upper()
        for pedido in self.pedidos:
            if pedido['tracking'].upper() == tracking_upper:
                return pedido
        return None
    
    def obtener_estadisticas_pedidos(self):
        """Obtiene estadísticas de pedidos"""
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        pedidos_hoy = len([p for p in self.pedidos if p['fecha'].startswith(hoy)])
        pedidos_en_proceso = len([p for p in self.pedidos if p['estado_envio'] != 'entregado'])
        pedidos_entregados = len([p for p in self.pedidos if p['estado_envio'] == 'entregado'])
        
        return {
            'pedidos_hoy': pedidos_hoy,
            'pedidos_en_proceso': pedidos_en_proceso,
            'pedidos_entregados': pedidos_entregados
        }
