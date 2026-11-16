TALLER 2 - PROGRAMACIÓN POR RESTRICCIONES
Ejercicio 1: Plantas de energía (problema de optimización)

REQUISITOS
  MiniZinc 2.9 o superior (paquete completo, que incluye Gecode, Chuffed y HiGHS).
  Probado con MiniZinc 2.9.3, Gecode 6.3.0 y HiGHS 1.9.0.
  La carpeta verificacion/ usa además Python 3.

ARCHIVOS
  PlantaEnergia.mzn          Modelo genérico (cualquier número de centrales, clientes y días).
  Datos.dzn                  Formato de entrada, con un ejemplo basado en el enunciado.
  tests/                     [Persona B] Las 10 instancias oficiales de pruebas.
  verificacion/verificar_optimo.py
                             Compara el óptimo de MiniZinc con un solucionador independiente
                             (programación dinámica escrita desde el enunciado) en instancias
                             pequeñas aleatorias.
  verificacion/generar_experimentos.py
                             Genera las instancias de verificacion/experimentos/.
  verificacion/experimentos/exp_01..12.dzn
                             Instancias para medir el efecto de cada elemento del modelo.
  verificacion/correr_experimentos.py
                             Corre esas instancias y guarda las estadísticas en un CSV.
  verificacion/resultados/   Estadísticas de esas corridas.

CÓMO EJECUTAR EL MODELO
  El modelo tiene dos parámetros de experimentación que se pasan con -D:
    impl      = qué implementación de las restricciones usar
    strategy  = qué estrategia de búsqueda usar

  minizinc --solver gecode -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"

  -s imprime las estadísticas (nodes, failures, peakDepth, solveTime, flatTime).
  La salida termina en "==========" cuando el solver demostró que la solución es óptima.
  En el MiniZinc IDE, al ejecutar se piden los valores de impl y strategy.

  Recomendado: impl=5 strategy=2.

  impl 1 = régimen alto (R4) con restricciones reificadas
  impl 2 = régimen alto (R4) con dos desigualdades lineales
  impl 3 = impl 2 + restricciones de dominancia RD1-RD4
  impl 4 = impl 3 + restricciones redundantes RR1 y RR2
  impl 5 = impl 4 + ruptura de simetrías RS1 y RS2
  strategy 1 = búsqueda por defecto del solver
  strategy 2 = orden de mérito: día por día, entregas a los clientes que más pagan y
               producción de las centrales más baratas, ambas con indomain_max
  strategy 3 = dom_w_deg / indomain_split

  Formato de datos (ver los comentarios de Datos.dzn):
    nPlantas, nombrePlanta, capacidad, costo, porcentajeAlto, diasAltoProhibidos
      (un valor por central, en el mismo orden);
    nClientes, nombreCliente, pago (un valor por cliente);
    nDias, demanda (una fila por cliente, una columna por día) y G.
  Todas las cantidades son enteras (MW enteros; costos y pagos por MW).

CÓMO REPETIR LA VERIFICACIÓN Y LOS EXPERIMENTOS (desde verificacion/)
  python3 verificar_optimo.py 400 2026              (impl 1-5 x strategy 1-3, instancias variadas)
  python3 verificar_optimo.py 300 77 dominancia     (impl 3 y 5, instancias con más capacidad)
  python3 generar_experimentos.py experimentos ../Datos.dzn
  python3 correr_experimentos.py resultados/ablacion_gecode.csv 1,2,3,4,5 2 experimentos/exp_0[1-9].dzn experimentos/exp_10.dzn
  python3 correr_experimentos.py resultados/grandes_gecode.csv 3,4,5 2 experimentos/exp_11.dzn experimentos/exp_12.dzn
  python3 correr_experimentos.py --solver=coin-bc resultados/referencia_coinbc.csv 5 1 experimentos/*.dzn
  python3 correr_experimentos.py --solver=highs resultados/referencia_highs.csv 5 1 experimentos/*.dzn
  python3 correr_experimentos.py --solver=highs resultados/dominancia_highs.csv 2,3 1 experimentos/exp_11.dzn experimentos/exp_12.dzn
  Con --solver=highs o --solver=coin-bc se exige brecha de optimalidad 0; esos solvers dan el óptimo
  de referencia para comparar las soluciones de Gecode.
