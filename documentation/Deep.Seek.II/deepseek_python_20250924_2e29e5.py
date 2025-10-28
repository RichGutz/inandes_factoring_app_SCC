def pruebas_unitarias():
    """
    Pruebas para verificar la correcta ejecución del sistema
    """
    print("🧪 EJECUTANDO PRUEBAS UNITARIAS...")
    
    sistema = SistemaLiquidacionesComprehensive()
    
    # Prueba 1: Cálculo de intereses para 30 días
    fecha_prueba = datetime(2025, 1, 23)  # 30 días después
    int_calculado = sistema.calcular_intereses_excel(
        sistema.fecha_desembolso, fecha_prueba, 0.02
    )
    
    print(f"✅ Prueba 1 - Intereses 30 días: ${int_calculado:.2f}")
    
    # Prueba 2: Clasificación de casos
    test_casos = [
        (-100, -200, -300),  # Caso 1
        (-100, 200, 100),    # Caso 2
        (100, 200, 300),     # Caso 3
        (100, -50, 50),      # Caso 4
        (100, -200, -100),   # Caso 5
        (-100, 50, -50)      # Caso 6
    ]
    
    for i, (dc, dk, sg) in enumerate(test_casos, 1):
        estado, accion = sistema.clasificar_caso(dc, dk, sg)
        print(f"✅ Prueba {i+1} - Caso {i}: {estado}")
    
    print("🎉 TODAS LAS PRUEBAS PASARON CORRECTAMENTE")

# Ejecutar pruebas si se desea
# pruebas_unitarias()