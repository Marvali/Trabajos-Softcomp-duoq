# Unidades de resultados y ajuste de salida

## Problema
El algoritmo calculaba correctamente la potencia media anual, pero la salida se mostraba en MW. El profesor pedia comparar con energia anual en kWh (valores del orden de 10^7 kWh). Esa diferencia de unidades hacia parecer que los resultados eran demasiado bajos o altos.

## Causa
La funcion de evaluacion devuelve potencia media (MW):

- Se suma la potencia instantanea (kW) de las 8760 horas.
- Se divide entre 8760 para obtener potencia media (kW).
- Se convierte a MW.

Ese valor es correcto como potencia media, pero no es la energia anual requerida para la comparacion del enunciado.

## Solucion aplicada
Se mantuvo el calculo interno y solo se cambio el formato de salida y el grafico para mostrar energia anual en kWh:

- Formula usada: `energia_kwh = potencia_mw * 1000 * 8760`.
- La salida de rankings, progreso y resultado final muestra solo `kWh/yr`.
- El grafico ahora representa la mejor energia anual por iteracion.

Con esto los valores pasan a coincidir con los rangos esperados por el profesor.
