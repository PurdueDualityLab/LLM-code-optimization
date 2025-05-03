include ../../.env
# sudo apt update
# sudo apt install openjdk-17-jdk
# sudo update-alternatives --config java
# sudo update-alternatives --config javac


JAVAC = javac
JAVA = java -server \
  -XX:+AggressiveOpts \
  -XX:+UseSuperWord \
  -XX:+TieredCompilation \
  -XX:TieredStopAtLevel=4 \
  -XX:MaxInlineSize=100 \
  -XX:FreqInlineSize=100
JFLAGS = -d . 

SRCS = *.java  
BENCHMARK_CLASS = jnt/scimark2/MonteCarloBenchmark	

MAIN_CLASS = jnt/scimark2/MonteCarlo
OPTIMIZED_CLASS = jnt.scimark2.MonteCarloOptimized

compile:
	rm -rf *.class
	rm -rf jnt/
	$(JAVAC) $(JFLAGS) $(SRCS) ../Random.java ../Stopwatch.java

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