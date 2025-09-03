# src/utils/pdf_generators.py

import os
import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from typing import List, Dict, Any

# --- Helper Functions for Templates ---

def _format_currency(value: float, currency: str = "PEN") -> str:
    """Formats a number as currency with a thousands separator and symbol."""
    if value is None:
        return ""
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
    return f"{currency} {val:,.2f}"

# --- Main PDF Generation Logic ---

def _generate_pdf_in_memory(
    template_name: str,
    template_data: Dict[str, Any]
) -> bytes | None:
    """
    Core PDF generation function that returns the PDF as bytes.
    """
    try:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        templates_dir = os.path.join(project_root, 'src', 'templates')
        
        env = Environment(loader=FileSystemLoader(templates_dir))
        env.globals['format_currency'] = _format_currency
        template = env.get_template(template_name)

        html_out = template.render(template_data)
        
        base_url = project_root
        return HTML(string=html_out, base_url=base_url).write_pdf()
        
    except Exception as e:
        print(f"[ERROR in PDF Generation]: {e}")
        return None

# --- Public Functions for Specific Reports ---

def generate_perfil_operacion_pdf(invoices_data: List[Dict[str, Any]]) -> bytes | None:
    """
    Generates the 'Perfil de Operación' PDF for one or more invoices and returns it as bytes.
    """
    template_data = {
        'invoices': invoices_data,
        'print_date': datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    }
    return _generate_pdf_in_memory("perfil_operacion.html", template_data)

def generate_efide_report_pdf(invoices_data: List[Dict[str, Any]], signatory_data: Dict[str, Any]) -> bytes | None:
    """
    Generates the EFIDE report PDF with all calculations and returns it as bytes.
    """
    # --- Calculate Totals for the Footer ---
    total_monto_total_factura = sum(inv.get('monto_total_factura', 0) for inv in invoices_data)
    total_detraccion_monto = sum(inv.get('detraccion_monto', 0) for inv in invoices_data)
    total_monto_neto_factura = sum(inv.get('monto_neto_factura', 0) for inv in invoices_data)
    
    weighted_sum_tasa_avance = sum(
        inv.get('monto_neto_factura', 0) * inv.get('recalculate_result', {}).get('resultado_busqueda', {}).get('tasa_avance_encontrada', 0)
        for inv in invoices_data
    )
    total_tasa_avance_aplicada = (weighted_sum_tasa_avance / total_monto_neto_factura) if total_monto_neto_factura > 0 else 0
    
    total_margen_seguridad = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('margen_seguridad', {}).get('monto', 0) for inv in invoices_data)
    total_capital = sum(inv.get('recalculate_result', {}).get('calculo_con_tasa_encontrada', {}).get('capital', 0) for inv in invoices_data)
    total_intereses = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('interes', {}).get('monto', 0) for inv in invoices_data)
    total_comision_estructuracion = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('comision_estructuracion', {}).get('monto', 0) for inv in invoices_data)
    total_comision_afiliacion = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('comision_afiliacion', {}).get('monto', 0) for inv in invoices_data)
    
    total_igv = sum(
        inv.get('recalculate_result', {}).get('calculo_con_tasa_encontrada', {}).get('igv_interes', 0) +
        inv.get('recalculate_result', {}).get('calculo_con_tasa_encontrada', {}).get('igv_comision_estructuracion', 0) +
        inv.get('recalculate_result', {}).get('calculo_con_tasa_encontrada', {}).get('igv_afiliacion', 0)
        for inv in invoices_data
    )
    
    total_monto_desembolsar = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('abono', {}).get('monto', 0) for inv in invoices_data)

    template_data = {
        'invoices': invoices_data,
        'print_date': datetime.datetime.now(),
        'main_invoice': invoices_data[0] if invoices_data else {},
        'signatory_data': signatory_data or {}, # Ensure it's a dict
        'total_monto_total_factura': total_monto_total_factura,
        'total_detraccion_monto': total_detraccion_monto,
        'total_monto_neto_factura': total_monto_neto_factura,
        'total_tasa_avance_aplicada': total_tasa_avance_aplicada,
        'total_margen_seguridad': total_margen_seguridad,
        'total_capital': total_capital,
        'total_intereses': total_intereses,
        'total_comision_estructuracion': total_comision_estructuracion,
        'total_comision_afiliacion': total_comision_afiliacion,
        'total_igv': total_igv,
        'total_monto_desembolsar': total_monto_desembolsar,
    }
    
    return _generate_pdf_in_memory("reporte_efide.html", template_data)

def generate_lote_report_pdf(report_data: Dict[str, Any]) -> bytes | None:
    """
    (Placeholder) Generates the batch liquidation report PDF and returns it as bytes.
    """
    return _generate_pdf_in_memory("reporte_lote.html", report_data)

def generate_liquidacion_consolidada_pdf(report_data: Dict[str, Any]) -> bytes | None:
    """
    Generates the consolidated liquidation PDF (formerly V6) and returns it as bytes.
    """
    return _generate_pdf_in_memory("liquidacion_consolidada.html", report_data)
