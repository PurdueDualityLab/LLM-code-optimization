# include ../../.env

compile:
	/usr/bin/g++ -g -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp ${FILE_NAME}.cpp -o ${FILE_NAME}.cpp.o
	/usr/bin/g++ -g ${FILE_NAME}.cpp.o -o ${FILE_NAME}.gpp_run -fopenmp 

compile_optimized:
	/usr/bin/g++ -g -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp optimized_${FILE_NAME}.cpp -o optimized_${FILE_NAME}.cpp.o
	/usr/bin/g++ -g optimized_${FILE_NAME}.cpp.o -o optimized_${FILE_NAME}.gpp_run -fopenmp 

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

generate_flame_report:
	chmod +x ./run_all_test_cases.sh
	sudo perf record -F 90000 -e cycles:u -g --call-graph dwarf -o data -- ./run_all_test_cases.sh
	sudo perf report -i data -f -n --stdio --sort overhead > flame_report.txt

compile_code_for_flame_report:
	/usr/bin/g++ -g -c -pipe -fomit-frame-pointer -march=native  -std=c++11 -fopenmp flamegraph_${FILE_NAME}.cpp -o flamegraph_${FILE_NAME}.cpp.o
	/usr/bin/g++ -g flamegraph_${FILE_NAME}.cpp.o -o flamegraph_${FILE_NAME}.gpp_run -fopenmp  

mem:
	 /usr/bin/time -v  ./${FILE_NAME}.gpp_run
valgrind:
	valgrind --tool=massif --stacks=yes  ./${FILE_NAME}.gpp_run

