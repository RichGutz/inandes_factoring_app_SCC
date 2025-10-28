# Flujo de Cálculo y Escenarios de Liquidación Universal

Este documento describe el pseudocódigo del proceso de liquidación de una operación de factoring, incluyendo la lógica del "Backdoor" para la condonación de saldos mínimos.

## Fase 1: Cálculo de Liquidación Normal

Esta es la base del cálculo. Determina la deuda total a una fecha de pago específica.

```
FUNCIÓN _liquidar_operacion_normal(operacion, fecha_pago, monto_pagado):

  // 1. Calcular Días
  dias_transcurridos = fecha_pago - fecha_desembolso_original
  dias_mora = fecha_pago - fecha_vencimiento_original (si es negativo, es 0)

  // 2. Calcular Intereses Devengados a la Fecha de Pago
  interes_compensatorio_devengado = calcular_interes(capital, tasa_mensual, dias_transcurridos)
  igv_interes_compensatorio = interes_compensatorio_devengado * 0.18

  // 3. Calcular Intereses Moratorios (si aplica)
  SI dias_mora > 0:
    interes_moratorio = calcular_interes(capital, tasa_moratoria_mensual, dias_mora)
    igv_moratorio = interes_moratorio * 0.18
  SINO:
    interes_moratorio = 0
    igv_moratorio = 0

  // 4. Calcular Deltas y Saldo Global
  //    (Diferencia entre lo provisionado originalmente y lo devengado ahora)
  delta_intereses = interes_compensatorio_devengado - interes_compensatorio_original
  delta_igv_intereses = igv_interes_compensatorio - igv_interes_original

  //    (CORRECCIÓN CLAVE: El capital pendiente se calcula contra el monto pagado)
  delta_capital = capital_original - monto_pagado

  //    (El saldo final es la suma de todos los componentes pendientes)
  saldo_global = delta_intereses + delta_igv_intereses + interes_moratorio + igv_moratorio + delta_capital

  // 5. Empaquetar y Retornar Resultado
  //    Este resultado incluye todos los cálculos, deltas, y un estado preliminar.
  //    Crucialmente, se inicializa con `back_door_aplicado = Falso`.
  RETORNAR resultado_liquidacion_normal

```

## Fase 2: Análisis de Escenarios y Aplicación de "Backdoor"

Aquí se toma el resultado del cálculo normal y se decide el camino a seguir.

```
FUNCIÓN liquidar_operacion_con_back_door(operacion, fecha_pago, monto_pagado, monto_minimo_backdoor):

  // 1. Obtener el cálculo base
  liquidacion_normal = _liquidar_operacion_normal(operacion, fecha_pago, monto_pagado)
  saldo_global = liquidacion_normal.saldo_global

  // --- INICIO DE ANÁLISIS DE ESCENARIOS ---

  // ESCENARIO 1: Pago en Exceso (Sobrepago)
  SI saldo_global < 0:
    estado_final = "Pagado con Excedente"
    accion = "Devolver el excedente (saldo_global) al cliente."
    RETORNAR liquidacion_normal (con el estado actualizado)

  // ESCENARIO 2: Pago Exacto
  SI saldo_global == 0:
    estado_final = "Pagado y Liquidado"
    accion = "Operación cerrada correctamente."
    RETORNAR liquidacion_normal (con el estado actualizado)

  // ESCENARIO 3: Pago Incompleto (Saldo Deudor)
  SI saldo_global > 0:

    // --- SUB-ESCENARIO 3.1: ¿Aplica el Backdoor? ---
    // CONDICIÓN A: El saldo pendiente es menor o igual al umbral definido.
    // CONDICIÓN B: No vale la pena perseguir la deuda (el saldo es menor al costo de cobranza).
    SI (saldo_global <= monto_minimo_backdoor) Y (saldo_global <= costo_transaccional):

      // ¡SE ACTIVA EL BACKDOOR!
      LLAMAR A _ejecutar_reduccion_secuencial(liquidacion_normal, saldo_global)
      // Esta función interna modificará la liquidación para:
      // - Poner `back_door_aplicado = Verdadero`
      // - Cambiar `estado_operacion` a "LIQUIDADO - BACK DOOR"
      // - Registrar las reducciones aplicadas.
      // - Poner el `saldo_global` final en 0 (o un valor residual mínimo).
      RETORNAR liquidacion_modificada_por_backdoor

    // --- SUB-ESCENARIO 3.2: No aplica Backdoor ---
    SINO:
      // La deuda es muy grande para ser condonada.
      estado_final = "Pago Parcial"
      accion = "Notificar al cliente sobre el saldo pendiente (saldo_global)."
      RETORNAR liquidacion_normal (con el estado actualizado)

```

## Fase 3: Ejecución de la Reducción Secuencial (Lógica del Backdoor)

Esta función se ejecuta solo si se activa el Backdoor. Su objetivo es "gastar" el saldo pendiente reduciéndolo de las deudas menos importantes primero.

```
FUNCIÓN _ejecutar_reduccion_secuencial(liquidacion, saldo_a_reducir):

  saldo_restante = saldo_a_reducir
  reducciones_aplicadas = []

  // 1. Reducir de Intereses Moratorios (y su IGV asociado)
  reduccion_posible = liquidacion.interes_moratorio
  monto_a_reducir = min(saldo_restante, reduccion_posible)
  SI monto_a_reducir > 0:
    liquidacion.interes_moratorio -= monto_a_reducir
    // (recalcular IGV moratorio)
    saldo_restante -= monto_a_reducir
    registrar_reduccion("moratorios", monto_a_reducir)

  // 2. Reducir de Intereses Compensatorios (y su IGV)
  SI saldo_restante > 0:
    reduccion_posible = liquidacion.delta_intereses
    monto_a_reducir = min(saldo_restante, reduccion_posible)
    SI monto_a_reducir > 0:
      liquidacion.delta_intereses -= monto_a_reducir
      // (recalcular IGV compensatorio)
      saldo_restante -= monto_a_reducir
      registrar_reduccion("compensatorios", monto_a_reducir)

  // 3. Reducir de Capital (Último recurso)
  SI saldo_restante > 0:
    reduccion_posible = liquidacion.delta_capital
    monto_a_reducir = min(saldo_restante, reduccion_posible)
    SI monto_a_reducir > 0:
      liquidacion.delta_capital -= monto_a_reducir
      saldo_restante -= monto_a_reducir
      registrar_reduccion("capital", monto_a_reducir)

  // Actualizar liquidación final
  liquidacion.saldo_global = saldo_restante // (debería ser casi 0)
  liquidacion.back_door_aplicado = Verdadero
  liquidacion.estado_operacion = "LIQUIDADO - BACK DOOR"
  liquidacion.reducciones_aplicadas = reducciones_aplicadas

  RETORNAR liquidacion
```
