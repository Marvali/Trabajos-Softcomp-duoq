import math
import os
import sys
import time
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import scipy.io
from scipy.interpolate import PPoly

from windSymPython.f_powerPlants_f1 import f_powerPlants_f1
from windSymPython.f_powerPlants_f2 import f_powerPlants_f2
from numba import njit
import pickle
from joblib import Parallel, delayed

class PersistentCoralCache:
    def __init__(self, filename="coral_cache.pkl"):
        self.filename = filename
        self.cache = {}
        self.modified = False
        self._load()

    def _load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "rb") as f:
                    self.cache = pickle.load(f)
                print(f"Cache cargado: {len(self.cache)} corales.")
            except Exception as e:
                print(f"Error cargando cache: {e}")
                self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def put(self, key, value):
        if key not in self.cache:
            self.cache[key] = value
            self.modified = True

    def save(self):
        if self.modified:
            try:
                with open(self.filename, "wb") as f:
                    pickle.dump(self.cache, f)
                self.modified = False
                print("Cache guardado en disco.")
            except Exception as e:
                print(f"Error guardando cache: {e}")

CORAL_CACHE = PersistentCoralCache()


@njit
def unique_tol(array: np.ndarray, tol: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Scale tolerance
    max_val = np.max(np.abs(array))
    tol = tol * max_val
    
    # Sort a copy
    array_copy = np.sort(array.copy())
    
    # Find unique elements
    n = len(array_copy)
    temp_res = np.empty(n, dtype=array.dtype)
    count = 0
    
    if n > 0:
        temp_res[0] = array_copy[0]
        count = 1
        for i in range(1, n):
            if np.abs(array_copy[i] - temp_res[count-1]) >= tol:
                temp_res[count] = array_copy[i]
                count += 1
                
    result = temp_res[:count]
    
    # Calculate ia
    ia = np.zeros(count, dtype=np.int64)
    for i in range(count):
        elem = result[i]
        for j in range(len(array)):
            if np.abs(array[j] - elem) <= tol:
                ia[i] = j
                break
    
    # Calculate ic
    ic = np.zeros(len(array), dtype=np.int64)
    for i in range(len(array)):
        valor = array[i]
        for j in range(count):
            if np.abs(result[j] - valor) <= tol:
                ic[i] = j
                break
                
    return result, ia, ic


def _calculate_coral_power_pure(gr: np.ndarray, vVec: np.ndarray, pwrCurveData: PPoly) -> float:
    """
    Función pura para calcular la potencia media anual de un coral en MW.
    Ideal para ejecución en paralelo.
    
    Returns:
        Potencia media anual en MW (promedio sobre 8760 horas)
    """
    if gr is None or gr.size == 0 or np.sum(gr) == 0:
        return 0.0

    nH = vVec.shape[1]  # 8760 horas
    avVec = np.arctan2(vVec[1, :], vVec[0, :])
    angVec, ia, ic = unique_tol(avVec, 1e-15)

    Nturb = int(np.sum(gr))
    rUDef_T = np.zeros((Nturb, Nturb, nH))

    for l in range(len(angVec)):
        rUDef = f_powerPlants_f1(vVec[:, ia[l]], gr, Nturb)
        rUDef_T[:, :, ic == l] = np.tile(rUDef[:, :, None], [1, 1, np.count_nonzero(ic == l)])

    pwr_sum = 0.0
    for l in range(nH):
        pwr_t, _, _, _, _, _ = f_powerPlants_f2(vVec[:, l], gr, pwrCurveData, rUDef_T[:, :, l], Nturb)
        pwr_sum += pwr_t

    # Calcular potencia media (kW promedio) y convertir a MW
    pwr_mean_kw = pwr_sum / nH
    pwr_mean_mw = pwr_mean_kw / 1000.0
    
    return float(pwr_mean_mw)


def calculate_coral_power(gr: np.ndarray, vVec: np.ndarray, pwrCurveData: PPoly) -> float:
    if gr is None or gr.size == 0 or np.sum(gr) == 0:
        return 0.0

    # Generar clave única para el array del coral
    gr_key = np.ascontiguousarray(gr).tobytes()
    cached_power = CORAL_CACHE.get(gr_key)
    
    if cached_power is not None:
        return cached_power

    # Si no está en cache, calculamos
    pwr_sum = _calculate_coral_power_pure(gr, vVec, pwrCurveData)

    CORAL_CACHE.put(gr_key, pwr_sum)
    return pwr_sum


def evaluate_reef_power(
    reef: List[List[Optional[np.ndarray]]],
    windSymData: np.ndarray,
    pwrCurveData: PPoly,
    existingRanking: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, List[List[Optional[np.ndarray]]]]:
    rows = len(reef)
    cols = len(reef[0])

    if existingRanking is None:
        existingRanking = []

    print("Evaluando potencia de los corales...")

    # Identificar qué corales necesitan cálculo y cuáles están en caché
    corals_to_eval_indices = []
    corals_to_eval_layouts = []
    
    # Estructura provisional para resultados: map (i, j) -> power
    reef_powers = {}
    
    for i in range(rows):
        for j in range(cols):
            layout = reef[i][j]
            if layout is not None and layout.size > 0:
                gr_key = np.ascontiguousarray(layout).tobytes()
                cached_power = CORAL_CACHE.get(gr_key)
                
                if cached_power is not None:
                    reef_powers[(i, j)] = cached_power
                else:
                    corals_to_eval_indices.append((i, j))
                    corals_to_eval_layouts.append(layout)

    # Calcular en paralelo los que faltan
    if corals_to_eval_layouts:
        print(f"Calculando {len(corals_to_eval_layouts)} corales en paralelo...")
        n_jobs = -1  # Usar todos los núcleos disponibles
        results = Parallel(n_jobs=n_jobs)(
            delayed(_calculate_coral_power_pure)(layout, windSymData, pwrCurveData)
            for layout in corals_to_eval_layouts
        )
        
        # Guardar en caché y en estructura provisional
        for (i, j), layout, pwr in zip(corals_to_eval_indices, corals_to_eval_layouts, results):
            gr_key = np.ascontiguousarray(layout).tobytes()
            CORAL_CACHE.put(gr_key, pwr)
            reef_powers[(i, j)] = pwr

    # Construir la lista final de entries
    entries = []
    for (i, j), pwr in reef_powers.items():
        entries.append([pwr, i + 1, j + 1])

    if not entries:
        print("No hay corales con potencia.")
        return np.array([]), reef

    entries = np.array(entries)
    idx = np.argsort(entries[:, 0])[::-1]
    coralRanking = entries[idx]

    print("Ranking de corales por potencia media anual:")
    for k in range(len(coralRanking)):
        print(
            f"{k+1:2d}) Potencia: {coralRanking[k,0]} MW      ->  Coral ({int(coralRanking[k,1])}, {int(coralRanking[k,2])})"
        )
    print("═════════════════════════════════════════════════════════")

    CORAL_CACHE.save()
    return coralRanking, reef


def sexual_reproduction(parent1: np.ndarray, parent2: np.ndarray, Kgr: int, maxTurb: int) -> np.ndarray:
    combined = np.logical_or(parent1, parent2)
    turbinePositions = np.flatnonzero(combined)

    if len(turbinePositions) > maxTurb:
        selectedIdx = np.random.choice(len(turbinePositions), maxTurb, replace=False)
        turbinePositions = turbinePositions[selectedIdx]

    childCoral = np.zeros((Kgr, Kgr))
    np.put(childCoral, turbinePositions, 1)

    return childCoral


def asexual_reproduction(parent: np.ndarray, Kgr: int, maxTurb: int) -> np.ndarray:
    childCoral = np.copy(parent)
    nMutations = np.random.randint(1, 6)

    turbinePositions = np.flatnonzero(parent)
    emptyPositions = np.flatnonzero(parent == 0)

    for _ in range(nMutations):
        if len(turbinePositions) > 0 and len(emptyPositions) > 0:
            removeIdx = np.random.randint(len(turbinePositions))
            addIdx = np.random.randint(len(emptyPositions))

            remPos = turbinePositions[removeIdx]
            addPos = emptyPositions[addIdx]

            np.put(childCoral, [remPos], 0)
            np.put(childCoral, [addPos], 1)

            turbinePositions[removeIdx] = emptyPositions[addIdx]
            emptyPositions = np.delete(emptyPositions, addIdx)

    return childCoral


def find_empty_positions(reef: List[List[Optional[np.ndarray]]]) -> np.ndarray:
    rows = len(reef)
    cols = len(reef[0])
    emptyPositions = []
    for i in range(rows):
        for j in range(cols):
            if reef[i][j] is None or reef[i][j].size == 0:
                emptyPositions.append([i + 1, j + 1])
    return np.array(emptyPositions)


def cro_algorithm(
    reef: List[List[Optional[np.ndarray]]],
    vVec: np.ndarray,
    pwrCurve: PPoly,
    Kgr: int,
    maxTurb: int,
    maxIter: int,
    maxStagnation: int,
    coralRanking: Optional[np.ndarray] = None,
) -> Tuple[List[List[Optional[np.ndarray]]], np.ndarray]:
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║         ALGORITMO CRO - Coral Reef Optimization          ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print("\n")

    if coralRanking is None or len(coralRanking) == 0:
        coralRanking, reef = evaluate_reef_power(reef, vVec, pwrCurve)

    bestPowerHistory: List[float] = []
    noImprovementCount = 0
    lastBestPower = 0.0

    if len(coralRanking) > 0:
        lastBestPower = coralRanking[0, 0]
        bestPowerHistory.append(lastBestPower)

    for iter_num in range(1, maxIter + 1):
        print(f"\n══════════════ ITERACIÓN {iter_num}/{maxIter} ══════════════\n")

        currentBestPower = coralRanking[0, 0]

        if currentBestPower > lastBestPower:
            noImprovementCount = 0
            lastBestPower = currentBestPower
            print(f"¡Mejora detectada! Nueva mejor potencia: {currentBestPower} MW")
        else:
            noImprovementCount += 1
            print(f"Sin mejora en {noImprovementCount} generaciones (Mejor actual: {currentBestPower} MW)")

        if noImprovementCount >= maxStagnation:
            print(f"Parada por estancamiento: No hubo mejora en {maxStagnation} generaciones consecutivas.")
            break

        nCorals = len(coralRanking)

        print("\n--- Reproducción Sexual (Crossover) ---")

        nSexual = int(np.floor(nCorals * 0.80))
        if nSexual % 2 != 0:
            nSexual -= 1

        if nSexual >= 2:
            sexualCorals = coralRanking[:nSexual, :]

            pairOrder = np.random.permutation(nSexual)
            nPairs = int(nSexual / 2)

            newChildren = []
            newChildrenPower = []

            print(f"Generando {nPairs} parejas para reproducción sexual...")

            # 1. Generación por lotes (Batch Generation)
            parents_pairs = []
            for p in range(nPairs):
                idx1 = pairOrder[2 * p]
                idx2 = pairOrder[2 * p + 1]

                parent1_pos = sexualCorals[idx1, 1:3].astype(int)
                parent2_pos = sexualCorals[idx2, 1:3].astype(int)

                parent1 = reef[parent1_pos[0] - 1][parent1_pos[1] - 1]
                parent2 = reef[parent2_pos[0] - 1][parent2_pos[1] - 1]
                
                parents_pairs.append((parent1, parent2))

            # No paralelizamos la generación (es rápida), paralelizamos la evaluación
            newChildren = [
                sexual_reproduction(p1, p2, Kgr, maxTurb) for p1, p2 in parents_pairs
            ]
            
            # 2. Evaluación en paralelo (Batch Evaluation)
            # Primero verificar caché para evitar re-calcular lo que ya tenemos
            children_to_calc_indices = []
            children_to_calc_layouts = []
            newChildrenPower = [0.0] * nPairs
            
            for idx, child in enumerate(newChildren):
                gr_key = np.ascontiguousarray(child).tobytes()
                cached = CORAL_CACHE.get(gr_key)
                if cached is not None:
                    newChildrenPower[idx] = cached
                else:
                    children_to_calc_indices.append(idx)
                    children_to_calc_layouts.append(child)
            
            if children_to_calc_layouts:
               results = Parallel(n_jobs=-1)(
                   delayed(_calculate_coral_power_pure)(child, vVec, pwrCurve)
                   for child in children_to_calc_layouts
               )
               # Actualizar caché y lista de potencias
               for idx, child, val in zip(children_to_calc_indices, children_to_calc_layouts, results):
                   gr_key = np.ascontiguousarray(child).tobytes()
                   CORAL_CACHE.put(gr_key, val)
                   newChildrenPower[idx] = val

            print(f"Evaluados {nPairs} hijos (sexual)")

            # 3. Inserción Secuencial (Batch Update)
            for p in range(nPairs):
                emptyPos = find_empty_positions(reef)

                if len(emptyPos) > 0:
                    posIdx = np.random.randint(len(emptyPos))
                    r = int(emptyPos[posIdx, 0])
                    c = int(emptyPos[posIdx, 1])

                    reef[r - 1][c - 1] = newChildren[p]
                    new_entry = np.array([[newChildrenPower[p], r, c]])
                    coralRanking = np.vstack([coralRanking, new_entry])
                else:
                    sortIdx = np.argsort(coralRanking[:, 0])
                    worstIdx = sortIdx[0]

                    if newChildrenPower[p] > coralRanking[worstIdx, 0]:
                        r = int(coralRanking[worstIdx, 1])
                        c = int(coralRanking[worstIdx, 2])
                        reef[r - 1][c - 1] = newChildren[p]
                        coralRanking[worstIdx, 0] = newChildrenPower[p]

            idx = np.argsort(coralRanking[:, 0])[::-1]
            coralRanking = coralRanking[idx]

        print("\n--- Reproducción Asexual (Mutación) ---")

        nCorals = len(coralRanking)
        nAsexual = max(1, int(np.floor(nCorals * 0.20)))

        bestCorals = coralRanking[:nAsexual, :]

        newMutants = []
        newMutantsPower = []

        # 1. Generación por lotes (Batch Generation)
        newMutants = []
        for m in range(nAsexual):
            parent_pos = bestCorals[m, 1:3].astype(int)
            parent = reef[parent_pos[0] - 1][parent_pos[1] - 1]
            mutant = asexual_reproduction(parent, Kgr, maxTurb)
            newMutants.append(mutant)

        # 2. Evaluación en paralelo (Batch Evaluation)
        newMutantsPower = [0.0] * nAsexual
        mutants_to_calc_indices = []
        mutants_to_calc_layouts = []

        for idx, mutant in enumerate(newMutants):
            gr_key = np.ascontiguousarray(mutant).tobytes()
            cached = CORAL_CACHE.get(gr_key)
            if cached is not None:
                newMutantsPower[idx] = cached
            else:
                mutants_to_calc_indices.append(idx)
                mutants_to_calc_layouts.append(mutant)

        if mutants_to_calc_layouts:
            results = Parallel(n_jobs=-1)(
                delayed(_calculate_coral_power_pure)(mutant, vVec, pwrCurve)
                for mutant in mutants_to_calc_layouts
            )
            for idx, mutant, val in zip(mutants_to_calc_indices, mutants_to_calc_layouts, results):
                gr_key = np.ascontiguousarray(mutant).tobytes()
                CORAL_CACHE.put(gr_key, val)
                newMutantsPower[idx] = val

        print(f"Evaluados {nAsexual} hijos (asexual)")

        # 3. Inserción Secuencial (Batch Update)
        for m in range(nAsexual):
            emptyPos = find_empty_positions(reef)

            if len(emptyPos) > 0:
                posIdx = np.random.randint(len(emptyPos))
                r = int(emptyPos[posIdx, 0])
                c = int(emptyPos[posIdx, 1])
                reef[r - 1][c - 1] = newMutants[m]
                new_entry = np.array([[newMutantsPower[m], r, c]])
                coralRanking = np.vstack([coralRanking, new_entry])
            else:
                sortIdx = np.argsort(coralRanking[:, 0])
                worstIdx = sortIdx[0]

                if newMutantsPower[m] > coralRanking[worstIdx, 0]:
                    r = int(coralRanking[worstIdx, 1])
                    c = int(coralRanking[worstIdx, 2])
                    reef[r - 1][c - 1] = newMutants[m]
                    coralRanking[worstIdx, 0] = newMutantsPower[m]

        idx = np.argsort(coralRanking[:, 0])[::-1]
        coralRanking = coralRanking[idx]

        bestPowerHistory.append(coralRanking[0, 0])

        print(f"\n--- Estado tras iteración {iter_num} ---")
        print(f"Mejor potencia: {coralRanking[0, 0]} MW")
        print(f"Peor potencia: {coralRanking[-1, 0]} MW")
        print(f"Total corales: {len(coralRanking)}")
        
        # Mostrar disposición del mejor coral
        best_pos = coralRanking[0, 1:3].astype(int)
        best_coral = reef[best_pos[0] - 1][best_pos[1] - 1]
        print("\n")
        visualize_reef(best_coral)

    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                    RESULTADO FINAL                       ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    finalRanking = coralRanking

    print("Ranking final de corales por potencia media anual:")
    limit = min(20, len(finalRanking))
    for k in range(limit):
        print(
            f"{k+1:2d}) Potencia: {finalRanking[k,0]} MW      ->  Coral ({int(finalRanking[k,1])}, {int(finalRanking[k,2])})"
        )

    if len(finalRanking) > 20:
        print(f"... y {len(finalRanking) - 20} corales mas")

    print("----------------------------------------------------------------")
    print(
        f"Mejor solucion encontrada: {finalRanking[0,0]} MW en posicion ({int(finalRanking[0,1])}, {int(finalRanking[0,2])})"
    )

    if len(finalRanking) > 0:
        best_pos = finalRanking[0, 1:3].astype(int)
        best_coral = reef[best_pos[0] - 1][best_pos[1] - 1]
        print("\nDisposicion final ganadora:")
        visualize_reef(best_coral)

    plt.figure()
    plt.plot(range(len(bestPowerHistory)), bestPowerHistory, "b-o", linewidth=2)
    plt.title("Progresión de la Mejor Potencia Media Anual (Algoritmo CRO)")
    plt.xlabel("Iteración")
    plt.ylabel("Potencia Media (MW)")
    plt.grid(True)
    print("Gráfico de progresión generado.")
    plt.show()

    CORAL_CACHE.save()
    return reef, finalRanking


def visualize_reef(coral: np.ndarray) -> None:
    if coral is None or coral.size == 0:
        print("No hay coral para visualizar")
        return
    
    rows = coral.shape[0]
    cols = coral.shape[1]

    if max(rows, cols) > 30:
        print("----------------------------------------------------------------")
        print("Disposicion de molinos (modo compacto)")
        print("(X = molino, _ = vacio)")
        print("----------------------------------------------------------------")
        for i in range(rows):
            row_str = "".join("X" if coral[i][j] == 1 else "_" for j in range(cols))
            print(f"{i+1:2d} {row_str}")
        print("")
        n_turbines = int(np.sum(coral))
        total_positions = rows * cols
        print(f"Total de molinos: {n_turbines} / {total_positions} posiciones")
        print("----------------------------------------------------------------")
        return

    print("═════════════════════════════════════════════════════")
    print("     Disposición de molinos en el mejor coral")
    print("           (X = molino, _ = vacío)")
    print("═════════════════════════════════════════════════════")
    print("\n")

    print("      ", end="")
    for j in range(1, cols + 1):
        print(f" {j:2d} ", end="")
    print("\n", end="")

    print("    ┌", end="")
    for j in range(cols):
        print("───", end="")
        if j < cols - 1:
            print("┬", end="")
    print("┐")

    for i in range(rows):
        print(f" {i+1:2d} │", end="")
        for j in range(cols):
            if coral[i][j] == 1:
                print(" X ", end="")
            else:
                print(" _ ", end="")
            if j < cols - 1:
                print("│", end="")
        print("│")

        if i < rows - 1:
            print("    ├", end="")
            for j in range(cols):
                print("───", end="")
                if j < cols - 1:
                    print("┼", end="")
            print("┤")

    print("    └", end="")
    for j in range(cols):
        print("───", end="")
        if j < cols - 1:
            print("┴", end="")
    print("┘")
    print("\n")

    n_turbines = int(np.sum(coral))
    total_positions = rows * cols

    print(f"Total de molinos: {n_turbines} / {total_positions} posiciones")
    print("═════════════════════════════════════════════════════")


def create_grid(Kgr: int, Nturb: int) -> np.ndarray:
    gr = np.zeros(Kgr * Kgr)
    indices = np.random.permutation(Kgr * Kgr)[:Nturb]
    gr[indices] = 1
    return gr.reshape((Kgr, Kgr))


def create_initial_reef(
    reefRows: int,
    reefCols: int,
    Kgr: int,
    Nturb: int,
    initFill: float,
) -> List[List[Optional[np.ndarray]]]:
    reefSize = reefRows * reefCols
    nInitCoral = round(reefSize * initFill)

    reef: List[List[Optional[np.ndarray]]] = [[None for _ in range(reefCols)] for _ in range(reefRows)]

    idxAll = np.random.permutation(reefSize)[:nInitCoral]
    rowsInit, colsInit = np.unravel_index(idxAll, (reefRows, reefCols), order="F")

    for k in range(nInitCoral):
        r = rowsInit[k]
        c = colsInit[k]
        reef[r][c] = create_grid(Kgr, Nturb)

    return reef


def load_wind_data(base_path: str) -> Tuple[np.ndarray, PPoly]:
    windSymData = scipy.io.loadmat(os.path.join(base_path, "WindSym_1.mat"))
    vVec = windSymData["vVec"]

    pcData = scipy.io.loadmat(os.path.join(base_path, "pwrCurve.mat"))
    ppPower_aux = pcData["ppPower"][0, 0]
    pwrCurve = PPoly(ppPower_aux[2].T, ppPower_aux[1].flatten())

    return vVec, pwrCurve
