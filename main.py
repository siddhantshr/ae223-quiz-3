import numpy as np

# # constants
T1 = 288.15
T3 = 1373.15
r = 10
k = 0.4 / 1.4

a = T1 * (r**k - 1)

def _cycle(eta_c: float, eta_t: float, pi_cc: float) -> tuple[float, float, float, float]:
    """Returns the efficiency and slopes of the cycle for given compressor and turbine efficiencies and combustor pressure ratio."""
    b = T3 * (1 - (pi_cc * r) ** (-k))
    T4s = T3 * (pi_cc * r) ** (-k)
    q = (T3 - T1) - a / eta_c
    efficiency = (eta_t * b - a / eta_c) / q

    slope_t = b / q
    slope_c = (a / eta_c**2) * (1 - efficiency) / q
    slope_pi = eta_t * k * T4s / (pi_cc * q)

    S_t = 0.55 * slope_t
    S_c = 0.55 * slope_c
    S_pi = 0.39 * slope_pi
    return efficiency, S_t, S_c, S_pi

def _find_switching_points() -> list[float]:
    """Finds the switching points of ratio of S_c and S_t switching around 1."""
    _switch_points = []

    for eta_t in np.arange(0.4, 0.95, 0.01): # keeping 0.01 as the resolution for eta_t
        for pi_cc in np.arange(0.6, 1.0, 0.01): # keeping 0.01 as the resolution for pi_cc

            compressor_was_winning = False
            for eta_c in np.arange(0.4, 0.95, 0.001): # keeping 0.001 as the resolution for eta_c
                efficiency, S_t, S_c, S_pi = _cycle(eta_c, eta_t, pi_cc)

                if efficiency <= 0:
                    continue

                if S_c > S_t:
                    compressor_was_winning = True
                elif compressor_was_winning:
                    _switch_points.append(eta_c)
                    break
                else:
                    break
    return _switch_points

def _analyze_compressor_vs_combustor(N: int = 100) -> tuple[int, int, float]:
    """Analyzes the compressor vs combustor performance over a grid of design points."""
    working_points = 0
    compressor_wins = 0

    for eta_c in np.linspace(0.4, 0.95, N):
        for eta_t in np.linspace(0.4, 0.95, N):
            for pi_cc in np.linspace(0.6, 1.0, 70):
                efficiency, _, S_c, S_pi = _cycle(eta_c, eta_t, pi_cc)

                if efficiency <= 0:
                    continue

                working_points += 1
                if S_c > S_pi:
                    compressor_wins += 1

    percent = 100 * compressor_wins / working_points if working_points > 0 else 0
    return working_points, compressor_wins, percent

def main() -> None:
    """The main function of the program."""
    switch_points = _find_switching_points()
    print("CHECK 1: switching point between compressor and turbine")
    print("  smallest switching value of eta_c =", round(min(switch_points), 3))
    print("  largest  switching value of eta_c =", round(max(switch_points), 3))

    working_points, compressor_wins, percent = _analyze_compressor_vs_combustor()
    print("\nCHECK 2: compressor vs combustor")
    print("  working design points tested :", working_points)
    print("  points where S_c > S_pi      :", compressor_wins)
    print("  percentage                   :", round(percent, 2), "%")

if __name__ == "__main__":
    main()
