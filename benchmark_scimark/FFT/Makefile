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
STOPWATCH_SRC = ../Stopwatch.java
FFTBENCHMARK_CLASS = jnt/scimark2/FFTBenchmark

MAIN_CLASS = jnt/scimark2/FFT
OPTIMIZED_CLASS = jnt.scimark2.FFTOptimized
KERNEL_CLASS = jnt.scimark2.Kernel

compile:
	$(JAVAC) $(JFLAGS) $(SRCS) $(RANDOM_SRC) $(STOPWATCH_SRC)
	$(JAVA) $(KERNEL_CLASS)

run:
	@$(JAVA) $(MAIN_CLASS)

run_optimized:
	@$(JAVA) $(OPTIMIZED_CLASS)

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(MAIN_CLASS)" java FFT
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(OPTIMIZED_CLASS)" java FFTOptimized
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure_mflops:
	@$(JAVA) $(FFTBENCHMARK_CLASS) false

measure_mflops_optimized:
	@$(JAVA) $(FFTBENCHMARK_CLASS) true

clean:
	rm -rf *.class