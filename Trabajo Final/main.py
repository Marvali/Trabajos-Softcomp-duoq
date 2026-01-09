import os
import sys
import sys
sys.stdout.reconfigure(encoding='utf-8')

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

    max_iterations = 150
    max_stagnation = 10 # Iteraciones maximas sin mejora

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
        max_stagnation,
        initialRanking,
    )


if __name__ == "__main__":
    main()
