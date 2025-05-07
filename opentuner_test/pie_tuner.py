#!/usr/bin/env python  
#  
# Autotune flags to g++ to optimize the performance of your C++ program  
#  
  
import os  
import opentuner  
from opentuner import ConfigurationManipulator  
from opentuner import EnumParameter  
from opentuner import IntegerParameter  
from opentuner import MeasurementInterface  
from opentuner import Result  
  
# # Common GCC optimization flags  
# GCC_FLAGS = [  
#     'align-functions', 'align-jumps', 'align-labels',  
#     'align-loops', 'asynchronous-unwind-tables',  
#     'branch-count-reg', 'branch-probabilities',  
#     'caller-saves', 'conserve-stack', 'defer-pop',  
#     'delayed-branch', 'delete-null-pointer-checks',  
#     'dse', 'gcse', 'expensive-optimizations',  
#     'fast-math', 'finite-math-only', 'float-store',  
#     'forward-propagate', 'guess-branch-probability',  
#     'if-conversion', 'if-conversion2', 'inline-functions',  
#     'inline-small-functions', 'ivopts',  
#     'jump-tables', 'math-errno', 'merge-constants',  
#     'modulo-sched', 'move-loop-invariants', 'omit-frame-pointer',  
#     'optimize-sibling-calls', 'peephole2', 'predictive-commoning',  
#     'prefetch-loop-arrays', 'regmove', 'rename-registers',  
#     'reorder-blocks', 'reorder-functions', 'rerun-cse-after-loop',  
#     'schedule-insns', 'schedule-insns2', 'strict-aliasing',  
#     'strict-overflow', 'thread-jumps', 'tree-pre',  
#     'tree-switch-conversion', 'tree-ter', 'tree-vrp',  
#     'unroll-loops', 'vectorize-loops', 'web'  
# ]  
  
# # Common GCC parameters  
# GCC_PARAMS = [  
#     ('early-inlining-insns', 0, 1000),  
#     ('gcse-cost-distance-ratio', 0, 100),  
#     ('iv-max-considered-uses', 0, 1000),  
#     ('inline-unit-growth', 0, 500),  
#     ('max-inline-insns-single', 0, 2000),  
#     ('max-inline-recursive-depth', 0, 20),  
#     ('max-unrolled-insns', 0, 1000),  
#     ('max-variable-expansions-in-unroller', 0, 100),  
#     ('max-completely-peel-times', 0, 100),  
#     ('max-unroll-times', 0, 100)  
# ]  

GCC_FLAGS = [
    'align-functions', 'align-jumps', 'align-labels',
    'align-loops', 'asynchronous-unwind-tables',
    'branch-count-reg', 'branch-probabilities',
    # ... (176 total)
]

# (name, min, max)
GCC_PARAMS = [
    ('early-inlining-insns', 0, 100),
    ('gcse-cost-distance-ratio', 0, 100),
    ('iv-max-considered-uses', 0, 100),
    # ... (145 total)
]

  
class CustomGccFlagsTuner(MeasurementInterface):  
  
    def manipulator(self):  
        """  
        Define the search space by creating a  
        ConfigurationManipulator  
        """  
        manipulator = ConfigurationManipulator()  
        manipulator.add_parameter(  
            IntegerParameter('opt_level', 0, 3))  
        for flag in GCC_FLAGS:  
            manipulator.add_parameter(  
                EnumParameter(flag,  
                              ['on', 'off', 'default']))  
        for param, min_val, max_val in GCC_PARAMS:  
            manipulator.add_parameter(  
                IntegerParameter(param, min_val, max_val))  
        return manipulator  
  
    def compile(self, cfg, id):  
        """  
        Compile a given configuration in parallel  
        """  
        # Create output directory if it doesn't exist  
        if not os.path.exists('./tmp'):  
            os.makedirs('./tmp')  
              
        # Build the compilation command  
        gcc_cmd = f'g++ {self.args.source_file} -o ./tmp/program_{id}.bin'  
        gcc_cmd += f' -O{cfg["opt_level"]}'  
          
        # Add flags  
        for flag in GCC_FLAGS:  
            if cfg[flag] == 'on':  
                gcc_cmd += f' -f{flag}'  
            elif cfg[flag] == 'off':  
                gcc_cmd += f' -fno-{flag}'  
          
        # Add parameters  
        for param, min_val, max_val in GCC_PARAMS:  
            gcc_cmd += f' --param {param}={cfg[param]}'  
        logging("\nCompiling and Running Program")
        logging(f"Compile Command ID {id}: {gcc_cmd}") # Log the compile command
          
        # Run the compilation  
        compile_output = self.call_program(gcc_cmd)  
        logging(f"Compile Result ID {id}: time={compile_output.get('time')}, timeout={compile_output.get('timeout')}") # New version
        return compile_output
  
    def run_precompiled(self, desired_result, input, limit, compile_result, id):  
        """  
        Run a compile_result from compile() sequentially and return performance  
        """  
        if compile_result['returncode'] != 0:  
            # Compilation failed  
            return Result(state='ERROR', time=float('inf'))  
  
        # Build the run command  
        run_cmd = f'./tmp/program_{id}.bin'  
          
        # Add input file if specified  
        if self.args.input_file:  
            run_cmd += f' < {self.args.input_file}'  

        # log run command
        logging(f"Run Command ID {id}: {run_cmd}")

        try:  
            # Run the program and measure performance  
            run_result = self.call_program(run_cmd, limit=limit)  
            # log run result
            logging(f"Run Result ID {id}: {run_result}") # Log the run result

            if run_result['returncode'] != 0:  
                # Program execution failed  
                return Result(state='ERROR', time=float('inf'))  
                  
            # Return the execution time as the result  
            return Result(time=run_result['time'])  
        finally:  
            # Clean up the binary  
            self.call_program(f'rm ./tmp/program_{id}.bin')  
    
  
    def compile_and_run(self, desired_result, input, limit):  
        """  
        Compile and run a given configuration then  
        return performance  
        """  
        cfg = desired_result.configuration.data  
        compile_result = self.compile(cfg, 0)  
        return self.run_precompiled(desired_result, input, limit, compile_result, 0)  
  
    def save_final_config(self, configuration):  
        """  
        Save the best configuration to a file  
        """  
        print("Best configuration:")  
        for param, value in configuration.data.items():  
            print(f"  {param}: {value}")  
              
        # Save to a file  
        with open('best_gcc_flags.txt', 'w') as f:  
            f.write(f"# Best GCC flags for {self.args.source_file}\n\n")  
            f.write(f"CXXFLAGS = -O{configuration.data['opt_level']}")  
              
            # Add enabled flags  
            for flag in GCC_FLAGS:  
                if configuration.data[flag] == 'on':  
                    f.write(f" -f{flag}")  
                elif configuration.data[flag] == 'off':  
                    f.write(f" -fno-{flag}")  
                      
            # Add parameters  
            for param, min_val, max_val in GCC_PARAMS:  
                f.write(f" --param {param}={configuration.data[param]}")  
                  
            f.write("\n")  
              
        print(f"\nBest flags saved to best_gcc_flags.txt")  
  

def logging(content):
    """  
    Custom logging function to log messages  
    """  
    with open('tuner.log', 'a') as f:  
        f.write(content + '\n')  
    # print(content)
    
if __name__ == '__main__':  
    # Create a custom argument parser  
    parser = opentuner.default_argparser()  
    parser.add_argument('--source-file', required=True,  
                      help='C++ source file to optimize')  
    parser.add_argument('--input-file',   
                      help='Input file to pass to the program')  
      
    # Parse arguments and run the tuner  
    args = parser.parse_args()  
    CustomGccFlagsTuner.main(args)
