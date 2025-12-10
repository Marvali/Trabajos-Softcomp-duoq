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
    target_power = 53500000.00

    reef = create_initial_reef(reef_rows, reef_cols, Kgr, Nturb, init_fill)

    visualize_reef(reef)

    print("\n--- Ranking Inicial (Generación Aleatoria) ---")
    initialRanking, reef = evaluate_reef_power(reef, vVec, pwrCurve)

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

    print("\n")
    visualize_reef(reef)


if __name__ == "__main__":
    main()
