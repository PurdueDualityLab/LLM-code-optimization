# LLM for software optimization
## About
## Table of Contents
- [Environment Requirement](#environment-requirement)
- [Reproduce Results](#reproduce-results)
- [Running the pipeline](#running-the-pipeline)
- [Analysis and evaluation](#analysis-and-evaluation)
- [Code Dependencies](#code-dependencies)

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

## Reproduce Results
To set up the pipeline for energy-efficient code optimization, follow these steps:
1. **Clone the repository:**
   ```bash
   git clone <repository-link>
   cd <project-directory>
2. **Install the required dependencies using the Makefile**
    ```bash
   make setup
3. **Create .env in root directory**
    This should include:
    ```bash
    API_KEY=your_openai_api_key_here
    USER_PREFIX=/path/to/E2COOL
4. **Update RAPL/main.c write path**
    Change line 31 to match your absolute path
    ```bash
    strcpy(path, “ABSOLUTE_PATH/E2COOL/energy/src/");
    ```
    Then run make in RAPL directory
    ```bash
    make
## Running the pipeline
5. **Run the main script in the home directory (/E2COOL)**
    ```bash
    make run (benchmark name) (model name)
    ```
    For example, to run the Binary Trees benchmark using `llama3.1:latest`,
   ```bash
   make run binarytrees.gpp-9.c++ llama3.1:latest
   ```
   Available models: use `openai` as model name for `gpt-4o-2024-08-06`. Open-souce LLMs are supported via ollama.
    

## Analysis and evaluation

The results of the optimizations are stored in "/llm/benchmarks_out/(benchmark name)/"
In 'results_file.txt', information about every optimization iteration is stored in the format:
```
(Iteration #): [
   optimized code,
   energy consumed,
   runtime
]
```

A summary of the LLM's optimizations on selected benchmarks can be found [here](https://docs.google.com/spreadsheets/d/16SBxRT3qgIaE904srtmaVqg7Rs7w_iRlNxEvjYius0w/edit?usp=sharing).

## Code Dependencies
Software we relied on (included in [requirements.txt](https://github.com/ArjunGupte44/E2COOL/blob/main/requirements.txt)):
```
openai==1.50.1
pydantic==2.9.2
pydantic_core==2.23.4
python-dotenv==1.0.1
```
