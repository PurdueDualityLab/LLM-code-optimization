include ../.env
# sudo apt update
# sudo apt install openjdk-17-jdk
# sudo update-alternatives --config java
# sudo update-alternatives --config javac


JAVAC = javac
JAVA = java
JFLAGS = -d . 

SRCS = *.java  
FFTBENCHMARK_CLASS = jnt/scimark2/FFTBenchmark
SORBENCHMARK_CLASS = jnt/scimark2/SORBenchmark
MONTECARLOBENCHMARK_CLASS = jnt/scimark2/MonteCarloBenchmark
SPARSECOMPROWBENCHMARK_CLASS = jnt/scimark2/SparseCompRowBenchmark
LUBENCHMARK_CLASS = jnt/scimark2/LUBenchmark

compile:
	$(JAVAC) $(JFLAGS) $(SRCS)

run:
	$(JAVA) $(MAIN_CLASS)

measureFFTBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(FFTBENCHMARK_CLASS)" java FFTBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measureSORBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(SORBENCHMARK_CLASS)" java SORBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measureMonteCarloBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(MONTECARLOBENCHMARK_CLASS)" java MonteCarloBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measureSparseCompRowBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(SPARSECOMPROWBENCHMARK_CLASS)" java SparseCompRowBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measureLUBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(LUBENCHMARK_CLASS)" java LUBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

clean:
	rm -rf *.class