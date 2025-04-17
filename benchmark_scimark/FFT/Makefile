include ../../.env
# sudo apt update
# sudo apt install openjdk-17-jdk
# sudo update-alternatives --config java
# sudo update-alternatives --config javac


JAVAC = javac
JAVA = java
JFLAGS = -d . 

SRCS = *.java  
BENCHMARK_CLASS = jnt/scimark2/FFTBenchmark

MAIN_CLASS = jnt/scimark2/FFT
OPTIMIZED_CLASS = jnt.scimark2.FFTOptimized

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
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(MAIN_CLASS)" java FFT
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "$(JAVA) $(OPTIMIZED_CLASS)" java FFTOptimized
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

measure_mflops:
	@$(JAVA) $(BENCHMARK_CLASS) false

measure_mflops_optimized:
	@$(JAVA) $(BENCHMARK_CLASS) true

# cpu profile
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=cpu,flat=10,file=cpu_profile.txt jnt/scimark2/FFT
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=wall,flat=10,file=wall_profile.txt jnt/scimark2/FFT

# alloc profile
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=alloc,flat=10,file=alloc_profile.txt jnt/scimark2/FFT

# native memory alocation
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=nativemem,flat=10,file=nativemem_profile.txt jnt/scimark2/FFT

# thread state (lock)
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=lock,flat=10,file=lock_profile.txt jnt/scimark2/FFT

# itimer 
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=itimer,flat=10,file=itimer_profile.txt jnt/scimark2/FFT

# ctimer
# java -agentpath:/home/leoDeng/SciMark/E2COOL/async-profiler/build/lib/libasyncProfiler.so=start,event=ctimer,flat=10,file=ctimer_profile.txt jnt/scimark2/FFT