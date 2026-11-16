"""Verificación independiente de PlantaEnergia.mzn.

Resuelve instancias pequeñas por programación dinámica sobre los días, escrita directamente
desde el enunciado (no usa el modelo de MiniZinc), y compara la ganancia óptima con la que
obtiene MiniZinc para cada implementación (impl 1 a 5).

Programación dinámica:
  - Cada día se prueban todas las producciones posibles de cada central (0..capacidad).
  - Para una producción total T, la mejor entrega se obtiene dando a cada cliente su mínimo
    y repartiendo el resto a los clientes que más pagan (reparto voraz, óptimo para T fijo).
  - El estado es, por central, cuántos días seguidos lleva en régimen alto; un día más en
    régimen alto solo se permite si no completa los días prohibidos.

Uso: python3 verificar_optimo.py [número de instancias] [semilla] [modo]
  modo "general" (por defecto): instancias variadas, muchas infactibles; prueba impl 1-5 x strategy 1-3.
  modo "dominancia": casi todas factibles y con más capacidad, donde las restricciones de
  dominancia actúan más; prueba impl 3 (dominancia) e impl 5 (modelo completo), con las tres estrategias.
"""
import itertools
import os
import random
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor

MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "PlantaEnergia.mzn")


def minimo_entrega(G, d):
    """Menor entrega entera que es al menos el G % de d."""
    return -(-G * d // 100)


def es_alto(p, porcentaje, capacidad):
    """Régimen alto: producir más del porcentaje de la capacidad (comparación exacta)."""
    return 100 * p > porcentaje * capacidad


def resolver_dp(inst):
    P, S, n = inst["nPlantas"], inst["nClientes"], inst["nDias"]
    cap, costo, pct, L = inst["capacidad"], inst["costo"], inst["porcentajeAlto"], inst["diasAltoProhibidos"]
    pago, dem, G = inst["pago"], inst["demanda"], inst["G"]
    orden = sorted(range(S), key=lambda s: -pago[s])
    estados = {tuple([0] * P): 0}
    for i in range(n):
        mins = [minimo_entrega(G, dem[s][i]) for s in range(S)]
        lo, hi = sum(mins), sum(dem[s][i] for s in range(S))

        def ingreso(T):
            resto, total = T - lo, sum(pago[s] * mins[s] for s in range(S))
            for s in orden:
                extra = min(resto, dem[s][i] - mins[s])
                total += pago[s] * extra
                resto -= extra
            return total

        nuevos = {}
        for estado, valor in estados.items():
            for prod in itertools.product(*[range(c + 1) for c in cap]):
                T = sum(prod)
                if not lo <= T <= hi:
                    continue
                sig = []
                for k in range(P):
                    if es_alto(prod[k], pct[k], cap[k]):
                        if estado[k] + 1 >= L[k]:
                            break
                        sig.append(estado[k] + 1)
                    else:
                        sig.append(0)
                else:
                    v = valor + ingreso(T) - sum(costo[k] * prod[k] for k in range(P))
                    t = tuple(sig)
                    if v > nuevos.get(t, -10**18):
                        nuevos[t] = v
        estados = nuevos
        if not estados:
            return None
    return max(estados.values())


MODO = "general"


def instancia_aleatoria(rnd):
    P, S, n = rnd.randint(1, 3), rnd.randint(1, 3), rnd.randint(1, 4)
    inst = {
        "nPlantas": P, "nClientes": S, "nDias": n,
        "capacidad": [rnd.randint(0, 7) for _ in range(P)],
        "costo": [rnd.randint(0, 12) for _ in range(P)],
        "porcentajeAlto": [rnd.choice([0, 50, 60, 75, 80, 100]) for _ in range(P)],
        "diasAltoProhibidos": [rnd.randint(1, 4) for _ in range(P)],
        "pago": [rnd.randint(0, 12) for _ in range(S)],
        "demanda": [[rnd.randint(0, 7) for _ in range(n)] for _ in range(S)],
        "G": rnd.choice([0, 25, 50, 75, 100]),
    }
    if MODO == "dominancia":
        inst["G"] = rnd.choice([0, 0, 25, 50])
        inst["capacidad"] = [rnd.randint(3, 10) for _ in range(P)]
    # A veces se copian centrales o clientes, para probar la ruptura de simetrías y los empates.
    if P >= 2 and rnd.random() < 0.3:
        for key in ("capacidad", "costo", "porcentajeAlto", "diasAltoProhibidos"):
            inst[key][1] = inst[key][0]
    if S >= 2 and rnd.random() < 0.3:
        inst["pago"][1] = inst["pago"][0]
        inst["demanda"][1] = list(inst["demanda"][0])
    return inst


def a_dzn(inst):
    def arr(v): return "[" + ", ".join(str(x) for x in v) + "]"
    filas = " | ".join(", ".join(str(x) for x in fila) for fila in inst["demanda"])
    return "\n".join([
        f"nPlantas = {inst['nPlantas']};",
        "nombrePlanta = [" + ", ".join(f'"P{k + 1}"' for k in range(inst["nPlantas"])) + "];",
        f"capacidad = {arr(inst['capacidad'])};", f"costo = {arr(inst['costo'])};",
        f"porcentajeAlto = {arr(inst['porcentajeAlto'])};",
        f"diasAltoProhibidos = {arr(inst['diasAltoProhibidos'])};",
        f"nClientes = {inst['nClientes']};",
        "nombreCliente = [" + ", ".join(f'"S{s + 1}"' for s in range(inst["nClientes"])) + "];",
        f"pago = {arr(inst['pago'])};", f"nDias = {inst['nDias']};",
        f"demanda = [| {filas} |];", f"G = {inst['G']};", ""])


def resolver_minizinc(dzn_path, impl, strategy, solver="gecode"):
    out = subprocess.run(["minizinc", "--solver", solver, "--time-limit", "30000", MODELO, dzn_path,
                          "-D", f"impl={impl};strategy={strategy}"], capture_output=True, text=True).stdout
    if "=====UNSATISFIABLE=====" in out:
        return None, True
    valores = [int(l.split("=")[1]) for l in out.splitlines() if l.startswith("ganancia = ")]
    return (valores[-1] if valores else "sin respuesta"), ("==========" in out)


def probar(args):
    idx, inst = args
    esperado = resolver_dp(inst)
    with tempfile.NamedTemporaryFile("w", suffix=".dzn", delete=False) as f:
        f.write(a_dzn(inst))
        ruta = f.name
    errores = []
    combinaciones = ([(i, s) for i in (3, 5) for s in (1, 2, 3)] if MODO == "dominancia"
                     else [(i, s) for i in range(1, 6) for s in (1, 2, 3)])
    for impl, strategy in combinaciones:
        valor, probado = resolver_minizinc(ruta, impl, strategy)
        if valor != esperado or not probado:
            errores.append(f"impl={impl} strategy={strategy}: MiniZinc={valor} "
                           f"(óptimo probado: {probado}), programación dinámica={esperado}")
    os.unlink(ruta)
    return idx, inst, esperado, errores


def main():
    global MODO
    MODO = sys.argv[3] if len(sys.argv) > 3 else "general"
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rnd = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 2026)
    instancias = [(i, instancia_aleatoria(rnd)) for i in range(total)]
    infactibles = fallas = 0
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 2) as pool:
        for idx, inst, esperado, errores in pool.map(probar, instancias):
            infactibles += esperado is None
            if errores:
                fallas += 1
                print(f"Instancia {idx}: {inst}", flush=True)
                for e in errores:
                    print("   ", e, flush=True)
            if (idx + 1) % 25 == 0:
                print(f"... {idx + 1} instancias revisadas", flush=True)
    corridas = "impl 3 y 5 x strategy 1-3" if MODO == "dominancia" else "impl 1-5 x strategy 1-3"
    print(f"Modo {MODO}: {total} instancias ({infactibles} infactibles), corridas por instancia: "
          f"{corridas}; {fallas} instancias con diferencias")


if __name__ == "__main__":
    main()
