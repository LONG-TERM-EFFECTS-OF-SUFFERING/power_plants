TALLER 2 - PROGRAMACION POR RESTRICCIONES
Ejercicio 1: Plantas de energia 

CONTENIDO DE LA ENTREGA
  readme.txt                  Este archivo: contenido y comandos de ejecucion.
  informe.pdf                 Informe final, generado desde main.tex.
  PlantaEnergia.mzn           Modelo generico de optimizacion.
  Datos.dzn                   Formato de entrada y ejemplo del enunciado.
  tests/PlantaEnergia_01.dzn a tests/PlantaEnergia_10.dzn
                              Diez instancias de prueba.
  content/01-problem.tex a content/07-conclusions.tex
                              Secciones del informe en archivos LaTeX.
  main.tex, preamble.tex,
  front_page.tex              Archivos LaTeX de entrada, formato y portada.
  bibliography.bib            Referencias del informe.
  verificacion/verificar_optimo.py
                              Verificacion independiente del optimo en instancias pequenas.
  verificacion/generar_experimentos.py
                              Genera las instancias de experimentacion.
  verificacion/experimentos/exp_01.dzn a exp_12.dzn
                              Instancias para ablacion, estrategias y solvers.
  verificacion/correr_experimentos.py
                              Ejecutor comun de experimentos y exportacion CSV.
  results/PlantaEnergia_gecode_base.csv
  results/PlantaEnergia_highs.csv
                              Resultados sobre las diez instancias de prueba.
  verificacion/resultados/ablacion_gecode.csv
  verificacion/resultados/estrategias_gecode.csv
  verificacion/resultados/grandes_gecode.csv
  verificacion/resultados/dominancia_highs.csv
  verificacion/resultados/referencia_highs.csv
  verificacion/resultados/referencia_coinbc.csv
                              CSV de ablacion, busqueda y referencias de optimalidad.

REQUISITOS
  MiniZinc 2.9 o superior con Gecode, HiGHS y COIN-BC.
  Python 3 para los scripts de verificacion.
  Una distribucion LaTeX con latexmk, biber, apa7 y biblatex-apa para compilar el informe.

COMO EJECUTAR EL MODELO
  Ejecutar los comandos desde esta carpeta (scr/):

  minizinc --solver gecode -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"
  minizinc --solver highs  -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=1"

  El parametro impl selecciona la implementacion:
    1 = R4 reificada.
    2 = R4 lineal.
    3 = impl 2 mas dominancia RD1-RD4.
    4 = impl 3 mas restricciones redundantes RR1-RR2.
    5 = impl 4 mas ruptura de simetrias RS1-RS2.

  El parametro strategy selecciona la busqueda:
    1 = busqueda por defecto del solver.
    2 = orden de merito: entregas de mayor a menor pago y producciones de menor a
        mayor costo, con indomain_max; regimen alto con indomain_min.
    3 = dom_w_deg e indomain_split para entregas y producciones; regimen alto con
        indomain_min.

  Los parametros se pasan con -D. "----------" separa soluciones; solo "==========" al
  final indica que el solver termino y demostro el optimo.

COMO REPETIR LAS PRUEBAS
  Desde scr/, el siguiente comando ejecuta las diez instancias con las cinco
  implementaciones y las tres estrategias, con Gecode:

  python3 verificacion/correr_experimentos.py results/PlantaEnergia_gecode.csv 1,2,3,4,5 1,2,3 tests/*.dzn

  Para obtener la referencia de HiGHS sobre las diez instancias:

  python3 verificacion/correr_experimentos.py --solver=highs results/PlantaEnergia_highs.csv 5 1 tests/*.dzn

  El ejecutor impone brecha absoluta y relativa cero para HiGHS y COIN-BC. Registra
  el estado (optimo, sat, insat o timeout), la ganancia, los tiempos de compilacion
  y resolucion, los nodos, fallos y profundidad cuando el solver los reporta.

COMO REPETIR LOS EXPERIMENTOS DE LA BUSQUEDA
  Las cuatro instancias representativas usadas para comparar strategy=1, 2 y 3
  se ejecutan asi:

  python3 verificacion/correr_experimentos.py verificacion/resultados/estrategias_gecode.csv 5 1,2,3 verificacion/experimentos/exp_01.dzn verificacion/experimentos/exp_08.dzn verificacion/experimentos/exp_11.dzn verificacion/experimentos/exp_12.dzn

  Referencias exactas con los dos solvers MIP, sobre las doce instancias:

  python3 verificacion/correr_experimentos.py --solver=highs verificacion/resultados/referencia_highs.csv 5 1 verificacion/experimentos/*.dzn
  python3 verificacion/correr_experimentos.py --solver=coin-bc verificacion/resultados/referencia_coinbc.csv 5 1 verificacion/experimentos/*.dzn

  Los solvers MIP demuestran el optimo de referencia. Sus nodos no son comparables
  con los de Gecode.

COMPILAR EL INFORME
  Desde la carpeta raiz del proyecto:

  latexmk

  El PDF se genera en build/main.pdf. Para la entrega, copiarlo como informe.pdf
  junto con este archivo, PlantaEnergia.mzn, Datos.dzn y las diez instancias .dzn.
