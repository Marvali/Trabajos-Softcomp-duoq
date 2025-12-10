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


# Helper to match MATLAB's uniquetol behavior with a tolerance tied to array magnitude
def unique_tol(array: np.ndarray, tol: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    tol = tol * np.max(np.abs(array))
    array_copy = np.sort(np.copy(array))
    result = [array_copy[0]]
    for i in range(len(array_copy) - 1):
        if np.abs(array_copy[i + 1] - result[-1]) >= tol:
            result.append(array_copy[i + 1])

    ia = []
    for elem in result:
        indice_ia = np.where(np.abs(array - elem) <= tol)[0][0]
        ia.append(indice_ia)

    ic = []
    result_copy = np.copy(result)
    for valor in array:
        indice_ic = np.where(np.abs(result_copy - valor) <= tol)[0][0]
        ic.append(indice_ic)
    return np.array(result), np.array(ia), np.array(ic)


def calculate_coral_power(gr: np.ndarray, vVec: np.ndarray, pwrCurveData: PPoly) -> float:
    if gr is None or gr.size == 0 or np.sum(gr) == 0:
        return 0.0

    nH = vVec.shape[1]
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

    return float(pwr_sum)


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

    entries = []
    if isinstance(existingRanking, np.ndarray):
        existingRanking = existingRanking.tolist()

    for i in range(rows):
        for j in range(cols):
            layout = reef[i][j]
            if layout is not None and layout.size > 0:
                alreadyCalculated = False
                if existingRanking:
                    idx = -1
                    for k, entry in enumerate(existingRanking):
                        if int(entry[1]) == i + 1 and int(entry[2]) == j + 1:
                            idx = k
                            break

                    if idx != -1:
                        entries.append(existingRanking[idx])
                        alreadyCalculated = True

                if not alreadyCalculated:
                    pwr = calculate_coral_power(layout, windSymData, pwrCurveData)
                    entries.append([pwr, i + 1, j + 1])

    if not entries:
        print("No hay corales con potencia.")
        return np.array([]), reef

    entries = np.array(entries)
    idx = np.argsort(entries[:, 0])[::-1]
    coralRanking = entries[idx]

    print("Ranking de corales por potencia (Raw):")
    for k in range(len(coralRanking)):
        print(
            f"{k+1:2d}) Potencia: {coralRanking[k,0]:10.2f}      ->  Coral ({int(coralRanking[k,1])}, {int(coralRanking[k,2])})"
        )
    print("═════════════════════════════════════════════════════")

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
    targetPower: float,
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

        if currentBestPower >= targetPower:
            print(f"¡Objetivo alcanzado! Potencia máxima: {currentBestPower:.2f} >= {targetPower:.2f}")
            break

        if currentBestPower > lastBestPower:
            noImprovementCount = 0
            lastBestPower = currentBestPower
            print(f"¡Mejora detectada! Nueva mejor potencia: {currentBestPower:.2f}")
        else:
            noImprovementCount += 1
            print(f"Sin mejora en {noImprovementCount} generaciones (Mejor actual: {currentBestPower:.2f})")

        if noImprovementCount >= 4:
            print("Parada por estancamiento: No hubo mejora en 4 generaciones consecutivas.")
            break

        nCorals = len(coralRanking)

        print("\n--- Reproducción Sexual (Crossover) ---")

        nSexual = int(np.floor(nCorals * 0.80))
        if nSexual % 2 != 0:
            nSexual -= 1

        if nSexual >= 2:
            worstCorals = coralRanking[nCorals - nSexual :, :]

            pairOrder = np.random.permutation(nSexual)
            nPairs = int(nSexual / 2)

            newChildren = []
            newChildrenPower = []

            for p in range(nPairs):
                idx1 = pairOrder[2 * p]
                idx2 = pairOrder[2 * p + 1]

                parent1_pos = worstCorals[idx1, 1:3].astype(int)
                parent2_pos = worstCorals[idx2, 1:3].astype(int)

                parent1 = reef[parent1_pos[0] - 1][parent1_pos[1] - 1]
                parent2 = reef[parent2_pos[0] - 1][parent2_pos[1] - 1]

                child = sexual_reproduction(parent1, parent2, Kgr, maxTurb)
                newChildren.append(child)

                newChildrenPower.append(calculate_coral_power(child, vVec, pwrCurve))

            print(f"Generados {nPairs} hijos por reproducción sexual")

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

        for m in range(nAsexual):
            parent_pos = bestCorals[m, 1:3].astype(int)
            parent = reef[parent_pos[0] - 1][parent_pos[1] - 1]

            mutant = asexual_reproduction(parent, Kgr, maxTurb)
            newMutants.append(mutant)

            newMutantsPower.append(calculate_coral_power(mutant, vVec, pwrCurve))

        print(f"Generados {nAsexual} hijos por reproducción asexual")

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
        print(f"Mejor potencia: {coralRanking[0, 0]:.2f}")
        print(f"Peor potencia: {coralRanking[-1, 0]:.2f}")
        print(f"Total corales: {len(coralRanking)}")

    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                    RESULTADO FINAL                       ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    finalRanking = coralRanking

    print("Ranking final de corales por potencia (Raw):")
    limit = min(20, len(finalRanking))
    for k in range(limit):
        print(
            f"{k+1:2d}) Potencia: {finalRanking[k,0]:10.2f}      ->  Coral ({int(finalRanking[k,1])}, {int(finalRanking[k,2])})"
        )

    if len(finalRanking) > 20:
        print(f"... y {len(finalRanking) - 20} corales más")

    print("═════════════════════════════════════════════════════════════")
    print(
        f"Mejor solución encontrada: {finalRanking[0,0]:.2f} en posición ({int(finalRanking[0,1])}, {int(finalRanking[0,2])})"
    )

    plt.figure()
    plt.plot(range(len(bestPowerHistory)), bestPowerHistory, "b-o", linewidth=2)
    plt.title("Progresión de la Mejor Potencia (Algoritmo CRO)")
    plt.xlabel("Iteración")
    plt.ylabel("Potencia (Raw)")
    plt.grid(True)
    print("Gráfico de progresión generado.")
    plt.show()

    return reef, finalRanking


def visualize_reef(reef: List[List[Optional[np.ndarray]]]) -> None:
    rows = len(reef)
    cols = len(reef[0])

    print("═════════════════════════════════════════════════════")
    print("           Mapa del arrecife de corales")
    print("           (X = coral ocupado, _ = vacío)")
    print("═════════════════════════════════════════════════════")
    print("\n")

    print("      ", end="")
    for j in range(1, cols + 1):
        print(f" {j}  ", end="")
    print("\n", end="")

    print("    ┌", end="")
    for j in range(cols):
        print("───", end="")
        if j < cols - 1:
            print("┬", end="")
    print("┐")

    for i in range(rows):
        print(f" {i+1}  │", end="")
        for j in range(cols):
            if reef[i][j] is not None and reef[i][j].size > 0:
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

    occupied = 0
    for i in range(rows):
        for j in range(cols):
            if reef[i][j] is not None and reef[i][j].size > 0:
                occupied += 1

    print(f"Total de corales: {occupied} / {rows*cols} posiciones")
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
