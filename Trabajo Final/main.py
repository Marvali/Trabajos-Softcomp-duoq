import numpy as np
import scipy.io
from scipy.interpolate import PPoly
import matplotlib.pyplot as plt
import sys
import os
import math
import time

# Add python folder to sys.path to import windSymPython modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

from windSymPython.f_powerPlants_f1 import f_powerPlants_f1
from windSymPython.f_powerPlants_f2 import f_powerPlants_f2

# Utility function from f_powerPlantsT_fast.py
def uniquetol(array, tol):
    tol = tol * np.max(np.abs(array))
    array_copy = np.sort(np.copy(array))
    result = [array_copy[0]]
    # hallamos el resultado de unique con toloreancia tol
    for i in range(len(array_copy)-1):
        if np.abs(array_copy[i+1]-result[-1]) >= tol:
            result.append(array_copy[i+1])
    # hallamos ia como los indices de cada elemento de result en array
    # se usa where porque array es un numpy.darray y no tiene .index()
    ia = []
    for elem in result:
        indice_ia = np.where(np.abs(array-elem)<=tol)[0][0]
        ia.append(indice_ia)
    # hallamos ic como los indices de cada elemento de array en result
    ic = []
    result_copy=np.copy(result)
    for valor in array:
        indice_ic = np.where(np.abs(result_copy-valor)<=tol)[0][0]
        ic.append(indice_ic)
    return np.array(result), np.array(ia), np.array(ic)

# %% Funciones

# Función para calcular potencia de un solo coral
def calculateCoralPower(gr, vVec, pwrCurveData):
    if gr is None or gr.size == 0 or np.sum(gr) == 0:
        return 0
    
    nH = vVec.shape[1]
    avVec = np.arctan2(vVec[1,:], vVec[0,:])
    angVec, ia, ic = uniquetol(avVec, 1e-15)
    
    Nturb = int(np.sum(gr))
    rUDef_T = np.zeros((Nturb, Nturb, nH))
    
    for l in range(len(angVec)):
        # Note: f_powerPlants_f1 in Python requires Nturb
        rUDef = f_powerPlants_f1(vVec[:, ia[l]], gr, Nturb)
        # Equivalent to repmat in MATLAB
        rUDef_T[:, :, ic == l] = np.tile(rUDef[:, :, None], [1, 1, np.count_nonzero(ic == l)])
    
    pwr_sum = 0
    for l in range(nH):
        # f_powerPlants_f2 returns: pwr_t, pwrGen, Ux, gan, cost, obj
        pwr_t, _, _, _, _, _ = f_powerPlants_f2(vVec[:, l], gr, pwrCurveData, rUDef_T[:, :, l], Nturb)
        pwr_sum += pwr_t
    
    # Devolver valor crudo (suma total) sin procesar unidades
    return pwr_sum

# Función para evaluar potencia del arrecife y devolver ranking ordenado
def evaluateReefPower(reef, windSymData, pwrCurveData, existingRanking=None):
    rows = len(reef)
    cols = len(reef[0])
    
    # Si hay ranking existente, solo evaluar los nuevos
    if existingRanking is None:
        existingRanking = []
    
    print('Evaluando potencia de los corales...')
    
    entries = []
    # existingRanking is expected to be a list of [pwr, i, j] or numpy array
    if isinstance(existingRanking, np.ndarray):
        existingRanking = existingRanking.tolist()
        
    for i in range(rows):
        for j in range(cols):
            layout = reef[i][j]
            if layout is not None and layout.size > 0:
                # Verificar si ya está calculado en el ranking existente
                alreadyCalculated = False
                if existingRanking:
                    # Check if [i+1, j+1] exists in existingRanking (using 1-based indexing for consistency with MATLAB output if desired, but let's stick to 0-based internally and convert for display)
                    # Actually, let's stick to 1-based indexing for i, j in the ranking to match MATLAB's output style
                    # MATLAB: entries = [pwr, i, j] where i,j are 1-based indices
                    
                    # Let's use 1-based indexing for storage in entries to match MATLAB logic exactly
                    idx = -1
                    for k, entry in enumerate(existingRanking):
                        if int(entry[1]) == i + 1 and int(entry[2]) == j + 1:
                            idx = k
                            break
                    
                    if idx != -1:
                        entries.append(existingRanking[idx])
                        alreadyCalculated = True
                
                if not alreadyCalculated:
                    pwr = calculateCoralPower(layout, windSymData, pwrCurveData)
                    entries.append([pwr, i + 1, j + 1]) # Store as 1-based index
    
    if not entries:
        print('No hay corales con potencia.')
        return np.array([]), reef
    
    entries = np.array(entries)
    
    # Ordenar por potencia descendente
    # sort by first column (power) descending
    idx = np.argsort(entries[:, 0])[::-1]
    coralRanking = entries[idx]
    
    print('Ranking de corales por potencia (Raw):')
    for k in range(len(coralRanking)):
        print(f'{k+1:2d}) Potencia: {coralRanking[k,0]:10.2f}      ->  Coral ({int(coralRanking[k,1])}, {int(coralRanking[k,2])})')
    print('═════════════════════════════════════════════════════')
    
    return coralRanking, reef

# Función de reproducción sexual (crossover entre dos corales)
def sexualReproduction(parent1, parent2, Kgr, maxTurb):
    # Mezcla aleatoria de las posiciones de turbinas de ambos padres
    # Respetando el número máximo de turbinas
    
    combined = np.logical_or(parent1, parent2) # Unión de posiciones
    turbinePositions = np.flatnonzero(combined) # Indices linear
    
    # Si hay más posiciones que el máximo, seleccionar aleatoriamente
    if len(turbinePositions) > maxTurb:
        selectedIdx = np.random.choice(len(turbinePositions), maxTurb, replace=False)
        turbinePositions = turbinePositions[selectedIdx]
    
    childCoral = np.zeros((Kgr, Kgr))
    # Set positions to 1. We need to convert linear indices back to 2D if we were doing it manually,
    # but flat assignment works if we flatten childCoral or use unravel_index
    # Easier:
    np.put(childCoral, turbinePositions, 1)
    
    return childCoral

# Función de reproducción asexual (mutación de un coral)
def asexualReproduction(parent, Kgr, maxTurb):
    # Mutación: cambiar aleatoriamente algunas posiciones de turbinas
    childCoral = np.copy(parent)
    
    # Número de mutaciones (entre 1 y 5 cambios)
    nMutations = np.random.randint(1, 6) # 1 to 5
    
    turbinePositions = np.flatnonzero(parent)
    emptyPositions = np.flatnonzero(parent == 0)
    
    for m in range(nMutations):
        if len(turbinePositions) > 0 and len(emptyPositions) > 0:
            # Mover una turbina a una posición vacía
            removeIdx = np.random.randint(len(turbinePositions))
            addIdx = np.random.randint(len(emptyPositions))
            
            # Update childCoral
            # We need linear indices
            remPos = turbinePositions[removeIdx]
            addPos = emptyPositions[addIdx]
            
            np.put(childCoral, [remPos], 0)
            np.put(childCoral, [addPos], 1)
            
            # Actualizar listas
            turbinePositions[removeIdx] = addPos
            # Remove used empty position from emptyPositions is tricky with arrays, 
            # but since we just swapped, the old turbine pos is now empty.
            # However, MATLAB code does:
            # turbinePositions(removeIdx) = emptyPositions(addIdx);
            # emptyPositions(addIdx) = [];
            # So it effectively moves one turbine to one empty spot.
            
            # Let's just re-calculate positions for simplicity and correctness in next iteration if needed,
            # but inside the loop we should update.
            # Updating numpy arrays by deleting is slow/complex.
            # Let's use lists for the indices management inside loop
            
            # Actually, let's just re-read from childCoral if we want to be safe, 
            # or just swap in the arrays.
            
            # MATLAB logic:
            # turbinePositions(removeIdx) = emptyPositions(addIdx); -> The turbine moved to the new spot
            # emptyPositions(addIdx) = []; -> The new spot is no longer empty
            
            # In Python:
            turbinePositions[removeIdx] = emptyPositions[addIdx]
            emptyPositions = np.delete(emptyPositions, addIdx)
            # And we should technically add the old turbine pos to emptyPositions?
            # MATLAB code doesn't seem to add the old turbine pos back to emptyPositions?
            # "emptyPositions(addIdx) = [];" removes the used empty spot.
            # It doesn't say "emptyPositions = [emptyPositions, oldTurbinePos]".
            # So the old turbine pos becomes empty but is not available for *this* batch of mutations?
            # That seems to be the logic.
            
    return childCoral

# Función para encontrar posiciones vacías en el arrecife
def findEmptyPositions(reef):
    rows = len(reef)
    cols = len(reef[0])
    emptyPositions = []
    for i in range(rows):
        for j in range(cols):
            if reef[i][j] is None or reef[i][j].size == 0:
                emptyPositions.append([i + 1, j + 1]) # 1-based indexing
    return np.array(emptyPositions)

# Algoritmo CRO principal
def CRO_Algorithm(reef, vVec, pwrCurve, Kgr, maxTurb, maxIter, targetPower, coralRanking=None):
    print('\n')
    print('╔═══════════════════════════════════════════════════════════╗')
    print('║         ALGORITMO CRO - Coral Reef Optimization          ║')
    print('╚═══════════════════════════════════════════════════════════╝')
    print('\n')
    
    # Evaluación inicial si no se proporciona
    if coralRanking is None or len(coralRanking) == 0:
        coralRanking, reef = evaluateReefPower(reef, vVec, pwrCurve)
    
    bestPowerHistory = []
    noImprovementCount = 0
    lastBestPower = 0
    
    if len(coralRanking) > 0:
        lastBestPower = coralRanking[0, 0]
        bestPowerHistory.append(lastBestPower)
    
    for iter_num in range(1, maxIter + 1):
        print(f'\n══════════════ ITERACIÓN {iter_num}/{maxIter} ══════════════\n')
        
        currentBestPower = coralRanking[0, 0]
        
        # Verificar condición de parada por potencia
        if currentBestPower >= targetPower:
            print(f'¡Objetivo alcanzado! Potencia máxima: {currentBestPower:.2f} >= {targetPower:.2f}')
            break
        
        # Verificar condición de parada por estancamiento (4 generaciones)
        if currentBestPower > lastBestPower:
            noImprovementCount = 0
            lastBestPower = currentBestPower
            print(f'¡Mejora detectada! Nueva mejor potencia: {currentBestPower:.2f}')
        else:
            noImprovementCount += 1
            print(f'Sin mejora en {noImprovementCount} generaciones (Mejor actual: {currentBestPower:.2f})')
        
        if noImprovementCount >= 4:
            print('Parada por estancamiento: No hubo mejora en 4 generaciones consecutivas.')
            break
        
        nCorals = len(coralRanking)
        
        # %% REPRODUCCIÓN SEXUAL (80% peor)
        print('\n--- Reproducción Sexual (Crossover) ---')
        
        # Calcular 80% peor (ajustado a número par)
        nSexual = int(np.floor(nCorals * 0.80))
        if nSexual % 2 != 0:
            nSexual -= 1  # Asegurar número par
        
        if nSexual >= 2:
            # Seleccionar el 80% peor (desde el final del ranking)
            # coralRanking is sorted descending, so worst are at the end
            worstCorals = coralRanking[nCorals-nSexual:, :]
            
            # Emparejar aleatoriamente
            pairOrder = np.random.permutation(nSexual)
            nPairs = int(nSexual / 2)
            
            newChildren = []
            newChildrenPower = []
            
            for p in range(nPairs):
                idx1 = pairOrder[2*p]
                idx2 = pairOrder[2*p + 1]
                
                parent1_pos = worstCorals[idx1, 1:3].astype(int)
                parent2_pos = worstCorals[idx2, 1:3].astype(int)
                
                # Adjust for 0-based indexing for reef access
                parent1 = reef[parent1_pos[0]-1][parent1_pos[1]-1]
                parent2 = reef[parent2_pos[0]-1][parent2_pos[1]-1]
                
                # Crear hijo por crossover
                child = sexualReproduction(parent1, parent2, Kgr, maxTurb)
                newChildren.append(child)
                
                # Calcular potencia del hijo
                newChildrenPower.append(calculateCoralPower(child, vVec, pwrCurve))
            
            print(f'Generados {nPairs} hijos por reproducción sexual')
            
            # Colocar hijos en el arrecife
            for p in range(nPairs):
                emptyPos = findEmptyPositions(reef)
                
                if len(emptyPos) > 0:
                    # Hay espacio disponible
                    posIdx = np.random.randint(len(emptyPos))
                    r = int(emptyPos[posIdx, 0])
                    c = int(emptyPos[posIdx, 1])
                    
                    reef[r-1][c-1] = newChildren[p]
                    # Add to ranking
                    new_entry = np.array([[newChildrenPower[p], r, c]])
                    coralRanking = np.vstack([coralRanking, new_entry])
                else:
                    # Reemplazar al peor si el hijo es mejor
                    # Sort ascending to find worst
                    sortIdx = np.argsort(coralRanking[:, 0])
                    worstIdx = sortIdx[0]
                    
                    if newChildrenPower[p] > coralRanking[worstIdx, 0]:
                        r = int(coralRanking[worstIdx, 1])
                        c = int(coralRanking[worstIdx, 2])
                        reef[r-1][c-1] = newChildren[p]
                        coralRanking[worstIdx, 0] = newChildrenPower[p]
            
            # Reordenar ranking
            idx = np.argsort(coralRanking[:, 0])[::-1]
            coralRanking = coralRanking[idx]
        
        # %% REPRODUCCIÓN ASEXUAL (20% mejor - mutación)
        print('\n--- Reproducción Asexual (Mutación) ---')
        
        nCorals = len(coralRanking)
        nAsexual = max(1, int(np.floor(nCorals * 0.20)))
        
        # Seleccionar el 20% mejor
        bestCorals = coralRanking[:nAsexual, :]
        
        newMutants = []
        newMutantsPower = []
        
        for m in range(nAsexual):
            parent_pos = bestCorals[m, 1:3].astype(int)
            parent = reef[parent_pos[0]-1][parent_pos[1]-1]
            
            # Crear hijo por mutación
            mutant = asexualReproduction(parent, Kgr, maxTurb)
            newMutants.append(mutant)
            
            # Calcular potencia del mutante
            newMutantsPower.append(calculateCoralPower(mutant, vVec, pwrCurve))
        
        print(f'Generados {nAsexual} hijos por reproducción asexual')
        
        # Colocar mutantes en el arrecife
        for m in range(nAsexual):
            emptyPos = findEmptyPositions(reef)
            
            if len(emptyPos) > 0:
                # Hay espacio disponible
                posIdx = np.random.randint(len(emptyPos))
                r = int(emptyPos[posIdx, 0])
                c = int(emptyPos[posIdx, 1])
                reef[r-1][c-1] = newMutants[m]
                new_entry = np.array([[newMutantsPower[m], r, c]])
                coralRanking = np.vstack([coralRanking, new_entry])
            else:
                # Reemplazar al peor si el mutante es mejor
                sortIdx = np.argsort(coralRanking[:, 0])
                worstIdx = sortIdx[0]
                
                if newMutantsPower[m] > coralRanking[worstIdx, 0]:
                    r = int(coralRanking[worstIdx, 1])
                    c = int(coralRanking[worstIdx, 2])
                    reef[r-1][c-1] = newMutants[m]
                    coralRanking[worstIdx, 0] = newMutantsPower[m]
        
        # Reordenar ranking final de la iteración
        idx = np.argsort(coralRanking[:, 0])[::-1]
        coralRanking = coralRanking[idx]
        
        # Guardar historia
        bestPowerHistory.append(coralRanking[0, 0])
        
        # Mostrar estado actual
        print(f'\n--- Estado tras iteración {iter_num} ---')
        print(f'Mejor potencia: {coralRanking[0, 0]:.2f}')
        print(f'Peor potencia: {coralRanking[-1, 0]:.2f}')
        print(f'Total corales: {len(coralRanking)}')
    
    # Resultado final
    print('\n')
    print('╔═══════════════════════════════════════════════════════════╗')
    print('║                    RESULTADO FINAL                       ║')
    print('╚═══════════════════════════════════════════════════════════╝')
    
    finalRanking = coralRanking
    
    print('Ranking final de corales por potencia (Raw):')
    limit = min(20, len(finalRanking))
    for k in range(limit):
        print(f'{k+1:2d}) Potencia: {finalRanking[k,0]:10.2f}      ->  Coral ({int(finalRanking[k,1])}, {int(finalRanking[k,2])})')
    
    if len(finalRanking) > 20:
        print(f'... y {len(finalRanking) - 20} corales más')
    
    print('═════════════════════════════════════════════════════════════')
    print(f'Mejor solución encontrada: {finalRanking[0,0]:.2f} en posición ({int(finalRanking[0,1])}, {int(finalRanking[0,2])})')
    
    # Graficar progresión
    plt.figure()
    plt.plot(range(len(bestPowerHistory)), bestPowerHistory, 'b-o', linewidth=2)
    plt.title('Progresión de la Mejor Potencia (Algoritmo CRO)')
    plt.xlabel('Iteración')
    plt.ylabel('Potencia (Raw)')
    plt.grid(True)
    print('Gráfico de progresión generado.')
    plt.show() # Show the plot
    
    return reef, finalRanking

# Funcion que genera una grilla con la disposicion de turbinas aleatoria
def visualizeReef(reef):
    rows = len(reef)
    cols = len(reef[0])
    
    # Mostrar como caracteres con separación
    print('═════════════════════════════════════════════════════')
    print('           Mapa del arrecife de corales')
    print('           (X = coral ocupado, _ = vacío)')
    print('═════════════════════════════════════════════════════')
    print('\n')
    
    # Encabezado con números de columna
    print('      ', end='')
    for j in range(1, cols + 1):
        print(f' {j}  ', end='')
    print('\n', end='')
    
    print('    ┌', end='')
    for j in range(cols):
        print('───', end='')
        if j < cols - 1:
            print('┬', end='')
    print('┐')
    
    # Filas del arrecife
    for i in range(rows):
        print(f' {i+1}  │', end='')
        for j in range(cols):
            if reef[i][j] is not None and reef[i][j].size > 0:
                print(' X ', end='')
            else:
                print(' _ ', end='')
            if j < cols - 1:
                print('│', end='')
        print('│')
        
        # Separador entre filas (excepto última)
        if i < rows - 1:
            print('    ├', end='')
            for j in range(cols):
                print('───', end='')
                if j < cols - 1:
                    print('┼', end='')
            print('┤')
    
    # Borde inferior
    print('    └', end='')
    for j in range(cols):
        print('───', end='')
        if j < cols - 1:
            print('┴', end='')
    print('┘')
    print('\n')
    
    # Count occupied
    occupied = 0
    for i in range(rows):
        for j in range(cols):
            if reef[i][j] is not None and reef[i][j].size > 0:
                occupied += 1
                
    print(f'Total de corales: {occupied} / {rows*cols} posiciones')
    print('═════════════════════════════════════════════════════')

# Funcion que genera una grilla con la disposicion de turbinas aleatoria
def createGrid(Kgr, Nturb):
    gr = np.zeros(Kgr*Kgr)
    # randperm in MATLAB: random permutation of integers 1:n
    # Here we want to select Nturb indices from Kgr^2
    indices = np.random.permutation(Kgr*Kgr)[:Nturb]
    gr[indices] = 1
    return gr.reshape((Kgr, Kgr))

# %% Main Execution

if __name__ == "__main__":
    # Clear console (optional)
    # os.system('cls' if os.name == 'nt' else 'clear')
    
    # %% Load Data
    # Data files live in windSymPython/dt alongside this script
    base_path = os.path.join(os.path.dirname(__file__), 'windSymPython', 'dt')
    
    try:
        windSymData = scipy.io.loadmat(os.path.join(base_path, 'WindSym_1.mat'))
        vVec = windSymData['vVec']
        
        pcData = scipy.io.loadmat(os.path.join(base_path, 'pwrCurve.mat'))
        ppPower_aux = pcData['ppPower'][0,0]
        # Create PPoly object similar to f_powerPlantsT_fast.py
        pwrCurve = PPoly(ppPower_aux[2].T, ppPower_aux[1].flatten())
        
    except FileNotFoundError:
        print("Error: Could not find data files in python/windSymPython/dt/")
        sys.exit(1)

    # %% Create Grid with Nturb Turbines
    Kgr   = 20   # Tamaño del Grid (tamaño de cada coral)
    Nturb = 20   # Numero de Turbinas por coral

    # %% Parámetros del arrecife
    reefRows   = 8
    reefCols   = 8
    reefSize   = reefRows * reefCols
    initFill   = 0.60                 # 60% de ocupación inicial
    nInitCoral = round(reefSize * initFill)

    # %% Parámetros del algoritmo CRO
    maxIterations = 100       # Máximo de iteraciones
    targetPower   = 53500000.00 # Potencia objetivo (Raw)

    # %% Inicializar arrecife

    # Arrecife: lista de listas 8x8, cada elemento es un coral (una matriz Kgr x Kgr)
    reef = [[None for _ in range(reefCols)] for _ in range(reefRows)]

    # Elegir posiciones aleatorias para los corales iniciales
    # randperm(reefSize, nInitCoral) -> indices 1 to 64
    idxAll = np.random.permutation(reefSize)[:nInitCoral]
    
    # ind2sub equivalent
    # MATLAB: [rowsInit, colsInit] = ind2sub([reefRows, reefCols], idxAll);
    # Python: unravel_index. Note MATLAB is column-major (Fortran-like), Python is row-major (C-like).
    # However, since we just want random positions, it doesn't strictly matter if we map 1->(0,0) or 1->(0,0) differently,
    # as long as we get unique positions.
    # But to be faithful, if we want exact mapping we should use order='F'.
    rowsInit, colsInit = np.unravel_index(idxAll, (reefRows, reefCols), order='F')

    # Rellenar el 60% del arrecife con corales (disposiciones gr aleatorias)
    for k in range(nInitCoral):
        r = rowsInit[k]
        c = colsInit[k]
        reef[r][c] = createGrid(Kgr, Nturb)

    # visualizar arrecife en forma de matriz mostrando una x en las posiciones ocupadas
    visualizeReef(reef)

    # %% Evaluar Generación Inicial
    print('\n--- Ranking Inicial (Generación Aleatoria) ---')
    initialRanking, reef = evaluateReefPower(reef, vVec, pwrCurve)

    # %% Ejecutar algoritmo CRO
    reef, finalRanking = CRO_Algorithm(reef, vVec, pwrCurve, Kgr, Nturb, maxIterations, targetPower, initialRanking)

    # %% Visualizar arrecife final
    print('\n')
    visualizeReef(reef)
