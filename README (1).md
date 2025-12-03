# 🚀 SmartStock - Sistema de Control de Incentivos Corporativos

---

## 1. Nombre del Equipo

# ⚡ System Shock

---

## 2. Integrantes del Equipo

### Equipo de Desarrollo

| Nombre | Carrera | Rol |
|--------|---------|-----|
| Pablo Iain Garza Garcia | Ing. en Sistemas Computacionales | Líder de Desarrollo |
| Luis Enrique Palacios Resendiz | Ing. en Sistemas Computacionales | Soporte de Desarrollo |
| Andres Isai Arrieta Sanchez | Ing. en Sistemas Computacionales | Testing & QA |
| Angel Daniel Cuervo Martinez | Ing. en Sistemas Computacionales | Testing & QA |
| Derek Emmanuel Estrada Priego | Ing. en Sistemas Computacionales | Documentación Técnica |

### Equipo de Logística y Propuesta

| Nombre | Carrera | Rol |
|--------|---------|-----|
| Melvin Uziel Hernandez Hernandez | Ing. en Gestión de TI | Líder de Logística & Propuesta |
| Leonardo Martínez Alvarado | Ing. en Gestión de TI | Presentación & Propuesta |
| Christopher Castellanos Mendez | Ing. en Electrónica y Telecomunicaciones | Propuesta de Valor |
| Cristian Alejandro Landero Domínguez | Ing. Industrial y de Sistemas | Análisis de Requerimientos |

---

## 3. Objetivo del Proyecto

**Problema:** Las empresas de tarjetas de incentivos corporativos gestionan pedidos de forma manual (WhatsApp, correo, Excel), lo que genera acaparamiento de tarjetas sin usar y quiebres de stock inesperados.

**Meta:** Desarrollar un sistema automatizado que valide pedidos en tiempo real, aplicando reglas de negocio inteligentes que eliminen el acaparamiento y optimicen el control de inventario.

---

## 4. Solución Propuesta

**SmartStock** es una plataforma web que integra:

- **Portal Cliente:** Los clientes visualizan sus contratos, solicitan tarjetas y rastrean sus pedidos en tiempo real.

- **Panel Administrativo:** El gerente de operaciones gestiona pedidos, monitorea inventario con alertas automáticas y analiza tendencias de demanda.

- **Regla de Oro (Motor de Validación):** Sistema que automáticamente limita los pedidos basándose en el uso real de tarjetas. Si un cliente tiene tarjetas sin usar, solo puede solicitar la cantidad equivalente a las que SÍ está utilizando.

- **Analytics Predictivo:** Análisis de 12 meses de historial para pronosticar demanda futura, identificar temporadas altas y calcular puntos de reorden automáticos.

**Características Clave:**
- ✅ Validación automática de pedidos contra contrato
- ✅ Eliminación del acaparamiento de tarjetas
- ✅ Alertas de inventario en tiempo real
- ✅ Tracking de envíos para clientes
- ✅ Pronóstico de demanda a 3 meses
- ✅ Cálculo automático de punto de reorden (ROP)

---

## 5. Stack Tecnológico

| Categoría | Tecnología |
|-----------|------------|
| **Backend** | Python 3.x, Flask, Flask-CORS |
| **Frontend** | React 18, Tailwind CSS, Chart.js |
| **Datos** | CSV (simulando base de datos) |
| **Visualización** | Chart.js (gráficas de dona, línea, barras) |
| **Arquitectura** | API REST, Servicios modulares |

**Estructura del Proyecto:**
```
SmartStock/
├── app.py                 # Servidor Flask con API REST
├── requirements.txt       # Dependencias Python
├── data/                  # Datos CSV (clientes, contratos, productos)
├── frontend/              # Interfaces HTML + React
│   ├── index.html         # Landing page
│   ├── index_admin.html   # Panel administrativo
│   └── index_cliente.html # Portal cliente
└── services/              # Lógica de negocio modular
    ├── data_service.py    # Carga de datos
    ├── motor_reglas.py    # Regla de Oro
    ├── pedidos_service.py # Gestión de pedidos
    ├── inventario_service.py # Control de stock
    ├── tracking_service.py   # Seguimiento de envíos
    └── analytics_service.py  # Métricas y pronósticos
```

---

## 6. Uso de IA

✅ **Sí, se utilizó Inteligencia Artificial en el desarrollo.**

**Herramienta:** Claude (Anthropic)

**Aplicación en el proyecto:**

- **Desarrollo de código:** Asistencia en la creación del backend (Flask API), frontend (React + Tailwind), y lógica de negocio (Motor de Reglas).

- **Arquitectura del sistema:** Diseño de la estructura modular de servicios y endpoints REST.

- **Algoritmos de Analytics:** Implementación de regresión lineal para pronósticos, cálculo de ROP (Punto de Reorden) y análisis de temporalidad.

- **Optimización:** Refactorización del código para compatibilidad con Python 3.13 (eliminación de dependencias problemáticas como pandas).

- **Documentación:** Generación de README, guías de uso y documentación técnica.

**Impacto:** El uso de IA aceleró significativamente el desarrollo, permitiendo al equipo enfocarse en la lógica de negocio y la experiencia de usuario mientras la IA asistía con la implementación técnica.

---

## 🚀 Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU-USUARIO/SmartStock.git
cd SmartStock

# 2. Instalar dependencias
pip install flask flask-cors

# 3. Ejecutar el servidor
python app.py

# 4. Abrir en navegador
# Admin:   frontend/index_admin.html
# Cliente: frontend/index_cliente.html
```

**Credenciales de prueba:**
| Portal | Usuario | Contraseña |
|--------|---------|------------|
| Admin | admin | admin |
| Cliente | laura | 1234 |

---

## 📄 Licencia

Proyecto desarrollado para el Hackathon 2025.

**Equipo System Shock** ⚡
