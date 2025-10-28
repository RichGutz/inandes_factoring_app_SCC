import pandas as pd
from datetime import datetime, timedelta
import math

class SistemaLiquidacionesComprehensive:
    """
    Sistema completo de liquidaciones financieras
    Réplica exacta de las fórmulas y lógica de Excel
    """
    
    def __init__(self):
        # PARÁMETROS PRINCIPALES (valores reales del Excel)
        self.fecha_desembolso = datetime(2024, 12, 24)
        self.capital = 17822.00536953091
        self.tasa_compensatoria = 0.02
        self.tasa_moratoria = 0.03
        self.fecha_pago = datetime(2025, 4, 1)
        
        # VALORES DE COBRANZA
        self.intereses_cobrados = 1202.835048660585
        self.igv_intereses_cobrados = 216.5103087589053
        self.desembolso_total = 16244.935264591071
        
        # CONFIGURACIÓN DE LIQUIDACIONES
        self.liquidaciones = [
            {'nombre': 'Liquidacion1', 'fecha': datetime(2025, 2, 24), 'pago': 17000},
            {'nombre': 'Liquidacion2', 'fecha': datetime(2025, 2, 24), 'pago': 15712.74},
            {'nombre': 'Liquidacion3', 'fecha': datetime(2025, 4, 1), 'pago': 16244.9353},
            {'nombre': 'Liquidacion4A', 'fecha': datetime(2025, 4, 4), 'pago': 15000}
        ]
    
    def calcular_intereses_excel(self, fecha_inicio, fecha_fin, tasa_mensual):
        """
        Réplica exacta de la fórmula Excel: (POWER((1+tasa/30), días)-1)*capital
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
        Procesa todas las liquidaciones y genera resultados
        """
        resultados = []
        
        for liq in self.liquidaciones:
            # CÁLCULO DE INTERESES COMPENSATORIOS
            int_comp = self.calcular_intereses_excel(
                self.fecha_desembolso, liq['fecha'], self.tasa_compensatoria
            )
            igv_comp = int_comp * 0.18
            
            # CÁLCULO DE INTERESES MORATORIOS
            if liq['fecha'] > self.fecha_pago:
                int_mora = self.calcular_intereses_excel(
                    self.fecha_pago, liq['fecha'], self.tasa_moratoria
                )
                igv_mora = int_mora * 0.18
            else:
                int_mora = 0
                igv_mora = 0
            
            # CÁLCULO DE DELTAS
            delta_comp = int_comp - self.intereses_cobrados
            delta_capital = self.desembolso_total - liq['pago']
            saldo_global = delta_comp + delta_capital
            
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
                'Delta_Capital': delta_capital,
                'Saldo_Global': saldo_global,
                'Estado': estado,
                'Accion_Recomendada': accion
            }
            
            resultados.append(resultado)
        
        return pd.DataFrame(resultados)
    
    def generar_reporte_detallado(self, df_resultados):
        """
        Genera un reporte ejecutivo detallado
        """
        print("=" * 80)
        print("📊 SISTEMA DE LIQUIDACIONES COMPREHENSIVE - REPORTE EJECUTIVO")
        print("=" * 80)
        
        print(f"\n📋 PARÁMETROS PRINCIPALES:")
        print(f"   • Fecha Desembolso: {self.fecha_desembolso.strftime('%Y-%m-%d')}")
        print(f"   • Capital: ${self.capital:,.2f}")
        print(f"   • Fecha Pago: {self.fecha_pago.strftime('%Y-%m-%d')}")
        print(f"   • Intereses Cobrados: ${self.intereses_cobrados:,.2f}")
        print(f"   • Desembolso Total: ${self.desembolso_total:,.2f}")
        
        print(f"\n💵 RESUMEN DE LIQUIDACIONES:")
        for _, row in df_resultados.iterrows():
            print(f"\n   {row['Liquidacion']} ({row['Fecha']}):")
            print(f"     Días: {row['Dias']}")
            print(f"     Intereses Comp.: ${row['Int_Compensatorios']:,.2f}")
            print(f"     Delta Comp.: ${row['Delta_Compensatorios']:,.2f}")
            print(f"     Delta Capital: ${row['Delta_Capital']:,.2f}")
            print(f"     Saldo Global: ${row['Saldo_Global']:,.2f}")
            print(f"     Estado: {row['Estado']}")
            print(f"     Acción: {row['Accion_Recomendada']}")
        
        print(f"\n🎯 ESTADÍSTICAS FINALES:")
        total_liquidado = len(df_resultados[df_resultados['Estado'].str.contains('LIQUIDADO')])
        total_proceso = len(df_resultados[df_resultados['Estado'].str.contains('EN PROCESO')])
        print(f"   • Liquidaciones Finalizadas: {total_liquidado}")
        print(f"   • Liquidaciones en Proceso: {total_proceso}")
        print(f"   • Total Procesado: {len(df_resultados)}")
        
        print("\n" + "=" * 80)

def main():
    """
    Función principal de ejecución del sistema
    """
    # INICIALIZAR SISTEMA
    sistema = SistemaLiquidacionesComprehensive()
    
    # PROCESAR LIQUIDACIONES
    print("🔄 Procesando liquidaciones...")
    resultados = sistema.procesar_liquidaciones()
    
    # MOSTRAR RESULTADOS TABULARES
    print("\n📈 RESULTADOS DETALLADOS:")
    print(resultados.to_string(index=False, float_format='%.2f'))
    
    # GENERAR REPORTE EJECUTIVO
    sistema.generar_reporte_detallado(resultados)
    
    # VERIFICACIÓN DE CÁLCULOS
    print("\n✅ VERIFICACIÓN DE PRECISIÓN:")
    liq1 = resultados[resultados['Liquidacion'] == 'Liquidacion1'].iloc[0]
    diferencia = liq1['Int_Compensatorios'] - sistema.intereses_cobrados
    print(f"   Diferencia en Liquidacion1: ${diferencia:.6f}")
    print(f"   Precisión: {'EXACTA' if abs(diferencia) < 0.01 else 'APROXIMADA'}")

if __name__ == "__main__":
    main()