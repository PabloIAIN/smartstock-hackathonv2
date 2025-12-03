"""
MotorReglas - Motor de validación con Regla de Oro
===================================================
Versión SIN pandas
"""


class MotorReglas:
    """Motor de validación de pedidos con Regla de Oro"""
    
    def __init__(self, data_service):
        self.data = data_service
    
    def validar_pedido(self, cliente_id, producto_id, cantidad):
        """
        Valida un pedido aplicando la Regla de Oro
        
        REGLA DE ORO:
        El máximo autorizable es el MENOR valor entre:
        1. Tarjetas en uso (card_current_amount - card_inactive_amount)
        2. Espacio en contrato (card_limit_amount - card_current_amount)
        3. Stock disponible (stock_current)
        """
        # 1. Buscar contrato
        contrato = self.data.obtener_contrato(cliente_id, producto_id)
        if not contrato:
            return {
                'estado': 'rechazado',
                'cantidad_solicitada': cantidad,
                'cantidad_aprobada': 0,
                'mensaje': 'No existe un contrato para esta combinación de cliente y producto.',
                'razon': 'sin_contrato'
            }
        
        # 2. Buscar producto (para stock)
        producto = self.data.obtener_producto(producto_id)
        if not producto:
            return {
                'estado': 'rechazado',
                'cantidad_solicitada': cantidad,
                'cantidad_aprobada': 0,
                'mensaje': 'Producto no encontrado.',
                'razon': 'producto_invalido'
            }
        
        # 3. Extraer valores del contrato (soporta ambos nombres de columnas)
        limite_contrato = int(contrato.get('card_limit_amount', contrato.get('limite_contrato', 0)))
        tarjetas_actuales = int(contrato.get('card_current_amount', contrato.get('tarjetas_actuales', 0)))
        tarjetas_inactivas = int(contrato.get('card_inactive_amount', contrato.get('tarjetas_inactivas', 0)))
        stock_disponible = int(producto.get('stock_current', producto.get('stock_actual', 0)))
        
        # 4. Calcular métricas
        tarjetas_en_uso = tarjetas_actuales - tarjetas_inactivas
        espacio_contrato = limite_contrato - tarjetas_actuales
        porcentaje_inactivas = round((tarjetas_inactivas / tarjetas_actuales * 100), 1) if tarjetas_actuales > 0 else 0
        
        # 5. APLICAR REGLA DE ORO
        maximo_autorizable = min(tarjetas_en_uso, espacio_contrato, stock_disponible)
        if maximo_autorizable < 0:
            maximo_autorizable = 0
        
        # 6. Construir detalles
        detalles = {
            'contrato': {
                'limite_contrato': limite_contrato,
                'tarjetas_actuales': tarjetas_actuales,
                'tarjetas_inactivas': tarjetas_inactivas,
                'tarjetas_en_uso': tarjetas_en_uso,
                'espacio_contrato': espacio_contrato
            },
            'inventario': {
                'stock_actual': stock_disponible,
                'stock_alerta': int(producto.get('stock_alert', producto.get('stock_minimo', 0)))
            },
            'regla_oro': {
                'aplicada': porcentaje_inactivas > 0,
                'maximo_por_regla': maximo_autorizable,
                'porcentaje_inactivas': porcentaje_inactivas
            }
        }
        
        # 7. Determinar resultado
        
        # CASO: No se puede aprobar nada
        if maximo_autorizable <= 0:
            if espacio_contrato <= 0:
                razon = 'limite_contrato'
                mensaje = 'Has alcanzado el límite de tu contrato. No puedes solicitar más tarjetas.'
            elif stock_disponible <= 0:
                razon = 'sin_stock'
                mensaje = 'No hay stock disponible para este producto.'
            else:
                razon = 'regla_oro'
                mensaje = f'Tienes {tarjetas_inactivas:,} tarjetas sin usar ({porcentaje_inactivas}%). Según la Regla de Oro, debes activar tus tarjetas actuales antes de solicitar más.'
            
            return {
                'estado': 'rechazado',
                'cantidad_solicitada': cantidad,
                'cantidad_aprobada': 0,
                'mensaje': mensaje,
                'razon': razon,
                'detalles': detalles
            }
        
        # CASO: Aprobación completa
        if cantidad <= maximo_autorizable:
            return {
                'estado': 'aprobado',
                'cantidad_solicitada': cantidad,
                'cantidad_aprobada': cantidad,
                'mensaje': f'Pedido aprobado por {cantidad:,} tarjetas.',
                'razon': 'aprobado',
                'detalles': detalles
            }
        
        # CASO: Aprobación parcial
        if cantidad > stock_disponible and stock_disponible < maximo_autorizable:
            razon = 'stock'
            mensaje = f'Solo hay {stock_disponible:,} tarjetas en stock. Se aprobaron {maximo_autorizable:,}.'
        elif cantidad > espacio_contrato and espacio_contrato < maximo_autorizable:
            razon = 'limite_contrato'
            mensaje = f'Tu contrato solo permite {espacio_contrato:,} tarjetas más. Se aprobaron {maximo_autorizable:,}.'
        else:
            razon = 'regla_oro'
            mensaje = f'Tienes {tarjetas_inactivas:,} tarjetas sin usar ({porcentaje_inactivas}%). Según la Regla de Oro, solo puedes pedir hasta {maximo_autorizable:,} tarjetas (igual a las que tienes en uso).'
        
        return {
            'estado': 'aprobado_parcial',
            'cantidad_solicitada': cantidad,
            'cantidad_aprobada': maximo_autorizable,
            'mensaje': mensaje,
            'razon': razon,
            'detalles': detalles
        }
    
    def obtener_estadisticas(self):
        """Calcula estadísticas generales del sistema"""
        contratos = self.data.contratos
        
        if not contratos:
            return {
                'total_tarjetas': 0,
                'total_en_uso': 0,
                'total_inactivas': 0,
                'porcentaje_uso': 0,
                'porcentaje_inactivas': 0,
                'total_contratos': 0,
                'total_clientes': 0,
                'contratos_problematicos': 0,
                'total_tarjetas_circulacion': 0,
                'desperdicio_estimado_mxn': 0
            }
        
        total_tarjetas = 0
        total_inactivas = 0
        contratos_problematicos = 0
        
        for c in contratos:
            actuales = int(c.get('card_current_amount', c.get('tarjetas_actuales', 0)))
            inactivas = int(c.get('card_inactive_amount', c.get('tarjetas_inactivas', 0)))
            total_tarjetas += actuales
            total_inactivas += inactivas
            
            if actuales > 0 and (inactivas / actuales * 100) > 50:
                contratos_problematicos += 1
        
        total_en_uso = total_tarjetas - total_inactivas
        
        return {
            'total_tarjetas': total_tarjetas,
            'total_en_uso': total_en_uso,
            'total_inactivas': total_inactivas,
            'porcentaje_uso': round(total_en_uso / total_tarjetas * 100, 1) if total_tarjetas > 0 else 0,
            'porcentaje_inactivas': round(total_inactivas / total_tarjetas * 100, 1) if total_tarjetas > 0 else 0,
            'total_contratos': len(contratos),
            'total_clientes': len(self.data.clientes),
            'contratos_problematicos': contratos_problematicos,
            'total_tarjetas_circulacion': total_tarjetas,
            'desperdicio_estimado_mxn': total_inactivas * 50
        }
    
    def detectar_acaparamiento(self, umbral=50):
        """Detecta contratos con alto porcentaje de tarjetas inactivas"""
        contratos = self.data.contratos
        
        if not contratos:
            return {'total_problematicos': 0, 'umbral_usado': umbral, 'contratos': []}
        
        resultado = []
        
        for c in contratos:
            cliente_id = int(c.get('client_id', c.get('cliente_id', 0)))
            producto_id = int(c.get('product_id', c.get('producto_id', 0)))
            tarjetas_actuales = int(c.get('card_current_amount', c.get('tarjetas_actuales', 0)))
            tarjetas_inactivas = int(c.get('card_inactive_amount', c.get('tarjetas_inactivas', 0)))
            
            if tarjetas_actuales <= 0:
                continue
            
            pct = tarjetas_inactivas / tarjetas_actuales * 100
            
            if pct > umbral:
                resultado.append({
                    'contrato_id': int(c.get('id', 0)),
                    'cliente_id': cliente_id,
                    'cliente_nombre': self.data.obtener_nombre_cliente(cliente_id),
                    'producto_id': producto_id,
                    'producto_nombre': self.data.obtener_nombre_producto(producto_id),
                    'tarjetas_totales': tarjetas_actuales,
                    'tarjetas_inactivas': tarjetas_inactivas,
                    'tarjetas_en_uso': tarjetas_actuales - tarjetas_inactivas,
                    'porcentaje_inactivas': round(pct, 1)
                })
        
        resultado.sort(key=lambda x: x['porcentaje_inactivas'], reverse=True)
        
        return {
            'total_problematicos': len(resultado),
            'umbral_usado': umbral,
            'contratos': resultado
        }
    
    def obtener_todos_contratos(self):
        """Obtiene todos los contratos con información detallada"""
        contratos = self.data.contratos
        
        if not contratos:
            return []
        
        resultado = []
        
        for c in contratos:
            cliente_id = int(c.get('client_id', c.get('cliente_id', 0)))
            producto_id = int(c.get('product_id', c.get('producto_id', 0)))
            
            tarjetas_actuales = int(c.get('card_current_amount', c.get('tarjetas_actuales', 0)))
            tarjetas_inactivas = int(c.get('card_inactive_amount', c.get('tarjetas_inactivas', 0)))
            tarjetas_en_uso = tarjetas_actuales - tarjetas_inactivas
            limite = int(c.get('card_limit_amount', c.get('limite_contrato', 0)))
            espacio = limite - tarjetas_actuales
            
            producto = self.data.obtener_producto(producto_id)
            stock = int(producto.get('stock_current', producto.get('stock_actual', 0))) if producto else 0
            
            maximo_pedido = max(0, min(tarjetas_en_uso, espacio, stock))
            porcentaje = round(tarjetas_inactivas / tarjetas_actuales * 100, 1) if tarjetas_actuales > 0 else 0
            
            resultado.append({
                'id': int(c.get('id', 0)),
                'cliente_id': cliente_id,
                'cliente_nombre': self.data.obtener_nombre_cliente(cliente_id),
                'producto_id': producto_id,
                'producto_nombre': self.data.obtener_nombre_producto(producto_id),
                'limite_contrato': limite,
                'tarjetas_actuales': tarjetas_actuales,
                'tarjetas_inactivas': tarjetas_inactivas,
                'tarjetas_en_uso': tarjetas_en_uso,
                'porcentaje_inactivas': porcentaje,
                'maximo_pedido': maximo_pedido
            })
        
        resultado.sort(key=lambda x: x['porcentaje_inactivas'], reverse=True)
        return resultado
    
    def obtener_contratos_cliente(self, cliente_id):
        """Obtiene los contratos de un cliente con máximo pedido calculado"""
        contratos = self.data.obtener_contratos_cliente(cliente_id)
        
        resultado = []
        for c in contratos:
            producto_id = int(c.get('product_id', c.get('producto_id', 0)))
            
            tarjetas_actuales = int(c.get('card_current_amount', c.get('tarjetas_actuales', 0)))
            tarjetas_inactivas = int(c.get('card_inactive_amount', c.get('tarjetas_inactivas', 0)))
            tarjetas_en_uso = tarjetas_actuales - tarjetas_inactivas
            limite = int(c.get('card_limit_amount', c.get('limite_contrato', 0)))
            espacio = limite - tarjetas_actuales
            
            producto = self.data.obtener_producto(producto_id)
            stock = int(producto.get('stock_current', producto.get('stock_actual', 0))) if producto else 0
            
            maximo_pedido = max(0, min(tarjetas_en_uso, espacio, stock))
            porcentaje = round(tarjetas_inactivas / tarjetas_actuales * 100, 1) if tarjetas_actuales > 0 else 0
            
            resultado.append({
                'producto_id': producto_id,
                'producto_nombre': self.data.obtener_nombre_producto(producto_id),
                'limite_contrato': limite,
                'tarjetas_actuales': tarjetas_actuales,
                'tarjetas_inactivas': tarjetas_inactivas,
                'tarjetas_en_uso': tarjetas_en_uso,
                'porcentaje_inactivas': porcentaje,
                'maximo_pedido': maximo_pedido
            })
        
        return resultado
