# 🎯 SmartStock - Control Inteligente de Incentivos Corporativos

Sistema de gestión de tarjetas de incentivos (Despensa, Gasolina, Premios) con validación automática basada en la **Regla de Oro** y analytics avanzado.

## 📋 Descripción del Problema

Nuestra empresa gestiona monederos electrónicos para grandes corporativos. El proceso actual es manual y presenta dos problemas graves:

1. **Acaparamiento**: Clientes con tarjetas guardadas sin usar, pidiendo más
2. **Quiebre de Stock**: Sin visibilidad del inventario real

## 💡 Solución: SmartStock

Sistema que automatiza la validación de pedidos aplicando la **Regla de Oro**:
> "Si tienes tarjetas sin usar (inactivas), te surtimos únicamente la cantidad que tienes en uso"

---

## 🚀 Instalación y Ejecución

### Requisitos
- Python 3.8+
- pip

### Pasos

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el servidor
python app.py

# 3. Abrir en navegador:
#    - Panel Admin: frontend/index_admin.html
#    - Portal Cliente: frontend/index_cliente.html
#    - Landing Page: frontend/index.html
```

El servidor correrá en `http://localhost:5000`

---

## 👥 Usuarios de Prueba

### Panel Administrativo
| Usuario | Contraseña |
|---------|------------|
| admin   | admin      |
| roberto | 1234       |

### Portal de Clientes
| Usuario | Contraseña | Empresa |
|---------|------------|---------|
| laura   | 1234       | The Charles Schwab Corporation |
| carlos  | 1234       | TEGNA Inc. |
| maria   | 1234       | Whirlpool Corporation |
| demo    | demo       | FS Investment Corporation |

---

## 📊 Funcionalidades

### Panel Administrativo

#### 1. Dashboard con Analytics
- **KPIs principales**: Clientes, contratos, pedidos, tarjetas
- **Riesgo de Cobertura Contractual**: Índice de riesgo, distribución por nivel, top contratos críticos
- **Tendencia de Demanda**: Gráfico de 12 meses + pronóstico 3 meses
- **Stock y ROP**: Punto de reorden, EOQ, días de cobertura
- **Temporadas**: Análisis por mes, empresa y tipo de tarjeta

#### 2. Operaciones
- Pedidos en proceso con actualización de estado
- Historial completo con búsqueda y exportación CSV

#### 3. Contratos
- Lista de todos los contratos
- Filtros: todos, con acaparamiento, cerca del límite
- Métricas: límite, actuales, inactivas, máximo pedido

#### 4. Inventario
- Stock por producto con alertas
- Indicadores visuales de estado

### Portal de Clientes

#### 1. Inicio
- Dashboard personal con KPIs
- Mis contratos con información detallada
- **Solicitar tarjetas** con:
  - Alertas de concientización (si tiene muchas sin usar)
  - Visualización del stock actual
  - Validación en tiempo real

#### 2. Mis Pedidos
- Lista de pedidos realizados
- Tracking integrado expandible
- Botón de actualizar

---

## 🔌 API Endpoints

### Sistema
```
GET /api/health              - Estado del sistema
GET /api/estadisticas        - Estadísticas generales
```

### Clientes
```
GET /api/clientes            - Lista de clientes
GET /api/cliente/<id>        - Cliente específico
GET /api/cliente/<id>/contratos - Contratos del cliente
```

### Productos
```
GET /api/productos           - Lista de productos
GET /api/producto/<id>       - Producto específico
```

### Inventario
```
GET /api/inventario          - Estado del inventario
GET /api/inventario/alertas  - Alertas de stock
```

### Contratos
```
GET /api/contratos           - Todos los contratos
GET /api/contratos/acaparamiento?umbral=50 - Detectar acaparamiento
```

### Pedidos
```
POST /api/pedido/validar     - Validar pedido (Regla de Oro)
POST /api/pedido/confirmar   - Confirmar pedido
GET  /api/pedidos/historial  - Historial de pedidos
GET  /api/pedidos/en-proceso - Pedidos pendientes
```

### Tracking
```
GET  /api/pedido/tracking/<tracking> - Buscar por tracking
POST /api/pedido/<id>/actualizar-estado - Actualizar estado
GET  /api/estados-envio      - Estados posibles
```

### Analytics
```
GET /api/analytics/dashboard        - Dashboard completo
GET /api/analytics/riesgo-cobertura - Métricas de riesgo
GET /api/analytics/tendencia-demanda - Tendencia y pronóstico
GET /api/analytics/stock-rop        - Stock y ROP
GET /api/analytics/temporadas       - Análisis de temporadas
GET /api/analytics/historial        - Historial 12 meses
```

---

## 📁 Estructura del Proyecto

```
SmartStock/
├── app.py                 # Servidor Flask principal
├── requirements.txt       # Dependencias Python
├── README.md             # Este archivo
│
├── data/                 # Datos CSV
│   ├── tabla_clientes.csv
│   ├── contratos_clientes.csv
│   └── productos.csv
│
├── services/             # Lógica de negocio
│   ├── __init__.py
│   ├── data_service.py       # Carga de datos
│   ├── motor_reglas.py       # Regla de Oro
│   ├── inventario_service.py # Gestión de inventario
│   ├── pedidos_service.py    # Gestión de pedidos
│   ├── tracking_service.py   # Seguimiento de envíos
│   └── analytics_service.py  # Métricas y pronósticos
│
└── frontend/             # Interfaces de usuario
    ├── index.html            # Landing page
    ├── index_admin.html      # Panel administrativo
    └── index_cliente.html    # Portal de clientes
```

---

## 🧮 Regla de Oro - Algoritmo

```python
maximo_pedido = min(
    tarjetas_en_uso,                    # Solo pedir lo que usas
    limite_contrato - tarjetas_actuales, # Espacio disponible
    stock_disponible                     # Stock físico
)
```

### Ejemplo:
- Límite contrato: 1,000 tarjetas
- Tarjetas actuales: 800
- Tarjetas inactivas: 600 (75%)
- Tarjetas en uso: 200

**Máximo pedido = 200** (no las 200 de espacio disponible, sino las 200 en uso)

---

## 📈 Métricas de Analytics

### Riesgo de Cobertura
- Calcula saturación de contratos
- Detecta acaparamiento
- Niveles: Crítico (>80%), Alto (60-80%), Medio (40-60%), Bajo (<40%)

### Pronóstico de Demanda
- Promedio móvil de 3 meses
- Regresión lineal para proyección
- Ajuste por temporalidad histórica

### Punto de Reorden (ROP)
```
ROP = (Demanda diaria × Lead time) + Stock de seguridad
EOQ = √(2 × Demanda anual × Costo pedido / Costo almacenamiento)
```

### Temporadas
- Análisis de 12 meses de historial simulado
- Identificación de meses pico por producto
- Heatmap de demanda empresa × mes

---

## 🎨 Tecnologías

### Backend
- Python 3.8+
- Flask
- Flask-CORS

### Frontend
- React 18 (CDN)
- Tailwind CSS
- Chart.js
- HTML5 / JavaScript

### Datos
- CSV (sin base de datos externa)

---

## 🏆 Hackathon OneCard 2024

**Equipo SmartStock** - 9 integrantes:
- 5 Ing. en Sistemas Computacionales
- 2 Ing. en Gestión de TI
- 1 Ing. Industrial
- 1 Ing. en Electrónica

---

## 📞 Soporte

Canal de Discord: #desafio-control-tarjetas
Mentora: Barbara Saldaña

---

## 📄 Licencia

Proyecto desarrollado para el Hackathon OneCard 2024.
