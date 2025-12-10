% filepath: c:\Users\jcneg\OneDrive - Universidad de Alcala\#uni\4 año\SOFT COMPUTING\Trabajos-Softcomp-duoq\Trabajo Final\Main.m
clear all; close all; clc;

addpath('windSym\dt\');addpath('.\windSym\utils\');

%% Load Data
load('WindSym_1.mat');
load('WindSym_1.mat');
pcData   = load('pwrCurve.mat');
pcFields = fieldnames(pcData);
pwrCurve = pcData.(pcFields{1});

%% Funciones

% Función para calcular potencia de un solo coral
function pwr = calculateCoralPower(gr, vVec, pwrCurveData)
    if isempty(gr)
        pwr = 0;
        return;
    end
    
    nH = size(vVec, 2);
    avVec = atan2(vVec(2,:), vVec(1,:));
    [angVec, ia, ic] = uniquetol(avVec, 1e-15);
    
    Nturb = sum(gr, 'all');
    rUDef_T = zeros(Nturb, Nturb, nH);
    for l = 1:length(angVec)
        rUDef = f_powerPlants_f1(vVec(:, ia(l)), gr);
        rUDef_T(:, :, ic == l) = repmat(rUDef, 1, 1, sum(ic == l));
    end
    
    pwr_sum = 0;
    for l = 1:nH
        [pwr_t, ~] = f_powerPlants_f2(vVec(:, l), gr, pwrCurveData, rUDef_T(:, :, l));
        pwr_sum = pwr_sum + pwr_t;
    end
    
    % Devolver valor crudo (suma total) sin procesar unidades
    pwr = pwr_sum; 
end

% Función para evaluar potencia del arrecife y devolver ranking ordenado
function [coralRanking, reef] = evaluateReefPower(reef, windSymData, pwrCurveData, existingRanking)
    [rows, cols] = size(reef);
    
    % Si hay ranking existente, solo evaluar los nuevos
    if nargin < 4
        existingRanking = [];
    end
    
    fprintf('Evaluando potencia de los corales...\n');
    
    entries = [];
    for i = 1:rows
        for j = 1:cols
            layout = reef{i,j};
            if ~isempty(layout)
                % Verificar si ya está calculado en el ranking existente
                alreadyCalculated = false;
                if ~isempty(existingRanking)
                    idx = find(existingRanking(:,2) == i & existingRanking(:,3) == j, 1);
                    if ~isempty(idx)
                        entries = [entries; existingRanking(idx, :)]; %#ok<AGROW>
                        alreadyCalculated = true;
                    end
                end
                
                if ~alreadyCalculated
                    pwr = calculateCoralPower(layout, windSymData, pwrCurveData);
                    entries = [entries; pwr, i, j]; %#ok<AGROW>
                end
            end
        end
    end
    
    if isempty(entries)
        disp('No hay corales con potencia.');
        coralRanking = [];
        return;
    end
    
    % Ordenar por potencia descendente
    [~, idx] = sort(entries(:,1), 'descend');
    coralRanking = entries(idx,:);
    
    disp('Ranking de corales por potencia (Raw):');
    for k = 1:size(coralRanking,1)
        fprintf('%2d) Potencia: %10.2f      ->  Coral (%d, %d)\n', ...
            k, coralRanking(k,1), coralRanking(k,2), coralRanking(k,3));
    end
    disp('═════════════════════════════════════════════════════');
end

% Función de reproducción sexual (crossover entre dos corales)
function childCoral = sexualReproduction(parent1, parent2, Kgr, maxTurb)
    % Mezcla aleatoria de las posiciones de turbinas de ambos padres
    % Respetando el número máximo de turbinas
    
    combined = parent1 | parent2;  % Unión de posiciones
    turbinePositions = find(combined);
    
    % Si hay más posiciones que el máximo, seleccionar aleatoriamente
    if length(turbinePositions) > maxTurb
        selectedIdx = randperm(length(turbinePositions), maxTurb);
        turbinePositions = turbinePositions(selectedIdx);
    end
    
    childCoral = zeros(Kgr);
    childCoral(turbinePositions) = 1;
end

% Función de reproducción asexual (mutación de un coral)
function childCoral = asexualReproduction(parent, Kgr, maxTurb)
    % Mutación: cambiar aleatoriamente algunas posiciones de turbinas
    childCoral = parent;
    
    % Número de mutaciones (entre 1 y 5 cambios)
    nMutations = randi([1, 5]);
    
    turbinePositions = find(parent);
    emptyPositions = find(~parent);
    
    for m = 1:nMutations
        if ~isempty(turbinePositions) && ~isempty(emptyPositions)
            % Mover una turbina a una posición vacía
            removeIdx = randi(length(turbinePositions));
            addIdx = randi(length(emptyPositions));
            
            childCoral(turbinePositions(removeIdx)) = 0;
            childCoral(emptyPositions(addIdx)) = 1;
            
            % Actualizar listas
            turbinePositions(removeIdx) = emptyPositions(addIdx);
            emptyPositions(addIdx) = [];
        end
    end
end

% Función para encontrar posiciones vacías en el arrecife
function emptyPositions = findEmptyPositions(reef)
    [rows, cols] = size(reef);
    emptyPositions = [];
    for i = 1:rows
        for j = 1:cols
            if isempty(reef{i,j})
                emptyPositions = [emptyPositions; i, j]; %#ok<AGROW>
            end
        end
    end
end

% Algoritmo CRO principal
function [reef, finalRanking] = CRO_Algorithm(reef, vVec, pwrCurve, Kgr, maxTurb, maxIter, targetPower, coralRanking)
    fprintf('\n');
    disp('╔═══════════════════════════════════════════════════════════╗');
    disp('║         ALGORITMO CRO - Coral Reef Optimization          ║');
    disp('╚═══════════════════════════════════════════════════════════╝');
    fprintf('\n');
    
    % Evaluación inicial si no se proporciona
    if nargin < 8 || isempty(coralRanking)
        [coralRanking, reef] = evaluateReefPower(reef, vVec, pwrCurve);
    end
    
    bestPowerHistory = [];
    noImprovementCount = 0;
    lastBestPower = 0;
    
    if ~isempty(coralRanking)
        lastBestPower = coralRanking(1,1);
        bestPowerHistory = [bestPowerHistory; lastBestPower];
    end

    for iter = 1:maxIter
        fprintf('\n══════════════ ITERACIÓN %d/%d ══════════════\n', iter, maxIter);
        
        currentBestPower = coralRanking(1,1);
        
        % Verificar condición de parada por potencia
        if currentBestPower >= targetPower
            fprintf('¡Objetivo alcanzado! Potencia máxima: %.2f >= %.2f\n', ...
                currentBestPower, targetPower);
            break;
        end
        
        % Verificar condición de parada por estancamiento (4 generaciones)
        if currentBestPower > lastBestPower
            noImprovementCount = 0;
            lastBestPower = currentBestPower;
            fprintf('¡Mejora detectada! Nueva mejor potencia: %.2f\n', currentBestPower);
        else
            noImprovementCount = noImprovementCount + 1;
            fprintf('Sin mejora en %d generaciones (Mejor actual: %.2f)\n', noImprovementCount, currentBestPower);
        end
        
        if noImprovementCount >= 4
            fprintf('Parada por estancamiento: No hubo mejora en 4 generaciones consecutivas.\n');
            break;
        end
        
        nCorals = size(coralRanking, 1);
        
        %% REPRODUCCIÓN SEXUAL (80% peor)
        fprintf('\n--- Reproducción Sexual (Crossover) ---\n');
        
        % Calcular 80% peor (ajustado a número par)
        nSexual = floor(nCorals * 0.80);
        if mod(nSexual, 2) ~= 0
            nSexual = nSexual - 1;  % Asegurar número par
        end
        
        if nSexual >= 2
            % Seleccionar el 80% peor (desde el final del ranking)
            worstCorals = coralRanking(end-nSexual+1:end, :);
            
            % Emparejar aleatoriamente
            pairOrder = randperm(nSexual);
            nPairs = nSexual / 2;
            
            newChildren = cell(nPairs, 1);
            newChildrenPower = zeros(nPairs, 1);
            
            for p = 1:nPairs
                idx1 = pairOrder(2*p - 1);
                idx2 = pairOrder(2*p);
                
                parent1_pos = worstCorals(idx1, 2:3);
                parent2_pos = worstCorals(idx2, 2:3);
                
                parent1 = reef{parent1_pos(1), parent1_pos(2)};
                parent2 = reef{parent2_pos(1), parent2_pos(2)};
                
                % Crear hijo por crossover
                child = sexualReproduction(parent1, parent2, Kgr, maxTurb);
                newChildren{p} = child;
                
                % Calcular potencia del hijo
                newChildrenPower(p) = calculateCoralPower(child, vVec, pwrCurve);
            end
            
            fprintf('Generados %d hijos por reproducción sexual\n', nPairs);
            
            % Colocar hijos en el arrecife
            for p = 1:nPairs
                emptyPos = findEmptyPositions(reef);
                
                if ~isempty(emptyPos)
                    % Hay espacio disponible
                    posIdx = randi(size(emptyPos, 1));
                    r = emptyPos(posIdx, 1);
                    c = emptyPos(posIdx, 2);
                    reef{r, c} = newChildren{p};
                    coralRanking = [coralRanking; newChildrenPower(p), r, c]; %#ok<AGROW>
                else
                    % Reemplazar al peor si el hijo es mejor
                    [~, sortIdx] = sort(coralRanking(:,1), 'ascend');
                    worstIdx = sortIdx(1);
                    
                    if newChildrenPower(p) > coralRanking(worstIdx, 1)
                        r = coralRanking(worstIdx, 2);
                        c = coralRanking(worstIdx, 3);
                        reef{r, c} = newChildren{p};
                        coralRanking(worstIdx, 1) = newChildrenPower(p);
                    end
                end
            end
            
            % Reordenar ranking
            [~, sortIdx] = sort(coralRanking(:,1), 'descend');
            coralRanking = coralRanking(sortIdx, :);
        end
        
        %% REPRODUCCIÓN ASEXUAL (20% mejor - mutación)
        fprintf('\n--- Reproducción Asexual (Mutación) ---\n');
        
        nCorals = size(coralRanking, 1);
        nAsexual = max(1, floor(nCorals * 0.20));
        
        % Seleccionar el 20% mejor
        bestCorals = coralRanking(1:nAsexual, :);
        
        newMutants = cell(nAsexual, 1);
        newMutantsPower = zeros(nAsexual, 1);
        
        for m = 1:nAsexual
            parent_pos = bestCorals(m, 2:3);
            parent = reef{parent_pos(1), parent_pos(2)};
            
            % Crear hijo por mutación
            mutant = asexualReproduction(parent, Kgr, maxTurb);
            newMutants{m} = mutant;
            
            % Calcular potencia del mutante
            newMutantsPower(m) = calculateCoralPower(mutant, vVec, pwrCurve);
        end
        
        fprintf('Generados %d hijos por reproducción asexual\n', nAsexual);
        
        % Colocar mutantes en el arrecife
        for m = 1:nAsexual
            emptyPos = findEmptyPositions(reef);
            
            if ~isempty(emptyPos)
                % Hay espacio disponible
                posIdx = randi(size(emptyPos, 1));
                r = emptyPos(posIdx, 1);
                c = emptyPos(posIdx, 2);
                reef{r, c} = newMutants{m};
                coralRanking = [coralRanking; newMutantsPower(m), r, c]; %#ok<AGROW>
            else
                % Reemplazar al peor si el mutante es mejor
                [~, sortIdx] = sort(coralRanking(:,1), 'ascend');
                worstIdx = sortIdx(1);
                
                if newMutantsPower(m) > coralRanking(worstIdx, 1)
                    r = coralRanking(worstIdx, 2);
                    c = coralRanking(worstIdx, 3);
                    reef{r, c} = newMutants{m};
                    coralRanking(worstIdx, 1) = newMutantsPower(m);
                end
            end
        end
        
        % Reordenar ranking final de la iteración
        [~, sortIdx] = sort(coralRanking(:,1), 'descend');
        coralRanking = coralRanking(sortIdx, :);
        
        % Guardar historia
        bestPowerHistory = [bestPowerHistory; coralRanking(1,1)]; %#ok<AGROW>
        
        % Mostrar estado actual
        fprintf('\n--- Estado tras iteración %d ---\n', iter);
        fprintf('Mejor potencia: %.2f\n', coralRanking(1,1));
        fprintf('Peor potencia: %.2f\n', coralRanking(end,1));
        fprintf('Total corales: %d\n', size(coralRanking, 1));
    end
    
    % Resultado final
    fprintf('\n');
    disp('╔═══════════════════════════════════════════════════════════╗');
    disp('║                    RESULTADO FINAL                       ║');
    disp('╚═══════════════════════════════════════════════════════════╝');
    
    finalRanking = coralRanking;
    
    disp('Ranking final de corales por potencia (Raw):');
    for k = 1:min(20, size(finalRanking,1))  % Mostrar top 20
        fprintf('%2d) Potencia: %10.2f      ->  Coral (%d, %d)\n', ...
            k, finalRanking(k,1), finalRanking(k,2), finalRanking(k,3));
    end
    if size(finalRanking,1) > 20
        fprintf('... y %d corales más\n', size(finalRanking,1) - 20);
    end
    disp('═════════════════════════════════════════════════════════════');
    fprintf('Mejor solución encontrada: %.2f en posición (%d, %d)\n', ...
        finalRanking(1,1), finalRanking(1,2), finalRanking(1,3));
        
    % Graficar progresión
    figure;
    plot(0:length(bestPowerHistory)-1, bestPowerHistory, 'b-o', 'LineWidth', 2);
    title('Progresión de la Mejor Potencia (Algoritmo CRO)');
    xlabel('Iteración');
    ylabel('Potencia (Raw)');
    grid on;
    fprintf('Gráfico de progresión generado.\n');
end

% Funcion que genera una grilla con la disposicion de turbinas aleatoria
% filepath: c:\Users\jcneg\OneDrive - Universidad de Alcala\#uni\4 año\SOFT COMPUTING\Trabajos-Softcomp-duoq\Trabajo Final\Main.m
% Funcion que genera una grilla con la disposicion de turbinas aleatoria
function visualizeReef(reef)
    [rows, cols] = size(reef);
    
    % Mostrar como caracteres con separación
    disp('═════════════════════════════════════════════════════');
    disp('           Mapa del arrecife de corales');
    disp('           (X = coral ocupado, _ = vacío)');
    disp('═════════════════════════════════════════════════════');
    fprintf('\n');
    
    % Encabezado con números de columna
    fprintf('      ');
    for j = 1:cols
        fprintf(' %d  ', j);
    end
    fprintf('\n');
    fprintf('    ┌');
    for j = 1:cols
        fprintf('───');
        if j < cols
            fprintf('┬');
        end
    end
    fprintf('┐\n');
    
    % Filas del arrecife
    for i = 1:rows
        fprintf(' %d  │', i);
        for j = 1:cols
            if ~isempty(reef{i,j})
                fprintf(' X ');
            else
                fprintf(' _ ');
            end
            if j < cols
                fprintf('│');
            end
        end
        fprintf('│\n');
        
        % Separador entre filas (excepto última)
        if i < rows
            fprintf('    ├');
            for j = 1:cols
                fprintf('───');
                if j < cols
                    fprintf('┼');
                end
            end
            fprintf('┤\n');
        end
    end
    
    % Borde inferior
    fprintf('    └');
    for j = 1:cols
        fprintf('───');
        if j < cols
            fprintf('┴');
        end
    end
    fprintf('┘\n');
    fprintf('\n');
    fprintf('Total de corales: %d / %d posiciones\n', sum(~cellfun(@isempty, reef(:))), rows*cols);
    disp('═════════════════════════════════════════════════════');
end
% Funcion que genera una grilla con la disposicion de turbinas aleatoria
function gr = createGrid(Kgr, Nturb)
    gr = zeros(Kgr);
    gr(randperm(Kgr^2, Nturb)) = 1;
end




%% Create Grid with Nturb Turbines
Kgr   = 20;   % Tamaño del Grid (tamaño de cada coral)
Nturb = 20;   % Numero de Turbinas por coral

%% Parámetros del arrecife
reefRows   = 8;
reefCols   = 8;
reefSize   = reefRows * reefCols;
initFill   = 0.60;                 % 60% de ocupación inicial
nInitCoral = round(reefSize * initFill);

%% Parámetros del algoritmo CRO
maxIterations = 100;       % Máximo de iteraciones
targetPower   = 53500000.00; % Potencia objetivo (Raw)

%% Inicializar arrecife

% Arrecife: celda 8x8, cada elemento es un coral (una matriz Kgr x Kgr)
reef = cell(reefRows, reefCols);

% Inicializar todo vacío
for i = 1:reefRows
    for j = 1:reefCols
        reef{i,j} = [];   % coral vacío
    end
end

% Elegir posiciones aleatorias para los corales iniciales
idxAll      = randperm(reefSize, nInitCoral);
[rowsInit, colsInit] = ind2sub([reefRows, reefCols], idxAll);

% Rellenar el 60% del arrecife con corales (disposiciones gr aleatorias)
for k = 1:nInitCoral
    r = rowsInit(k);
    c = colsInit(k);
    reef{r,c} = createGrid(Kgr, Nturb);
end

%visualizar arrecife en forma de matriz mostrando una x en las posiciones ocupadas
visualizeReef(reef);

%% Evaluar Generación Inicial
fprintf('\n--- Ranking Inicial (Generación Aleatoria) ---\n');
[initialRanking, reef] = evaluateReefPower(reef, vVec, pwrCurve);

%% Ejecutar algoritmo CRO
[reef, finalRanking] = CRO_Algorithm(reef, vVec, pwrCurve, Kgr, Nturb, maxIterations, targetPower, initialRanking);

%% Visualizar arrecife final
fprintf('\n');
visualizeReef(reef);





    


