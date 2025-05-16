## Opentuner

`pie_tuner.py` is a implementation of a GCC compiler flag optimizer using OpenTuner. It automatically searches for the best combination of compiler flags and parameters to optimize the performance of a C++ program.

### How it works
1. Defining a search space of possible compiler configurations
2. Compiling and running the program with different configurations
3. Measuring the execution time of each configuration
4. Using OpenTuner's search algorithms to find the optimal configuration

### Experience with how it works
I think opentuner is simple to use as for the gcc compiler flag optimization method. There are other optimizaiton method that opentuner provide like processing the seach space in parallel and choesing different optimization techniques that could also be implemented. 

### Performance Gain
