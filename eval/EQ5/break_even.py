# Full, self-contained code to generate the combined break-even plot for BioJava and PMD
# (and optionally the individual plots). This saves PNG files to /mnt/data and prints paths.

import numpy as np
import matplotlib.pyplot as plt

# --- Inputs: break-even runs (from your computed results) ---
BIOJAVA_ENERGY_RUNS = 229.67166655373245
BIOJAVA_LATENCY_RUNS = 414.40117560149486
PMD_ENERGY_RUNS = 717.615309126595
PMD_LATENCY_RUNS = 5186.363321874111

# --- Usage frequencies to plot (runs per day) ---
runs_per_day = np.array([5, 10, 20, 50, 100, 200, 500, 1000], dtype=float)

def days_to_break_even(break_even_runs, runs_per_day_values):
    """Compute days to break-even = break-even runs / runs per day."""
    return break_even_runs / runs_per_day_values

# --- Compute curves (days to break-even for each metric/app) ---
biojava_energy_days  = days_to_break_even(BIOJAVA_ENERGY_RUNS,  runs_per_day)
biojava_latency_days = days_to_break_even(BIOJAVA_LATENCY_RUNS, runs_per_day)
pmd_energy_days      = days_to_break_even(PMD_ENERGY_RUNS,      runs_per_day)
pmd_latency_days     = days_to_break_even(PMD_LATENCY_RUNS,     runs_per_day)

# --- Plot: Combined (BioJava + PMD) ---
plt.figure(figsize=(7, 5))
plt.plot(runs_per_day, biojava_energy_days,  marker='o', label='BioJava Energy')
plt.plot(runs_per_day, biojava_latency_days, marker='s', label='BioJava Latency')
plt.plot(runs_per_day, pmd_energy_days,      marker='^', label='PMD Energy')
plt.plot(runs_per_day, pmd_latency_days,     marker='d', label='PMD Latency')
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Runs per day (log scale)')
plt.ylabel('Days to break-even (log scale)')
plt.title('Time to Break-even vs Usage Frequency')
plt.legend()
plt.grid(True, which='both', linestyle='-', linewidth=0.5)  # solid grid lines
plt.xticks(runs_per_day, runs_per_day)  # detailed ticks from the dataset
plt.yticks(
    [1, 5, 10, 20, 50, 100, 200, 500, 1000],
    [str(t) for t in [1, 5, 10, 20, 50, 100, 200, 500, 1000]]
)
plt.tight_layout()
combined_fig_path = 'combined_break_even.png'
plt.savefig(combined_fig_path, dpi=200)
plt.close()

combined_fig_path

# Let's make a combined plot similar to "Step 3" style:
# - X-axis: executions per month (linear scale)
# - Y-axis: time to break-even (in months, linear scale)
# - This will make the table-style interpretation easier to visualize.

# --- Convert to executions per month (assuming 30 days/month) ---
exec_per_month = runs_per_day * 30

# --- Compute time to break-even in months ---
def months_to_break_even(break_even_runs, exec_month_values):
    return break_even_runs / exec_month_values

biojava_energy_months  = months_to_break_even(BIOJAVA_ENERGY_RUNS,  exec_per_month)
biojava_latency_months = months_to_break_even(BIOJAVA_LATENCY_RUNS, exec_per_month)
pmd_energy_months      = months_to_break_even(PMD_ENERGY_RUNS,      exec_per_month)
pmd_latency_months     = months_to_break_even(PMD_LATENCY_RUNS,     exec_per_month)

# --- Plot ---
plt.figure(figsize=(7, 5))
plt.plot(exec_per_month, biojava_energy_months,  marker='o', label='BioJava Energy')
plt.plot(exec_per_month, biojava_latency_months, marker='s', label='BioJava Latency')
plt.plot(exec_per_month, pmd_energy_months,      marker='^', label='PMD Energy')
plt.plot(exec_per_month, pmd_latency_months,     marker='d', label='PMD Latency')

plt.xlabel('Executions per month')
plt.ylabel('Months to break-even')
plt.title('Time to Break-even vs Monthly Execution Frequency')
plt.legend()
plt.grid(True, linestyle='--', linewidth=0.5)
plt.tight_layout()

linear_fig_path = 'combined_break_even_linear.png'
plt.savefig(linear_fig_path, dpi=200)
plt.close()

linear_fig_path

# Hybrid plot: X-axis log scale (executions/month), Y-axis linear scale (months to break-even)

plt.figure(figsize=(7, 5))
plt.plot(exec_per_month, biojava_energy_months,  marker='o', label='BioJava Energy')
plt.plot(exec_per_month, biojava_latency_months, marker='s', label='BioJava Latency')
plt.plot(exec_per_month, pmd_energy_months,      marker='^', label='PMD Energy')
plt.plot(exec_per_month, pmd_latency_months,     marker='d', label='PMD Latency')

plt.xscale('log')  # Wide range of execution frequencies
plt.xlabel('Executions per month (log scale)')
plt.ylabel('Months to break-even (linear scale)')
plt.title('Time to Break-even vs Monthly Execution Frequency')
plt.legend()
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

plt.tight_layout()
hybrid_fig_path = 'combined_break_even_hybrid.png'
plt.savefig(hybrid_fig_path, dpi=200)
plt.close()

hybrid_fig_path