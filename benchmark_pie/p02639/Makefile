# include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp p02639_s662076996_t004750872.cpp -o p02639_s662076996_t004750872.cpp.o &&  /usr/bin/g++ p02639_s662076996_t004750872.cpp.o -o p02639_s662076996_t004750872.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_p02639_s662076996_t004750872.cpp -o optimized_p02639_s662076996_t004750872.cpp.o &&  /usr/bin/g++ optimized_p02639_s662076996_t004750872.cpp.o -o optimized_p02639_s662076996_t004750872.gpp_run -fopenmp 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/p02639_s662076996_t004750872.gpp_run $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/optimized_p02639_s662076996_t004750872.gpp_run $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./p02639_s662076996_t004750872.gpp_run $(input)

run_optimized:
	./optimized_p02639_s662076996_t004750872.gpp_run $(input)

mem:
	 /usr/bin/time -v  ./p02639_s662076996_t004750872.gpp_run $(input)
valgrind:
	valgrind --tool=massif --stacks=yes  ./p02639_s662076996_t004750872.gpp_run $(input)

