# include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp p02587_s745947670_t841869061.cpp -o p02587_s745947670_t841869061.cpp.o &&  /usr/bin/g++ p02587_s745947670_t841869061.cpp.o -o p02587_s745947670_t841869061.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_p02587_s745947670_t841869061.cpp -o optimized_p02587_s745947670_t841869061.cpp.o &&  /usr/bin/g++ optimized_p02587_s745947670_t841869061.cpp.o -o optimized_p02587_s745947670_t841869061.gpp_run -fopenmp 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/p02587_s745947670_t841869061.gpp_run < $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/optimized_p02587_s745947670_t841869061.gpp_run < $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./p02587_s745947670_t841869061.gpp_run

run_optimized:
	./optimized_p02587_s745947670_t841869061.gpp_run

mem:
	 /usr/bin/time -v  ./p02587_s745947670_t841869061.gpp_run
valgrind:
	valgrind --tool=massif --stacks=yes  ./p02587_s745947670_t841869061.gpp_run

