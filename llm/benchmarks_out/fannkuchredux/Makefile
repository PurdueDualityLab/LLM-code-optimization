include ../../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp fannkuchredux.gpp-5.c++ -o fannkuchredux.gpp-5.c++.o &&  /usr/bin/g++ fannkuchredux.gpp-5.c++.o -o fannkuchredux.gpp-5.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_fannkuchredux.gpp-5.c++ -o optimized_fannkuchredux.gpp-5.c++.o &&  /usr/bin/g++ optimized_fannkuchredux.gpp-5.c++.o -o optimized_fannkuchredux.gpp-5.gpp_run -fopenmp 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/llm/benchmarks_out/fannkuchredux/fannkuchredux.gpp-5.gpp_run 12" c++ fannkuch-redux
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/llm/benchmarks_out/fannkuchredux/optimized_fannkuchredux.gpp-5.gpp_run 12" c++ fannkuch-redux
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./fannkuchredux.gpp-5.gpp_run 12

run_optimized:
	./optimized_fannkuchredux.gpp-5.gpp_run 12

mem:
	 /usr/bin/time -v  ./fannkuchredux.gpp-5.gpp_run 12
valgrind:
	valgrind --tool=massif --stacks=yes  ./fannkuchredux.gpp-5.gpp_run 12

