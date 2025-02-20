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

compile:
	$(JAVAC) $(JFLAGS) $(SRCS) $(RANDOM_SRC) $(STOPWATCH_SRC)

run:
	$(JAVA) $(MAIN_CLASS)

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(FFTBENCHMARK_CLASS)" java FFTBenchmark
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

clean:
	rm -rf *.class