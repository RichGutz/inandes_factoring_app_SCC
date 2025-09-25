import pandas as pd
from datetime import datetime, timedelta
import math

class SistemaLiquidacionesComprehensive:
    """
    Sistema completo de liquidaciones financieras
    Réplica EXACTA de todas las fórmulas del Excel
    """
    
    def __init__(self):
        # PARÁMETROS PRINCIPALES (valores exactos del Excel)
        self.fecha_desembolso = datetime(2024, 12, 24)
        self.capital = 17822.00536953091
        self.tasa_compensatoria = 0.02
        self.tasa_moratoria = 0.03
        self.fecha_pago = datetime(2025, 4, 1)
        
        # VALORES DE COBRANZA
        self.intereses_cobrados = 1202.835048660585
        self.igv_intereses_cobrados = 216.5103087589053
        self.desembolso_total = 16244.935264591071
        
        # CONFIGURACIÓN DE TODAS LAS LIQUIDACIONES DEL EXCEL (con fechas exactas)
        self.liquidaciones = [
            {'nombre': 'Liquidacion1', 'fecha': datetime(2025, 2, 24), 'pago': 17000},
            {'nombre': 'Liquidacion2', 'fecha': datetime(2025, 2, 24), 'pago': 15712.74},
            {'nombre': 'Liquidacion3', 'fecha': datetime(2025, 4, 1), 'pago': 16244.9353},
            {'nombre': 'Liquidacion4', 'fecha': datetime(2025, 4, 4), 'pago': 14000},
            {'nombre': 'Liquidacion5', 'fecha': datetime(2025, 4, 4), 'pago': 16350},
            {'nombre': 'Liquidacion6', 'fecha': datetime(2025, 3, 28), 'pago': 16200},
            {'nombre': 'Liquidacion7', 'fecha': datetime(2025, 4, 3), 'pago': 16000},
            {'nombre': 'Liquidacion8', 'fecha': datetime(2025, 4, 4), 'pago': 16500},
            {'nombre': 'Liquidacion9A', 'fecha': datetime(2025, 4, 4), 'pago': 15000}
        ]
    
    def calcular_intereses_excel(self, fecha_inicio, fecha_fin, tasa_mensual):
        """
        Réplica EXACTA de la fórmula Excel: (POWER((1+tasa/30), días)-1)*capital
        """
        dias = (fecha_fin - fecha_inicio).days
        if dias <= 0:
            return 0
        
        tasa_diaria = tasa_mensual / 30
        factor = math.pow(1 + tasa_diaria, dias)
        return (factor - 1) * self.capital
    
    def clasificar_caso(self, delta_comp, delta_capital, saldo_global):
        """
        Clasifica según los 6 casos definidos en el Excel
        """
        if delta_comp < 0 and delta_capital < 0 and saldo_global < 0:
            return "LIQUIDADO - Caso 1", "Generar NC, devolver dinero"
        elif delta_comp < 0 and delta_capital > 0 and saldo_global > 0:
            return "EN PROCESO - Caso 2", "Generar NC, nuevo calendario"
        elif delta_comp > 0 and delta_capital > 0 and saldo_global > 0:
            return "EN PROCESO - Caso 3", "Facturar más intereses, nuevo calendario"
        elif delta_comp > 0 and delta_capital < 0 and saldo_global > 0:
            return "EN PROCESO - Caso 4", "Facturar más intereses, nuevo calendario"
        elif delta_comp > 0 and delta_capital < 0 and saldo_global < 0:
            return "LIQUIDADO - Caso 5", "Facturar intereses, devolver exceso"
        elif delta_comp < 0 and delta_capital > 0 and saldo_global < 0:
            return "LIQUIDADO - Caso 6", "Generar NC, devolver dinero"
        else:
            return "NO CLASIFICADO", "Revisar manualmente"
    
    def procesar_liquidaciones(self):
        """
        Procesa TODAS las liquidaciones del Excel
        """
        resultados = []
        
        for liq in self.liquidaciones:
            # CÁLCULO DE INTERESES COMPENSATORIOS (EXACTA FÓRMULA EXCEL)
            int_comp = self.calcular_intereses_excel(
                self.fecha_desembolso, liq['fecha'], self.tasa_compensatoria
            )
            igv_comp = int_comp * 0.18
            
            # CÁLCULO DE INTERESES MORATORIOS (si aplica)
            int_mora = 0
            igv_mora = 0
            if liq['fecha'] > self.fecha_pago:
                int_mora = self.calcular_intereses_excel(
                    self.fecha_pago, liq['fecha'], self.tasa_moratoria
                )
                igv_mora = int_mora * 0.18
            
            # CÁLCULO DE DELTAS (EXACTAMENTE COMO EN EXCEL)
            delta_comp = int_comp - self.intereses_cobrados
            delta_igv_comp = igv_comp - self.igv_intereses_cobrados
            delta_capital = self.desembolso_total - liq['pago']
            
            # SALDO GLOBAL (suma de todos los deltas + moratorios)
            saldo_global = delta_comp + delta_igv_comp + int_mora + igv_mora + delta_capital
            
            # CLASIFICACIÓN
            estado, accion = self.clasificar_caso(delta_comp, delta_capital, saldo_global)
            
            # REGISTRO DE RESULTADOS
            resultado = {
                'Liquidacion': liq['nombre'],
                'Fecha': liq['fecha'].strftime('%Y-%m-%d'),
                'Dias': (liq['fecha'] - self.fecha_desembolso).days,
                'Int_Compensatorios': int_comp,
                'IGV_Compensatorios': igv_comp,
                'Int_Moratorios': int_mora,
                'IGV_Moratorios': igv_mora,
                'Delta_Compensatorios': delta_comp,
                'Delta_IGV_Compensatorios': delta_igv_comp,
                'Delta_Capital': delta_capital,
                'Saldo_Global': saldo_global,
                'Estado': estado,
                'Accion_Recomendada': accion
            }
            
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)

# VERIFICACIÓN INMEDIATA DE LOS CÁLCULOS CLAVE
print("=== VERIFICACIÓN DE CÁLCULOS CLAVE ===")

# Parámetros exactos
fecha_desembolso = datetime(2024, 12, 24)
capital = 17822.00536953091
tasa = 0.02
intereses_cobrados = 1202.835048660585
desembolso_total = 16244.935264591071

# Función de cálculo exacta
def calcular_intereses(dias):
    tasa_diaria = tasa / 30
    factor = math.pow(1 + tasa_diaria, dias)
    return (factor - 1) * capital

# Liquidacion1: 62 días (24-feb-2025)
dias_liq1 = (datetime(2025, 2, 24) - fecha_desembolso).days
int_comp_liq1 = calcular_intereses(dias_liq1)

# Liquidacion3: 98 días (1-abr-2025) - Fila 109 del Excel
dias_liq3 = (datetime(2025, 4, 1) - fecha_desembolso).days
int_comp_liq3 = calcular_intereses(dias_liq3)

# Liquidacion4: 101 días (4-abr-2025) - Fila 105 del Excel
dias_liq4 = (datetime(2025, 4, 4) - fecha_desembolso).days
int_comp_liq4 = calcular_intereses(dias_liq4)

print(f"Liquidacion1 (62 días):")
print(f"  Intereses calculados: {int_comp_liq1:.10f}")
print(f"  Intereses cobrados:   {intereses_cobrados:.10f}")
print(f"  ¿Coinciden? {'✅ EXACTO' if abs(int_comp_liq1 - intereses_cobrados) < 0.0000001 else '❌ DIFERENTE'}")

print(f"\nLiquidacion3 (98 días):")
print(f"  Intereses calculados: {int_comp_liq3:.10f}")
print(f"  Delta compensatorios: {int_comp_liq3 - intereses_cobrados:.10f}")

print(f"\nLiquidacion4 (101 días):")
print(f"  Intereses calculados: {int_comp_liq4:.10f}")
print(f"  Delta compensatorios: {int_comp_liq4 - intereses_cobrados:.10f}")

# EJECUTAR SISTEMA COMPLETO
print("\n" + "="*80)
print("SISTEMA COMPLETO DE LIQUIDACIONES")
print("="*80)

sistema = SistemaLiquidacionesComprehensive()
resultados = sistema.procesar_liquidaciones()

# Mostrar resultados en formato tabla
pd.set_option('display.float_format', '{:.6f}'.format)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

print("\nRESULTADOS COMPLETOS:")
print(resultados.to_string(index=False))

# RESUMEN POR CASOS
print("\n" + "="*80)
print("RESUMEN POR CASOS DE CLASIFICACIÓN")
print("="*80)

for caso in range(1, 7):
    liquidaciones_caso = resultados[resultados['Estado'].str.contains(f'Caso {caso}')]
    if len(liquidaciones_caso) > 0:
        print(f"\nCASO {caso}: {len(liquidaciones_caso)} liquidación(es)")
        for _, liq in liquidaciones_caso.iterrows():
            print(f"  {liq['Liquidacion']}: {liq['Estado']}")
            print(f"    Saldo Global: ${liq['Saldo_Global']:,.2f}")
            print(f"    Acción: {liq['Accion_Recomendada']}")