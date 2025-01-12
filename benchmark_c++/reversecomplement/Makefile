include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -mtune=native -mfpmath=sse -msse2 revcomp.gpp-4.c++ -o revcomp.gpp-4.c++.o &&  /usr/bin/g++ revcomp.gpp-4.c++.o -o revcomp.gpp-4.gpp_run -pthread 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -mtune=native -mfpmath=sse -msse2 optimized_revcomp.gpp-4.c++ -o optimized_revcomp.gpp-4.c++.o &&  /usr/bin/g++ optimized_revcomp.gpp-4.c++.o -o optimized_revcomp.gpp-4.gpp_run -pthread 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./revcomp.gpp-4.gpp_run 0 < revcomp-input25000000.txt" c++ reverse-complement
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_revcomp.gpp-4.gpp_run 0 < revcomp-input25000000.txt" c++ reverse-complement
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./revcomp.gpp-4.gpp_run 0 < revcomp-input25000000.txt

run_optimized:
	./optimized_revcomp.gpp-4.gpp_run 0 < revcomp-input25000000.txt

mem:
	/usr/bin/time -v ./revcomp.gpp-4.gpp_run 0 < revcomp-input25000000.txt

valgrind:
	valgrind --tool=massif --stacks=yes ./revcomp.gpp-4.gpp_run 0 < revcomp-input25000000.txt
