# Propuesta de Nueva Estructura de Proyecto: `inandes_factoring_app`

Basado en el análisis, se propone la siguiente estructura de carpetas para organizar el proyecto de una manera lógica, modular y profesional. Esta estructura separa claramente la configuración, la lógica de negocio, las aplicaciones y los recursos estáticos.

El nuevo proyecto vivirá en una carpeta raíz llamada `inandes_factoring_app`.

```
inandes_factoring_app/
│
├── .streamlit/                 # Carpeta de configuración para Streamlit Cloud
│   └── config.toml             # Configuración de temas, etc.
│
├── src/                        # Carpeta principal para todo el código fuente
│   │
│   ├── api/                    # Lógica del backend (FastAPI)
│   │   ├── __init__.py
│   │   ├── main.py             # El entrypoint de la API FastAPI
│   │   └── routers/            # (Opcional) Para organizar endpoints si la API crece
│   │       ├── __init__.py
│   │       └── operations.py
│   │       └── liquidations.py
│   │
│   ├── core/                   # Lógica de negocio principal (los motores de cálculo)
│   │   ├── __init__.py
│   │   ├── factoring_calculator.py  # Antes 'calculadora_factoring_V_CLI.py'
│   │   └── liquidation_calculator.py # Antes 'calculadora_liquidacion.py'
│   │
│   ├── data/                   # Lógica de acceso a datos (Supabase)
│   │   ├── __init__.py
│   │   ├── supabase_client.py    # Cliente Supabase centralizado (de 'supabase_queries.py')
│   │   └── supabase_repository.py # Unifica ambos handlers (operaciones y liquidación)
│   │
│   ├── services/               # Servicios auxiliares como el parser de PDF
│   │   ├── __init__.py
│   │   └── pdf_parser.py         # El parser de PDF estable
│   │
│   ├── templates/              # Plantillas para la generación de PDFs
│   │   ├── perfil_operacion.html # Plantilla para el perfil
│   │   ├── reporte_efide.html    # Plantilla para el reporte EFIDE
│   │   └── liquidacion_consolidada.html # Plantilla para la liquidación V6
│   │
│   └── utils/                  # Funciones de utilidad y generadores de PDF
│       ├── __init__.py
│       ├── pdf_generators.py   # Unifica la lógica de los generadores de PDF
│       └── helpers.py          # Funciones de ayuda (ej. flatten_dict)
│
├── apps/                       # Las aplicaciones Streamlit que son los puntos de entrada
│   ├── 01_Operaciones.py         # App principal de operaciones (antes 'frontend_app_V.CLI.py')
│   └── 02_Liquidaciones.py       # App de liquidación por lotes
│
├── .env                        # UNICO archivo de variables de entorno para todo el proyecto
├── .gitignore                  # Para ignorar archivos y carpetas como venv, __pycache__
├── Dockerfile                  # Para construir la imagen Docker del proyecto
├── requirements.txt            # Lista única y consolidada de todas las dependencias
└── README.md                   # Documentación principal del proyecto

```

## Justificación de la Estructura

-   **Separación de Responsabilidades (SoC)**: Cada carpeta tiene un propósito claro (api, core, data, apps), lo que facilita encontrar y mantener el código.
-   **`src` (Source) Layout**: Usar una carpeta `src` es una práctica estándar en Python que evita problemas de importación y organiza el código de manera limpia.
-   **Modularidad**: La lógica de negocio (`core`), el acceso a datos (`data`) y la interfaz de usuario (`apps`) están desacoplados, lo que permite modificarlos de forma independiente.
-   **Configuración Centralizada**: Un único `.env` y un único `requirements.txt` en la raíz simplifican la configuración y la gestión de dependencias.
-   **Preparado para Despliegue**: La inclusión de `Dockerfile`, `.streamlit/config.toml` y `requirements.txt` desde el principio facilita la dockerización y el despliegue en la nube.
-   **Nomenclatura Profesional**: Los nombres de los archivos y carpetas son más descriptivos y siguen convenciones comunes (ej. `factoring_calculator.py` en lugar de `calculadora_factoring_V.CLI.py`).
-   **Consolidación**: Se propone unificar los dos `supabase_handler` en un único `supabase_repository.py` y los generadores de PDF en `pdf_generators.py` para reducir la duplicación de código.
