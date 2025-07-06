# LLM for software optimization
## About
## Table of Contents
- [Environment Requirement](#environment-requirement)
- [Environment Setup](#environment-setup)
- [Running the pipeline](#running-the-pipeline)

## Environment Requirement
This artifact requires a machine with the following capabilities to support RAPL (Running Average Power Limit) and read MSR (Model-Specific Registers):

1. **Hardware**
- Intel Processor: Machine with Intel processors supporting RAPL (Sandy Bridge or newer).
- MSR Support: Machine must allow access to MSRs.

2. **Operating System**
- Linux-based OS (e.g., Ubuntu 16.04+).
- Linux Kernel Version 3.13+ required for RAPL support.
- Root Access: MSRs can only be accessed with root/superuser privileges.

3. **Software**
- msr-tools: Install for reading MSRs:
  ```bash
  sudo apt-get install msr-tools
  ```

## Environment Setup
1. **Clone the repository:**
   ```bash
   git clone <repository-link>
   cd <project-directory>
   ```
2. **Install the required dependencies using the Makefile**
    ```bash
   make setup
   ```
3. **Create `.env` file in the root directory**
    Add the following:
    ```bash
    API_KEY=your_openai_api_key_here
    USER_PREFIX=$(pwd)
    ```
    Then source your env with
    ```bash
    . .env
    ```
4. **Compile performance measurement module**
    In the `MEASURE` directory, run:
    ```bash
    make
    ```

## Project Structure

The repository is organized as follows:

```
LLM-code-optimization/
├── MEASURE/                # Code for performance measurement (compile with `make`)
├── benchmark_scimark/      # SciMark benchmark programs
├── benchmark_human_eval/   # HumanEval_cpp benchmark programs
├── benchmark_dacapo/       # Dacapobench benchmark programs and build infrastructure
├── eval/                   # Evaluation, scripts, and results
├── pattern_catalog/        # Complete list of performance optimization pattern catalog
├── src/                    # Main source code
│   ├── main.py             # Entry point: main pipeline script
│   ├── llm/
│   |   ├── agent.py        # LLM agent class and logic
│   │   ├── llm_prompts/    # Prompts used for all llms
│   │   ├── generator_llm.py    # LLM code generation logic
│   │   ├── evaluator_llm.py    # LLM evaluation logic
│   │   └── advisor_llm.py      # LLM advisor for optimization patterns
│   ├── benchmarks
|   |   ├── scimark_benchmark.py    # SciMark benchmark integration
|   |   ├── humaneval_benchmark.py    # HumanEval benchmark integration
|   |   └── dacapo/
|   |       ├── dacapo_apps.py    # Dacapo apps configuration
│   |       └── dacapo_benchmark.py # DaCapo benchmark integration
|   ├── java_code_extraction/    # Java module to extract and replace source code from a java file
|   └── flamegraph_profiling.py     # Code for getting performance hotspot
└── README.md               # Project documentation
```

## Running the pipeline
1. **Run the main script from the project root**
    Run HumanEval_CPP benchmark
    ```bash
    make run ARGS="--benchmark HumanEval --llm gpt-4o --self_optimization_step 2 --num_programs 2"
    ```
    Run SciMark benchmark
    ```bash
    make run ARGS="--benchmark SciMark --llm gpt-4o --self_optimization_step 2"
    ```
    Run Dacapo benchmark
    Prebuild the target application following the Dacapobench official instruction, then run:
    ```bash
    make run ARGS="--benchmark Dacapobench --llm gpt-4o --self_optimization_step 2 --application_name biojava"
