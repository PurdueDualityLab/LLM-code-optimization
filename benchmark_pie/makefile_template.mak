# include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp ${FILE_NAME}.cpp -o ${FILE_NAME}.cpp.o &&  /usr/bin/g++ ${FILE_NAME}.cpp.o -o ${FILE_NAME}.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_${FILE_NAME}.cpp -o optimized_${FILE_NAME}.cpp.o &&  /usr/bin/g++ optimized_${FILE_NAME}.cpp.o -o optimized_${FILE_NAME}.gpp_run -fopenmp 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/${FILE_NAME}.gpp_run < $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_pie/$(problem_id)/optimized_${FILE_NAME}.gpp_run < $(input)" c++ $(problem_id)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

run:
	./${FILE_NAME}.gpp_run

run_optimized:
	./optimized_${FILE_NAME}.gpp_run

mem:
	 /usr/bin/time -v  ./${FILE_NAME}.gpp_run
valgrind:
	valgrind --tool=massif --stacks=yes  ./${FILE_NAME}.gpp_run

