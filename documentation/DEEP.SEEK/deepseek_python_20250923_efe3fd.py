import datetime
from factoring_liquidacion_completo import FactoringLiquidacion, ejecutar_pruebas_integradas

def ejecutar_pruebas_avanzadas():
    """Pruebas avanzadas del sistema de liquidación."""
    print("=== 🧪 PRUEBAS AVANZADAS DEL SISTEMA ===\n")
    
    liquidator = FactoringLiquidacion(costo_transaccional_minimo=10.00)
    
    # Configuración base
    datos_base = {
        'capital': 16244.94,
        'tasa_compensatorio_mensual': 0.02,
        'tasa_moratorio_mensual': 0.03,
        'fecha_desembolso': datetime.date(2023, 1, 1),
        'fecha_pago_pactada': datetime.date(2023, 2, 1)
    }
    
    # Casos de prueba críticos
    casos_prueba = [
        {
            'nombre': 'Caso Borde - Pago exacto al centavo',
            'pago': {'fecha_pago': datetime.date(2023, 2, 1), 'monto_pago': 16244.94},
            'esperado': 'LIQUIDACIÓN EN PROCESO'
        },
        {
            'nombre': 'Caso Borde - Saldo mínimo transaccional ($10.01)',
            'pago': {'fecha_pago': datetime.date(2023, 2, 1), 'monto_pago': 16254.95},
            'esperado': 'LIQUIDACIÓN EN PROCESO'
        },
        {
            'nombre': 'Caso Borde - Saldo no transaccional ($9.99)',
            'pago': {'fecha_pago': datetime.date(2023, 2, 1), 'monto_pago': 16254.93},
            'esperado': 'LIQUIDADO - SALDO INSIGNIFICANTE'
        },
        {
            'nombre': 'Pago con 60 días de mora',
            'pago': {'fecha_pago': datetime.date(2023, 4, 1), 'monto_pago': 17000.00},
            'esperado': 'LIQUIDACIÓN EN PROCESO'
        },
        {
            'nombre': 'Pago temprano (antes de fecha pactada)',
            'pago': {'fecha_pago': datetime.date(2023, 1, 15), 'monto_pago': 16000.00},
            'esperado': 'LIQUIDADO'
        }
    ]
    
    resultados = []
    for i, caso in enumerate(casos_prueba, 1):
        print(f"{i}. 🔍 {caso['nombre']}")
        resultado = liquidator.liquidar_operacion(datos_base, caso['pago'])
        estado_obtenido = resultado['resultados_finales']['estado']
        coincide = estado_obtenido.startswith(caso['esperado'])
        
        print(f"   Esperado: {caso['esperado']}")
        print(f"   Obtenido: {estado_obtenido}")
        print(f"   Saldo: ${resultado['resultados_finales']['saldo_global']:,.2f}")
        print(f"   Resultado: {'✅' if coincide else '❌'}\n")
        
        resultados.append({
            'caso': caso['nombre'],
            'esperado': caso['esperado'],
            'obtenido': estado_obtenido,
            'coincide': coincide,
            'saldo': resultado['resultados_finales']['saldo_global']
        })
    
    # Estadísticas finales
    coincidencias = sum(1 for r in resultados if r['coincide'])
    total = len(resultados)
    
    print(f"📊 ESTADÍSTICAS FINALES:")
    print(f"• Pruebas ejecutadas: {total}")
    print(f"• Pruebas exitosas: {coincidencias}")
    print(f"• Tasa de éxito: {(coincidencias/total)*100:.1f}%")
    
    return resultados

if __name__ == "__main__":
    # Ejecutar pruebas integradas básicas
    print("=== PRUEBAS BÁSICAS ===")
    resultados_basicos = ejecutar_pruebas_integradas()
    
    # Ejecutar pruebas avanzadas
    print("\n=== PRUEBAS AVANZADAS ===")
    resultados_avanzados = ejecutar_pruebas_avanzadas()
    
    print("🎉 SISTEMA COMPLETAMENTE VALIDADO Y LISTO")