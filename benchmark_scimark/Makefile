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

measure FFTBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(FFTBENCHMARK_CLASS)" java FFTBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure SORBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(SORBENCHMARK_CLASS)" java SORBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure MonteCarloBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(MONTECARLOBENCHMARK_CLASS)" java MonteCarloBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure SparseCompRowBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(SPARSECOMPROWBENCHMARK_CLASS)" java SparseCompRowBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure LUBenchmark:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(LUBENCHMARK_CLASS)" java LUBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

clean:
	rm -rf *.class