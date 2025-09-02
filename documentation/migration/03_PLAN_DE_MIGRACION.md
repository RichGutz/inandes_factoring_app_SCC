# Plan de Migración: De `Inandes.TECH` a `inandes_factoring_app`

Este documento describe el plan de acción detallado para migrar el proyecto desde su estructura actual a la nueva arquitectura profesional. Se debe seguir en orden para garantizar una transición suave.

**Objetivo:** Crear un proyecto autocontenido, portable, versionable y listo para despliegue.

### Fase 1: Preparación y Creación de la Nueva Estructura

1.  **Crear la Carpeta Raíz:**
    -   Crear una nueva carpeta principal llamada `inandes_factoring_app` fuera del directorio actual.

2.  **Crear la Estructura de Subcarpetas:**
    -   Dentro de `inandes_factoring_app`, crear todas las carpetas propuestas en `02_NUEVA_ESTRUCTURA.md`:
        - `.streamlit/`
        - `src/api/routers/`
        - `src/core/`
        - `src/data/`
        - `src/services/`
        - `src/templates/`
        - `src/utils/`
        - `apps/`

3.  **Crear Archivos `__init__.py`:**
    -   Crear archivos `__init__.py` vacíos en todas las subcarpetas dentro de `src` para que Python las reconozca como paquetes.

### Fase 2: Migración y Refactorización de Archivos

1.  **Copiar y Renombrar Archivos Clave:**
    -   Copiar `backend/frontend_app_V.CLI.py` a `apps/01_Operaciones.py`.
    -   Copiar `liquidacion.por.lotes/liquidacion_por_lotes_app.py` a `apps/02_Liquidaciones.py`.
    -   Copiar `backend/main.py` a `src/api/main.py`.
    -   Copiar `backend/calculadora_factoring_V_CLI.py` a `src/core/factoring_calculator.py`.
    -   Copiar `liquidacion/backend/calculadora_liquidacion.py` a `src/core/liquidation_calculator.py`.
    -   Copiar `backend/pdf_parser.py` a `src/services/pdf_parser.py`.

2.  **Consolidar Lógica de Base de Datos:**
    -   Crear `src/data/supabase_client.py` y mover la lógica de `get_supabase_client()` de `supabase_client/supabase_queries.py`.
    -   Crear `src/data/supabase_repository.py` y unificar las funciones de `backend/supabase_handler.py` y `liquidacion.por.lotes/liquidacion_supabase_handler.py`. Se deben eliminar funciones duplicadas como `get_proposal_details_by_id`.

3.  **Consolidar Generadores de PDF:**
    -   **Copiar las plantillas HTML/Jinja2** al directorio `src/templates/`.
    -   Crear `src/utils/pdf_generators.py`. Copiar y adaptar las funciones de generación de PDF de los scripts `html_generator_V6.py`, `efide_report_generator.py`, etc., para que sean funciones que se puedan llamar directamente en lugar de usar `subprocess`.

4.  **Mover Archivos de Utilidad:**
    -   Crear `src/utils/helpers.py` y mover funciones auxiliares como `flatten_dict` de `variable_data_pdf_generator.py`.

### Fase 3: Corrección del Código y Rutas

Esta es la fase más crítica.

1.  **Eliminar Rutas Absolutas (Hardcoded Paths)**:
    -   Revisar **todos** los archivos migrados y reemplazar las rutas absolutas (ej. `C:/Users/rguti/...`) por rutas relativas. Se debe usar `os.path.join` y la variable `__file__` para construir rutas dinámicas y portables.
    -   **Ejemplo:** En lugar de `st.image("C:/.../logo.png")`, se debe copiar el logo a una carpeta `static` y referenciarlo con una ruta relativa.

2.  **Corregir Todas las Declaraciones `import`:**
    -   Actualizar todas las declaraciones `import` para que reflejen la nueva estructura `src`.
    -   **Ejemplo en `apps/01_Operaciones.py`:**
        -   `import pdf_parser` se convertirá en `from src.services import pdf_parser`.
        -   `import supabase_handler` se convertirá en `from src.data.supabase_repository import ...`
        -   La llamada a la API con `requests` deberá apuntar a la URL donde se despliegue la API de FastAPI, o a `http://localhost:8000` durante el desarrollo local.

3.  **Eliminar `subprocess` para Generar PDFs:**
    -   Reemplazar todas las llamadas a `subprocess.run(["python", "script.py", ...])`.
    -   En su lugar, importar las funciones directamente desde `src.utils.pdf_generators` y llamarlas con los datos necesarios.

### Fase 4: Gestión de Dependencias y Entorno

1.  **Crear `requirements.txt` Consolidado:**
    -   Analizar todas las librerías importadas en el proyecto (`streamlit`, `fastapi`, `uvicorn`, `pdfplumber`, `supabase`, `python-dotenv`, `jinja2`, etc.).
    -   Crear un único archivo `requirements.txt` en la raíz de `inandes_factoring_app` con la lista completa de dependencias y sus versiones.

2.  **Crear Archivo `.env`:**
    -   Crear un archivo `.env` en la raíz del proyecto.
    -   Añadir las variables `SUPABASE_URL` y `SUPABASE_KEY`.
    -   Asegurarse de que el código (`supabase_client.py`) ahora busque este archivo `.env` en la raíz.

3.  **Crear `Dockerfile`:**
    -   Crear el `Dockerfile` en la raíz del proyecto (ver `04_DOCKERFILE_PROPUESTO.txt`). Este Dockerfile deberá:
        -   Usar una imagen base de Python.
        -   Copiar el código del proyecto.
        -   Instalar las dependencias desde `requirements.txt`.
        -   Exponer los puertos necesarios (para FastAPI y Streamlit).
        -   Definir el comando para iniciar la aplicación (probablemente un script de shell que inicie tanto la API como la app de Streamlit).

4.  **Configurar Streamlit Cloud (`config.toml`):**
    -   Crear el archivo `.streamlit/config.toml`.
    -   Definir configuraciones básicas como el tema principal y colores para que coincida con la marca Inandes.

### Fase 5: Verificación y Pruebas

1.  **Probar Localmente:**
    -   Crear un nuevo entorno virtual, instalar las dependencias desde `requirements.txt` y probar que ambas aplicaciones (`Operaciones` y `Liquidaciones`) y la API funcionen correctamente.

2.  **Probar Docker:**
    -   Construir la imagen de Docker y ejecutar el contenedor para verificar que la aplicación es completamente funcional dentro de un entorno aislado.

3.  **Desplegar en Streamlit Community Cloud:**
    -   Subir el nuevo repositorio a GitHub.
    -   Conectar el repositorio a Streamlit Community Cloud y desplegar una de las aplicaciones (ej. `apps/01_Operaciones.py`).
    -   **Nota:** Streamlit Community Cloud no puede ejecutar la API de FastAPI y la app de Streamlit al mismo tiempo. Esto requerirá desplegar la API de FastAPI en un servicio separado (como Heroku, Vercel, o un VPS) y configurar la app de Streamlit para que apunte a la URL de la API desplegada.
