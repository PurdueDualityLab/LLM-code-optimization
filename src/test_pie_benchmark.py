from pie_benchmark import PIEBenchmark, get_valid_pie_programs
import os
from dotenv import load_dotenv
import sys
from utils import Logger

load_dotenv()
logger = Logger("logs", "test").logger

def test_pie_benchmark():
    # Get first program from PIE benchmark
    programs = get_valid_pie_programs(1)  # Get just 1 program to test
    if not programs:
        logger.error("No programs found in PIE benchmark")
        return
        
    program = programs[0]
    logger.info(f"Testing with program: {program}")
    
    # Create benchmark instance
    benchmark = PIEBenchmark(program)
    
    # Run original code measurement
    success = benchmark.set_original_energy()
    if not success:
        logger.error("Failed to measure original code energy")
        return
        
    # Get the results
    energy_data = benchmark.get_energy_data()
    
    # Print results
    logger.info("\nTest Results:")
    logger.info(f"Number of measurements: {len(energy_data)}")
    for iteration, (code, energy, runtime, lines) in energy_data.items():
        logger.info(f"\nIteration {iteration}:")
        logger.info(f"Average Energy: {energy}")
        logger.info(f"Average Runtime: {runtime}")

if __name__ == "__main__":
    test_pie_benchmark() 