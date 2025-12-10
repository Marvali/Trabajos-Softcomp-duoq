import os
import sys

from reef_optimization import (
    cro_algorithm,
    create_initial_reef,
    evaluate_reef_power,
    load_wind_data,
    visualize_reef,
)


def main() -> None:
    base_path = os.path.join(os.path.dirname(__file__), "windSymPython", "dt")

    try:
        vVec, pwrCurve = load_wind_data(base_path)
    except FileNotFoundError:
        print("Error: Could not find data files in windSymPython/dt/")
        sys.exit(1)

    Kgr = 20
    Nturb = 20

    reef_rows = 8
    reef_cols = 8
    init_fill = 0.60

    max_iterations = 100
    target_power = 53.50  # MW (potencia media anual objetivo)

    reef = create_initial_reef(reef_rows, reef_cols, Kgr, Nturb, init_fill)

    print("\n--- Ranking Inicial (Generación Aleatoria) ---")
    initialRanking, reef = evaluate_reef_power(reef, vVec, pwrCurve)
    
    if len(initialRanking) > 0:
        best_pos = initialRanking[0, 1:3].astype(int)
        best_coral = reef[best_pos[0] - 1][best_pos[1] - 1]
        visualize_reef(best_coral)

    reef, finalRanking = cro_algorithm(
        reef,
        vVec,
        pwrCurve,
        Kgr,
        Nturb,
        max_iterations,
        target_power,
        initialRanking,
    )


if __name__ == "__main__":
    main()
