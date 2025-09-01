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
    # ... (código de desembolso ya implementado)
    pass

# --- Routers ---
app.include_router(liquidaciones.router, prefix="/liquidaciones", tags=["liquidaciones"])

@app.post("/calcular_desembolso_lote")
async def calcular_desembolso_lote_endpoint(payload: List[Dict[str, Any]]):
    """
    Calcula el desembolso inicial para un lote de facturas.
    """
    try:
        result = procesar_lote_desembolso_inicial(payload)
        return {"resultados_por_factura": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/encontrar_tasa_lote")
async def encontrar_tasa_lote_endpoint(payload: List[Dict[str, Any]]):
    """
    Encuentra la tasa de avance para un lote de facturas dado un monto objetivo.
    """
    try:
        result = procesar_lote_encontrar_tasa(payload)
        return {"resultados_por_factura": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- Endpoints Antiguos / de Cálculo ---

# ... (resto de los endpoints sin cambios)
