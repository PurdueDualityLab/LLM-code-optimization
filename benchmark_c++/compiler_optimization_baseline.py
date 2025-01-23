import os
import subprocess
from dotenv import load_dotenv
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')

benchmark_dirs = ["pidigits", "k-nucleotide", "binary-trees", "fannkuch-redux", "n-body", "regex-redux"]
full_report = {}

#Clean energy/data/C++.csv by opening and closing it
energy_csv_file = open(f"{USER_PREFIX}/energy/data/C++.csv", 'w')
energy_csv_file.close()

compiler_optimized = False

#Iterate through all the folders in benchmarks folder
for benchmark in benchmark_dirs:
    #Compile the benchmark's code
    try:
        if compiler_optimized:
            result = subprocess.run("make compile_compiler_optimized", cwd= f"{USER_PREFIX}/benchmarks/{benchmark}", stderr=subprocess.PIPE, check=True, shell=True)
        else:
            result = subprocess.run("make compile", cwd= f"{USER_PREFIX}/benchmarks/{benchmark}", stderr=subprocess.PIPE, check=True, shell=True)
        print(f"Successfully compiled {benchmark}.")
    except subprocess.CalledProcessError as e:
        print(f"Error while compiling {benchmark} raw code:")
        print(e.stderr.decode(), "\n") 
    
    #Run benchmark and measure energy (automatically runs it 5 times as 5 was specified in RAP/main.c)
    try:
        result = subprocess.run("make measure", cwd= f"{USER_PREFIX}/benchmarks/{benchmark}", stderr=subprocess.PIPE, check=True, shell=True)
        print(f"Successfully measured energy data for {benchmark}.")
    except subprocess.CalledProcessError as e:
        print(f"Error while measuring energy for {benchmark}:")
        print(e.stderr.decode(), "\n") 

    

#Now process C++.csv NUM_TRIALS lines at a time and get average energy and runtime values
energy_data_file = open(f"{USER_PREFIX}/energy/data/C++.csv")
benchmark_data = []

for line in energy_data_file:
    parts = line.split(';')
    benchmark_name = parts[0].strip()
    energy_data = [vals.strip() for vals in parts[1].split(',')]
    
    #Remove empty strings for CPU, GPU, DRAM and convert remaining numbers to floats
    energy_data = [float(num) for num in energy_data if num]
    benchmark_data.append((benchmark_name, *energy_data))

#Find average energy usage and average runtime
averages = []
for i in range(0, len(benchmark_data), 5):
    n_runs_data = benchmark_data[i:i + 5]

    total_energy = 0
    total_runtime = 0
    count = 0
    
    for data in n_runs_data:
        total_energy += data[1]
        total_runtime += data[2]
        count += 1

    avg_energy = round(total_energy / count, 3)
    avg_runtime = round(total_runtime / count, 3)

    full_report[n_runs_data[0][0]] = (avg_energy, avg_runtime)

#Print out results nicely
for benchmark in full_report.keys():
    print(f"{benchmark}  |  Avg Energy (J): {full_report[benchmark][0]}  | Avg Runtime (ms): {full_report[benchmark][1]}")
