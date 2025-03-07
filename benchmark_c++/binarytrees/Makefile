include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++14 -fopenmp -I/usr/include/apr-1.0 binarytrees.gpp-9.c++ -o binarytrees.gpp-9.c++.o &&  /usr/bin/g++ binarytrees.gpp-9.c++.o -o binarytrees.gpp-9.gpp_run -fopenmp -lapr-1 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  -std=c++14 -fopenmp -I/usr/include/apr-1.0 optimized_binarytrees.gpp-9.c++ -o optimized_binarytrees.gpp-9.c++.o &&  /usr/bin/g++ optimized_binarytrees.gpp-9.c++.o -o optimized_binarytrees.gpp-9.gpp_run -fopenmp -lapr-1

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_c++/binarytrees/binarytrees.gpp-9.gpp_run 21" c++ binary-trees
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "${USER_PREFIX}/benchmark_c++/binarytrees/optimized_binarytrees.gpp-9.gpp_run 21" c++ binary-trees
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

run:
	./binarytrees.gpp-9.gpp_run 21

run_optimized:
	./optimized_binarytrees.gpp-9.gpp_run 21

mem:
	/usr/bin/time -v ./binarytrees.gpp-9.gpp_run 21

valgrind:
	valgrind --tool=massif --stacks=yes ./binarytrees.gpp-9.gpp_run 21
