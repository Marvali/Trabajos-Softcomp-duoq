function ffast_hardcoded_con_comparativa()
clc;

addpath('windSym/utils');   
addpath('windSym/dt');

load('WindSym_1.mat');

layouts = struct();
idx = 0;

% --------------------------------------------------------
% UMBRAL DEL PROFESOR
% --------------------------------------------------------
P_profesor_MW  = 5.28;
P_profesor_kW  = P_profesor_MW * 1000;
E_profesor_GWh = P_profesor_kW * 8760 / 1e6;

% --------------------------------------------------------
% TECHO TEÓRICO DEL PARQUE (20 turbinas × 1.2 MW máx)
% --------------------------------------------------------
P_teorico_MW = 20 * 1.2;            % 24 MW
P_teorico_kW = P_teorico_MW * 1000;

fprintf('\n============================================\n');
fprintf('   EVALUACIÓN COMPLETA DE LAYOUTS (FAST)\n');
fprintf('============================================\n');


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 1) LAYOUTS BUENOS (20 turbinas exactas)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

idx = idx+1;
S1=zeros(20,20);
S1(4,[4 7 10 13 16])=1;
S1(7,[5 8 11 14 17])=1;
S1(10,[4 7 10 13 16])=1;
S1(13,[5 8 11 14 17])=1;
layouts(idx).name="Shakoor (2015)";
layouts(idx).grid=S1;

idx = idx+1;
G=zeros(20,20);
G(4,[3 5 7 9 11])=1;
G(9,[4 6 8 10 12])=1;
G(14,[3 5 7 9 11])=1;
G(18,[4 6 8 10 12])=1;
layouts(idx).name="Grady (2005)";
layouts(idx).grid=G;

idx = idx+1;
M=zeros(20,20);
M(3,[4 7 10 13 16])=1;
M(7,[3 7 11 15 19])=1;
M(11,[4 8 12 16 20])=1;
M(15,[5 9 13 17 20])=1;
layouts(idx).name="Mosetti (1994)";
layouts(idx).grid=M;

idx = idx+1;
MM=zeros(20,20);
MM(3,[4 7 10 13 16])=1;
MM(8,[5 8 11 14 17])=1;
MM(12,[4 7 10 13 16])=1;
MM(16,[5 8 11 14 17])=1;
layouts(idx).name="Marmidis (2008)";
layouts(idx).grid=MM;

idx = idx+1;
T=zeros(20,20);
T(4,3:2:17)=1;
T(10,3:2:17)=1;
T(16,[5 9 13 17])=1;
layouts(idx).name="Turner (2005)";
layouts(idx).grid=T;

idx = idx+1;
R=zeros(20,20);
R([5 7 9],[3 6 9 12 15 18])=1;
R(12,[4 8])=1;
layouts(idx).name="Rahmani (2010)";
layouts(idx).grid=R;

idx = idx+1;
E=zeros(20,20);
E(4,[4 8 12 16])=1;
E(8,[5 10 15])=1;
E(12,[4 8 12 16])=1;
E(16,[5 10 15])=1;
E(6,[4 8 12 16])=1;
E(14,[6 10])=1;
layouts(idx).name="Emami (2010)";
layouts(idx).grid=E;

idx = idx+1;
S2=zeros(20,20);
S2(4,3:2:17)=1;
S2(10,3:2:17)=1;
S2(16,[5 9 13 17])=1;
layouts(idx).name="Serrano (2010)";
layouts(idx).grid=S2;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 2) LAYOUTS MALOS
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

idx = idx+1;
B1=zeros(20,20); B1(3,1:20)=1;
layouts(idx).name="BAD #1 — fila compacta";
layouts(idx).grid=B1;

idx = idx+1;
B2=zeros(20,20); B2(:,10)=1;
layouts(idx).name="BAD #2 — columna vertical";
layouts(idx).grid=B2;

idx = idx+1;
B3=zeros(20,20); B3(3:6,3:7)=1;
layouts(idx).name="BAD #3 — bloque 4x5";
layouts(idx).grid=B3;

idx = idx+1;
B4=zeros(20,20);
B4(1:10,7)=1; B4(1:10,9)=1;
layouts(idx).name="BAD #4 — columnas paralelas";
layouts(idx).grid=B4;

idx = idx+1;
B5=zeros(20,20);
pos=[ ...
    3 3; 4 5; 5 7; 6 9; 7 11; 8 13; 9 15; 10 17; 11 19; 12 20;
    14 2; 15 4; 16 6; 17 8; 18 10; 19 12; 5 18; 8 2; 12 5; 16 17];
for k=1:size(pos,1)
    B5(pos(k,1),pos(k,2))=1;
end
layouts(idx).name="BAD #5 — disperso";
layouts(idx).grid=B5;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 3) EVALUACIÓN INDIVIDUAL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

N = length(layouts);
Resultados = struct([]);

for i = 1:N
    
    name = layouts(i).name;
    gr   = layouts(i).grid;

    fprintf('\n--------------------------------------------\n');
    fprintf(' Layout: %s\n', name);
    fprintf('--------------------------------------------\n');

    printLayout(gr);

    [pwr_T, gan_T, cost_T, obj_T] = f_powerPlantsT_fast(vVec, gr);

    % ============================
    % Cálculos exactos sin redondeo
    % ============================
    E_kWh = pwr_T;      
    E_GWh = E_kWh / 1e6;

    P_kW  = E_kWh / 8760;
    P_MW  = P_kW / 1000;

    mejora_pct = ((P_MW - P_profesor_MW) / P_profesor_MW) * 100;
    fraccion_techo = (P_MW / P_teorico_MW) * 100;

    clas = "MALA";
    if P_MW >= P_profesor_MW
        clas = "BUENA";
    end

    % ============================
    % IMPRESIÓN EXACTA
    % ============================
    fprintf("  → Energía anual total = %.12f kWh (%.12f GWh)\n", E_kWh, E_GWh);
    fprintf("  → Potencia media      = %.12f kW  (%.12f MW)\n", P_kW, P_MW);
    fprintf("  → Mejora respecto al profesor: %.12f %%\n", mejora_pct);
    fprintf("  → Comparado con el techo teórico del parque: %.12f %%\n", fraccion_techo);
    fprintf("  → Clasificación final: %s\n", clas);

    % Guardar resultados
    Resultados(i).name   = name;
    Resultados(i).E_GWh  = E_GWh;
    Resultados(i).P_MW   = P_MW;
    Resultados(i).mejora = mejora_pct;
    Resultados(i).techo  = fraccion_techo;
    Resultados(i).clas   = clas;
end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% 4) RANKING FINAL
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

fprintf('\n============================================\n');
fprintf('                 RANKING FINAL\n');
fprintf('============================================\n\n');

[~,ord] = sort([Resultados.P_MW], 'descend');

for k = ord
    fprintf('%-25s | %.12f MW | %+8.3f %% | %s\n', ...
        Resultados(k).name, ...
        Resultados(k).P_MW, ...
        Resultados(k).mejora, ...
        Resultados(k).clas);
end

fprintf('\n============================================\n');
fprintf('   FIN — RESULTADOS EXPORTADOS A TXT (usando diary)\n');
fprintf('============================================\n');

end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% IMPRESIÓN DEL LAYOUT BONITO CON ■ y ·
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

function printLayout(gr)
fprintf("\n  Distribución del parque (20×20):\n");
fprintf("  Leyenda: [■] turbina   [·] vacío\n\n");

for r = 1:20
    line = "";
    for c = 1:20
        if gr(r,c)==1, line=line+"■ ";
        else,          line=line+"· ";
        end
    end
    fprintf("   %s\n", line);
end
fprintf('\n');
end
