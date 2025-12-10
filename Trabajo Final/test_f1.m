clc; clear;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONFIGURACIÓN INICIAL
%
% Añadimos las carpetas donde están:
%  - Las funciones del profesor (f1, f2, fast, powerGen)
%  - Los .mat con la curva de potencia y el viento anual
%
% Usamos rutas RELATIVAS para que funcione también en el PC de mi compañero.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath('windSym/utils');   % funciones
addpath('windSym/dt');      % datos (.mat)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CREACIÓN DE UN LAYOUT DE PRUEBA (20 TURBINAS)
%
% Vamos a crear un layout fijo y "limpio" para entender cómo devuelve wakes
% la función f_powerPlants_f1.
%
% Este layout es una *cuadrícula regular* de 4 filas × 5 columnas:
%
%   Filas:    3, 7, 11, 15
%   Columnas: 3, 6, 9, 12, 15
%
% Total turbinas = 4 × 5 = 20 turbinas.
%
% Ventaja de este layout:
%  → Es MUY fácil visualizar dónde están las turbinas.
%  → Es ideal para comprobar cómo f1 detecta qué turbinas están detrás de otras.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

gr = zeros(20,20);   % mapa 20x20 vacío (0 = no hay turbina)

% Colocamos turbinas "a mano" sin bucles, para que quede visual:
gr(3,  [3 6 9 12 15]) = 1;   % primera fila de turbinas
gr(7,  [3 6 9 12 15]) = 1;   % segunda fila
gr(11, [3 6 9 12 15]) = 1;   % tercera fila
gr(15, [3 6 9 12 15]) = 1;   % cuarta fila



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% NOTA IMPORTANTÍSIMA SOBRE EL VIENTO
%
% En este test de f1 usamos un viento artificial muy simple:
%       [1 ; 0]  → viento hacia la DERECHA
%
% Esto lo hacemos SOLO para comprobar visualmente que f1 detecta
% wakes cuando las turbinas están alineadas con la dirección del viento.
%
% PERO EN EL TRABAJO REAL:
%   → NO elegimos la velocidad del viento
%   → NO ponemos valores manuales como [8;0] o [1;0]
%
% El viento REAL del proyecto viene en el archivo del profesor:
%
%       windSym/dt/WindSym_1.mat
%
% Dentro está la variable:
%       vVec  (2×8760)
%
% Cada columna de vVec es el viento REAL de esa hora del año.
% El evaluador final f_powerPlantsT_fast usa AUTOMÁTICAMENTE
% todo ese viento real para calcular la potencia anual.
%
% Este script solo usa viento simplificado para entender f1.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

vVec_hour = [1; 0];   % viento hacia +X (derecha)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EJECUTAR f1 → DETECTAR WAKES
%
% f_powerPlants_f1 devuelve una matriz rUDef de tamaño:
%     número_de_turbinas × número_de_turbinas
%
% rUDef(i, j) = distancia proyectada entre turbina i → j si j está en el wake.
%
% Interpretación:
%  - rUDef(i,j) = 0     → la turbina j NO está detrás de i (no hay wake)
%  - rUDef(i,j) > 0     → la turbina j SÍ está en el wake de i
%
% OJO: f1 NO calcula potencias. Solo geometría de "quién molesta a quién".
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

rUDef = f_powerPlants_f1(vVec_hour, gr);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MOSTRAR RESULTADOS
%
% La matriz rUDef nos muestra qué turbinas están detrás de otras para ESTE
% viento concreto. Si ves muchos ceros:
%
%    → las turbinas NO están alineadas con la dirección del viento.
%
% Si ves valores positivos:
%
%    → f1 ha detectado que una turbina está "aguas abajo" de otra.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

disp('Wake matrix rUDef (distancias proyectadas entre turbinas):');
disp(rUDef);
