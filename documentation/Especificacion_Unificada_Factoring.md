## 9. Troubleshooting de Despliegue en Streamlit Cloud

Esta sección documenta los errores comunes encontrados durante el proceso de despliegue en Streamlit Community Cloud y las soluciones aplicadas.

### 9.1. `ModuleNotFoundError: No module named 'src'` (Inicial)

*   **Causa:** El bloque de configuración de ruta (`Path Setup`) no estaba al inicio del archivo principal (`00_Home.py`) o no estaba correctamente configurado en los archivos de página.
*   **Solución:**
    *   Mover el bloque `Path Setup` al inicio de `00_Home.py`.
    *   Asegurar que el `Path Setup` en todos los archivos de página (`apps/pages/*.py`) calcule correctamente la raíz del proyecto: `project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))`.

### 9.2. `streamlit.errors.StreamlitAPIException: Could not find page: apps/01_Operaciones.py`

*   **Causa:** Estructura incorrecta de la aplicación multi-página de Streamlit y rutas incorrectas en `st.switch_page()`.
*   **Solución:**
    *   Mover todos los archivos de página de `apps/` a `apps/pages/`.
    *   Actualizar las llamadas a `st.switch_page()` en `00_Home.py` para que referencien las páginas solo por su nombre de archivo (ej. `st.switch_page(f"{page_name}.py")`).

### 9.3. `ModuleNotFoundError: No module named 'nombre_de_libreria'` (ej. `streamlit_mermaid`, `pdfplumber`)

*   **Causa:** Dependencias de Python faltantes en `requirements.txt` o formato incorrecto del archivo.
*   **Solución:**
    *   Añadir todas las librerías necesarias a `requirements.txt`.
    *   **Asegurar que cada librería esté en una línea separada** en `requirements.txt`.

### 9.4. `KeyError: st.secrets['google_oauth']`

*   **Causa:** Secretos de la aplicación no configurados correctamente en la sección "Secrets" de Streamlit Cloud.
*   **Solución:** Pegar el contenido de la sección `[google_oauth]` del `secrets.toml` local **exactamente como está**, incluyendo el encabezado `[google_oauth]`, en la configuración de secretos de Streamlit Cloud.

### 9.5. `OSError: cannot load library 'libpango-1.0-0'` (y otros errores de librerías del sistema)

*   **Causa:** Faltan dependencias a nivel de sistema operativo necesarias para librerías como `weasyprint`.
*   **Solución:** Crear un archivo `packages.txt` en la raíz del repositorio y listar las librerías del sistema necesarias (ej. `libcairo2`, `libpango-1.0-0`, `libpangocairo-1.0-0`, `libgdk-pixbuf2.0-0`, `libffi-dev`, `shared-mime-info`, `fontconfig`).

### 9.6. Problema Persistente: `ModuleNotFoundError: No module named 'src'` en Archivos de Página

*   **Descripción:** A pesar de haber aplicado la corrección del `Path Setup` (`project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))`) en todos los archivos de `apps/pages/`, y de haber verificado que el código correcto está en GitHub, este error sigue apareciendo al navegar a las páginas secundarias en Streamlit Cloud.
*   **Estado:** **SIN RESOLVER.** Este problema sugiere una interacción compleja o un comportamiento inesperado del entorno de Streamlit Cloud con la gestión de rutas de Python en aplicaciones multi-página cuando los archivos de página están en una sub-subcarpeta (`apps/pages/`). Se requiere una investigación adicional o una solución alternativa para la gestión de rutas en los archivos de página.

--- 

## 9.7. Troubleshooting de Despliegue Completo (Sept 2025)

Se realizó un proceso de depuración exhaustivo para un redespliegue desde cero que resolvió el problema 9.6. Se encontraron y solucionaron los siguientes problemas en secuencia:

### 9.7.1. Error: `ModuleNotFoundError: No module named 'src'`
*   **Síntoma:** La aplicación no podía iniciarse en Streamlit Cloud.
*   **Causa:** La estructura del proyecto (`apps/pages/`) no era la estándar de Streamlit, causando conflictos de importación.
*   **Solución:** Se reestructuró el proyecto al formato estándar: `00_Home.py` en la raíz y las páginas secundarias en una carpeta `pages/` en la raíz. Se eliminó la carpeta `apps/`.

### 9.7.2. Error: `Could not find page: ...` en botones de Home
*   **Síntoma:** El menú lateral funcionaba, pero los botones personalizados en `00_Home.py` no navegaban.
*   **Causa:** La función `st.switch_page` era llamada sin el prefijo de la carpeta `pages/`.
*   **Solución:** Se modificó la llamada a `st.switch_page(f"pages/{page_name}.py")` para incluir la ruta correcta.

### 9.7.3. Error: Ventana de Login de Google en blanco
*   **Síntoma:** Al hacer clic en "Login con Google", la ventana emergente aparecía en blanco.
*   **Causa:** Al redesplegar la app, Streamlit Cloud asignó una nueva URL. Esta nueva URL no estaba autorizada en la configuración de OAuth en Google Cloud Console.
*   **Solución:** Se añadió la nueva URL de la aplicación (`https://...streamlit.app`) a "Orígenes de JavaScript autorizados" y "URIs de redireccionamiento autorizados" en la credencial de OAuth 2.0.

### 9.7.4. Error: Conexión rechazada después del Login
*   **Síntoma:** Después de un login exitoso con Google, la ventana emergente mostraba un error de conexión.
*   **Causa:** El `redirect_uri` en los Secrets de Streamlit estaba apuntando a `localhost` en lugar de la URL pública de la aplicación.
*   **Solución:** Se actualizó el valor de `redirect_uri` en los Secrets de Streamlit Cloud para que fuera la URL pública de la aplicación.

### 9.7.5. Error: `FileNotFoundError: .env file not found`
*   **Síntoma:** La app fallaba después del login al intentar conectar con Supabase.
*   **Causa:** El código buscaba un archivo `.env` para las credenciales, el cual no existe en el entorno de la nube.
*   **Solución:** Se refactorizó `supabase_client.py` para leer las credenciales desde `st.secrets` en lugar de un archivo `.env`.

### 9.7.6. Error: `ValueError: Supabase credentials not found`
*   **Síntoma:** La app seguía fallando, indicando que no encontraba las credenciales en `st.secrets`.
*   **Causa:** Error de formato en los Secrets de Streamlit. Las claves (`url`, `key`) y la sección (`[supabase]`) deben estar en minúsculas.
*   **Solución:** Se corrigió el formato en la configuración de Secrets de Streamlit Cloud para que coincidiera exactamente con lo que esperaba el código (`[supabase]`, `url`, `key`).

### 9.7.7. Error: Botones de navegación no funcionan sin dar error
*   **Síntoma:** Los botones en la página principal no navegaban, pero tampoco mostraban un error.
*   **Causa:** El uso del callback `on_click` en los botones estaba siendo interferido por el ciclo de ejecución de Streamlit.
*   **Solución:** Se cambió la lógica de los botones para usar un `if st.button(...):` explícito, que es un patrón más robusto para la navegación.

### 9.7.8. Error: Conexión con API Backend Rechazada (`404 Not Found` inicial)
*   **Síntoma:** Al intentar calcular en el módulo "Operaciones", la aplicación mostraba `Error de conexión con la API: HTTPConnectionPool(host='127.0.0.1', port=8000): ... Connection refused`.
*   **Causa:** El frontend de Streamlit, al estar en la nube, intentaba conectarse a un backend en `localhost` (su propia máquina virtual), no al servidor backend público.
*   **Solución:** Se modificó `pages/01_Operaciones.py` para que `API_BASE_URL` leyera desde `st.secrets["backend_api"]["url"]`. Se instruyó al usuario a añadir la URL pública de su backend (ej. `https://inandes-back.onrender.com`) a los Secrets de Streamlit Cloud.

### 9.7.9. Error: API Backend `404 Not Found` (Endpoint Mismatch)
*   **Síntoma:** Después de la corrección anterior, el error cambió a `404 Client Error: Not Found for url: https://inandes-back.onrender.com/calcular_desembolso_lote`.
*   **Causa:** El frontend llamaba al endpoint `/calcular_desembolso_lote`, pero el backend (`src/api/main.py`) tenía definido el endpoint `/desembolsar_lote` (para registrar desembolsos, no para calcular). El backend no exponía los endpoints de cálculo esperados por el frontend.
*   **Solución:** Se añadieron los endpoints `@app.post("/calcular_desembolso_lote")` y `@app.post("/encontrar_tasa_lote")` a `src/api/main.py` en el backend, que llaman a las funciones de cálculo correspondientes.

### 9.7.10. Problema: Persistencia de Errores por Caché de Streamlit Cloud
*   **Síntoma:** A pesar de subir las correcciones al repositorio, la aplicación desplegada en Streamlit Cloud seguía mostrando errores de versiones antiguas del código (ej. `404 Not Found` para `/calcular_desembolso_lote` incluso después de corregir el frontend).
*   **Causa:** Streamlit Cloud a veces no detecta o no refresca completamente su caché del repositorio con los últimos cambios, especialmente si los cambios son pequeños o si hay problemas de sincronización.
*   **Solución:** Se forzaron múltiples redespliegues añadiendo comentarios triviales a los archivos afectados (`00_Home.py`, `pages/01_Operaciones.py`) y subiendo nuevos commits. Esto genera un nuevo hash de commit que obliga a Streamlit a realizar una nueva clonación/pull del repositorio.

### 9.7.11. Ajuste de Estilo: Alineación Vertical de Títulos
*   **Síntoma:** En la sección "Configuración Global" de los módulos "Operaciones" y "Calculadora Factoring", los títulos de las columnas ("Comisiones Globales", "Tasas Globales", "Fechas Globales") aparecían desalineados verticalmente (efecto "escalera").
*   **Causa:** El CSS inyectado en el código (`st.markdown("<style>...")`) tenía la propiedad `align-items: center` para los bloques horizontales, lo que centraba los elementos verticalmente en lugar de alinearlos en la parte superior.
*   **Solución:** Se modificó la propiedad CSS a `align-items: flex-start` en los archivos `pages/07_Calculadora_Factoring.py` y `pages/01_Operaciones.py`.

### 9.7.12. Error: `KeyError: 'resultados_por_factura'` al procesar la respuesta del backend
*   **Síntoma:** La aplicación fallaba con un `KeyError` en la línea `invoice['initial_calc_result'] = initial_calc_results_lote["resultados_por_factura"][idx]` dentro de `pages/01_Operaciones.py`, incluso después de que la API devolviera un código de estado 200 (OK).
*   **Causa:** La respuesta de la API del backend (en `src/api/main.py`) estaba anidando la respuesta del módulo de cálculo dentro de otro diccionario. En lugar de devolver `{"resultados_por_factura": [...]}` directamente, devolvía `{"resultados_por_factura": {"resultados_por_factura": [...]}}`. Este anidamiento extra causaba que el frontend no encontrara la clave en el primer nivel del diccionario de respuesta. El mismo error existía en los endpoints `/calcular_desembolso_lote` y `/encontrar_tasa_lote`.
*   **Solución:** Se modificaron los endpoints afectados en `src/api/main.py` para que devolvieran directamente el resultado del módulo de cálculo (`return result`) en lugar de anidarlo en un nuevo diccionario (`return {"resultados_por_factura": result}`). Esto aplanó la estructura de la respuesta JSON para que coincidiera con lo que el frontend esperaba.

--- 

## Como desarrollar en local mientras se mantiene la app en Streamlit community cloud

Esta guía consolida los pasos necesarios para configurar y ejecutar el frontend de la aplicación Streamlit en un entorno de desarrollo local (Windows), mientras se conecta a los servicios de backend (Render) y base de datos (Supabase) que están en producción en la nube.

### 1. Configuración de Prerrequisitos (Tareas Únicas)

Antes de poder ejecutar la aplicación localmente, es necesario asegurarse de que los servicios externos permitan la conexión desde `localhost`.

*   **Google Cloud Console:** El servicio de autenticación de Google (OAuth 2.0) debe confiar en la URL de desarrollo local. 
    1.  Ve a la página de [Credenciales de Google Cloud](https://console.cloud.google.com/apis/credentials).
    2.  Busca y edita el "ID de cliente de OAuth 2.0" correspondiente a esta aplicación.
    3.  En la sección "URIs de redireccionamiento autorizados", añade la siguiente URL exactamente como se muestra: `http://localhost:8504`.
    4.  Guarda los cambios.

*   **Código Fuente:** El código de la aplicación ya está preparado para manejar dinámicamente los diferentes entornos (local vs. nube) para las URLs de la API y de redirección de Google.

### 2. Pasos para la Ejecución Local (Cada vez que se desarrolla)

Sigue esta secuencia cada vez que abras una nueva terminal para trabajar en el proyecto.

1.  **Abrir Terminal:** Inicia una nueva ventana del Símbolo del sistema (`cmd.exe`).

2.  **Navegar al Directorio del Proyecto:**
    ```bash
    cd C:\Users\rguti\inandes_factoring_app_SCC
    ```

3.  **Establecer Variables de Entorno:** Ejecuta los siguientes tres comandos para configurar las credenciales necesarias para la sesión actual de la terminal. **Importante: Los valores se ponen sin comillas.**

    *   **Para el Backend:**
        ```bash
        set BACKEND_API_URL=URL_DE_TU_BACKEND_EN_RENDER
        ```

    *   **Para la Base de Datos (Supabase):**
        ```bash
        set SUPABASE_URL=URL_DE_TU_PROYECTO_SUPABASE
        set SUPABASE_KEY=LLAVE_PUBLICA_ANON_DE_SUPABASE
        ```

4.  **Lanzar la Aplicación:** Usa el siguiente comando para iniciar el servidor de Streamlit, especificando el puerto correcto que autorizaste en Google Cloud.
    ```bash
    streamlit run 00_Home.py --server.port 8504
    ```

Si todos los pasos se han seguido correctamente, la aplicación se abrirá en tu navegador en `http://localhost:8504` y debería ser completamente funcional, permitiéndote iniciar sesión y utilizar todos los módulos que se conectan a los servicios en la nube。

--- 

## 9.7.13. Problema: Cambio de Estado de Facturas (ACTIVO a DESEMBOLSADA)

*   **Síntoma:** Las facturas no cambiaban de estado de 'ACTIVO' a 'DESEMBOLSADA' después de un desembolso exitoso, a pesar de que el frontend mostraba un mensaje de "Lote procesado por la API".
*   **Diagnóstico Inicial:**
    *   El frontend (`pages/02_Desembolsos.py`) no realizaba directamente el cambio de estado en la base de datos.
    *   La lógica de cambio de estado residía en el backend, pero el endpoint `/desembolsar_lote` en `src/api/main.py` estaba vacío (`pass`).
*   **Soluciones Implementadas:**
    *   **Implementación del Endpoint `/desembolsar_lote`:** Se añadió la lógica necesaria en `src/api/main.py` para que este endpoint:
        *   Itere sobre las facturas recibidas.
        *   Actualice el estado de cada `proposal_id` a 'DESEMBOLSADA' utilizando `db.update_proposal_status()`.
        *   Registre un evento de auditoría (`db.add_audit_event`) para cada cambio de estado.
        *   Devuelva una respuesta estructurada al frontend con el estado de cada factura procesada.
    *   **Corrección de Importación `db`:** Se ajustó la importación de `supabase_repository` en `src/api/main.py` para que el objeto `db` fuera accesible dentro del endpoint.
    *   **Mejoras en Mensajes de Frontend:**
        *   Se cambió `st.success` a `st.toast` para mensajes individuales de éxito en `pages/02_Desembolsos.py` para una notificación menos intrusiva.
        *   Se añadió un mensaje de resumen final (`st.success` o `st.error`) en `pages/02_Desembolsos.py` para consolidar el resultado del procesamiento del lote.
        *   Se corrigió un error de formato en la f-string de los mensajes de depuración en `pages/02_Desembolsos.py` para que mostraran correctamente los valores de `status` y `message` de `API`.

--- 

## 9.7.14. Problema: Proyección de Deuda (404 Client Error: Not Found para `/get_projected_balance`)

*   **Síntoma:** Al intentar acceder a la proyección de deuda en el módulo de Liquidación, la aplicación mostraba un error `404 Client Error: Not Found` para la URL `https://inandes-back.onrender.com/get_projected_balance`.
*   **Diagnóstico:** El endpoint `/get_projected_balance` no estaba definido en el archivo `src/api/main.py` del backend.
*   **Soluciones Implementadas (o en Proceso):**
    *   **Implementación del Endpoint `/get_projected_balance`:** Se añadió la lógica para este endpoint en el backend. Este endpoint:
        *   Recibe `proposal_id`, `fecha_inicio_proyeccion` y `initial_capital`.
        *   Obtiene las tasas de interés (`interes_mensual`, `interes_moratorio`) de los detalles de la propuesta.
        *   Llama a la función `proyectar_saldo_diario` de `core.liquidation_calculator` para calcular la proyección.
        *   Devuelve la proyección futura.
    *   **Reubicación del Endpoint:** Para una mejor organización y evitar conflictos, se decidió mover el endpoint `/get_projected_balance` del `main.py` al router de `liquidaciones` (`src/api/routers/liquidaciones.py`). Esto significa que la URL correcta para este endpoint ahora es `/liquidaciones/get_projected_balance`.
    *   **Actualización del Frontend:** Se actualizó la llamada en `pages/03_Liquidaciones.py` para que apunte a la nueva URL del endpoint (`/liquidaciones/get_projected_balance`).

--- 

## Tareas Pendientes

*   **Verificación de Proyección de Deuda:** Confirmar que el endpoint `/liquidaciones/get_projected_balance` funciona correctamente después de su reubicación y la actualización del frontend.
*   **Verificación de Cambio de Estado (Desembolso):** Confirmar que el estado de las facturas cambia de 'ACTIVO' a 'DESEMBOLSADA' después de un desembolso exitoso.
*   **Verificación de Cambio de Estado (Liquidación):** Confirmar que los cambios de estado de liquidación (`'LIQUIDADA'` o `'EN PROCESO DE LIQUIDACION'`) se aplican correctamente en la base de datos después de procesar una liquidación.
