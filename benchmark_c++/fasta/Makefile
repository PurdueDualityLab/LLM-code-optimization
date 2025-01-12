include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native -mfpmath=sse -msse3 -std=c++11 fasta.gpp-5.c++ -o fasta.gpp-5.c++.o &&  /usr/bin/g++ fasta.gpp-5.c++.o -o fasta.gpp-5.gpp_run -lpthread 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native -mfpmath=sse -msse3 -std=c++11 optimized_fasta.gpp-5.c++ -o optimized_fasta.gpp-5.c++.o &&  /usr/bin/g++ optimized_fasta.gpp-5.c++.o -o optimized_fasta.gpp-5.gpp_run -lpthread 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./fasta.gpp-5.gpp_run 25000000" c++ fasta
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv
	
measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_fasta.gpp-5.gpp_run 25000000" C++ fasta
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./fasta.gpp-5.gpp_run 25000000

run_optimized:
	./optimized_fasta.gpp-5.gpp_run 25000000

mem:
	/usr/bin/time -v ./fasta.gpp-5.gpp_run 25000000

valgrind:
	valgrind --tool=massif --stacks=yes ./fasta.gpp-5.gpp_run 25000000

