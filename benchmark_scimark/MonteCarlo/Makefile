include ../../.env
# sudo apt update
# sudo apt install openjdk-17-jdk
# sudo update-alternatives --config java
# sudo update-alternatives --config javac


JAVAC = javac
JAVA = java
JFLAGS = -d . 

SRCS = *.java  
RANDOM_SRC = ../Random.java
BENCHMARK_CLASS = jnt/scimark2/MonteCarloBenchmark	

MAIN_CLASS = jnt/scimark2/MonteCarlo
OPTIMIZED_CLASS = jnt.scimark2.MonteCarloOptimized

compile:
	$(JAVAC) $(JFLAGS) $(SRCS) $(RANDOM_SRC) 

run:
	@$(JAVA) $(MAIN_CLASS)

run_optimized:
	@$(JAVA) $(OPTIMIZED_CLASS)

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(MAIN_CLASS)" java MonteCarlo
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(OPTIMIZED_CLASS)" java MonteCarloOptimized
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure_mflops:
	@$(JAVA) $(BENCHMARK_CLASS) false

measure_mflops_optimized:
	@$(JAVA) $(BENCHMARK_CLASS) true

clean:
	rm -rf *.class