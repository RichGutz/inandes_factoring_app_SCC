# Análisis de la Arquitectura Actual del Proyecto Inandes.TECH

Este documento resume la estructura, componentes y dependencias del proyecto en su estado actual. El análisis se basa en la revisión de los archivos de código clave.

## 1. Componentes Principales

El proyecto se compone de tres partes funcionales principales:

1.  **Módulo de Operaciones (Frontend)**: Una aplicación Streamlit (`frontend_app_V.CLI.py`) que permite a los usuarios cargar facturas en PDF, extraer sus datos, realizar cálculos de factoring y guardar los resultados como "propuestas".

2.  **Módulo de Liquidación por Lotes (Frontend)**: Una segunda aplicación Streamlit (`liquidacion_por_lotes_app.py`) dedicada a buscar lotes de propuestas previamente guardadas, aplicar pagos y calcular la liquidación final (intereses, moras, etc.).

3.  **API de Lógica de Negocio (Backend)**: Un servidor FastAPI (`main.py`) que centraliza y ejecuta toda la lógica de negocio y los cálculos financieros complejos. Las aplicaciones de Streamlit actúan como clientes de esta API.

## 2. Arquitectura y Flujo de Datos

La arquitectura, aunque desorganizada en la estructura de archivos, sigue un patrón cliente-servidor bien definido:

-   **Cliente (UI)**: Las aplicaciones Streamlit (`.py`) gestionan la interfaz de usuario, la entrada de datos y el estado de la sesión.
-   **Servidor (Lógica)**: La API de FastAPI (`main.py`) recibe las solicitudes de las aplicaciones Streamlit, importa los módulos de cálculo correspondientes (`calculadora_factoring_V_CLI.py`, `calculadora_liquidacion.py`) y devuelve los resultados.
-   **Base de Datos**: Supabase se utiliza como la base de datos principal. La comunicación se gestiona a través de dos "manejadores" o capas de acceso a datos (`supabase_handler.py` y `liquidacion_supabase_handler.py`).
-   **Generación de Documentos**: El sistema utiliza scripts externos de Python (`html_generator_V6.py`, `lote_report_generator.py`, etc.) para generar documentos PDF a partir de plantillas HTML/Jinja2.

## 3. Dependencias Clave

Se han identificado las siguientes dependencias críticas:

-   **Librerías de Python**: `streamlit`, `fastapi`, `uvicorn`, `requests`, `pandas`, `pdfplumber`, `supabase`, `python-dotenv`, `jinja2`, `reportlab`, etc. **No existe un archivo `requirements.txt` consolidado**, lo que es un punto crítico a resolver.

-   **Módulos Locales (Acoplamiento Interno)**:
    -   Las Apps de Streamlit dependen de la API de FastAPI.
    -   La API de FastAPI depende de `calculadora_factoring_V_CLI.py` y `calculadora_liquidacion.py`.
    -   Ambas apps y la API dependen de sus respectivos manejadores de Supabase (`supabase_handler.py`, `liquidacion_supabase_handler.py`).
    -   El manejador de liquidación (`liquidacion_supabase_handler.py`) depende de un cliente Supabase centralizado en `supabase_client/supabase_queries.py`.

## 4. Problemas Identificados

1.  **Estructura de Archivos Desorganizada**: Los archivos de diferentes módulos (operaciones, liquidación, backend, frontend) están mezclados. Hay archivos de respaldo, copias y pruebas en directorios de producción, lo que dificulta el mantenimiento.

2.  **Dependencia Externa Crítica (Bloqueador)**: La aplicación de operaciones tiene una dependencia codificada a una ruta absoluta fuera del directorio del proyecto (`C:/Users/rguti/Adicionales.Inandes.HTML/html_generator_V6.py`). Esto impide la portabilidad, la dockerización y el despliegue.

3.  **Rutas Absolutas (Hardcoded Paths)**: El código está lleno de rutas absolutas al sistema de archivos local del usuario (ej. `C:/Users/rguti/...`). Esto debe ser reemplazado por rutas relativas para que el proyecto funcione en cualquier otro entorno.

4.  **Ausencia de `requirements.txt`**: La falta de un archivo de requisitos único y consolidado hace que la replicación del entorno de desarrollo sea manual y propensa a errores.

5.  **Código Duplicado**: Se ha identificado lógica duplicada, como la función `get_proposal_details_by_id` que existe en ambos manejadores de Supabase. Esto puede ser refactorizado para mejorar la mantenibilidad.

6.  **Manejo de Credenciales**: Las credenciales se cargan desde un archivo `.env` en la carpeta `supabase_client`. Este es un buen patrón, pero debe ser gestionado correctamente en el nuevo diseño y en el despliegue.
