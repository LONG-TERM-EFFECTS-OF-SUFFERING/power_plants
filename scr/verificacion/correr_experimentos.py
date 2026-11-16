"""Corre PlantaEnergia.mzn con cada combinación instancia x impl x strategy y guarda un CSV.

Protocolo del Taller 1: Gecode, 60 s por corrida (incluida la compilación).
estado: optimo (óptimo demostrado), sat (solución sin demostrar que es óptima),
        insat (no hay solución), timeout (sin ninguna solución en el tiempo límite).
Uso: python3 correr_experimentos.py [--solver=<id>] <salida.csv> <impls> <estrategias> <dzn> [<dzn> ...]
     p. ej. python3 correr_experimentos.py exp.csv 1,2,3,4,5 1,2,3 experimentos/*.dzn
     Con un solver MIP (highs, coin-bc) se exige brecha de optimalidad 0 (--relGap 0 --absGap 0);
     los nodos que reportan los solvers MIP no son comparables con los de Gecode.
"""
import csv
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "PlantaEnergia.mzn")


def stat(salida, nombre):
    m = re.search(rf"^%%%mzn-stat: {nombre}=(\S+)", salida, re.M)
    return m.group(1) if m else ""


SOLVER = "gecode"
MIP = ("highs", "coin-bc", "cbc")


def correr(args):
    dzn, impl, strategy = args
    brecha = ["--relGap", "0", "--absGap", "0"] if SOLVER in MIP else []
    salida = subprocess.run(["minizinc", "--solver", SOLVER, "-s", "--time-limit", "60000", *brecha,
                             MODELO, dzn, "-D", f"impl={impl};strategy={strategy}"],
                            capture_output=True, text=True).stdout
    valores = re.findall(r"^ganancia = (-?\d+)", salida, re.M)
    if "=====UNSATISFIABLE=====" in salida:
        estado = "insat"
    elif "==========" in salida:
        estado = "optimo"
    elif valores:
        estado = "sat"
    else:
        estado = "timeout"
    return [os.path.basename(dzn).removesuffix(".dzn"), impl, strategy, SOLVER, estado,
            valores[-1] if valores else "", stat(salida, "flatTime"), stat(salida, "solveTime"),
            stat(salida, "nodes"), stat(salida, "failures"), stat(salida, "peakDepth")]


def main():
    global SOLVER
    args = sys.argv[1:]
    if args and args[0].startswith("--solver="):
        SOLVER = args.pop(0).split("=", 1)[1]
    salida, impls, estrategias, dzns = args[0], args[1].split(","), args[2].split(","), args[3:]
    trabajos = [(d, i, s) for d in dzns for i in impls for s in estrategias]
    with ThreadPoolExecutor(max_workers=2) as pool:
        filas = list(pool.map(correr, trabajos))
    with open(salida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["instancia", "impl", "estrategia", "solver", "estado", "ganancia",
                    "tiempo_compilacion_s", "tiempo_s", "nodos", "fallos", "profundidad"])
        w.writerows(filas)
    print(f"{len(filas)} corridas en {salida}")


if __name__ == "__main__":
    main()
