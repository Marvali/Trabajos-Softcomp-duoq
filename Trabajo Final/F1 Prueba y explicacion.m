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
% DEFINIR EL VIENTO PARA LA PRUEBA
%
% f1 SOLO necesita un vector de viento (2x1), es decir:
%     [vx ; vy]
%
% Aquí usamos viento hacia la DERECHA:
%     [1 ; 0]
% Esto significa que una turbina estará en el wake de otra si está
% a la DERECHA de ella y dentro del cono de turbulencias.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

vVec_hour = [1; 0];   % viento hacia +X (derecha)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EJECUTAR f1 → DETECTAR WAKES
%
% f_powerPlants_f1 devuelve una matriz rUDef de tamaño:
%     número_de_turbinas × número_de_turbinas
%
% rUDef(i, j) = distancia proyectada entre turbina i → j si j está en el wake.
%  - Si rUDef(i,j) = 0  → No hay wake entre esas dos turbinas
%  - Si rUDef(i,j) > 0  → La turbina j está detrás de la turbina i (wake)
%
% Esta matriz NO tiene potencias ni velocidades, sólo geometría de wake.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

rUDef = f_powerPlants_f1(vVec_hour, gr);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MOSTRAR RESULTADOS
%
% La matriz rUDef nos muestra qué turbinas están detrás de otras.
% Si ves muchos ceros → las turbinas no están alineadas con el viento.
% Si ves valores positivos → f1 ha detectado wake.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

disp('Wake matrix rUDef (distancias proyectadas entre turbinas):');
disp(rUDef);
