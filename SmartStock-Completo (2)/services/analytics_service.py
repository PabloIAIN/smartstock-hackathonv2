"""
Analytics Service - SmartStock
==============================
Servicio de análisis avanzado - SIN pandas
"""

import random
from datetime import datetime, timedelta
from collections import defaultdict
import math

class AnalyticsService:
    def __init__(self, data_service, motor_reglas):
        self.data_service = data_service
        self.motor_reglas = motor_reglas
        self.historial_generado = []
        self._generar_historial_simulado()
        print("   ✓ Analytics Service inicializado")
        print(f"     → {len(self.historial_generado)} registros históricos generados")
    
    def _generar_historial_simulado(self):
        """Genera 12 meses de historial de pedidos simulado"""
        clientes = self.data_service.obtener_clientes()
        productos = self.data_service.obtener_productos()
        contratos = self.data_service.contratos  # Lista de diccionarios
        
        # Patrones de temporalidad
        temporalidad = {
            1: 0.8, 2: 0.9, 3: 1.0, 4: 1.1, 5: 1.2, 6: 1.0,
            7: 0.9, 8: 0.85, 9: 1.1, 10: 1.15, 11: 1.3, 12: 1.5,
        }
        
        producto_temporalidad = {
            'Despensa': {12: 1.8, 11: 1.4, 5: 1.3, 9: 1.2},
            'Gasolina': {12: 1.3, 7: 1.2, 8: 1.2, 4: 1.1},
            'Books': {1: 1.3, 8: 1.4, 9: 1.5},
            'Gym': {1: 1.6, 9: 1.3},
            'Streaming': {11: 1.3, 12: 1.4},
            'Restaurant': {2: 1.3, 5: 1.4, 12: 1.5},
            'Travel': {7: 1.5, 8: 1.5, 12: 1.4, 4: 1.3},
            'Education': {1: 1.4, 8: 1.5, 9: 1.3},
        }
        
        historial = []
        pedido_id = 1
        fecha_actual = datetime.now()
        
        for meses_atras in range(12, 0, -1):
            fecha_mes = fecha_actual - timedelta(days=meses_atras * 30)
            mes = fecha_mes.month
            
            for cliente in clientes:
                cliente_id = cliente['id']
                cliente_nombre = cliente['name']
                
                # Buscar contratos del cliente usando client_id (nombre real de columna)
                contratos_cliente = []
                for c in contratos:
                    cid = c.get('client_id', c.get('cliente_id'))
                    if cid == cliente_id:
                        contratos_cliente.append(c)
                
                if not contratos_cliente:
                    continue
                
                num_pedidos = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1])[0]
                
                if len(contratos_cliente) > 3:
                    num_pedidos = min(num_pedidos + 1, 4)
                
                for _ in range(num_pedidos):
                    contrato = random.choice(contratos_cliente)
                    producto_id = contrato.get('product_id', contrato.get('producto_id'))
                    
                    producto = self.data_service.obtener_producto(producto_id)
                    if not producto:
                        continue
                    
                    cantidad_base = random.randint(20, 200)
                    mult_temp = temporalidad.get(mes, 1.0)
                    
                    producto_nombre = producto.get('name', '')
                    for key, mult in producto_temporalidad.items():
                        if key in producto_nombre:
                            mult_temp *= mult.get(mes, 1.0)
                            break
                    
                    cantidad = int(cantidad_base * mult_temp)
                    dia = random.randint(1, 28)
                    fecha_pedido = fecha_mes.replace(day=dia)
                    
                    historial.append({
                        'id': pedido_id,
                        'cliente_id': cliente_id,
                        'cliente_nombre': cliente_nombre,
                        'producto_id': producto_id,
                        'producto_nombre': producto_nombre,
                        'cantidad': cantidad,
                        'fecha': fecha_pedido.strftime('%Y-%m-%d'),
                        'mes': mes,
                        'anio': fecha_pedido.year,
                        'estado': 'entregado'
                    })
                    pedido_id += 1
        
        historial.sort(key=lambda x: x['fecha'])
        self.historial_generado = historial
    
    def obtener_historial_completo(self):
        return self.historial_generado
    
    def obtener_riesgo_cobertura_contractual(self):
        contratos = self.motor_reglas.obtener_todos_contratos()
        
        riesgos = []
        total_riesgo = 0
        
        for contrato in contratos:
            limite = contrato.get('limite_contrato', 0)
            actuales = contrato.get('tarjetas_actuales', 0)
            maximo_pedido = contrato.get('maximo_pedido', 0)
            
            if limite == 0:
                continue
            
            uso_porcentaje = (actuales / limite) * 100 if limite > 0 else 0
            capacidad_restante = limite - actuales
            
            riesgo = 0
            if uso_porcentaje >= 90:
                riesgo = 90
            elif uso_porcentaje >= 75:
                riesgo = 70
            elif uso_porcentaje >= 50:
                riesgo = 40
            else:
                riesgo = 20
            
            inactivas_pct = contrato.get('porcentaje_inactivas', 0)
            if inactivas_pct > 70:
                riesgo += 20
            elif inactivas_pct > 50:
                riesgo += 10
            
            riesgo = min(riesgo, 100)
            
            if riesgo >= 80:
                nivel = 'critico'
            elif riesgo >= 60:
                nivel = 'alto'
            elif riesgo >= 40:
                nivel = 'medio'
            else:
                nivel = 'bajo'
            
            riesgos.append({
                'cliente_id': contrato.get('cliente_id'),
                'cliente_nombre': contrato.get('cliente_nombre'),
                'producto_id': contrato.get('producto_id'),
                'producto_nombre': contrato.get('producto_nombre'),
                'limite_contrato': limite,
                'tarjetas_actuales': actuales,
                'uso_porcentaje': round(uso_porcentaje, 1),
                'capacidad_restante': capacidad_restante,
                'maximo_pedido': maximo_pedido,
                'porcentaje_inactivas': inactivas_pct,
                'riesgo_score': riesgo,
                'nivel_riesgo': nivel
            })
            
            total_riesgo += riesgo
        
        promedio_riesgo = total_riesgo / len(riesgos) if riesgos else 0
        
        por_nivel = {
            'critico': len([r for r in riesgos if r['nivel_riesgo'] == 'critico']),
            'alto': len([r for r in riesgos if r['nivel_riesgo'] == 'alto']),
            'medio': len([r for r in riesgos if r['nivel_riesgo'] == 'medio']),
            'bajo': len([r for r in riesgos if r['nivel_riesgo'] == 'bajo']),
        }
        
        riesgos_ordenados = sorted(riesgos, key=lambda x: x['riesgo_score'], reverse=True)
        
        return {
            'promedio_riesgo': round(promedio_riesgo, 1),
            'total_contratos': len(riesgos),
            'por_nivel': por_nivel,
            'top_criticos': riesgos_ordenados[:10],
            'detalle': riesgos_ordenados
        }
    
    def obtener_tendencia_demanda(self):
        demanda_por_mes = defaultdict(lambda: {'cantidad': 0, 'pedidos': 0})
        
        for pedido in self.historial_generado:
            key = f"{pedido['anio']}-{pedido['mes']:02d}"
            demanda_por_mes[key]['cantidad'] += pedido['cantidad']
            demanda_por_mes[key]['pedidos'] += 1
        
        meses_ordenados = sorted(demanda_por_mes.keys())
        datos_tendencia = []
        
        for i, mes in enumerate(meses_ordenados):
            datos_tendencia.append({
                'mes': mes,
                'mes_nombre': self._nombre_mes(int(mes.split('-')[1])),
                'cantidad': demanda_por_mes[mes]['cantidad'],
                'pedidos': demanda_por_mes[mes]['pedidos'],
                'indice': i
            })
        
        for i, dato in enumerate(datos_tendencia):
            if i >= 2:
                promedio = sum(datos_tendencia[j]['cantidad'] for j in range(i-2, i+1)) / 3
                dato['promedio_movil'] = round(promedio)
            else:
                dato['promedio_movil'] = dato['cantidad']
        
        n = len(datos_tendencia)
        pronostico = []
        
        if n > 1:
            x_vals = [d['indice'] for d in datos_tendencia]
            y_vals = [d['cantidad'] for d in datos_tendencia]
            
            x_mean = sum(x_vals) / n
            y_mean = sum(y_vals) / n
            
            numerador = sum((x_vals[i] - x_mean) * (y_vals[i] - y_mean) for i in range(n))
            denominador = sum((x_vals[i] - x_mean) ** 2 for i in range(n))
            
            pendiente = numerador / denominador if denominador != 0 else 0
            intercepto = y_mean - pendiente * x_mean
            
            ultimo_mes = datetime.strptime(meses_ordenados[-1], '%Y-%m')
            
            for i in range(1, 4):
                mes_futuro = ultimo_mes + timedelta(days=30 * i)
                indice_futuro = n + i - 1
                cantidad_pronosticada = intercepto + pendiente * indice_futuro
                
                temporalidad_historica = self._obtener_factor_temporalidad(mes_futuro.month)
                cantidad_ajustada = cantidad_pronosticada * temporalidad_historica
                
                pronostico.append({
                    'mes': mes_futuro.strftime('%Y-%m'),
                    'mes_nombre': self._nombre_mes(mes_futuro.month),
                    'cantidad_pronosticada': max(0, round(cantidad_ajustada)),
                    'confianza': 85 - (i * 10)
                })
        
        if len(datos_tendencia) >= 2:
            inicio = sum(d['cantidad'] for d in datos_tendencia[:3]) / min(3, len(datos_tendencia))
            fin = sum(d['cantidad'] for d in datos_tendencia[-3:]) / min(3, len(datos_tendencia))
            cambio_porcentual = ((fin - inicio) / inicio) * 100 if inicio > 0 else 0
            
            if cambio_porcentual > 10:
                tendencia = 'creciente'
            elif cambio_porcentual < -10:
                tendencia = 'decreciente'
            else:
                tendencia = 'estable'
        else:
            tendencia = 'sin_datos'
            cambio_porcentual = 0
        
        return {
            'historico': datos_tendencia,
            'pronostico': pronostico,
            'tendencia': tendencia,
            'cambio_porcentual': round(cambio_porcentual, 1),
            'total_historico': sum(d['cantidad'] for d in datos_tendencia),
            'promedio_mensual': round(sum(d['cantidad'] for d in datos_tendencia) / len(datos_tendencia)) if datos_tendencia else 0
        }
    
    def _obtener_factor_temporalidad(self, mes):
        cantidades_mes = [p['cantidad'] for p in self.historial_generado if p['mes'] == mes]
        promedio_mes = sum(cantidades_mes) / len(cantidades_mes) if cantidades_mes else 0
        promedio_general = sum(p['cantidad'] for p in self.historial_generado) / len(self.historial_generado) if self.historial_generado else 1
        return promedio_mes / promedio_general if promedio_general > 0 else 1.0
    
    def _nombre_mes(self, mes):
        meses = ['', 'Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        return meses[mes] if 1 <= mes <= 12 else ''
    
    def obtener_stock_rop(self):
        productos = self.data_service.obtener_productos()
        
        demanda_producto = defaultdict(list)
        for pedido in self.historial_generado:
            demanda_producto[pedido['producto_id']].append(pedido['cantidad'])
        
        resultado = []
        
        for producto in productos:
            pid = producto['id']
            stock_actual = producto.get('stock_current', producto.get('stock_actual', 0))
            stock_minimo = producto.get('stock_alert', producto.get('stock_minimo', 50))
            
            cantidades = demanda_producto.get(pid, [0])
            demanda_total = sum(cantidades)
            demanda_mensual = demanda_total / 12
            demanda_diaria = demanda_mensual / 30
            
            lead_time = 7
            factor_seguridad = 1.5
            
            demanda_lead_time = demanda_diaria * lead_time
            stock_seguridad = demanda_diaria * lead_time * (factor_seguridad - 1)
            rop = demanda_lead_time + stock_seguridad
            
            eoq = math.sqrt(2 * demanda_mensual * 12 * 50 / 2) if demanda_mensual > 0 else 100
            dias_cobertura = stock_actual / demanda_diaria if demanda_diaria > 0 else 999
            
            if stock_actual <= stock_minimo:
                estado = 'critico'
                alerta = '🔴 Stock crítico - Reordenar inmediatamente'
            elif stock_actual <= rop:
                estado = 'reordenar'
                alerta = '🟡 Alcanzó ROP - Generar orden de compra'
            elif stock_actual <= rop * 1.5:
                estado = 'precaucion'
                alerta = '🟠 Próximo a ROP - Monitorear'
            else:
                estado = 'ok'
                alerta = '🟢 Stock saludable'
            
            resultado.append({
                'producto_id': pid,
                'producto_nombre': producto.get('name', 'N/A'),
                'stock_actual': int(stock_actual),
                'stock_minimo': int(stock_minimo),
                'rop': round(rop),
                'eoq': round(eoq),
                'demanda_diaria': round(demanda_diaria, 1),
                'demanda_mensual': round(demanda_mensual),
                'dias_cobertura': min(round(dias_cobertura), 999),
                'stock_seguridad': round(stock_seguridad),
                'estado': estado,
                'alerta': alerta,
                'porcentaje_stock': round((stock_actual / (rop * 2)) * 100) if rop > 0 else 100
            })
        
        orden_estado = {'critico': 0, 'reordenar': 1, 'precaucion': 2, 'ok': 3}
        resultado.sort(key=lambda x: orden_estado.get(x['estado'], 4))
        
        resumen = {
            'criticos': len([r for r in resultado if r['estado'] == 'critico']),
            'reordenar': len([r for r in resultado if r['estado'] == 'reordenar']),
            'precaucion': len([r for r in resultado if r['estado'] == 'precaucion']),
            'ok': len([r for r in resultado if r['estado'] == 'ok']),
        }
        
        return {
            'productos': resultado,
            'resumen': resumen,
            'lead_time_dias': 7,
            'factor_seguridad': 1.5
        }
    
    def obtener_temporadas_demanda(self):
        demanda_mes = defaultdict(lambda: {'cantidad': 0, 'pedidos': 0})
        for pedido in self.historial_generado:
            mes = pedido['mes']
            demanda_mes[mes]['cantidad'] += pedido['cantidad']
            demanda_mes[mes]['pedidos'] += 1
        
        demanda_mes_lista = []
        max_cantidad = max((d['cantidad'] for d in demanda_mes.values()), default=1)
        
        for mes in range(1, 13):
            datos = demanda_mes.get(mes, {'cantidad': 0, 'pedidos': 0})
            demanda_mes_lista.append({
                'mes': mes,
                'mes_nombre': self._nombre_mes_completo(mes),
                'cantidad': datos['cantidad'],
                'pedidos': datos['pedidos'],
                'porcentaje': round((datos['cantidad'] / max_cantidad) * 100) if max_cantidad > 0 else 0,
                'es_temporada_alta': datos['cantidad'] > (max_cantidad * 0.7)
            })
        
        demanda_empresa = defaultdict(lambda: {'cantidad': 0, 'pedidos': 0})
        for pedido in self.historial_generado:
            empresa = pedido['cliente_nombre']
            demanda_empresa[empresa]['cantidad'] += pedido['cantidad']
            demanda_empresa[empresa]['pedidos'] += 1
        
        top_empresas = sorted(
            [{'empresa': k, **v} for k, v in demanda_empresa.items()],
            key=lambda x: x['cantidad'],
            reverse=True
        )[:10]
        
        demanda_producto = defaultdict(lambda: {'cantidad': 0, 'pedidos': 0, 'meses_pico': []})
        demanda_producto_mes = defaultdict(lambda: defaultdict(int))
        
        for pedido in self.historial_generado:
            producto = pedido['producto_nombre']
            demanda_producto[producto]['cantidad'] += pedido['cantidad']
            demanda_producto[producto]['pedidos'] += 1
            demanda_producto_mes[producto][pedido['mes']] += pedido['cantidad']
        
        for producto, meses in demanda_producto_mes.items():
            if meses:
                max_mes_cantidad = max(meses.values())
                meses_pico = [self._nombre_mes_completo(m) for m, c in meses.items() 
                            if c >= max_mes_cantidad * 0.8]
                demanda_producto[producto]['meses_pico'] = meses_pico[:3]
        
        demanda_tarjeta = sorted(
            [{'producto': k, **v} for k, v in demanda_producto.items()],
            key=lambda x: x['cantidad'],
            reverse=True
        )
        
        heatmap_data = []
        top_5_empresas = [e['empresa'] for e in top_empresas[:5]]
        
        for empresa in top_5_empresas:
            pedidos_empresa = [p for p in self.historial_generado if p['cliente_nombre'] == empresa]
            fila = {'empresa': empresa[:20] + '...' if len(empresa) > 20 else empresa}
            for mes in range(1, 13):
                cantidad = sum(p['cantidad'] for p in pedidos_empresa if p['mes'] == mes)
                fila[self._nombre_mes(mes)] = cantidad
            heatmap_data.append(fila)
        
        temporadas_altas = [m for m in demanda_mes_lista if m['es_temporada_alta']]
        
        return {
            'por_mes': demanda_mes_lista,
            'top_empresas': top_empresas,
            'por_producto': demanda_tarjeta,
            'heatmap': heatmap_data,
            'temporadas_altas': temporadas_altas,
            'mes_mas_alto': max(demanda_mes_lista, key=lambda x: x['cantidad']) if demanda_mes_lista else None,
            'mes_mas_bajo': min(demanda_mes_lista, key=lambda x: x['cantidad']) if demanda_mes_lista else None
        }
    
    def _nombre_mes_completo(self, mes):
        meses = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return meses[mes] if 1 <= mes <= 12 else ''
    
    def obtener_dashboard_completo(self):
        return {
            'riesgo_cobertura': self.obtener_riesgo_cobertura_contractual(),
            'tendencia_demanda': self.obtener_tendencia_demanda(),
            'stock_rop': self.obtener_stock_rop(),
            'temporadas': self.obtener_temporadas_demanda()
        }
