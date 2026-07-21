import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def main():
    # Set up CLI argument parser
    parser = argparse.ArgumentParser(
        description="Process BLDC motor thrust stand CSV benchmark data."
    )
    parser.add_argument(
        "csv_path",
        type=Path,
        help="Relative or absolute path to the benchmark CSV file (e.g., benchmark_runs/test_run.csv)"
    )
    
    args = parser.parse_args()
    csv_file = args.csv_path.resolve()

    # Validate file existence
    if not csv_file.is_file():
        print(f"[ERROR] Specified CSV file does not exist: {args.csv_path}")
        return

    print(f"[INFO] Loading benchmark data from: {csv_file}")
    df = pd.read_csv(csv_file)

    # 1. Curve Fitting
    # Quadratic fit for Thrust (g) vs. Throttle (µs)
    p_thrust = np.polyfit(df["throttle_us"], df["thrust_g"], 2)
    fit_thrust = np.poly1d(p_thrust)

    # Cubic fit for Power (W) vs. Throttle (µs)
    p_power = np.polyfit(df["throttle_us"], df["power_w"], 3)
    fit_power = np.poly1d(p_power)

    # Print polynomial equations
    print("\n--- Model Fitting Summary ---")
    print(f"Thrust Fit (2nd order): Thrust(PWM) = {p_thrust[0]:.6e}*PWM² + {p_thrust[1]:.6e}*PWM + {p_thrust[2]:.4f}")
    print(f"Power Fit  (3rd order): Power(PWM)  = {p_power[0]:.6e}*PWM³ + {p_power[1]:.6e}*PWM² + {p_power[2]:.6e}*PWM + {p_power[3]:.4f}")

    # 2. Plotting
    fig, ax1 = plt.subplots(figsize=(9, 5.5))

    # Dense PWM range for smooth curve plotting
    pwm_dense = np.linspace(df["throttle_us"].min(), df["throttle_us"].max(), 100)

    # Plot Measured vs Fitted Thrust
    ax1.set_xlabel("Throttle Pulse Width (µs)")
    ax1.set_ylabel("Thrust (g)", color="tab:blue")
    ax1.plot(df["throttle_us"], df["thrust_g"], 'o', color="tab:blue", label="Measured Thrust")
    ax1.plot(pwm_dense, fit_thrust(pwm_dense), '--', color="tab:blue", label="Fit (Quadratic)")
    ax1.tick_params(axis='y', labelcolor="tab:blue")
    ax1.grid(True, linestyle=':', alpha=0.6)

    # Plot Measured vs Fitted Power on twin axis
    ax2 = ax1.twinx()
    ax2.set_ylabel("Electrical Power (W)", color="tab:red")
    ax2.plot(df["throttle_us"], df["power_w"], 's', color="tab:red", label="Measured Power")
    ax2.plot(pwm_dense, fit_power(pwm_dense), ':', color="tab:red", label="Fit (Cubic)")
    ax2.tick_params(axis='y', labelcolor="tab:red")

    title_name = csv_file.stem.replace('_', ' ').title()
    plt.title(f"Thrust & Power Characterization\n({title_name})")
    fig.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()