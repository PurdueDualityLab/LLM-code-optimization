# include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp p03375_s925695849_t696378187.cpp -o p03375_s925695849_t696378187.cpp.o &&  /usr/bin/g++ p03375_s925695849_t696378187.cpp.o -o p03375_s925695849_t696378187.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_p03375_s925695849_t696378187.cpp -o optimized_p03375_s925695849_t696378187.cpp.o &&  /usr/bin/g++ optimized_p03375_s925695849_t696378187.cpp.o -o optimized_p03375_s925695849_t696378187.gpp_run -fopenmp 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/p03375_s925695849_t696378187.gpp_run < $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/optimized_p03375_s925695849_t696378187.gpp_run < $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./p03375_s925695849_t696378187.gpp_run

run_optimized:
	./optimized_p03375_s925695849_t696378187.gpp_run

mem:
	 /usr/bin/time -v  ./p03375_s925695849_t696378187.gpp_run
valgrind:
	valgrind --tool=massif --stacks=yes  ./p03375_s925695849_t696378187.gpp_run

