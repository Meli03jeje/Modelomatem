"""
Ejercicio 3 — Modelo Matemático de Asignación Binaria
Asignación óptima de 5 analistas a 5 operaciones (Bridger Compliance)
"""

from pulp import LpProblem, LpMinimize, LpVariable, lpSum, LpBinary, value, LpStatus

# ─────────────────────────────────────────────
# DATOS DEL PROBLEMA
# ─────────────────────────────────────────────

ANALISTAS = ["Andrea", "Beatriz", "Carlos", "Daniel", "Esteban"]
OPERACIONES = ["MT103", "MT202", "MT700", "MT760", "MT940"]

# Tiempos en minutos (None = celda bloqueada por compliance)
TIEMPOS = {
    ("Andrea",  "MT103"): 25,
    ("Andrea",  "MT202"): 30,
    ("Andrea",  "MT700"): None,   # LC — bloqueado
    ("Andrea",  "MT760"): None,   # Garantía — bloqueado
    ("Andrea",  "MT940"): 20,

    ("Beatriz", "MT103"): 35,
    ("Beatriz", "MT202"): 28,
    ("Beatriz", "MT700"): 40,
    ("Beatriz", "MT760"): 45,
    ("Beatriz", "MT940"): 22,

    ("Carlos",  "MT103"): 40,
    ("Carlos",  "MT202"): 45,
    ("Carlos",  "MT700"): 35,
    ("Carlos",  "MT760"): 30,
    ("Carlos",  "MT940"): 25,

    ("Daniel",  "MT103"): 30,
    ("Daniel",  "MT202"): 32,
    ("Daniel",  "MT700"): 50,
    ("Daniel",  "MT760"): None,   # Garantía — bloqueado
    ("Daniel",  "MT940"): 18,

    ("Esteban", "MT103"): None,   # Re-certificación — bloqueado
    ("Esteban", "MT202"): None,   # Re-certificación — bloqueado
    ("Esteban", "MT700"): 30,
    ("Esteban", "MT760"): 28,
    ("Esteban", "MT940"): 30,
}

# Celdas bloqueadas (compliance Bridger)
BLOQUEADAS = {(a, o) for (a, o), t in TIEMPOS.items() if t is None}


def resolver():
    """Resuelve el modelo de asignación binaria y retorna el resultado."""

    # ── Modelo ──────────────────────────────────
    prob = LpProblem("Asignacion_Analistas_Bridger", LpMinimize)

    # Variables binarias x[analista, operacion]
    x = {
        (a, o): LpVariable(f"x_{a[0]}_{o}", cat=LpBinary)
        for a in ANALISTAS
        for o in OPERACIONES
    }

    # ── Función objetivo ────────────────────────
    prob += lpSum(
        TIEMPOS[(a, o)] * x[(a, o)]
        for a in ANALISTAS
        for o in OPERACIONES
        if (a, o) not in BLOQUEADAS
    ), "Minimizar_Tiempo_Total"

    # ── Restricciones ───────────────────────────

    # 1. Cada operación debe ser asignada exactamente a 1 analista
    for o in OPERACIONES:
        prob += lpSum(x[(a, o)] for a in ANALISTAS) == 1, f"Op_{o}"

    # 2. Cada analista realiza exactamente 1 operación
    for a in ANALISTAS:
        prob += lpSum(x[(a, o)] for o in OPERACIONES) == 1, f"Analista_{a}"

    # 3. Compliance Bridger — celdas bloqueadas = 0
    for (a, o) in BLOQUEADAS:
        prob += x[(a, o)] == 0, f"Compliance_{a[0]}_{o}"

    # ── Resolver ────────────────────────────────
    prob.solve()

    # ── Extraer resultados ──────────────────────
    estado = LpStatus[prob.status]
    tiempo_total = value(prob.objective)

    asignaciones = []
    for a in ANALISTAS:
        for o in OPERACIONES:
            if value(x[(a, o)]) == 1:
                asignaciones.append({
                    "analista": a,
                    "operacion": o,
                    "tiempo": TIEMPOS[(a, o)],
                })

    return {
        "estado": estado,
        "tiempo_total": tiempo_total,
        "asignaciones": asignaciones,
        "variables": {(a, o): value(x[(a, o)]) for a in ANALISTAS for o in OPERACIONES},
    }


if __name__ == "__main__":
    res = resolver()
    print(f"\nEstado: {res['estado']}")
    print(f"Tiempo total mínimo: {res['tiempo_total']} minutos\n")
    print("Asignaciones óptimas:")
    for item in res["asignaciones"]:
        print(f"  {item['analista']:10s} → {item['operacion']}  ({item['tiempo']} min)")
