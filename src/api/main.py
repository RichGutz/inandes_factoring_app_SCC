import sys
import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# --- Configuración de Path para Módulos ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from core.factoring_calculator import (
    calcular_desembolso_inicial,
    encontrar_tasa_de_avance,
    procesar_lote_desembolso_inicial,
    procesar_lote_encontrar_tasa
)
from data import supabase_repository as db
from data.supabase_repository import (
    get_or_create_desembolso_resumen,
    add_desembolso_evento,
    add_audit_event
)
from api.routers import liquidaciones

app = FastAPI(
    title="API de Calculadora de Factoring INANDES",
    description="Provee endpoints para los cálculos de factoring y gestión de operaciones.",
    version="3.1.0",
)

# --- Middleware de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Modelos de Datos (Pydantic) ---

class DesembolsoInfo(BaseModel):
    proposal_id: str
    monto_desembolsado: float
    fecha_desembolso_real: str # Format: DD-MM-YYYY

class DesembolsarLoteRequest(BaseModel):
    usuario_id: str
    desembolsos: List[DesembolsoInfo]

# --- Endpoints de Gestión de Estado ---

@app.post("/desembolsar_lote")
async def desembolsar_lote_endpoint(request: DesembolsarLoteRequest):
    results = []
    for desembolso_info in request.desembolsos:
        proposal_id = desembolso_info.proposal_id
        try:
            # Update status to DESEMBOLSADA
            db.update_proposal_status(proposal_id, 'DESEMBOLSADA')
            
            # Add audit event (assuming initial status was 'ACTIVO')
            db.add_audit_event(
                usuario_id=request.usuario_id,
                entidad_id=proposal_id,
                accion="DESEMBOLSO",
                estado_anterior="ACTIVO",
                estado_nuevo="DESEMBOLSADA",
                detalles_adicionales={"monto_desembolsado": desembolso_info.monto_desembolsado, "fecha_desembolso": desembolso_info.fecha_desembolso_real}
            )
            
            results.append({"proposal_id": proposal_id, "status": "SUCCESS", "message": "Estado actualizado a DESEMBOLSADA."})
        except Exception as e:
            results.append({"proposal_id": proposal_id, "status": "ERROR", "message": f"Error al actualizar estado: {e}"})
    
    return {"resultados_del_lote": results}

# --- Routers ---
app.include_router(liquidaciones.router, prefix="/liquidaciones", tags=["liquidaciones"])

@app.post("/calcular_desembolso_lote")
async def calcular_desembolso_lote_endpoint(payload: List[Dict[str, Any]]):
    """
    Calcula el desembolso inicial para un lote de facturas.
    """
    try:
        result = procesar_lote_desembolso_inicial(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/encontrar_tasa_lote")
async def encontrar_tasa_lote_endpoint(payload: List[Dict[str, Any]]):
    """
    Encuentra la tasa de avance para un lote de facturas dado un monto objetivo.
    """
    try:
        result = procesar_lote_encontrar_tasa(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Endpoints Antiguos / de Cálculo ---

@app.post("/get_projected_balance")
async def get_projected_balance_endpoint(request: GetProjectedBalanceRequest):
    try:
        # 1. Get proposal details to extract interest rates
        datos_operacion = db.get_proposal_details_by_id(request.proposal_id)
        if not datos_operacion:
            raise HTTPException(status_code=404, detail=f"Propuesta {request.proposal_id} no encontrada.")
        
        tasa_compensatoria_mensual = datos_operacion.get('interes_mensual', 0.0)
        tasa_moratoria_mensual = datos_operacion.get('interes_moratorio', 0.0) # Assuming this is monthly, adjust if annual

        # 2. Convert date string to datetime.date object
        try:
            fecha_inicio_proyeccion_date = datetime.strptime(request.fecha_inicio_proyeccion, '%Y-%m-%d').date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Formato de fecha_inicio_proyeccion inválido. Se espera YYYY-MM-DD.")

        # 3. Define projection days (e.g., 30 days for a monthly view)
        dias_proyeccion = 30 # Or a more dynamic value if needed

        # 4. Call the projection function from liquidation_calculator
        from core.liquidation_calculator import proyectar_saldo_diario # Import here to avoid circular dependency if needed
        
        proyeccion_futura = proyectar_saldo_diario(
            capital_inicial=request.initial_capital,
            fecha_inicio=fecha_inicio_proyeccion_date,
            tasa_compensatoria_mensual=tasa_compensatoria_mensual,
            tasa_moratoria_mensual=tasa_moratoria_mensual,
            dias_proyeccion=dias_proyeccion
        )
        
        return {"proyeccion_futura": proyeccion_futura}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor al proyectar saldo: {e}")

# --- Endpoints Antiguos / de Cálculo ---

# ... (resto de los endpoints sin cambios)
