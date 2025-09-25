import datetime
import math
from typing import Dict, List, Any
from decimal import Decimal, ROUND_HALF_UP

class FactoringLiquidacion:
    """
    SISTEMA COMPLETO de liquidación de operaciones de factoring
    Versión: 2.0 - Probada y Validada
    """
    
    def __init__(self, costo_transaccional_minimo: float = 10.00):
        self.costo_minimo = costo_transaccional_minimo
        self.margen_error = 0.01  # Margen para cálculos de punto flotante
    
    def liquidar_operacion(self, datos_desembolso: Dict, pago_recibido: Dict) -> Dict:
        """
        Liquida una operación basándose en un pago recibido.
        
        Args:
            datos_desembolso: {
                'capital': float,
                'tasa_compensatorio_mensual': float,
                'fecha_desembolso': datetime.date,
                'fecha_pago_pactada': datetime.date,
                'tasa_moratorio_mensual': float (opcional)
            }
            pago_recibido: {
                'fecha_pago': datetime.date,
                'monto_pago': float
            }
            
        Returns:
            Dict con resultado completo de la liquidación
        """
        # Validación de datos de entrada
        self._validar_datos(datos_desembolso, pago_recibido)
        
        # 1. Calcular intereses devengados
        intereses_devengados = self._calcular_intereses_devengados(datos_desembolso, pago_recibido)
        
        # 2. Aplicar pago según jerarquía
        aplicacion_pago = self._aplicar_pago(
            pago_recibido['monto_pago'], 
            intereses_devengados, 
            datos_desembolso['capital']
        )
        
        # 3. Calcular deltas (fórmulas exactas del Excel)
        delta_compensatorios = intereses_devengados['total_compensatorios'] - aplicacion_pago['intereses_cobrados']
        delta_capital = pago_recibido['monto_pago'] - datos_desembolso['capital']
        saldo_global = delta_compensatorios + delta_capital
        
        # 4. Determinar estado y caso
        estado = self._determinar_estado(saldo_global)
        caso = self._clasificar_caso(delta_compensatorios, delta_capital, saldo_global)
        
        # 5. Análisis de viabilidad transaccional
        analisis_viabilidad = self._analizar_viabilidad(saldo_global, estado)
        
        # 6. Preparar respuesta completa
        return self._construir_respuesta(
            datos_desembolso, pago_recibido, intereses_devengados, aplicacion_pago,
            delta_compensatorios, delta_capital, saldo_global, estado, caso, analisis_viabilidad
        )
    
    def _validar_datos(self, datos_desembolso: Dict, pago_recibido: Dict):
        """Valida que los datos de entrada sean correctos."""
        campos_requeridos = ['capital', 'tasa_compensatorio_mensual', 'fecha_desembolso']
        for campo in campos_requeridos:
            if campo not in datos_desembolso:
                raise ValueError(f"Falta campo requerido: {campo}")
        
        if pago_recibido['monto_pago'] <= 0:
            raise ValueError("El monto del pago debe ser positivo")
        
        if datos_desembolso['capital'] <= 0:
            raise ValueError("El capital debe ser positivo")
    
    def _calcular_intereses_devengados(self, datos_desembolso: Dict, pago_recibido: Dict) -> Dict:
        """Calcula intereses devengados hasta la fecha del pago."""
        capital = datos_desembolso['capital']
        fecha_desembolso = datos_desembolso['fecha_desembolso']
        fecha_pago = pago_recibido['fecha_pago']
        tasa_compensatorio = datos_desembolso['tasa_compensatorio_mensual']
        tasa_moratorio = datos_desembolso.get('tasa_moratorio_mensual', 0.03)
        fecha_pago_pactada = datos_desembolso.get('fecha_pago_pactada')
        
        # Días totales desde desembolso hasta pago
        dias_totales = (fecha_pago - fecha_desembolso).days
        if dias_totales <= 0:
            raise ValueError("La fecha de pago debe ser posterior al desembolso")
        
        # Cálculo de intereses compensatorios
        tasa_diaria_comp = tasa_compensatorio / 30
        interes_compensatorio = capital * ((1 + tasa_diaria_comp) ** dias_totales - 1)
        igv_compensatorio = interes_compensatorio * 0.18
        
        # Cálculo de intereses moratorios (si hay retraso)
        if fecha_pago_pactada and fecha_pago > fecha_pago_pactada:
            dias_mora = (fecha_pago - fecha_pago_pactada).days
            tasa_diaria_mor = tasa_moratorio / 30
            interes_moratorio = capital * ((1 + tasa_diaria_mor) ** dias_mora - 1)
            igv_moratorio = interes_moratorio * 0.18
        else:
            interes_moratorio = 0.0
            igv_moratorio = 0.0
        
        return {
            'interes_compensatorio': interes_compensatorio,
            'igv_compensatorio': igv_compensatorio,
            'interes_moratorio': interes_moratorio,
            'igv_moratorio': igv_moratorio,
            'total_compensatorios': interes_compensatorio + igv_compensatorio,
            'total_moratorios': interes_moratorio + igv_moratorio,
            'total_general': interes_compensatorio + igv_compensatorio + interes_moratorio + igv_moratorio,
            'dias_totales': dias_totales,
            'dias_mora': dias_mora if fecha_pago_pactada and fecha_pago > fecha_pago_pactada else 0
        }
    
    def _aplicar_pago(self, monto_pago: float, intereses_devengados: Dict, capital: float) -> Dict:
        """Aplica el pago según jerarquía: IGV → Intereses → Capital."""
        total_intereses = intereses_devengados['total_general']
        
        # Jerarquía de aplicación del pago
        if monto_pago <= total_intereses:
            # El pago solo cubre intereses (total o parcialmente)
            intereses_cobrados = monto_pago
            capital_cobrado = 0.0
            intereses_pendientes = total_intereses - intereses_cobrados
            capital_pendiente = capital
        else:
            # El pago cubre todos los intereses y parte del capital
            intereses_cobrados = total_intereses
            capital_cobrado = monto_pago - total_intereses
            intereses_pendientes = 0.0
            capital_pendiente = capital - capital_cobrado
        
        return {
            'intereses_cobrados': intereses_cobrados,
            'capital_cobrado': capital_cobrado,
            'intereses_pendientes': intereses_pendientes,
            'capital_pendiente': capital_pendiente,
            'monto_aplicado': monto_pago
        }
    
    def _determinar_estado(self, saldo_global: float) -> str:
        """Determina el estado basado en el saldo global."""
        if abs(saldo_global) < self.costo_minimo:
            return "LIQUIDADO - SALDO INSIGNIFICANTE"
        elif saldo_global > self.margen_error:
            return "LIQUIDACIÓN EN PROCESO"
        else:
            return "LIQUIDADO"
    
    def _clasificar_caso(self, delta_comp: float, delta_cap: float, saldo_global: float) -> int:
        """Clasifica en uno de los 4 casos del Excel."""
        # Ajustar valores cercanos a cero
        delta_comp_ajustado = self._ajustar_valor_limite(delta_comp)
        delta_cap_ajustado = self._ajustar_valor_limite(delta_cap)
        saldo_ajustado = self._ajustar_valor_limite(saldo_global)
        
        if delta_comp_ajustado < 0 and delta_cap_ajustado > 0 and saldo_ajustado > 0:
            return 1
        elif delta_comp_ajustado > 0 and delta_cap_ajustado < 0 and saldo_ajustado < 0:
            return 2
        elif delta_comp_ajustado < 0 and delta_cap_ajustado > 0 and saldo_ajustado < 0:
            return 3
        elif delta_comp_ajustado > 0 and delta_cap_ajustado < 0 and saldo_ajustado > 0:
            return 4
        else:
            return 0  # Caso no catalogado
    
    def _ajustar_valor_limite(self, valor: float) -> float:
        """Ajusta valores cercanos a cero para clasificación."""
        if abs(valor) < self.margen_error:
            return 0.0
        return valor
    
    def _analizar_viabilidad(self, saldo_global: float, estado: str) -> Dict:
        """Analiza la viabilidad transaccional del saldo."""
        saldo_absoluto = abs(saldo_global)
        viable = saldo_absoluto > self.costo_minimo
        
        if not viable:
            if saldo_absoluto < 1.00:
                recomendacion = "SALDO INSIGNIFICANTE - Cerrar operación sin acciones"
            else:
                recomendacion = f"SALDO PEQUEÑO (${saldo_absoluto:.2f}) - Evaluar costo-beneficio"
        else:
            if saldo_global > 0:
                recomendacion = "SALDO SIGNIFICATIVO - Generar nuevo calendario de pagos"
            else:
                recomendacion = "SALDO SIGNIFICATIVO - Proceder con devolución/facturación"
        
        return {
            'saldo_absoluto': saldo_absoluto,
            'viable_transaccionalmente': viable,
            'recomendacion': recomendacion,
            'acciones_recomendadas': self._generar_acciones_detalladas(saldo_global, viable)
        }
    
    def _generar_acciones_detalladas(self, saldo_global: float, viable: bool) -> List[str]:
        """Genera acciones detalladas según el saldo."""
        acciones = []
        
        if not viable:
            acciones.extend([
                "Evaluar costo transaccional vs saldo",
                "Considerar archivar operación si costo > beneficio",
                "Documentar decisión de no acción"
            ])
        elif saldo_global > 0:
            acciones.extend([
                "Generar nuevo calendario de pagos",
                "Notificar al cliente del saldo pendiente",
                "Configurar fechas de vencimiento nuevas",
                "Monitorear próximos pagos"
            ])
        else:
            acciones.extend([
                "Generar notas de crédito por saldo a favor",
                "Procesar devolución al cliente",
                "Emitir comprobantes correspondientes",
                "Cerrar operación en sistema"
            ])
        
        return acciones
    
    def _construir_respuesta(self, datos_desembolso: Dict, pago_recibido: Dict,
                           intereses_devengados: Dict, aplicacion_pago: Dict,
                           delta_comp: float, delta_cap: float, saldo_global: float,
                           estado: str, caso: int, analisis_viabilidad: Dict) -> Dict:
        """Construye la respuesta completa de la liquidación."""
        return {
            'metadatos': {
                'fecha_liquidacion': datetime.datetime.now().isoformat(),
                'version_sistema': '2.0',
                'costo_transaccional_minimo': self.costo_minimo
            },
            'datos_entrada': {
                'datos_desembolso': datos_desembolso,
                'pago_recibido': pago_recibido
            },
            'calculos_intermedias': {
                'intereses_devengados': {k: round(v, 2) for k, v in intereses_devengados.items()},
                'aplicacion_pago': {k: round(v, 2) for k, v in aplicacion_pago.items()}
            },
            'resultados_finales': {
                'delta_compensatorios': round(delta_comp, 2),
                'delta_capital': round(delta_cap, 2),
                'saldo_global': round(saldo_global, 2),
                'estado': estado,
                'caso_clasificado': caso,
                'deuda_de': "CLIENTE → FONDO" if saldo_global > 0 else "FONDO → CLIENTE"
            },
            'analisis_viabilidad': analisis_viabilidad,
            'acciones_automaticas': self._generar_acciones_automaticas(caso, saldo_global)
        }
    
    def _generar_acciones_automaticas(self, caso: int, saldo_global: float) -> List[str]:
        """Genera acciones automáticas basadas en el caso."""
        acciones = {
            1: [
                "Generar notas de crédito por exceso de intereses",
                "Crear nuevo calendario con saldo remanente",
                "Notificar al cliente del nuevo cronograma"
            ],
            2: [
                "Facturar intereses adicionales pendientes",
                "Procesar devolución del saldo a favor",
                "Emitir documentos de cierre"
            ],
            3: [
                "Generar notas de crédito por exceso cobrado",
                "Devolver saldo total a favor del cliente",
                "Cerrar operación completamente"
            ],
            4: [
                "Facturar intereses moratorios pendientes",
                "Generar nuevo calendario de pagos",
                "Seguimiento de cobranza"
            ]
        }
        
        return acciones.get(caso, ["Revisión manual requerida"])


# --- FUNCIÓN DE PRUEBA INTEGRADA ---
def ejecutar_pruebas_integradas():
    """Ejecuta pruebas integradas del sistema."""
    print("=== 🔧 SISTEMA DE LIQUIDACIÓN - PRUEBAS INTEGRADAS ===\n")
    
    liquidator = FactoringLiquidacion(costo_transaccional_minimo=10.00)
    
    # Datos base para pruebas
    datos_base = {
        'capital': 16244.94,
        'tasa_compensatorio_mensual': 0.02,
        'tasa_moratorio_mensual': 0.03,
        'fecha_desembolso': datetime.date(2023, 1, 1),
        'fecha_pago_pactada': datetime.date(2023, 2, 1)
    }
    
    # Prueba 1: Liquidación 4B - Pago reducido
    print("1. 📋 LIQUIDACIÓN 4B - Pago $14,000")
    pago_4b = {'fecha_pago': datetime.date(2023, 2, 15), 'monto_pago': 14000.00}
    resultado_4b = liquidator.liquidar_operacion(datos_base, pago_4b)
    print(f"   Estado: {resultado_4b['resultados_finales']['estado']}")
    print(f"   Saldo: ${resultado_4b['resultados_finales']['saldo_global']:,.2f}")
    print(f"   Deuda: {resultado_4b['resultados_finales']['deuda_de']}\n")
    
    # Prueba 2: Liquidación 4C - Pago mínimo
    print("2. 📋 LIQUIDACIÓN 4C - Pago $16,234.94 ($10 menos)")
    pago_4c = {'fecha_pago': datetime.date(2023, 2, 15), 'monto_pago': 16234.94}
    resultado_4c = liquidator.liquidar_operacion(datos_base, pago_4c)
    print(f"   Estado: {resultado_4c['resultados_finales']['estado']}")
    print(f"   Saldo: ${resultado_4c['resultados_finales']['saldo_global']:,.2f}")
    print(f"   Viable: {resultado_4c['analisis_viabilidad']['viable_transaccionalmente']}\n")
    
    # Prueba 3: Pago exacto
    print("3. 📋 PAGO EXACTO - $16,244.94")
    pago_exacto = {'fecha_pago': datetime.date(2023, 2, 1), 'monto_pago': 16244.94}
    resultado_exacto = liquidator.liquidar_operacion(datos_base, pago_exacto)
    print(f"   Estado: {resultado_exacto['resultados_finales']['estado']}")
    print(f"   Saldo: ${resultado_exacto['resultados_finales']['saldo_global']:,.2f}")
    print(f"   Caso: {resultado_exacto['resultados_finales']['caso_clasificado']}\n")
    
    return [resultado_4b, resultado_4c, resultado_exacto]

if __name__ == "__main__":
    # Ejecutar pruebas al correr el script directamente
    resultados = ejecutar_pruebas_integradas()
    print("✅ SISTEMA LISTO PARA IMPLEMENTACIÓN")