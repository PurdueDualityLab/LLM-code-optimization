import os
import subprocess
import time

# ── CONFIG ──────────────────────────────────────────────────────────────────────
WARMUP_RUNS    = 2
NTIMES         = 5
LOG_DIR        = "/home/hpeng/E2COOL/src/runtime_logs/"
PERF_EVENTS    = "cycles"

# RAPL MSR offsets
MSR_BASE               = "/dev/cpu/{}/msr"
MSR_RAPL_POWER_UNIT    = 0x606
MSR_PKG_ENERGY_STATUS  = 0x611
MSR_PP0_ENERGY_STATUS  = 0x639
MSR_DRAM_ENERGY_STATUS = 0x619
# ── END CONFIG ──────────────────────────────────────────────────────────────────


def read_msr(core: int, msr_reg: int) -> int:
    """Low‑level: read a 64‑bit MSR register from /dev/cpu/<core>/msr."""
    with open(MSR_BASE.format(core), "rb") as f:
        f.seek(msr_reg)
        return int.from_bytes(f.read(8), "little")


def get_energy_units(core: int = 0) -> float:
    """Parse MSR_RAPL_POWER_UNIT to get Joules‑per‑tick."""
    raw = read_msr(core, MSR_RAPL_POWER_UNIT)
    # bits 8–12 hold the energy unit exponent
    exp = (raw >> 8) & 0x1F
    return pow(0.5, exp)


def read_energy(core: int = 0, domain: str = "package") -> float:
    """
    Read energy consumed so far in Joules from RAPL.
      domain = "package" | "core" | "dram"
    """
    if domain == "package":
        reg = MSR_PKG_ENERGY_STATUS
    elif domain == "core":
        reg = MSR_PP0_ENERGY_STATUS
    elif domain == "dram":
        reg = MSR_DRAM_ENERGY_STATUS
    else:
        raise ValueError(f"Unknown RAPL domain: {domain!r}")
    return read_msr(core, reg) * get_energy_units(core)


def run_benchmark(command: str, language: str, test_name: str, core: int = 0):
    """
    Benchmark an arbitrary shell command:
      • warm‑ups
      • NTIMES runs measuring:
        – elapsed time (time.time())
        – CPU cycles (perf stat -e cycles)
        – peak memory (time -f '%M')
        – energy (package, core, DRAM)
      • logs to `<LOG_DIR>/<language>.csv`
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, f"{language}.csv")

    # Warm‑up runs
    for _ in range(WARMUP_RUNS):
        subprocess.run(command, shell=True, check=True)

    total_start = time.time()
    with open(log_path, "a") as fp:
        for _ in range(NTIMES):
            fp.write(f"{test_name}, ")

            perf_cmd = (
                f"/usr/bin/time -f '%M' -o memory_usage.txt "
                f"perf stat -e {PERF_EVENTS} -x , -o perf_output.txt "
                f"bash -c \"{command}\""
            )

            # record energy before
            pkg_before  = read_energy(core, "package")
            core_before = read_energy(core, "core")
            dram_before = read_energy(core, "dram")

            # run benchmark
            start = time.time()
            subprocess.run(perf_cmd, shell=True, check=True)
            end   = time.time()

            # record energy after
            pkg_after  = read_energy(core, "package")
            core_after = read_energy(core, "core")
            dram_after = read_energy(core, "dram")

            # compute deltas
            elapsed      = end - start
            pkg_energy   = pkg_after  - pkg_before
            core_energy  = core_after - core_before
            dram_energy  = dram_after - dram_before

            # parse CPU cycles
            cycles = 0
            with open("perf_output.txt") as f:
                for line in f:
                    if "cycles" in line:
                        cycles = int(line.split(",")[0])
                        break
            os.remove("perf_output.txt")

            # parse peak memory (KB)
            with open("memory_usage.txt") as f:
                peak_mem = int(f.read().strip())
            os.remove("memory_usage.txt")

            # log CSV: test, time(s), cycles, mem(KB), pkg(J), core(J), dram(J)
            fp.write(f"{elapsed:.6f}, {cycles}, {peak_mem}, "
                     f"{pkg_energy:.6f}, {core_energy:.6f}, {dram_energy:.6f}\n")

        total_end = time.time()
        throughput = NTIMES / (total_end - total_start)
        fp.write(f"Throughput (executions per second), {throughput:.6f}\n")

    print("Benchmarking complete.")


if __name__ == "__main__":
    # example usage:
    cmd = "./your_binary --arg1 foo"
    run_benchmark(cmd, "cpp", "fft_test")
