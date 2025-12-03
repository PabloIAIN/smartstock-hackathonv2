"""
SmartStock - API Backend
========================
Sistema de Control Inteligente de Incentivos
Hackathon OneCard 2024

Ejecutar: python app.py
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from services import DataService, MotorReglas, InventarioService, PedidosService, TrackingService, AnalyticsService

# ============================================================
# INICIALIZACIÓN
# ============================================================

app = Flask(__name__)
CORS(app)

# Inicializar servicios
print("\n" + "=" * 60)
print("🚀 SmartStock - Sistema de Control de Incentivos")
print("=" * 60)

data_service = DataService(data_path='data')
motor_reglas = MotorReglas(data_service)
inventario_service = InventarioService(data_service)
pedidos_service = PedidosService(data_service, motor_reglas)
tracking_service = TrackingService(pedidos_service)
analytics_service = AnalyticsService(data_service, motor_reglas)

print("=" * 60)

# ============================================================
# MIDDLEWARE
# ============================================================

@app.after_request
def after_request(response):
    """Agrega headers de seguridad y CORS"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

# ============================================================
# ENDPOINTS - SISTEMA
# ============================================================

@app.route('/api/health', methods=['GET'])
def health():
    """Estado del sistema"""
    return jsonify({
        'status': 'ok',
        'sistema': 'SmartStock',
        'version': '2.1'
    })

@app.route('/api/estadisticas', methods=['GET'])
def estadisticas():
    """Estadísticas generales del sistema"""
    stats = motor_reglas.obtener_estadisticas()
    pedidos_stats = pedidos_service.obtener_estadisticas_pedidos()
    
    return jsonify({
        **stats,
        **pedidos_stats
    })

# ============================================================
# ENDPOINTS - CLIENTES
# ============================================================

@app.route('/api/clientes', methods=['GET'])
def clientes():
    """Lista de todos los clientes"""
    return jsonify({
        'clientes': data_service.obtener_clientes()
    })

@app.route('/api/cliente/<int:cliente_id>', methods=['GET'])
def cliente(cliente_id):
    """Obtiene un cliente específico"""
    cliente = data_service.obtener_cliente(cliente_id)
    if not cliente:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    return jsonify(cliente)

@app.route('/api/cliente/<int:cliente_id>/contratos', methods=['GET'])
def cliente_contratos(cliente_id):
    """Obtiene los contratos de un cliente con máximo pedido calculado"""
    contratos = motor_reglas.obtener_contratos_cliente(cliente_id)
    return jsonify({
        'cliente_id': cliente_id,
        'contratos': contratos
    })

# ============================================================
# ENDPOINTS - PRODUCTOS
# ============================================================

@app.route('/api/productos', methods=['GET'])
def productos():
    """Lista de todos los productos"""
    return jsonify({
        'productos': data_service.obtener_productos()
    })

@app.route('/api/producto/<int:producto_id>', methods=['GET'])
def producto(producto_id):
    """Obtiene un producto específico"""
    producto = data_service.obtener_producto(producto_id)
    if not producto:
        return jsonify({'error': 'Producto no encontrado'}), 404
    return jsonify(producto)

# ============================================================
# ENDPOINTS - INVENTARIO
# ============================================================

@app.route('/api/inventario', methods=['GET'])
def inventario():
    """Estado completo del inventario"""
    return jsonify(inventario_service.obtener_estado_inventario())

@app.route('/api/inventario/alertas', methods=['GET'])
def inventario_alertas():
    """Solo alertas de inventario"""
    return jsonify({
        'alertas': inventario_service.obtener_alertas()
    })

# ============================================================
# ENDPOINTS - CONTRATOS
# ============================================================

@app.route('/api/contratos', methods=['GET'])
def contratos():
    """Todos los contratos con información detallada"""
    return jsonify({
        'contratos': motor_reglas.obtener_todos_contratos()
    })

@app.route('/api/contratos/acaparamiento', methods=['GET'])
def contratos_acaparamiento():
    """Detecta contratos con alto porcentaje de inactivas"""
    umbral = request.args.get('umbral', 50, type=int)
    return jsonify(motor_reglas.detectar_acaparamiento(umbral))

# ============================================================
# ENDPOINTS - PEDIDOS
# ============================================================

@app.route('/api/pedido/validar', methods=['POST'])
def validar_pedido():
    """
    Valida un pedido aplicando la Regla de Oro
    Body: { cliente_id, producto_id, cantidad }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    cliente_id = data.get('cliente_id')
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad')
    
    if not all([cliente_id, producto_id, cantidad]):
        return jsonify({'error': 'Faltan campos: cliente_id, producto_id, cantidad'}), 400
    
    resultado = motor_reglas.validar_pedido(cliente_id, producto_id, cantidad)
    return jsonify(resultado)

@app.route('/api/pedido/confirmar', methods=['POST'])
def confirmar_pedido():
    """
    Confirma un pedido y actualiza contratos + inventario
    Body: { cliente_id, producto_id, cantidad }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Datos requeridos'}), 400
    
    cliente_id = data.get('cliente_id')
    producto_id = data.get('producto_id')
    cantidad = data.get('cantidad')
    
    if not all([cliente_id, producto_id, cantidad]):
        return jsonify({'error': 'Faltan campos: cliente_id, producto_id, cantidad'}), 400
    
    resultado = pedidos_service.confirmar_pedido(cliente_id, producto_id, cantidad)
    return jsonify(resultado)

@app.route('/api/pedidos/historial', methods=['GET'])
def pedidos_historial():
    """Historial completo de pedidos"""
    return jsonify({
        'pedidos': pedidos_service.obtener_historial()
    })

@app.route('/api/pedidos/en-proceso', methods=['GET'])
def pedidos_en_proceso():
    """Pedidos pendientes de entrega"""
    return jsonify({
        'pedidos': pedidos_service.obtener_pedidos_en_proceso()
    })

# ============================================================
# ENDPOINTS - TRACKING
# ============================================================

@app.route('/api/pedido/tracking/<tracking>', methods=['GET'])
def buscar_tracking(tracking):
    """Busca un pedido por su tracking (público)"""
    resultado = tracking_service.buscar_por_tracking(tracking)
    if 'error' in resultado:
        return jsonify(resultado), 404
    return jsonify(resultado)

@app.route('/api/pedido/<int:pedido_id>/actualizar-estado', methods=['POST'])
def actualizar_estado_pedido(pedido_id):
    """Actualiza el estado de envío de un pedido"""
    data = request.get_json()
    
    if not data or 'estado' not in data:
        return jsonify({'error': 'Estado requerido'}), 400
    
    resultado = tracking_service.actualizar_estado(
        pedido_id,
        data['estado'],
        data.get('comentario'),
        data.get('ubicacion')
    )
    
    if not resultado['success']:
        return jsonify(resultado), 400
    
    return jsonify(resultado)

@app.route('/api/estados-envio', methods=['GET'])
def estados_envio():
    """Lista de estados de envío posibles"""
    return jsonify(tracking_service.obtener_estados_info())

# ============================================================
# ENDPOINTS - ANALYTICS
# ============================================================

@app.route('/api/analytics/dashboard', methods=['GET'])
def analytics_dashboard():
    """Dashboard completo con todas las métricas"""
    return jsonify(analytics_service.obtener_dashboard_completo())

@app.route('/api/analytics/riesgo-cobertura', methods=['GET'])
def analytics_riesgo():
    """Métricas de riesgo de cobertura contractual"""
    return jsonify(analytics_service.obtener_riesgo_cobertura_contractual())

@app.route('/api/analytics/tendencia-demanda', methods=['GET'])
def analytics_tendencia():
    """Tendencia de demanda y pronóstico"""
    return jsonify(analytics_service.obtener_tendencia_demanda())

@app.route('/api/analytics/stock-rop', methods=['GET'])
def analytics_rop():
    """Stock físico y Punto de Reorden (ROP)"""
    return jsonify(analytics_service.obtener_stock_rop())

@app.route('/api/analytics/temporadas', methods=['GET'])
def analytics_temporadas():
    """Análisis de temporadas de demanda"""
    return jsonify(analytics_service.obtener_temporadas_demanda())

@app.route('/api/analytics/historial', methods=['GET'])
def analytics_historial():
    """Historial completo de pedidos (12 meses)"""
    return jsonify({
        'pedidos': analytics_service.obtener_historial_completo()
    })

# ============================================================
# MANEJO DE ERRORES
# ============================================================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Endpoint no encontrado'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Error interno del servidor'}), 500

@app.errorhandler(400)
def bad_request(e):
    return jsonify({'error': 'Solicitud inválida'}), 400

# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == '__main__':
    print("\n🌐 API corriendo en: http://localhost:5000")
    print("\n📚 Endpoints disponibles:")
    print("   - GET  /api/health")
    print("   - GET  /api/estadisticas")
    print("   - GET  /api/clientes")
    print("   - GET  /api/cliente/<id>/contratos")
    print("   - GET  /api/productos")
    print("   - GET  /api/inventario")
    print("   - GET  /api/contratos")
    print("   - GET  /api/contratos/acaparamiento")
    print("   - POST /api/pedido/validar")
    print("   - POST /api/pedido/confirmar")
    print("   - GET  /api/pedidos/historial")
    print("   - GET  /api/pedidos/en-proceso")
    print("   - GET  /api/pedido/tracking/<tracking>")
    print("   - POST /api/pedido/<id>/actualizar-estado")
    print("\n📊 Analytics:")
    print("   - GET  /api/analytics/dashboard")
    print("   - GET  /api/analytics/riesgo-cobertura")
    print("   - GET  /api/analytics/tendencia-demanda")
    print("   - GET  /api/analytics/stock-rop")
    print("   - GET  /api/analytics/temporadas")
    print("   - GET  /api/analytics/historial")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
