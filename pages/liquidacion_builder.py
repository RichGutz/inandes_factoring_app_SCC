
import datetime
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        # No header by default
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        # Page number
        # self.cell(0, 10, 'Page ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def generar_pdf_liquidacion_lucy(datos):
    """
    Genera un archivo PDF de liquidación con el formato específico de LUCY.

    Args:
        datos (dict): Un diccionario conteniendo toda la información necesaria para la liquidación.
                      Ej: {
                          'razon_social_descontadora': 'MI EMPRESA S.A.C.',
                          'RUC_empresa_descontadora': '20111111111',
                          'lote_id': 'OPER-001',
                          'moneda': 'Soles',
                          'tasa_mensual': 0.03,
                          'plazo_operacion': 30,
                          'numero_factura': 'F001-00123',
                          'fecha_emision': '01/08/2025',
                          'fecha_pago': '31/08/2025',
                          'importe_total_factura': 10000.00,
                          'intereses': 300.00,
                          'comision_desembolso': 50.00,
                          'neto_a_desembolsar': 8150.00
                      }
    """
    pdf = PDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Arial', '', 10)

    # === 1. TÍTULO Y FECHA ===
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'LIQUIDACIÓN DE OPERACIÓN DE FACTORING', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, 'CONTRATO DE ADELANTO DE CUENTAS POR COBRAR', 0, 1, 'C')
    pdf.ln(10)

    fecha_liquidacion = datetime.datetime.now().strftime("%d de %B de %Y")
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f'Lima, {fecha_liquidacion}', 0, 1, 'R')
    pdf.ln(5)

    # === 2. DATOS DEL CLIENTE ===
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, 'SEÑORES:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, datos.get('razon_social_descontadora', ''), 0, 1, 'L')
    pdf.cell(0, 5, f"RUC: {datos.get('RUC_empresa_descontadora', '')}", 0, 1, 'L')
    pdf.cell(0, 5, 'Presente.-', 0, 1, 'L')
    pdf.ln(5)

    # === 3. PÁRRAFO INTRODUCTORIO ===
    pdf.cell(0, 5, 'De nuestra consideración:', 0, 1, 'L')
    pdf.ln(5)
    pdf.multi_cell(0, 5, 
        'Por medio de la presente, y en el marco del Contrato de Adelanto de Cuentas por Cobrar (en adelante, el "Contrato"), '
        'cumplimos con remitirles la liquidación correspondiente al adelanto sobre las cuentas por cobrar que han sido '
        'cedidas a nuestra empresa.'
    )
    pdf.ln(10)

    # === 4. RESUMEN DE LA OPERACIÓN ===
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '1. Resumen de la Operación', 0, 1, 'L')
    
    tasa_mensual = datos.get('tasa_mensual', 0)
    tea = ((1 + tasa_mensual) ** 12 - 1) * 100 if tasa_mensual else 0

    resumen_data = {
        "Código de Operación:": datos.get('lote_id', 'N/A'),
        "Fecha de Liquidación:": fecha_liquidacion,
        "Moneda:": datos.get('moneda', 'Soles'),
        "Tasa de Interés Efectiva Anual (TEA):": f"{tea:.2f}%",
        "Plazo de la Operación:": f"{datos.get('plazo_operacion', 0)} días"
    }

    pdf.set_font('Arial', '', 10)
    for key, value in resumen_data.items():
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(70, 6, key, 0, 0, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, value, 0, 1, 'L')
    pdf.ln(10)

    # === 5. DETALLE DE INSTRUMENTOS NEGOCIADOS ===
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '2. Detalle de Instrumentos Negociados', 0, 1, 'L')
    
    # Table Header
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font('Arial', 'B', 9)
    pdf.cell(35, 7, 'Tipo de Documento', 1, 0, 'C', 1)
    pdf.cell(40, 7, 'N° de Documento', 1, 0, 'C', 1)
    pdf.cell(30, 7, 'Fecha de Emisión', 1, 0, 'C', 1)
    pdf.cell(35, 7, 'Fecha de Vencimiento', 1, 0, 'C', 1)
    pdf.cell(40, 7, 'Valor Nominal', 1, 1, 'C', 1)

    # Table Row
    pdf.set_font('Arial', '', 9)
    valor_nominal = datos.get('importe_total_factura', 0)
    pdf.cell(35, 7, 'Factura', 1, 0, 'C')
    pdf.cell(40, 7, datos.get('numero_factura', ''), 1, 0, 'C')
    pdf.cell(30, 7, datos.get('fecha_emision', ''), 1, 0, 'C')
    pdf.cell(35, 7, datos.get('fecha_pago', ''), 1, 0, 'C')
    pdf.cell(40, 7, f"S/ {valor_nominal:,.2f}", 1, 1, 'R')
    pdf.ln(10)

    # === 6. DETALLE DE LA LIQUIDACIÓN ===
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 10, '3. Detalle de la Liquidación', 0, 1, 'L')

    adelanto_pct = 0.85
    adelanto_monto = valor_nominal * adelanto_pct
    total_descuentos = datos.get('intereses', 0) + datos.get('comision_desembolso', 0)
    monto_a_abonar = adelanto_monto - total_descuentos

    liquidacion_data = {
        "Valor Nominal Total:": f"S/ {valor_nominal:,.2f}",
        f"Adelanto ({adelanto_pct:.2%}):": f"S/ {adelanto_monto:,.2f}",
        "Intereses:": f"- S/ {datos.get('intereses', 0):,.2f}",
        "Comisiones / Otros:": f"- S/ {datos.get('comision_desembolso', 0):,.2f}",
        "Monto a Abonar:": f"S/ {datos.get('neto_a_desembolsar', 0):,.2f}" # Usamos el del front por si hay logica adicional
    }
    
    pdf.set_font('Arial', '', 10)
    for key, value in liquidacion_data.items():
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(70, 6, key, 0, 0, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, value, 0, 1, 'L')
    pdf.ln(15)

    # === 7. CIERRE Y FIRMA ===
    pdf.cell(0, 5, 'Sin otro particular, quedamos de ustedes.', 0, 1, 'L')
    pdf.ln(5)
    pdf.cell(0, 5, 'Atentamente,', 0, 1, 'L')
    pdf.ln(20)

    pdf.cell(0, 5, '_________________________', 0, 1, 'L')
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 5, 'p. LUCY CAPITAL S.A.C.', 0, 1, 'L')
    pdf.cell(0, 5, 'RUC 20610143293', 0, 1, 'L')

    # --- Guardar el PDF ---
    # El guardado se hará en el script principal para poder servirlo al usuario
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

