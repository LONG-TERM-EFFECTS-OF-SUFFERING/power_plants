TALLER 2 - PROGRAMACIÓN POR RESTRICCIONES
Ejercicio 1: Plantas de energía (problema de optimización)

INTEGRANTES
  Brandon Calderón Prieto (2125974)
  Orlando Alexis Rengifo Mejia (2223878)
  Santiago Nuñez Ramirez (2225625)

CONTENIDO DE LA ENTREGA
  readme.txt                  Este archivo: contenido y comandos de ejecución.
  InformeTaller2.pdf          Informe del taller.
  PlantaEnergia.mzn           Modelo genérico (cualquier número de centrales, clientes y días).
  Datos.dzn                   Formato de entrada, con un ejemplo basado en el enunciado.
  tests/PlantaEnergia_01.dzn a tests/PlantaEnergia_10.dzn
                              Las diez instancias de prueba (sección Pruebas del informe).
  results/PlantaEnergia_gecode_base.csv
                              Las diez instancias con Gecode, impl 5 y strategy 2.
  results/PlantaEnergia_gecode_estrategias.csv
                              Las diez instancias con Gecode, impl 5 y strategy 1, 2 y 3.
  results/PlantaEnergia_highs.csv
                              Las diez instancias con HiGHS, impl 2 (óptimo de referencia).
  verificacion/verificar_optimo.py
                              Compara el óptimo de MiniZinc con un solucionador independiente
                              (programación dinámica escrita desde el enunciado) en instancias
                              pequeñas aleatorias.
  verificacion/generar_experimentos.py
                              Genera las instancias de verificacion/experimentos/.
  verificacion/experimentos/exp_01.dzn a exp_12.dzn
                              Instancias para medir el efecto de cada elemento del modelo y
                              comparar las estrategias y los solvers.
  verificacion/correr_experimentos.py
                              Corre el modelo con cada combinación instancia x impl x strategy
                              y guarda las estadísticas en un CSV.
  verificacion/resultados/ablacion_gecode.csv
  verificacion/resultados/grandes_gecode.csv
  verificacion/resultados/estrategias_gecode.csv
  verificacion/resultados/dominancia_highs.csv
  verificacion/resultados/referencia_highs.csv
  verificacion/resultados/referencia_coinbc.csv
                              Estadísticas de las corridas sobre exp_01 a exp_12: efecto de
                              cada elemento, estrategias y óptimos de referencia.

REQUISITOS
  MiniZinc 2.9 o superior (paquete completo, que incluye Gecode, HiGHS y COIN-BC).
  Probado con MiniZinc 2.9.3, Gecode 6.3.0, HiGHS 1.9.0 y COIN-BC 2.10.12.
  Python 3 para los scripts de verificacion/.

CÓMO EJECUTAR EL MODELO
  Los comandos se ejecutan desde esta carpeta. El modelo tiene dos parámetros de
  experimentación que se pasan con -D:
    impl      = qué implementación de las restricciones usar
    strategy  = qué estrategia de búsqueda usar

  minizinc --solver gecode -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"
  minizinc --solver highs  -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=1"

  -s imprime las estadísticas (nodes, failures, peakDepth, solveTime, flatTime).
  "----------" separa las soluciones; solo "==========" al final indica que el solver
  terminó y demostró que la última es óptima.
  En el MiniZinc IDE, al ejecutar se piden los valores de impl y strategy.

  Recomendado: impl=5 strategy=2.

  impl 1 = régimen alto (R4) con restricciones reificadas
  impl 2 = régimen alto (R4) con dos desigualdades lineales
  impl 3 = impl 2 + restricciones de dominancia RD1-RD4
  impl 4 = impl 3 + restricciones redundantes RR1 y RR2
  impl 5 = impl 4 + ruptura de simetrías RS1 y RS2
  strategy 1 = búsqueda por defecto del solver
  strategy 2 = orden de mérito: día por día, entregas de mayor a menor pago y producción
               de menor a mayor costo, con indomain_max; régimen alto con indomain_min
  strategy 3 = dom_w_deg e indomain_split sobre entregas y producción; régimen alto
               con indomain_min

  Formato de datos (ver los comentarios de Datos.dzn):
    nPlantas, nombrePlanta, capacidad, costo, porcentajeAlto, diasAltoProhibidos
      (un valor por central, en el mismo orden);
    nClientes, nombreCliente, pago (un valor por cliente);
    nDias, demanda (una fila por cliente, una columna por día) y G.
  Todas las cantidades son enteras (MW enteros; costos y pagos por MW).

CÓMO REPETIR LAS PRUEBAS (desde esta carpeta)
  correr_experimentos.py usa 60 s por corrida y, con HiGHS o COIN-BC, exige brecha de
  optimalidad 0. Registra el estado (optimo, sat, insat o timeout), la ganancia, los
  tiempos de compilación y de búsqueda, y los nodos, fallos y profundidad cuando el
  solver los reporta.

  python3 verificacion/correr_experimentos.py results/PlantaEnergia_gecode_base.csv 5 2 tests/*.dzn
  python3 verificacion/correr_experimentos.py results/PlantaEnergia_gecode_estrategias.csv 5 1,2,3 tests/*.dzn
  python3 verificacion/correr_experimentos.py --solver=highs results/PlantaEnergia_highs.csv 2 1 tests/*.dzn

CÓMO REPETIR LA VERIFICACIÓN Y LOS EXPERIMENTOS (desde verificacion/)
  python3 verificar_optimo.py 400 2026              (impl 1-5 x strategy 1-3, instancias variadas)
  python3 verificar_optimo.py 300 77 dominancia     (impl 3 y 5, instancias con más capacidad)
  python3 generar_experimentos.py experimentos ../Datos.dzn
  python3 correr_experimentos.py resultados/ablacion_gecode.csv 1,2,3,4,5 2 experimentos/exp_0[1-9].dzn experimentos/exp_10.dzn
  python3 correr_experimentos.py resultados/grandes_gecode.csv 3,4,5 2 experimentos/exp_11.dzn experimentos/exp_12.dzn
  python3 correr_experimentos.py resultados/estrategias_gecode.csv 5 1,2,3 experimentos/exp_01.dzn experimentos/exp_08.dzn experimentos/exp_11.dzn experimentos/exp_12.dzn
  python3 correr_experimentos.py --solver=highs resultados/referencia_highs.csv 5 1 experimentos/*.dzn
  python3 correr_experimentos.py --solver=coin-bc resultados/referencia_coinbc.csv 5 1 experimentos/*.dzn
  python3 correr_experimentos.py --solver=highs resultados/dominancia_highs.csv 2,3 1 experimentos/exp_11.dzn experimentos/exp_12.dzn

  Los solvers MIP dan el óptimo de referencia; sus nodos no son comparables con los de
  Gecode. Los tiempos, y los nodos y la ganancia de las corridas que llegan al límite,
  dependen del equipo.
