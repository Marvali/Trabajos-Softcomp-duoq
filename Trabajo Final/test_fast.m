clc; clear;

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CONFIGURACIÓN INICIAL
%
% Añadimos carpetas con:
%  - Funciones del profesor (f1, f2, fast, powerGen)
%  - Datos (.mat): curva de potencia + viento REAL (8760 horas)
%
% Usamos rutas relativas para que funcione en cualquier PC del grupo.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

addpath('windSym/utils');   % funciones
addpath('windSym/dt');      % datos (.mat)



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CARGAR EL VIENTO REAL DEL PROYECTO (IMPORTANTE)
%
% Este archivo contiene:
%
%       vVec   → matriz 2×8760
%
% vVec(:,h) = [vx ; vy] es el viento REAL en la hora h del año.
%
% Esto significa:
%   → ya no elegimos el viento manualmente
%   → el evaluador trabaja con 8760 horas reales
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

load('WindSym_1.mat');   % crea variable vVec



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% CREAR UN LAYOUT DE PRUEBA (20 TURBINAS)
%
% Usamos el mismo layout limpio del test de f1 y f2:
%
%   Cuadrícula de 4 filas × 5 columnas:
%     Filas:    3, 7, 11, 15
%     Columnas: 3, 6, 9, 12, 15
%
% Ventajas:
%  → Fácil de visualizar
%  → Perfecto para comprobar que todo el pipeline funciona
%
% NOTA: Esto NO es un layout optimizado, es solo un test.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

gr = zeros(20,20);
gr(3,  [3 6 9 12 15]) = 1;
gr(7,  [3 6 9 12 15]) = 1;
gr(11, [3 6 9 12 15]) = 1;
gr(15, [3 6 9 12 15]) = 1;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% EJECUTAR fast → EVALUADOR REAL DEL PROYECTO
%
% f_powerPlantsT_fast hace TODO esto:
%
%   1) Agrupa las horas por direcciones de viento únicas.
%   2) Para cada dirección única, llama a f1 UNA vez (optimización).
%   3) Para cada una de las 8760 horas:
%          - calcula Ux (viento efectivo por turbina)
%          - aplica la curva de potencia
%          - suma la potencia de todas las turbinas
%   4) Suma toda la potencia anual → pwr_T
%   5) Calcula la ganancia anual, coste y función objetivo.
%
% Resultado:
%   pwr_T  → potencia anual total (lo que queremos maximizar)
%   gan_T  → ganancia anual
%   cost_T → coste del parque (constante según nº turbinas)
%   obj_T  → cost / gan  (métrica original del profe → minimizar)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

[pwr_T, gan_T, cost_T, obj_T] = f_powerPlantsT_fast(vVec, gr);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% MOSTRAR RESULTADOS GLOBALES (ANUALES)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

fprintf('\n============================================\n');
fprintf('RESULTADOS DEL EVALUADOR FAST (ANUAL)\n');
fprintf('============================================\n');

fprintf('Potencia TOTAL anual generada = %.2f kW\n', pwr_T);
fprintf('Ganancia total anual          = %.2f €\n', gan_T);
fprintf('Coste del parque              = %.2f\n', cost_T);
fprintf('Valor función objetivo        = %.6f\n', obj_T);

fprintf([ ...
    '\nINTERPRETACIÓN:\n' ...
    ' - pwr_T es la métrica que usarás para comparar layouts (cuanto MÁS alto, mejor).\n' ...
    ' - obj_T es la métrica original del profesor (coste/ganancia): cuanto MENOR, mejor.\n' ...
    ' - Este resultado YA usa las 8760 horas del dataset real.\n' ...
    ' - Si esto funciona → tu pipeline completo también funcionará en el GA.\n' ...
]);
