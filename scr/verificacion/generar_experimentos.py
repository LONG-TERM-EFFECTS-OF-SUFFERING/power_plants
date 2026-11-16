"""Instancias para medir el efecto de cada elemento del modelo (impl 1 a 5).

No reemplazan las 10 instancias oficiales de pruebas (las genera la Persona B); sirven para
justificar en el informe la forma lineal de R4, la dominancia, las restricciones redundantes y
la ruptura de simetrías. Todas son reproducibles: cada familia usa su propia semilla.

  exp_01  Datos.dzn (copia): el ejemplo basado en el enunciado
  exp_02  Datos.dzn a escala 1/10 (dominios de decenas de MW)
  exp_03  capacidad escasa: el mínimo del 60 % es la restricción que manda
  exp_04  mediana: 3 centrales, 4 clientes, 7 días
  exp_05  mediana: 4 centrales, 5 clientes, 7 días
  exp_06  con simetrías: 4 centrales (2 idénticas), 4 clientes (2 idénticos)
  exp_07  con simetrías, otra semilla
  exp_08  con simetrías, otra semilla
  exp_09  diminuta: capacidades de 5 a 9 MW (para comparar R4 reificada y lineal sin dominancia)
  exp_10  diminuta, otra semilla
  exp_11  grande: 5 centrales, 8 clientes, 14 días
  exp_12  grande: 6 centrales, 12 clientes, 30 días

Uso: python3 generar_experimentos.py <carpeta de salida> <ruta de Datos.dzn>
"""
import os
import random
import shutil
import sys


def escribir(ruta, comentario, plantas, clientes, demanda, G):
    def arr(v): return "[" + ", ".join(str(x) for x in v) + "]"
    def txt(v): return "[" + ", ".join(f'"{x}"' for x in v) + "]"
    filas = "\n           | ".join(", ".join(f"{x:4d}" for x in fila) for fila in demanda)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"% {comentario}\n")
        f.write(f"nPlantas           = {len(plantas)};\n")
        f.write(f"nombrePlanta       = {txt([p[0] for p in plantas])};\n")
        f.write(f"capacidad          = {arr([p[1] for p in plantas])};\n")
        f.write(f"costo              = {arr([p[2] for p in plantas])};\n")
        f.write(f"porcentajeAlto     = {arr([p[3] for p in plantas])};\n")
        f.write(f"diasAltoProhibidos = {arr([p[4] for p in plantas])};\n")
        f.write(f"nClientes     = {len(clientes)};\n")
        f.write(f"nombreCliente = {txt([c[0] for c in clientes])};\n")
        f.write(f"pago          = {arr([c[1] for c in clientes])};\n")
        f.write(f"nDias   = {len(demanda[0])};\n")
        f.write(f"demanda = [| {filas} |];\n")
        f.write(f"G = {G};\n")


def aleatoria(rnd, P, S, n, rango_cap):
    """Instancia aleatoria con demandas proporcionales a la capacidad total."""
    caps = [rnd.randint(*rango_cap) for _ in range(P)]
    costo = [rnd.randint(5, 60) for _ in range(P)]
    pct = [rnd.choice([60, 70, 80]) for _ in range(P)]
    L = [rnd.randint(2, 3) for _ in range(P)]
    pago = [rnd.randint(20, 90) for _ in range(S)]
    total = sum(caps)
    dem = [[rnd.randint(total // (3 * S), int(1.3 * total / S)) for _ in range(n)] for _ in range(S)]
    return caps, costo, pct, L, pago, dem


def a_listas(caps, costo, pct, L, pago, dem):
    plantas = [(f"P{k + 1}", caps[k], costo[k], pct[k], L[k]) for k in range(len(caps))]
    clientes = [(f"S{s + 1}", pago[s]) for s in range(len(pago))]
    return plantas, clientes, dem


def main():
    out, datos = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    shutil.copy(datos, f"{out}/exp_01.dzn")

    # exp_02 y exp_03: variantes del ejemplo del enunciado.
    plantas = [("N", 100, 30, 80, 2), ("H", 30, 10, 80, 2), ("T", 50, 80, 80, 2)]
    clientes = [("S1", 70), ("S2", 90), ("S3", 55)]
    demanda = [[8, 11, 10, 12, 9], [15, 10, 20, 26, 34], [30, 25, 41, 28, 13]]
    escribir(f"{out}/exp_02.dzn", "exp_02: Datos.dzn a escala 1/10", plantas, clientes, demanda, 50)
    plantas3 = [("N", 40, 30, 80, 2), ("H", 30, 10, 70, 2), ("T", 20, 80, 90, 3)]
    escribir(f"{out}/exp_03.dzn", "exp_03: capacidad escasa; el mínimo del 60 % es la restricción activa",
             plantas3, clientes, demanda, 60)

    # exp_04 y exp_05: medianas (semilla 5).
    rnd = random.Random(5)
    for nombre, P, S, n, rango in (("exp_04", 3, 4, 7, (100, 400)), ("exp_05", 4, 5, 7, (100, 600))):
        escribir(f"{out}/{nombre}.dzn", f"{nombre}: mediana, {P} centrales, {S} clientes, {n} días (semilla 5)",
                 *a_listas(*aleatoria(rnd, P, S, n, rango)), 50)

    # exp_06 a exp_08: con una central y un cliente repetidos (semilla 21).
    rnd = random.Random(21)
    sim = []
    for _ in range(4):
        P, S, n = 3, 3, rnd.randint(4, 5)
        caps = [rnd.randint(40, 120) for _ in range(P)]
        costo = [rnd.randint(5, 60) for _ in range(P)]
        pct = [rnd.choice([60, 70, 80]) for _ in range(P)]
        L = [rnd.randint(2, 3) for _ in range(P)]
        pago = [rnd.randint(20, 90) for _ in range(S)]
        total = sum(caps) + caps[0]
        dem = [[rnd.randint(total // 8, total // 3) for _ in range(n)] for _ in range(S)]
        caps.append(caps[0]); costo.append(costo[0]); pct.append(pct[0]); L.append(L[0])
        pago.append(pago[0]); dem.append(list(dem[0]))
        sim.append((caps, costo, pct, L, pago, dem))
    for nombre, idx in (("exp_06", 1), ("exp_07", 3), ("exp_08", 0)):
        escribir(f"{out}/{nombre}.dzn",
                 f"{nombre}: con simetrías; P4 es idéntica a P1 y S4 es idéntico a S1 (semilla 21)",
                 *a_listas(*sim[idx]), 50)

    # exp_09 y exp_10: diminutas (semilla 8).
    rnd = random.Random(8)
    mini = []
    for _ in range(4):
        P, S, n = 3, 3, 4
        caps = [rnd.randint(5, 9) for _ in range(P)]
        costo = [rnd.randint(1, 12) for _ in range(P)]
        pct = [rnd.choice([50, 60, 70, 80]) for _ in range(P)]
        pago = [rnd.randint(2, 14) for _ in range(S)]
        dem = [[rnd.randint(2, 8) for _ in range(n)] for _ in range(S)]
        mini.append((caps, costo, pct, [2] * P, pago, dem))
    for nombre, idx in (("exp_09", 1), ("exp_10", 0)):
        escribir(f"{out}/{nombre}.dzn", f"{nombre}: diminuta, capacidades de 5 a 9 MW (semilla 8)",
                 *a_listas(*mini[idx]), 50)

    # exp_11 y exp_12: tamaño realista (semilla 4).
    rnd = random.Random(4)
    for nombre, nP, nC, nD in (("exp_11", 5, 8, 14), ("exp_12", 6, 12, 30)):
        ps = [(f"P{k + 1}", rnd.choice([300, 500, 800, 1000]), rnd.randint(10, 90),
               rnd.choice([70, 80, 90]), rnd.randint(2, 4)) for k in range(nP)]
        cs = [(f"S{s + 1}", rnd.randint(40, 120)) for s in range(nC)]
        cap_total = sum(p[1] for p in ps)
        dem = [[rnd.randint(30, int(1.6 * cap_total / nC)) for _ in range(nD)] for _ in range(nC)]
        escribir(f"{out}/{nombre}.dzn", f"{nombre}: grande, {nP} centrales, {nC} clientes, {nD} días (semilla 4)",
                 ps, cs, dem, 50)


if __name__ == "__main__":
    main()
