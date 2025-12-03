"""
TrackingService - Servicio de seguimiento de envíos
====================================================
"""

from datetime import datetime


class TrackingService:
    """Servicio para gestionar el tracking de pedidos"""
    
    ESTADOS = ['solicitado', 'aprobado', 'en_preparacion', 'en_camino', 'entregado']
    
    ESTADOS_INFO = {
        'solicitado': {
            'orden': 0,
            'nombre': 'Solicitado',
            'descripcion': 'Pedido recibido en el sistema',
            'icono': '📝',
            'color': '#4169E1'
        },
        'aprobado': {
            'orden': 1,
            'nombre': 'Aprobado',
            'descripcion': 'Pedido validado y aprobado',
            'icono': '✅',
            'color': '#10b981'
        },
        'en_preparacion': {
            'orden': 2,
            'nombre': 'En Preparación',
            'descripcion': 'Almacén preparando el pedido',
            'icono': '📦',
            'color': '#f59e0b'
        },
        'en_camino': {
            'orden': 3,
            'nombre': 'En Camino',
            'descripcion': 'Pedido en ruta de entrega',
            'icono': '🚚',
            'color': '#8b5cf6'
        },
        'entregado': {
            'orden': 4,
            'nombre': 'Entregado',
            'descripcion': 'Pedido entregado al cliente',
            'icono': '🎉',
            'color': '#10b981'
        }
    }
    
    UBICACIONES = {
        'solicitado': 'Pendiente de procesamiento',
        'aprobado': 'Almacén Central',
        'en_preparacion': 'Almacén Central - Área de Empaque',
        'en_camino': 'En ruta de entrega',
        'entregado': 'Entregado al cliente'
    }
    
    def __init__(self, pedidos_service):
        self.pedidos = pedidos_service
    
    def buscar_por_tracking(self, tracking):
        """Busca un pedido por su número de tracking"""
        pedido = self.pedidos.obtener_pedido_por_tracking(tracking)
        
        if not pedido:
            return {'error': 'Pedido no encontrado'}
        
        estado_actual = pedido.get('estado_envio', 'solicitado')
        progreso = self._calcular_progreso(estado_actual)
        
        return {
            'pedido': pedido,
            'estado_actual': estado_actual,
            'estado_info': self.ESTADOS_INFO.get(estado_actual, {}),
            'progreso': progreso,
            'ubicacion': pedido.get('ubicacion_actual', self.UBICACIONES.get(estado_actual, ''))
        }
    
    def _calcular_progreso(self, estado):
        """Calcula el porcentaje de progreso"""
        if estado not in self.ESTADOS:
            return 0
        idx = self.ESTADOS.index(estado)
        return ((idx + 1) / len(self.ESTADOS)) * 100
    
    def actualizar_estado(self, pedido_id, nuevo_estado, comentario=None, ubicacion=None):
        """Actualiza el estado de envío de un pedido"""
        pedido = self.pedidos.obtener_pedido(pedido_id)
        
        if not pedido:
            return {'success': False, 'error': 'Pedido no encontrado'}
        
        if nuevo_estado not in self.ESTADOS:
            return {'success': False, 'error': f'Estado inválido: {nuevo_estado}'}
        
        estado_actual = pedido.get('estado_envio', 'solicitado')
        idx_actual = self.ESTADOS.index(estado_actual)
        idx_nuevo = self.ESTADOS.index(nuevo_estado)
        
        if idx_nuevo <= idx_actual:
            return {'success': False, 'error': 'No se puede retroceder el estado de envío'}
        
        # Actualizar estado
        pedido['estado_envio'] = nuevo_estado
        pedido['ubicacion_actual'] = ubicacion or self.UBICACIONES.get(nuevo_estado, '')
        
        # Agregar al historial
        pedido['historial_envio'].append({
            'estado': nuevo_estado,
            'fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'comentario': comentario or self.ESTADOS_INFO[nuevo_estado]['descripcion']
        })
        
        return {
            'success': True,
            'mensaje': f'Estado actualizado a: {self.ESTADOS_INFO[nuevo_estado]["nombre"]}',
            'pedido': pedido
        }
    
    def obtener_estados_info(self):
        """Obtiene información de todos los estados"""
        return self.ESTADOS_INFO
    
    def obtener_timeline(self, pedido_id):
        """Obtiene el timeline completo de un pedido"""
        pedido = self.pedidos.obtener_pedido(pedido_id)
        
        if not pedido:
            return {'error': 'Pedido no encontrado'}
        
        estado_actual = pedido.get('estado_envio', 'solicitado')
        idx_actual = self.ESTADOS.index(estado_actual)
        
        timeline = []
        for i, estado in enumerate(self.ESTADOS):
            info = self.ESTADOS_INFO[estado]
            timeline.append({
                'estado': estado,
                'nombre': info['nombre'],
                'icono': info['icono'],
                'color': info['color'],
                'completado': i <= idx_actual,
                'actual': estado == estado_actual
            })
        
        return {
            'pedido': pedido,
            'timeline': timeline,
            'progreso': self._calcular_progreso(estado_actual)
        }
