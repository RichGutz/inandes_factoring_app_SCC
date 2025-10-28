class LiquidacionBackdoorSystem:
    def __init__(self):
        self.BACKDOOR_ACCESS_KEY = "BACKDOOR_2025_INANDES"
        self.auditoria = []
    
    def autenticar_backdoor(self, clave_usuario):
        return clave_usuario == self.BACKDOOR_ACCESS_KEY
    
    def aplicar_backdoor(self, liquidacion, clave_usuario):
        if not self.autenticar_backdoor(clave_usuario):
            return {"error": "Clave de backdoor no válida"}
        
        if liquidacion['estado'] != 'LIQUIDACION_EN_PROCESO':
            return {"error": "Solo aplicable a liquidaciones en proceso"}
        
        saldo_actual = liquidacion['saldo_global']
        if saldo_actual == 0:
            return {"error": "Saldo ya es cero"}
        
        historial = []
        componentes = ['moratorios', 'compensatorios', 'capital_remanente']
        
        # Reducción en cascada
        for componente in componentes:
            if saldo_actual <= 0:
                break
                
            valor_componente = liquidacion.get(componente, 0)
            if valor_componente > 0:
                reduccion = min(valor_componente, saldo_actual)
                liquidacion[componente] -= reduccion
                saldo_actual -= reduccion
                historial.append(f"{componente}: -{reduccion:.2f}")
        
        liquidacion['saldo_global'] = 0
        liquidacion['estado'] = 'LIQUIDADO_BACKDOOR'
        liquidacion['backdoor_aplicado'] = True
        liquidacion['fecha_backdoor'] = '2025-04-07'  # Timestamp actual
        
        # Auditoría
        self.auditoria.append({
            'liquidacion_id': liquidacion['id'],
            'accion': 'BACKDOOR_APLICADO',
            'saldo_anterior': saldo_actual,
            'historial': historial,
            'usuario': 'USER_BACKDOOR'
        })
        
        return {
            'estado': 'BACKDOOR_APLICADO_EXITOSO',
            'saldo_final': 0,
            'historial_reduccion': historial,
            'liquidacion_actualizada': liquidacion
        }

# EJEMPLO DE USO
sistema = LiquidacionBackdoorSystem()

liquidacion_ejemplo = {
    'id': 'LQ-003',
    'estado': 'LIQUIDACION_EN_PROCESO',
    'saldo_global': 80.09,
    'moratorios': 53.52,
    'compensatorios': 38.08,
    'capital_remanente': 17822.00
}

resultado = sistema.aplicar_backdoor(liquidacion_ejemplo, "BACKDOOR_2025_INANDES")
print(resultado)