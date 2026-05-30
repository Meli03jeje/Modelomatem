"""
app.py — Streamlit App: Ejercicio 3 Modelo Matemático Bridger
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from modelo import resolver, ANALISTAS, OPERACIONES, TIEMPOS, BLOQUEADAS

# ─────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Ejercicio 3 — Asignación Bridger",
    page_icon="📊",
    layout="wide",
)

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title  { font-size: 2.2rem; font-weight: 800; color: #1a3a6b; margin-bottom: 0; }
    .sub-title   { font-size: 1rem; color: #6b7280; margin-top: 0; }
    .metric-box  { background: #1a3a6b; color: white; border-radius: 12px;
                   padding: 1.2rem 1.6rem; text-align: center; }
    .metric-val  { font-size: 2.4rem; font-weight: 800; }
    .metric-lbl  { font-size: 0.85rem; opacity: 0.85; }
    .badge-opt   { background: #16a34a; color: white; border-radius: 6px;
                   padding: 2px 10px; font-size: 0.85rem; font-weight: 600; }
    .badge-inf   { background: #dc2626; color: white; border-radius: 6px;
                   padding: 2px 10px; font-size: 0.85rem; font-weight: 600; }
    .section-hdr { font-size: 1.15rem; font-weight: 700; color: #1a3a6b;
                   border-left: 4px solid #e63946; padding-left: 10px; margin: 1.2rem 0 0.6rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ENCABEZADO
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">📊 Ejercicio 3 — Modelo Matemático</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Asignación óptima de analistas a operaciones · Compliance Bridger · Programación Binaria</p>', unsafe_allow_html=True)
st.divider()

# ─────────────────────────────────────────────
# TABLA DE TIEMPOS (input visual)
# ─────────────────────────────────────────────
st.markdown('<p class="section-hdr">Tiempos en minutos · 5 analistas × 5 operaciones = 25 variables binarias</p>', unsafe_allow_html=True)

# Construir DataFrame para mostrar
tabla = {}
for a in ANALISTAS:
    fila = {}
    for o in OPERACIONES:
        if (a, o) in BLOQUEADAS:
            fila[o] = "🚫"
        else:
            fila[o] = TIEMPOS[(a, o)]
    tabla[a] = fila

df_tiempos = pd.DataFrame(tabla).T
df_tiempos.index.name = "Analista"

st.dataframe(
    df_tiempos.style
    .map(lambda v: "background-color:#fde8e8; color:#9b1c1c;" if v == "🚫" else "")
    .set_properties(**{"text-align": "center", "font-weight": "600"}),
    use_container_width=True,
    height=230,
)

# ─────────────────────────────────────────────
# RESTRICCIONES DE COMPLIANCE
# ─────────────────────────────────────────────
with st.expander("⚖️ Restricciones de compliance Bridger", expanded=False):
    st.markdown("""
| Analista | Operación bloqueada | Motivo |
|----------|---------------------|--------|
| Andrea   | MT700               | LC (Carta de Crédito) |
| Andrea   | MT760   | Garantía |
| Daniel   | MT760   | Garantía |
| Esteban  | MT103   | Re-certificación |
| Esteban  | MT202   | Re-certificación |
    """)

# ─────────────────────────────────────────────
# BOTÓN RESOLVER
# ─────────────────────────────────────────────
st.markdown('<p class="section-hdr">Solución del modelo</p>', unsafe_allow_html=True)

if st.button("▶️ Resolver modelo", type="primary", use_container_width=False):
    with st.spinner("Resolviendo con PuLP (Branch & Bound)..."):
        resultado = resolver()

    estado = resultado["estado"]
    tiempo_total = resultado["tiempo_total"]
    asignaciones = resultado["asignaciones"]

    # ── Estado ──
    col_e, col_t, col_v = st.columns([1, 1, 1])
    badge = "badge-opt" if estado == "Optimal" else "badge-inf"
    label = "✅ Solución Óptima" if estado == "Optimal" else f"❌ {estado}"
    with col_e:
        st.markdown(f'<div class="metric-box"><div class="metric-val"><span class="{badge}">{label}</span></div><div class="metric-lbl">Estado del solver</div></div>', unsafe_allow_html=True)
    with col_t:
        st.markdown(f'<div class="metric-box"><div class="metric-val">{int(tiempo_total)} min</div><div class="metric-lbl">Tiempo total mínimo</div></div>', unsafe_allow_html=True)
    with col_v:
        st.markdown(f'<div class="metric-box"><div class="metric-val">25</div><div class="metric-lbl">Variables binarias</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # ── Tabla de asignaciones ──
    st.markdown('<p class="section-hdr">Asignaciones óptimas</p>', unsafe_allow_html=True)
    df_asig = pd.DataFrame(asignaciones).rename(columns={
        "analista": "Analista", "operacion": "Operación", "tiempo": "Tiempo (min)"
    })
    st.dataframe(df_asig, use_container_width=True, hide_index=True)

    # ── Heatmap de variables ──
    st.markdown('<p class="section-hdr">Mapa de asignación (variables x = 1)</p>', unsafe_allow_html=True)

    z = []
    text = []
    for a in ANALISTAS:
        fila_z, fila_t = [], []
        for o in OPERACIONES:
            val = resultado["variables"].get((a, o), 0)
            fila_z.append(val if val is not None else 0)
            if (a, o) in BLOQUEADAS:
                fila_t.append("🚫")
            elif val == 1:
                fila_t.append(f"✅ {TIEMPOS[(a,o)]} min")
            else:
                fila_t.append(f"{TIEMPOS[(a,o)]} min")
        z.append(fila_z)
        text.append(fila_t)

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=OPERACIONES,
        y=ANALISTAS,
        text=text,
        texttemplate="%{text}",
        colorscale=[[0, "#f0f4ff"], [1, "#1a3a6b"]],
        showscale=False,
        hoverongaps=False,
    ))
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        font=dict(family="monospace"),
        xaxis=dict(side="top"),
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Fórmula objetivo expandida ──
    st.markdown('<p class="section-hdr">Función objetivo (términos activos)</p>', unsafe_allow_html=True)
    terminos = " + ".join([f"{item['tiempo']}·x{item['analista'][0]}{OPERACIONES.index(item['operacion'])+1}" for item in asignaciones])
    st.code(f"Min Z = {terminos}\n      = {int(tiempo_total)} minutos", language="text")

else:
    st.info("Haz clic en **▶️ Resolver modelo** para ejecutar el solver.")

# ─────────────────────────────────────────────
# MODELO MATEMÁTICO RESUMIDO
# ─────────────────────────────────────────────
with st.expander("📐 Ver modelo matemático completo", expanded=False):
    st.markdown("""
**Variables:** $x_{ij} \\in \\{0,1\\}$ — 1 si el analista $i$ realiza la operación $j$

**Función objetivo:**
$$\\text{Min } Z = \\sum_{i=1}^{5}\\sum_{j=1}^{5} c_{ij} \\cdot x_{ij}$$

**Restricciones:**

- Cada operación tiene exactamente 1 analista:
$$\\sum_{i} x_{ij} = 1 \\quad \\forall j$$

- Cada analista realiza exactamente 1 operación:
$$\\sum_{j} x_{ij} = 1 \\quad \\forall i$$

- Compliance Bridger (celdas bloqueadas):
$$x_{A,MT700} = x_{A,MT760} = x_{D,MT760} = x_{E,MT103} = x_{E,MT202} = 0$$
    """)

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.divider()
st.caption("Ejercicio 3 · Programación Binaria · Solver: PuLP + CBC · Visualización: Streamlit + Plotly")
