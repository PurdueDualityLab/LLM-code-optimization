include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++14 knucleotide.gpp-3.c++ -o knucleotide.gpp-3.c++.o &&  /usr/bin/g++ knucleotide.gpp-3.c++.o -o knucleotide.gpp-3.gpp_run -Wl,--no-as-needed -lpthread 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++14 optimized_knucleotide.gpp-3.c++ -o optimized_knucleotide.gpp-3.c++.o &&  /usr/bin/g++ optimized_knucleotide.gpp-3.c++.o -o optimized_knucleotide.gpp-3.gpp_run -Wl,--no-as-needed -lpthread 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./knucleotide.gpp-3.gpp_run 0 < knucleotide-input25000000.txt" c++ k-nucleotide
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_knucleotide.gpp-3.gpp_run 0 < knucleotide-input25000000.txt" c++ k-nucleotide
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./knucleotide.gpp-3.gpp_run 0 < knucleotide-input25000000.txt

run_optimized:
	./optimized_knucleotide.gpp-3.gpp_run 0 < knucleotide-input25000000.txt

mem:
	/usr/bin/time -v ./knucleotide.gpp-3.gpp_run 0 < knucleotide-input25000000.txt

valgrind:
	valgrind --tool=massif --stacks=yes ./knucleotide.gpp-3.gpp_run 0 < knucleotide-input25000000.txt