clc; clear;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONFIGURACIÓN INICIAL
%
% Añadimos carpetas con funciones y los datos (.mat).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath('windSym/utils');   % f1, f2, fast, powerGen...
addpath('windSym/dt');      % pwrCurve.mat, WindSym_1.mat



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CARGAR LA CURVA DE POTENCIA
%
% f2 NECESITA la curva de potencia del aerogenerador (ppPower),
% que está guardada en pwrCurve.mat.
%
% Esta curva convierte "velocidad del viento" -> "potencia en kW".
%
% Básicamente f2 hará:  pwr = powerGen(Ux, ppPower);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

load('pwrCurve.mat');   % crea variable ppPower en el workspace



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CREACIÓN DE UN LAYOUT DE PRUEBA (20 TURBINAS)
%
% Usamos el mismo layout que el test de f1 → 4 filas × 5 columnas:
%
% Filas:    3, 7, 11, 15
% Columnas: 3, 6, 9, 12, 15
%
% Total turbinas: 20
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

gr = zeros(20,20);
gr(3,  [3 6 9 12 15]) = 1;
gr(7,  [3 6 9 12 15]) = 1;
gr(11, [3 6 9 12 15]) = 1;
gr(15, [3 6 9 12 15]) = 1;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% NOTA IMPORTANTÍSIMA SOBRE EL VIENTO
%
% En ESTE test para f2 usamos un viento artificial que elegimos nosotros:
%
%       vVec_hour = [8 ; 0]
%
% Esto es solo para entender cómo funciona f2 de forma aislada.
%
% ─────────────────────────────────────────────────────────────────────────
% PERO EN EL TRABAJO REAL:
%   → NO elegimos la velocidad del viento
%   → NO definimos valores como [8;0], [1;0], etc.
%
% El viento REAL viene de:
%
%       windSym/dt/WindSym_1.mat
%
% Dentro está la variable:
%       vVec (2×8760)
%
% Cada columna es el viento REAL de una hora del año.
% La función f_powerPlantsT_fast usa AUTOMÁTICAMENTE esas 8760 horas.
%
% Este script solo usa viento inventado para comprobar el funcionamiento
% interno de f2 antes de meter el dataset real.
% ─────────────────────────────────────────────────────────────────────────
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

vVec_hour = [8 ; 0];   % viento fuerte hacia la derecha (solo para test)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CALCULAR rUDef CON f1
%
% f2 NECESITA rUDef para saber qué turbinas reciben wake.
%
% rUDef(i,j) > 0 → la turbina j está detrás de la turbina i (wake)
%
% rUDef afecta directamente a Ux (velocidad efectiva por turbina).
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

rUDef = f_powerPlants_f1(vVec_hour, gr);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EJECUTAR f2
%
% f_powerPlants_f2 devuelve:
%
%   pwr_t   → potencia total de TODAS las turbinas en esta hora
%   pwrGen  → potencia individual de cada turbina (vector 1×Nturb)
%   Ux      → viento efectivo por turbina (tras aplicar wakes)
%   gan     → ganancia económica en ESTA hora
%   cost    → coste total del parque (depende del nº de turbinas)
%   obj     → coste/ganancia (función objetivo original)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

[pwr_t, pwrGen, Ux, gan, cost, obj] = ...
    f_powerPlants_f2(vVec_hour, gr, ppPower, rUDef);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MOSTRAR RESULTADOS Y EXPLICARLOS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

disp('Velocidad efectiva Ux de cada turbina (m/s):');
disp(Ux);

disp('Potencia generada por cada turbina (kW):');
disp(pwrGen);
