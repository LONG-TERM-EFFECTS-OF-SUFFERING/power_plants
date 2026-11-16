% =====================================================================
% Taller 2 - Programación por Restricciones
% Ejercicio 1: Plantas de energía (problema de optimización, COP)
% Autores: Brandon Calderón Prieto (2125974), Orlando Alexis Rengifo Mejia (2223878),
%          Santiago Nuñez Ramirez (2225625)
% Uso:     minizinc --solver gecode -s PlantaEnergia.mzn Datos.dzn -D "impl=5;strategy=2"
%
% Implementaciones (impl):
%   1 = R4 (definición del régimen alto) con restricciones reificadas: alto <-> p > umbral
%   2 = R4 con dos desigualdades lineales, sin reificación
%   3 = impl 2 + restricciones de dominancia RD1-RD4 (descartan soluciones que no pueden ser óptimas)
%   4 = impl 3 + redundantes RR1 (producción máxima por ventana) y RR2 (cota de la ganancia)
%   5 = impl 4 + ruptura de simetrías RS1 (centrales idénticas) y RS2 (clientes idénticos)
% Estrategias (strategy):
%   1 = búsqueda por defecto del solver (sin anotación)
%   2 = "orden de mérito": día por día, primero las entregas a los clientes que más pagan
%       (indomain_max) y luego la producción de las centrales más baratas (indomain_max)
%   3 = dom_w_deg / indomain_split sobre entregas y producción
% =====================================================================

include "globals.mzn";

% ---------------------------------------------------------------------
% 1. PARÁMETROS (vienen del .dzn; ver Datos.dzn)
% ---------------------------------------------------------------------
int: nPlantas;                                   % número de centrales
int: nClientes;                                  % número de clientes
int: nDias;                                      % horizonte de planificación (días)
set of int: PLANTAS  = 1..nPlantas;
set of int: CLIENTES = 1..nClientes;
set of int: DIAS     = 1..nDias;

array[PLANTAS] of string: nombrePlanta;          % solo para la salida (p. ej. "N", "H", "T")
array[PLANTAS] of int: capacidad;                % producción máxima diaria de cada central (MW)
array[PLANTAS] of int: costo;                    % costo de producir 1 MW en cada central
array[PLANTAS] of int: porcentajeAlto;           % régimen alto: producir más de este % de la capacidad
array[PLANTAS] of int: diasAltoProhibidos;       % se prohíbe estar este número de días seguidos en régimen alto

array[CLIENTES] of string: nombreCliente;        % solo para la salida (p. ej. "S1")
array[CLIENTES] of int: pago;                    % lo que paga cada cliente por 1 MW entregado
array[CLIENTES, DIAS] of int: demanda;           % demanda[s, i] = MW que pide el cliente s el día i
int: G;                                          % % mínimo de la demanda que se entrega a cada cliente cada día

% --- Parámetros derivados (se calculan de los datos; NO son variables) ---
% Umbral del régimen alto: producir más de umbral[k] MW es régimen alto.
% Como la producción es entera, p > porcentaje * capacidad / 100  <=>  p > (porcentaje * capacidad) div 100.
array[PLANTAS] of int: umbral = [ (porcentajeAlto[k] * capacidad[k]) div 100 | k in PLANTAS ];
% ¿Puede la central k estar alguna vez en régimen alto? (hay valores por encima del umbral
% y se permite al menos un día en régimen alto)
array[PLANTAS] of bool: puedeAlto = [ umbral[k] < capacidad[k] /\ diasAltoProhibidos[k] >= 2 | k in PLANTAS ];
% Entrega mínima: el G % de la demanda, redondeado hacia arriba (ceil(G * d / 100)).
array[CLIENTES, DIAS] of int: minimo = array2d(CLIENTES, DIAS,
  [ (G * demanda[s,i] + 99) div 100 | s in CLIENTES, i in DIAS ]);
% Producción máxima posible de cada central (si nunca puede estar en régimen alto, el umbral).
array[PLANTAS] of int: maxP = [ if puedeAlto[k] then capacidad[k] else min(umbral[k], capacidad[k]) endif
                              | k in PLANTAS ];
int: costoMin = min(costo);
% Órdenes útiles para la búsqueda: clientes de mayor a menor pago, centrales de menor a mayor costo.
array[CLIENTES] of CLIENTES: clientesPorPago = arg_sort([ -pago[s] | s in CLIENTES ]);
array[PLANTAS]  of PLANTAS:  plantasPorCosto = arg_sort(costo);

% --- Validación de los datos ---
constraint assert(nPlantas >= 1 /\ nClientes >= 1 /\ nDias >= 1,
  "Datos inválidos: debe haber al menos una central, un cliente y un día");
constraint assert(forall(k in PLANTAS)(capacidad[k] >= 0 /\ costo[k] >= 0),
  "Datos inválidos: capacidades y costos deben ser no negativos");
constraint assert(forall(k in PLANTAS)(porcentajeAlto[k] in 0..100 /\ diasAltoProhibidos[k] >= 1),
  "Datos inválidos: porcentajeAlto debe estar en 0..100 y diasAltoProhibidos debe ser al menos 1");
constraint assert(forall(s in CLIENTES)(pago[s] >= 0) /\ forall(s in CLIENTES, i in DIAS)(demanda[s,i] >= 0),
  "Datos inválidos: pagos y demandas deben ser no negativos");
constraint assert(G in 0..100, "Datos inválidos: G debe estar en 0..100");
% Aviso (no error): si en un día ni con todas las centrales al máximo se alcanza el mínimo,
% el problema no tiene solución y el solver lo reportará como UNSATISFIABLE.
constraint forall(i in DIAS)(
  if sum(s in CLIENTES)(minimo[s,i]) > sum(capacidad)
  then trace("Aviso: el día \(i) el mínimo exigido (\(sum(s in CLIENTES)(minimo[s,i])) MW) supera la capacidad total (\(sum(capacidad)) MW)\n")
  else true endif);

% ---------------------------------------------------------------------
% 2. PARÁMETROS DE EXPERIMENTACIÓN (se pasan con -D "impl=..;strategy=..")
% ---------------------------------------------------------------------
int: impl;
int: strategy;
constraint assert(impl in 1..5 /\ strategy in 1..3, "impl debe estar en 1..5 y strategy en 1..3");

% ---------------------------------------------------------------------
% 3. VARIABLES DE DECISIÓN (cada una con el dominio más ajustado que permiten los datos)
% ---------------------------------------------------------------------
% p[k, i] = MW que produce la central k el día i.
%           Si la central nunca puede estar en régimen alto, su máximo es el umbral.
array[PLANTAS, DIAS] of var int: p = array2d(PLANTAS, DIAS,
  [ let { var 0..maxP[k]: v } in v | k in PLANTAS, i in DIAS ]);
% e[s, i] = MW que se entregan al cliente s el día i: entre el G % de su demanda y su demanda.
array[CLIENTES, DIAS] of var int: e = array2d(CLIENTES, DIAS,
  [ let { var minimo[s,i]..demanda[s,i]: v } in v | s in CLIENTES, i in DIAS ]);
% alto[k, i] = 1 si la central k está en régimen alto el día i (p[k, i] > umbral[k]); 0 si no.
array[PLANTAS, DIAS] of var int: alto = array2d(PLANTAS, DIAS,
  [ let { var 0..bool2int(puedeAlto[k]): v } in v | k in PLANTAS, i in DIAS ]);

% Función objetivo: ganancia neta = pagos recibidos - costo de producción
var int: ganancia = sum(s in CLIENTES, i in DIAS)(pago[s] * e[s,i])
                  - sum(k in PLANTAS, i in DIAS)(costo[k] * p[k,i]);

% ---------------------------------------------------------------------
% 4. RESTRICCIONES DEL PROBLEMA
% ---------------------------------------------------------------------
% R1: balance diario. Toda la energía producida se entrega (la electricidad no se almacena).
constraint forall(i in DIAS)( sum(k in PLANTAS)(p[k,i]) = sum(s in CLIENTES)(e[s,i]) );

% R2: cada cliente recibe al menos el G % de su demanda (y nunca más que su demanda)
%     -> garantizada por el dominio de e.
% R3: ninguna central produce más que su capacidad -> garantizada por el dominio de p.

% R4: alto[k, i] = 1  <=>  p[k, i] > umbral[k]
constraint forall(k in PLANTAS, i in DIAS where puedeAlto[k])(
  if impl = 1 then
    alto[k,i] = bool2int(p[k,i] > umbral[k])                               % reificada
  else
       p[k,i] >= (umbral[k] + 1) * alto[k,i]                               % alto = 1 -> p > umbral
    /\ p[k,i] <= umbral[k] + (capacidad[k] - umbral[k]) * alto[k,i]        % alto = 0 -> p <= umbral
  endif);

% R5: se prohíbe estar diasAltoProhibidos[k] días seguidos en régimen alto:
%     en cada ventana de L = diasAltoProhibidos[k] días seguidos, a lo más L - 1 son de régimen alto.
constraint forall(k in PLANTAS where puedeAlto[k],
                  i in 1..nDias - diasAltoProhibidos[k] + 1)(
  sum(j in i..i + diasAltoProhibidos[k] - 1)(alto[k,j]) <= diasAltoProhibidos[k] - 1);

% ---------------------------------------------------------------------
% 5. RESTRICCIONES DE DOMINANCIA (impl >= 3)
% ---------------------------------------------------------------------
% No son redundantes: eliminan soluciones factibles. Pero solo eliminan soluciones que se pueden
% mejorar moviendo 1 MW, así que TODA solución óptima las cumple y el óptimo no cambia (ver informe).
% La central k está "saturada" el día i si no puede producir 1 MW más sin arriesgar el régimen alto:
% ya está en su máximo, o está justo en el umbral (1 MW más la pondría en régimen alto).
predicate saturada(int: k, int: i) =
  p[k,i] = maxP[k] \/ (puedeAlto[k] /\ p[k,i] = umbral[k]);

constraint if impl >= 3 then
     % RD1: si s paga más que s2, no puede s quedar sin completar mientras s2 recibe más del mínimo.
     forall(s, s2 in CLIENTES, i in DIAS where pago[s] > pago[s2])(
       e[s,i] = demanda[s,i] \/ e[s2,i] = minimo[s2,i])
     % RD2: si k es más barata que k2, no puede k2 producir mientras k tiene capacidad libre.
  /\ forall(k, k2 in PLANTAS, i in DIAS where costo[k] < costo[k2])(
       p[k2,i] = 0 \/ saturada(k, i))
     % RD3: si s paga más de lo que cuesta producir en k, no puede s quedar sin completar
     %      mientras k tiene capacidad libre.
  /\ forall(s in CLIENTES, k in PLANTAS, i in DIAS where pago[s] > costo[k])(
       e[s,i] = demanda[s,i] \/ saturada(k, i))
     % RD4: si s paga menos de lo que cuesta producir en k, no puede s recibir más del mínimo
     %      mientras k produce.
  /\ forall(s in CLIENTES, k in PLANTAS, i in DIAS where pago[s] < costo[k])(
       e[s,i] = minimo[s,i] \/ p[k,i] = 0)
else true endif;

% ---------------------------------------------------------------------
% 6. RESTRICCIONES REDUNDANTES (impl >= 4)
% ---------------------------------------------------------------------
% RR1: en cada ventana de L días seguidos, la central k produce a lo más
%      (L - 1) * capacidad + umbral (a lo más L - 1 días por encima del umbral).
constraint if impl >= 4 then
  forall(k in PLANTAS where puedeAlto[k], i in 1..nDias - diasAltoProhibidos[k] + 1)(
    sum(j in i..i + diasAltoProhibidos[k] - 1)(p[k,j])
      <= (diasAltoProhibidos[k] - 1) * capacidad[k] + umbral[k])
else true endif;

% RR2: cota superior de la ganancia. Cada MW entregado se produjo con costo >= costoMin, así que
%      ganancia <= suma de (pago - costoMin) * entregas.
constraint if impl >= 4 then
  ganancia <= sum(s in CLIENTES, i in DIAS)((pago[s] - costoMin) * e[s,i])
else true endif;

% ---------------------------------------------------------------------
% 7. RUPTURA DE SIMETRÍAS (impl = 5)
% ---------------------------------------------------------------------
% Dos centrales son idénticas si tienen la misma capacidad, costo, porcentaje y días prohibidos;
% dos clientes son idénticos si pagan lo mismo y tienen la misma demanda todos los días.
function bool: plantasIguales(int: a, int: b) =
  capacidad[a] = capacidad[b] /\ costo[a] = costo[b] /\
  porcentajeAlto[a] = porcentajeAlto[b] /\ diasAltoProhibidos[a] = diasAltoProhibidos[b];
function bool: clientesIguales(int: a, int: b) =
  pago[a] = pago[b] /\ forall(i in DIAS)(demanda[a,i] = demanda[b,i]);

% RS1: entre centrales idénticas, el plan de producción de la de menor índice es
%      lexicográficamente mayor o igual (se compara con la siguiente central idéntica).
constraint if impl = 5 then
  forall(a in PLANTAS, b in a+1..nPlantas
         where plantasIguales(a, b) /\ not exists(c in a+1..b-1)(plantasIguales(a, c)))(
    lex_greatereq([ p[a,i] | i in DIAS ], [ p[b,i] | i in DIAS ]))
else true endif;

% RS2: lo mismo para clientes idénticos y sus entregas.
constraint if impl = 5 then
  forall(a in CLIENTES, b in a+1..nClientes
         where clientesIguales(a, b) /\ not exists(c in a+1..b-1)(clientesIguales(a, c)))(
    lex_greatereq([ e[a,i] | i in DIAS ], [ e[b,i] | i in DIAS ]))
else true endif;

% ---------------------------------------------------------------------
% 8. FUNCIÓN OBJETIVO Y ESTRATEGIA DE BÚSQUEDA
% ---------------------------------------------------------------------
% Orden de mérito: día por día, entregas (mejor pago primero) y producción (menor costo primero).
array[int] of var int: varsMerito =
  [ v | i in DIAS,
        v in [ e[clientesPorPago[r], i] | r in CLIENTES ] ++ [ p[plantasPorCosto[r], i] | r in PLANTAS ] ];
array[int] of var int: todas = [ e[s,i] | s in CLIENTES, i in DIAS ] ++ [ p[k,i] | k in PLANTAS, i in DIAS ];
array[int] of var int: altos = [ alto[k,i] | k in PLANTAS, i in DIAS ];

solve :: if strategy = 2 then
           seq_search([ int_search(varsMerito, input_order, indomain_max),
                        int_search(altos, input_order, indomain_min) ])
         elseif strategy = 3 then
           seq_search([ int_search(todas, dom_w_deg, indomain_split),
                        int_search(altos, input_order, indomain_min) ])
         else
           seq_search([])        % estrategia 1: búsqueda por defecto del solver
         endif
      maximize ganancia;

% ---------------------------------------------------------------------
% 9. SALIDA
% ---------------------------------------------------------------------
function string: rellenar(string: t, int: n) = t ++ concat([ " " | j in 1..n - string_length(t) ]);
output ["impl=\(impl) strategy=\(strategy)\n",
        "ganancia = \(ganancia)\n\n",
        "Producción (MW; * = régimen alto)\n", rellenar("central", 10)] ++
       [ "  día " ++ show_int(2, i) | i in DIAS ] ++ ["\n"] ++
       [ if i = 1 then rellenar(nombrePlanta[k], 10) else "" endif
         ++ show_int(7, p[k,i]) ++ if fix(alto[k,i]) = 1 then "*" else " " endif
         ++ if i = nDias then "\n" else "" endif
       | k in PLANTAS, i in DIAS ] ++
       ["\nEntregas (MW entregados / MW pedidos)\n", rellenar("cliente", 10)] ++
       [ "      día " ++ show_int(2, i) | i in DIAS ] ++ ["\n"] ++
       [ if i = 1 then rellenar(nombreCliente[s], 10) else "" endif
         ++ show_int(6, e[s,i]) ++ "/" ++ show_int(-5, demanda[s,i])
         ++ if i = nDias then "\n" else "" endif
       | s in CLIENTES, i in DIAS ];
