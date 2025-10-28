# Documentación: Módulo de Liquidación Universal

**Fecha:** 24 de septiembre de 2025

## 1. Objetivo del Módulo

El objetivo principal de este módulo es introducir un nuevo flujo de liquidación para operaciones de factoring que incorpora:
*   Una corrección crítica en la fórmula de cálculo del capital pendiente.
*   Una nueva lógica de negocio ("Backdoor") para la gestión de saldos mínimos.
*   Una arquitectura inicial que permite el desarrollo y las pruebas de forma aislada del sistema de liquidación existente.

## 2. Arquitectura Implementada (Fase de Pruebas)

Para esta fase inicial de desarrollo y pruebas, se ha optado por una arquitectura donde la lógica de backend reside directamente dentro de la aplicación de Streamlit. Esto permite una iteración rápida y una validación directa de la nueva lógica sin depender de un despliegue de API externo.

*   **Frontend:** `pages/liquidacion_universal.py`
    *   Es una nueva página de Streamlit que proporciona la interfaz de usuario para buscar operaciones, introducir datos de pago, ejecutar el cálculo y guardar los resultados.
    *   Reutiliza la lógica de conexión y búsqueda de Supabase del módulo de liquidación antiguo (`03_Liquidaciones.py`).

*   **Lógica de Backend (Motor de Cálculo):** `src/core/factoring_system.py`
    *   Contiene la clase `SistemaFactoringCompleto`, que encapsula toda la nueva lógica de negocio:
        *   Cálculo corregido de liquidaciones.
        *   Módulo de originación (aunque no expuesto directamente en este frontend aún).
        *   Lógica de "Backdoor" para saldos mínimos.
    *   Esta clase es instanciada y utilizada directamente por `liquidacion_universal.py`.

*   **Almacenamiento de Datos:** Supabase (a través de `src/data/supabase_repository.py`)
    *   La página `liquidacion_universal.py` utiliza las funciones existentes en `supabase_repository.py` para:
        *   `db.get_disbursed_proposals_by_lote`: Buscar propuestas por lote.
        *   `db.get_proposal_details_by_id`: Obtener detalles completos de una propuesta.
        *   `db.get_or_create_liquidacion_resumen`: Obtener o crear el resumen de liquidación.
        *   `db.add_liquidacion_evento`: Registrar cada evento de liquidación.
        *   `db.update_liquidacion_resumen_saldo`: Actualizar el saldo actual de la liquidación.
        *   `db.update_proposal_status`: Actualizar el estado de la propuesta principal.

## 3. Funcionalidades Clave Implementadas

*   **Corrección Crítica del Cálculo:** Se ha implementado la fórmula correcta para el `delta_capital` (`capital_operacion - monto_pagado`), resolviendo un error fundamental en el cálculo anterior.
*   **Lógica de "Backdoor" para Saldos Mínimos:**
    *   Si el saldo pendiente de una operación es positivo pero inferior a un umbral configurable (ej. S/ 100.00), el sistema lo liquida forzosamente a cero.
    *   La reducción se aplica secuencialmente a: intereses moratorios, intereses compensatorios y, finalmente, capital.
    *   Se registra un evento de auditoría para cada aplicación del "backdoor".
*   **Flujo de Usuario:**
    *   **Paso 1: Búsqueda:** El usuario introduce un ID de lote para cargar las facturas asociadas.
    *   **Paso 2: Configuración y Cálculo:**
        *   Se define una fecha de pago global y un monto mínimo para el "backdoor".
        *   Para cada factura, se introduce el monto recibido.
        *   Al hacer clic en "Calcular Liquidación Universal", se ejecuta la nueva lógica de `SistemaFactoringCompleto`.
    *   **Paso 3: Resultados y Guardado:**
        *   Se muestran los resultados detallados de la liquidación para cada factura, incluyendo el saldo final, el estado y si se aplicó el "backdoor".
        *   Un botón "Guardar Liquidaciones en Supabase" persiste los resultados en la base de datos, actualizando los resúmenes y eventos de liquidación, así como el estado de la propuesta.

## 4. Enfoque por Fases y Próximos Pasos

La decisión de integrar la lógica de backend directamente en el frontend de Streamlit se tomó para agilizar la validación de la nueva lógica de negocio.

*   **Fase Actual:** Pruebas y validación del funcionamiento de la lógica de cálculo y el flujo de usuario en Streamlit Cloud.
*   **Próxima Fase (Migración a Render):** Una vez que la funcionalidad sea validada y estable, se procederá a migrar la lógica de `SistemaFactoringCompleto` a un backend dedicado en Render. Esto implicará:
    *   Crear un nuevo proyecto de API o extender el existente en Render.
    *   Implementar un nuevo endpoint en la API que exponga la funcionalidad de liquidación universal.
    *   Modificar `liquidacion_universal.py` para que llame a este nuevo endpoint de Render en lugar de ejecutar la lógica localmente.

## 5. Commits Relevantes

*   `feat: Add universal liquidation module`: Implementación inicial del módulo de liquidación universal.
*   `revert: Revert filename to lowercase for cloud compatibility`: Corrección del nombre del archivo de la página para asegurar la compatibilidad con el despliegue en Streamlit Cloud.

## 6. Estado Actual

El módulo está desplegado en Streamlit Cloud y listo para ser probado. Se ha reportado un "Server Error" genérico, que se sospecha es un problema temporal del entorno de Streamlit Cloud.
