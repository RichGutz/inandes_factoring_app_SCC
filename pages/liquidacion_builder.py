import os
import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from typing import List, Dict, Any

def _format_currency(value: float, currency: str = "PEN") -> str:
    """Formats a number as currency with a thousands separator and symbol."""
    if value is None:
        return ""
    try:
        val = float(value)
    except (ValueError, TypeError):
        return str(value)
    
    if currency:
        return f"{currency} {val:,.2f}"
    else:
        return f"{val:,.2f}"

def generar_anexo_liquidacion_pdf(invoices_data: List[Dict[str, Any]]) -> bytes | None:
    """
    Generates the 'Anexo de Liquidación' PDF for one or more invoices.
    This follows the project's standard of using Jinja2 templates and WeasyPrint.
    """
    try:
        # --- 1. Setup Paths and Jinja2 Environment ---
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Corrected path
        templates_dir = os.path.join(project_root, 'src', 'templates')
        static_dir = os.path.join(project_root, 'static')

        env = Environment(loader=FileSystemLoader(templates_dir))
        env.filters['format_currency'] = _format_currency # Changed to filters
        template = env.get_template("anexo_liquidacion.html")

        # --- 2. Process Data and Calculate Totals ---
        if not invoices_data:
            return None

        # Data for the header (assuming it's the same for all invoices in the batch)
        first_invoice = invoices_data[0]
        emisor = {
            'nombre': first_invoice.get('emisor_nombre', ''),
            'ruc': first_invoice.get('emisor_ruc', '')
        }
        pagador = {
            'nombre': first_invoice.get('aceptante_nombre', ''),
            'ruc': first_invoice.get('aceptante_ruc', '')
        }

        # Calculate totals for the main table footer
        totals = {
            'monto_neto': sum(inv.get('monto_neto_factura', 0) for inv in invoices_data),
            'capital': sum(inv.get('recalculate_result', {}).get('calculo_con_tasa_encontrada', {}).get('capital', 0) for inv in invoices_data),
            'intereses': sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('interes', {}).get('monto', 0) for inv in invoices_data),
            'monto_desembolsar': sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('abono', {}).get('monto', 0) for inv in invoices_data)
        }

        # Calculate totals for the summary table
        total_comisiones = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('comision_estructuracion', {}).get('monto', 0) for inv in invoices_data)
        total_margen_seguridad = sum(inv.get('recalculate_result', {}).get('desglose_final_detallado', {}).get('margen_seguridad', {}).get('monto', 0) for inv in invoices_data)
        total_igv = sum(inv.get('recalculate_result', {}).get('calculo_con_tasa_encontrada', {}).get('igv_total', 0) for inv in invoices_data)
        
        # This is the final amount the client receives
        neto_a_desembolsar_final = totals['monto_desembolsar'] - total_comisiones - total_igv

        totals['comisiones'] = total_comisiones
        totals['margen_seguridad'] = total_margen_seguridad
        totals['igv'] = total_igv
        totals['neto_desembolsar'] = neto_a_desembolsar_final

        # --- 3. Prepare Template Data ---
        template_data = {
            'invoices': invoices_data,
            'emisor': emisor,
            'pagador': pagador,
            'moneda': first_invoice.get('moneda_factura', 'PEN'),
            'anexo_number': first_invoice.get('anexo_number', '' ),
            'print_date': datetime.datetime.now(),
            'totals': totals
        }

        # --- 4. Render HTML and Convert to PDF ---
        html_out = template.render(template_data)
        
        # The base_url is crucial for WeasyPrint to find local files like logos or CSS
        base_url = project_root
        
        return HTML(string=html_out, base_url=base_url).write_pdf()

    except Exception as e:
        print(f"[ERROR in PDF Generation]: {e}")
        # Optionally, re-raise or handle the exception as needed
        raise e