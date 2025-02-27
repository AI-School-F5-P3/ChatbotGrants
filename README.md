![](./chatbotgrants.png)


Sistema de chat inteligente para identificación y evaluación de subvenciones, diseñado para ayudar a comerciales y clientes a encontrar y evaluar oportunidades de financiación.

## 🎯 Objetivo Principal

Desarrollar un sistema de chat inteligente que permita a comerciales y clientes:
- Identificar subvenciones disponibles
- Evaluar elegibilidad para proyectos específicos
- Determinar la adecuación de subvenciones
- Maximizar el retorno posible de financiación
- Interactuar de manera natural con consultas sobre subvenciones

## 🏗️ Arquitectura

El sistema está compuesto por los siguientes componentes principales:

### Frontend
- Interfaz de chat interactiva
- Desarrollado en React
- Diseño responsive
- Integración con sistema de autenticación

### Backend
- Servicios en contenedores
- Integración con API de subvenciones (Fandit)
- Sistema ETL para gestión de datos
- Base de datos intermedia para filtrado

### Servicios AWS
- **Bedrock**: Motor de IA para procesamiento de lenguaje natural
- **Kendra**: Sistema de búsqueda inteligente
- **S3**: Almacenamiento de documentos
- **DynamoDB**: Base de datos de alta velocidad
- **EC2**: Instancias para despliegue de servicios

### Seguridad
- **KeyCloak**: Sistema de autenticación para comerciales
- Security Groups configurados
- Protección de datos GDPR

## ⚡ Características Clave

1. **Interfaz de Chat Inteligente**
   - Interacción en lenguaje natural
   - Respuestas contextualizadas
   - Evaluación automática de elegibilidad

2. **Gestión de Datos**
   - Integración con API de Fandit
   - Base de datos intermedia para filtrado eficiente
   - Actualización automática de información

3. **Procesamiento de Documentos**
   - Soporte para archivos PDF
   - Análisis de documentación
   - Almacenamiento seguro

4. **Sistema de Filtrado**
   - Búsqueda por sector
   - Filtrado por cuantía
   - Selección por región
   - Criterios de elegibilidad

## 🚀 Requisitos Técnicos

### Funcionales
- Autenticación de usuarios
- Interacción en lenguaje natural
- Gestión de archivos PDF
- Sistema de filtrado avanzado
- Base de datos intermedia
- Procesamiento de consultas

### No Funcionales
- Alta disponibilidad
- Rendimiento optimizado
- Diseño responsive
- Seguridad de datos
- Escalabilidad

## 💻 Tecnologías

- **Frontend**: React
- **Backend**: Python
- **IA**: AWS Bedrock
- **Base de Datos**: PostgreSQL (RDS)
- **Almacenamiento**: AWS S3
- **Autenticación**: KeyCloak
- **Contenedores**: Docker
- **Orquestación**: AWS Fargate

## 🛠️ Instalación y Desarrollo

### Prerrequisitos
- Cuenta AWS
- Docker y Docker Compose
- Node.js y npm
- Python 3.9+
- Git

### Configuración del Entorno
1. Clonar el repositorio
2. Configurar variables de entorno
3. Instalar dependencias
4. Configurar servicios AWS

### Estructura del Proyecto
```
chatbot-grants/
├── frontend/          # Aplicación React
├── backend/           # Servicios Python
│   ├── etl/          # Sistema ETL
│   ├── api/          # API REST
│   └── chat/         # Lógica del chatbot
├── infrastructure/    # Configuración AWS
└── docs/             # Documentación
```

## 📝 API y Recursos

### API de Fandit
- Endpoint: `https://fandit.es/api/business`
- Límite: 200 consultas mensuales
- Actualización: Diaria a las 13:00

### Filtros Disponibles
- is_open
- search_by_text
- max_budget
- max_total_amount
- min_total_amount
- Otros filtros específicos

## 🔄 Flujo de Trabajo

1. **Entrada de Usuario**
   - Consulta en lenguaje natural
   - Carga de documentos
   - Selección de filtros

2. **Procesamiento**
   - Análisis de consulta
   - Búsqueda en base de datos
   - Evaluación de elegibilidad

3. **Respuesta**
   - Subvenciones relevantes
   - Análisis de adecuación
   - Recomendaciones

## 📊 Monitoreo y Mantenimiento

- Logs del sistema
- Métricas de uso
- Control de cuota API
- Backups de base de datos

## 👥 Equipo y Soporte

- Desarrollo Frontend
- Desarrollo Backend
- DevOps
- Equipo de Negocio

## 📫 Contacto y Ayuda

Para soporte y consultas:
- Crear issue en el repositorio
- Contactar al equipo de desarrollo
- Consultar documentación interna

## 📜 Licencia

Este es un proyecto pedagógico y público.