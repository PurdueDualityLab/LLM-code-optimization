include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -fopenmp regexredux.gpp-3.c++ -o regexredux.gpp-3.c++.o &&  /usr/bin/g++ regexredux.gpp-3.c++.o -o regexredux.gpp-3.gpp_run -fopenmp -lboost_regex 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -fopenmp optimized_regexredux.gpp-3.c++ -o optimized_regexredux.gpp-3.c++.o &&  /usr/bin/g++ optimized_regexredux.gpp-3.c++.o -o optimized_regexredux.gpp-3.gpp_run -fopenmp -lboost_regex 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./regexredux.gpp-3.gpp_run 0 < regexredux-input5000000.txt" c++ regex-redux
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_regexredux.gpp-3.gpp_run 0 < regexredux-input5000000.txt" c++ regex-redux
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv
	
run:
	./regexredux.gpp-3.gpp_run 0 < regexredux-input5000000.txt

run_optimized:
	./optimized_regexredux.gpp-3.gpp_run 0 < regexredux-input5000000.txt

mem:
	/usr/bin/time -v ./regexredux.gpp-3.gpp_run 0 < regexredux-input5000000.txt

valgrind:
	valgrind --tool=massif --stacks=yes ./regexredux.gpp-3.gpp_run 0 < regexredux-input5000000.txt
