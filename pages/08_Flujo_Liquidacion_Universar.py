import streamlit as st
from streamlit_mermaid import st_mermaid

st.set_page_config(
    page_title="Flujo de Liquidación Universal",
    page_icon="🌊",
    layout="wide"
)

st.title("Diagrama de Flujo del Proceso de Liquidación Universal")

st.info("Versión ultra-simplificada para evitar errores de sintaxis.")

mermaid_code = """graph TD
    A[Inicio] --> B{Calcular Liquidacion};
    B --> C[Saldo Calculado];
    C --> D{Saldo Menor a 0};
    D -- Si --> E[Estado: Excedente];
    D -- No --> F{Saldo Igual a 0};
    F -- Si --> G[Estado: Liquidado];
    F -- No --> H{Saldo Mayor a 0};
    H -- Si --> I{Aplica Backdoor};
    I -- Si --> J[Proceso: Reduccion Secuencial];
    J --> K[Estado: Liquidado por Backdoor];
    I -- No --> L[Estado: Pago Parcial];
    E --> Z[Fin];
    G --> Z[Fin];
    K --> Z[Fin];
    L --> Z[Fin];
"""

st_mermaid(mermaid_code, height="800px")
