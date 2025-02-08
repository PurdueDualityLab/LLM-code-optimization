# include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp p03415_s788158351_t217805451.cpp -o p03415_s788158351_t217805451.cpp.o &&  /usr/bin/g++ p03415_s788158351_t217805451.cpp.o -o p03415_s788158351_t217805451.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_p03415_s788158351_t217805451.cpp -o optimized_p03415_s788158351_t217805451.cpp.o &&  /usr/bin/g++ optimized_p03415_s788158351_t217805451.cpp.o -o optimized_p03415_s788158351_t217805451.gpp_run -fopenmp 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/p03415_s788158351_t217805451.gpp_run $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/optimized_p03415_s788158351_t217805451.gpp_run $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./p03415_s788158351_t217805451.gpp_run $(input)

run_optimized:
	./optimized_p03415_s788158351_t217805451.gpp_run $(input)

mem:
	 /usr/bin/time -v  ./p03415_s788158351_t217805451.gpp_run $(input)
valgrind:
	valgrind --tool=massif --stacks=yes  ./p03415_s788158351_t217805451.gpp_run $(input)

