import subprocess
import os
import re
from dotenv import load_dotenv
load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')
import sys
from utils import Logger

TEST_OUTPUT_FILE = f"{USER_PREFIX}/src/runtime_logs/regression_test_log.txt"
UNOPTIMIZED_OUTPUT = f"{USER_PREFIX}/src/runtime_logs/unoptimized_output.txt"
OPTIMIZED_OUTPUT = f"{USER_PREFIX}/src/runtime_logs/optimized_output.txt"
ITERATION_OUTPUT_DIR = f"{USER_PREFIX}/src/runtime_logs"

logger = Logger("logs", sys.argv[2]).logger

false_positive_counter = 0
comparison_count = 0
output_different_counter = 0
def compile_program(output_log, optimized):
    try: 
        # Redirect stdout and stderr to the regression_test_log file
        if not optimized:
            subprocess.run(
                    ["make", "compile"], 
                    check=True,
                    stdout=output_log, 
                    stderr=output_log  # Redirect stderr to the same file as stdout
            )
        else:
            subprocess.run(
                    ["make", "compile_optimized"], 
                    check=True,
                    stdout=output_log, 
                    stderr=output_log  # Redirect stderr to the same file as stdout
            )
        logger.info(f"regression_test: Makefile compile successfully. Optimized: {optimized}.\n")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"regression_test: Makefile compile failed: {e} Optimized: {optimized}.\n")
        return False

def run_program(exec_path, output_file, optimized):
    # Run the make command and capture the output in a variable
    if not optimized:
        result = subprocess.run(["make", "run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin-1')
    else:
        result = subprocess.run(["make", "run_optimized"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='latin-1')
    
    # Check for errors
    if result.returncode != 0:
        with open(output_file, 'w+') as f:
            f.write(result.stderr)
        logger.error(f"Runtime error on {exec_path} with error message: {result.stderr}")
        return False

    # Filter out the unwanted lines
    filtered_output = "\n".join(
        line for line in result.stdout.splitlines()
        if not (line.startswith("make[") or line.startswith("./"))
    )
    
    # Write the filtered output to the file
    with open(output_file, 'w+') as f:
        f.write(filtered_output)
    
    return True

def process_output_content(content):
    """Remove all spaces, newline characters, and tabs for cleaner comparison."""
    # If content is a list of lines, join it into a single string
    if isinstance(content, list):
        content = ''.join(content)
    # Remove all whitespace characters
    return re.sub(r'\s+', '', content)

def save_output(cleaned_content1, cleaned_content2, output_string):
    global comparison_count
    global false_positive_counter
    global output_different_counter

    with open(f"{ITERATION_OUTPUT_DIR}/output_compare.txt", 'w') as file:
        file.write(f"{output_string}\n")
        file.write(f"Number of comparison: {comparison_count}\n")
        file.write(f"Number of output difference: {output_different_counter}\n")
        file.write(f"Number of false-positive: {false_positive_counter}\n")
        file.write(f"Original:\n{cleaned_content1}\n")
        file.write(f"Optimized:\n{cleaned_content2}\n\n")
        
    logger.info(f"false positive count: {false_positive_counter}")
    logger.info(f"comparison count: {comparison_count}")

def compare_outputs(file1, file2, output_log):
    global comparison_count
    global output_different_counter
    global false_positive_counter

    comparison_count += 1
    logger.info(f"comparison_count is {comparison_count}")
    with open(file1, 'r') as f1, open(file2, 'r') as f2:
        file1_content = f1.readlines()
        file2_content = f2.readlines()

        # whitespace remove
        cleaned_content1 = process_output_content(file1_content)
        cleaned_content2 = process_output_content(file2_content)

        # if file content (w/o whitspace remove) is different but cleaned content (with whitespace remove) is same
        if (file1_content != file2_content) and (cleaned_content1 == cleaned_content2):
            false_positive_counter += 1

        if cleaned_content1 == cleaned_content2:
            save_output(cleaned_content1, cleaned_content2, "Output is correct!!!")
            output_log.write("Outputs are the same.\n")
            return True
        else:
            # call save_output to strip all whitespaces
            output_different_counter += 1
            # save_output(file1_content, file2_content)
            save_output(cleaned_content1, cleaned_content2, "Output is Different sad :(")
            output_log.write("Outputs are different.\n")
            output_log.write(f"Original program output:\n{cleaned_content1}\n")
            output_log.write(f"Optimized program output:\n{cleaned_content2}\n\n")
            return False

def regression_test(filename): 
    unoptimized_file_exec = f"{USER_PREFIX}/benchmark_c++/{filename.split('.')[0]}/{filename.split('.')[0]}"
    optimized_file_exec = f"{USER_PREFIX}/benchmark_c++/{filename.split('.')[0]}/optimized_{filename}"

    # Needed for makefiles
    os.chdir(f"{USER_PREFIX}/benchmark_c++/{filename.split('.')[0].split('_')[-1]}")   
    with open(TEST_OUTPUT_FILE, 'w+') as output_log:
        if not compile_program(output_log, False):
            # Return code when unoptimized file does not compile
            return -2
        if not compile_program(output_log, True):
            # Return code when optimized file does not compile
            return -1

        run_program(unoptimized_file_exec, UNOPTIMIZED_OUTPUT, False)
        run_program(optimized_file_exec, OPTIMIZED_OUTPUT, True)

        if not compare_outputs(UNOPTIMIZED_OUTPUT, OPTIMIZED_OUTPUT, output_log):
            return 0
        else:
            output_log.write("Regression test successful. Outputs are the same.\n\n")
            return 1

if __name__ == "__main__":
    regression_test("binarytrees.c", "optimized_binarytrees.c", "binarytrees")