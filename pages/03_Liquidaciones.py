# liquidacion_por_lotes_app.py
import os

# --- Path Setup ---
# The main script (00_Home.py) handles adding 'src' to the path.
# This page only needs to know the project root for static assets.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import datetime
import requests
import json
import subprocess
from src.utils.pdf_generators import generate_lote_report_pdf

# --- Module Imports from `src` ---
from src.data import supabase_repository as db

# --- Estrategia Unificada para la URL del Backend ---

# 1. Intenta leer la URL desde una variable de entorno local (para desarrollo).
#    Esta es la que usarás para apuntar a Render desde tu máquina.
API_BASE_URL = os.getenv("BACKEND_API_URL")

# 2. Si no la encuentra, intenta leerla desde los secretos de Streamlit (para la nube).
if not API_BASE_URL:
    try:
        API_BASE_URL = st.secrets["backend_api"]["url"]
    except (KeyError, AttributeError):
        # 3. Si todo falla, muestra un error claro.
        st.error("La URL del backend no está configurada. Define BACKEND_API_URL o configúrala en st.secrets.")
        st.stop() # Detiene la ejecución si no hay URL

# --- Configuración de la Página ---
st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_title="Módulo de Liquidación INANDES",
    page_icon="💰"
)

# --- Inicialización del Session State ---
if 'vista_actual' not in st.session_state: st.session_state.vista_actual = 'busqueda'
if 'lote_encontrado' not in st.session_state: st.session_state.lote_encontrado = []
if 'facturas_seleccionadas' not in st.session_state: st.session_state.facturas_seleccionadas = {}
if 'facturas_a_liquidar' not in st.session_state: st.session_state.facturas_a_liquidar = []
if 'resultados_liquidacion_lote' not in st.session_state: st.session_state.resultados_liquidacion_lote = None
if 'global_liquidation_vars' not in st.session_state: 
    st.session_state.global_liquidation_vars = {
        'fecha_pago': datetime.date.today(), 
        'tasa_mora_anual': 1.0, 
        'tasa_interes_compensatoria_pct': 0.0 
    }
if 'contract_number' not in st.session_state: st.session_state.contract_number = ''
if 'anexo_number' not in st.session_state: st.session_state.anexo_number = ''
if 'sustento_unico' not in st.session_state: st.session_state.sustento_unico = False
if 'consolidated_proof_file' not in st.session_state: st.session_state.consolidated_proof_file = None
if 'individual_proof_files' not in st.session_state: st.session_state.individual_proof_files = {}
 

# --- Funciones de Ayuda ---
def parse_invoice_number(proposal_id: str) -> str:
    try:
        parts = proposal_id.split('-')
        return f"{parts[1]}-{parts[2]}" if len(parts) > 2 else proposal_id
    except (IndexError, AttributeError):
        return proposal_id

# --- Funciones de Despliegue de Información ---
def _display_operation_profile_batch(data):
    st.subheader("Perfil de la Operación Original")
    recalc_result_json = data.get('recalculate_result_json')
    if not recalc_result_json: 
        st.warning("No se encontraron datos de cálculo en la propuesta original.")
        return

    try:
        recalc_result = json.loads(recalc_result_json)
    except json.JSONDecodeError:
        st.error("Error al leer los datos del perfil de operación original.")
        return

    desglose = recalc_result.get('desglose_final_detallado', {})
    calculos = recalc_result.get('calculo_con_tasa_encontrada', {})
    busqueda = recalc_result.get('resultado_busqueda', {})
    moneda = data.get('moneda_factura', 'PEN')

    st.markdown(
        f"**Emisor:** {data.get('emisor_nombre', 'N/A')} | "
        f"**Aceptante:** {data.get('aceptante_nombre', 'N/A')} | "
        f"**Factura:** {data.get('numero_factura', 'N/A')} | "
        f"**F. Pago Original:** {data.get('fecha_pago_calculada', 'N/A')} | "
        f"**Monto Total:** {data.get('moneda_factura', '')} {data.get('monto_total_factura', 0):,.2f} | "
        f"**Monto Neto:** {data.get('moneda_factura', '')} {data.get('monto_neto_factura', 0):,.2f} | "
        f"**Int. Compensatorio:** {data.get('interes_mensual', 0.0):.2f}% | "
        f"**Int. Moratorio:** {data.get('interes_moratorio', 0.0):.2f}%"
    )

    tasa_avance_pct = busqueda.get('tasa_avance_encontrada', 0) * 100
    monto_neto = data.get('monto_neto_factura', 0)
    capital = calculos.get('capital', 0)
    abono = desglose.get('abono', {})
    interes = desglose.get('interes', {})
    com_est = desglose.get('comision_estructuracion', {})
    com_afi = desglose.get('comision_afiliacion', {})
    igv_total = desglose.get('igv_total', {})
    margen = desglose.get('margen_seguridad', {})

    lines = [
        f"| Item | Monto ({moneda}) | % sobre Neto | Detalle del Cálculo |",