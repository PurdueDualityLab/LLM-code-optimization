from dotenv import load_dotenv
import json
import os
import re
import shutil
import subprocess
import sys


load_dotenv()
USER_PREFIX = os.getenv('USER_PREFIX')

def get_valid_pie_programs(num_programs):
    slow_fast_pairs = []
    selected_problem_ids = set()
    source_code = []

    #Extract the first 5 unique problems from the validation set
    file = open(f"{USER_PREFIX}/benchmark_pie/val.jsonl", "r")
    for line in file:
        json_line = json.loads(line)
        if json_line["problem_id"] not in selected_problem_ids and len(selected_problem_ids) != num_programs:
            selected_problem_ids.add(json_line["problem_id"])
            slow_fast_pairs.append(json_line)
            source_code.append(json_line["src_code"])
        if len(selected_problem_ids) == num_programs:
            break
    file.close()

    #Return only the program names
    valid_programs = [f"{pair['problem_id']}_{pair['src_id']}_t{pair['tgt_id'][1:]}.cpp" for pair in slow_fast_pairs]
    setup_benchmarks(valid_programs, source_code)

    return valid_programs

def setup_benchmarks(valid_programs, source_code):
    for i, program in enumerate(valid_programs):
        #Create the folder if it does not exist
        folder_path = f"{USER_PREFIX}/benchmark_pie/{program.split('_')[0]}"
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        #Create a new cpp file in the folder with the source code
        file = open(f"{folder_path}/{program}", "w")
        file.write(f"{source_code[i]}")
        file.close()
        
        #Copy the test case folder from all_test_cases/ into the program's folder
        problem_id = program.split('_')[0]
        test_case_folder_src = f"{USER_PREFIX}/benchmark_pie/all_test_cases/{problem_id}"
        test_case_folder_dest = f"{folder_path}/test_cases"
        if not os.path.exists(test_case_folder_dest):
            shutil.copytree(test_case_folder_src, test_case_folder_dest)

        #Create parameterized Makefile for each problem id folder
        #Open template file
            #replace ${FILE_NAME} with program name and ${PROBLEM_ID} with problem id
        #Write to new file
        makefile_template = open(f"{USER_PREFIX}/benchmark_pie/makefile_template.mak", "r")
        makefile_content = makefile_template.read()
        makefile_content = makefile_content.replace("${FILE_NAME}", program.split('.')[0])
        makefile_content = makefile_content.replace("${PROBLEM_ID}", problem_id)
        makefile_template.close()
        makefile_template = open(f"{folder_path}/Makefile", "w")
        makefile_template.write(makefile_content)
        makefile_template.close()

if __name__ == "__main__":
    num_benchmarks = 5
    output = get_valid_pie_programs(num_benchmarks)
    print(output)
