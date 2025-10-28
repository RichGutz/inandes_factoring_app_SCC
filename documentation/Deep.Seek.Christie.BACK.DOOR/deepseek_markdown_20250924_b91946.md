# SISTEMA BACKDOOR - LIQUIDACIONES

## 🎯 PROPÓSITO
Permitir cierre excepcional de liquidaciones mediante reducción escalonada de componentes.

## 🔐 AUTENTICACIÓN
- **Clave requerida**: `BACKDOOR_ACCESS`
- **Solo usuarios autorizados**
- **Registro de auditoría obligatorio**

## 🔄 SECUENCIA DE REDUCCIÓN
1. **Moratorios** → Intereses por mora
2. **Compensatorios** → Intereses compensatorios  
3. **Capital** → Capital remanente

## 📊 ESTADOS POST-BACKDOOR
- `LIQUIDADO_BACKDOOR`: Cierre excepcional aplicado
- **No genera** documentos tributarios (NC/ND)
- **Sí genera** registro contable interno

## ⚠️ RESTRICCIONES
- Aplicable solo a `LIQUIDACION_EN_PROCESO`
- Requiere justificación comercial
- Máximo 1 backdoor por liquidación