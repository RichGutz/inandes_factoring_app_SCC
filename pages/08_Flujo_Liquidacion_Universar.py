import streamlit as st
from streamlit_mermaid import st_mermaid

st.set_page_config(
    page_title="Flujo de Liquidación Universal",
    page_icon="🌊",
    layout="wide"
)

st.title("Diagrama de Flujo del Proceso de Liquidación Universal")

mermaid_code = """graph TD
    A[Inicio: Liquidar Operación] --> B{Calcular Liquidación Normal};
    B --> C{saldo_global calculado};

    C --> D{saldo_global < 0 ?};
    D -- Sí (Excedente) --> E[Estado: Pagado con Excedente];

    D -- No --> F{saldo_global == 0 ?};
    F -- Sí (Exacto) --> G[Estado: Pagado y Liquidado];

    F -- No --> H{saldo_global > 0 ?};
    H -- Sí (Deuda) --> I{Aplica Backdoor? <br/> saldo_global <= monto_minimo <br/> Y <br/> saldo_global <= costo_cobranza};
    
    I -- Sí --> J[Proceso: Ejecutar Reducción Secuencial];
    J --> K[Estado: LIQUIDADO - BACK DOOR];

    I -- No --> L[Estado: Pago Parcial <br/> (Deuda es muy grande)];

    E --> Z[Fin];
    G --> Z[Fin];
    K --> Z[Fin];
    L --> Z[Fin];

    subgraph "Cálculo Base"
        B
    end

    subgraph "Análisis de Escenarios"
        C
        D
        F
        H
    end

    subgraph "Lógica de Condonación (Backdoor)"
        I
        J
    end

    subgraph "Resultados Finales"
        E
        G
        K
        L
    end
"""

st_mermaid(mermaid_code, height="800px")
