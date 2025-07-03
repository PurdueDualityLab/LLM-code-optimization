include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native -mfpmath=sse -msse3 --std=c++11 nbody.gpp-8.c++ -o nbody.gpp-8.c++.o &&  /usr/bin/g++ nbody.gpp-8.c++.o -o nbody.gpp-8.gpp_run -fopenmp

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native -mfpmath=sse -msse3 --std=c++11 optimized_nbody.gpp-8.c++ -o optimized_nbody.gpp-8.c++.o &&  /usr/bin/g++ optimized_nbody.gpp-8.c++.o -o optimized_nbody.gpp-8.gpp_run -fopenmp

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./nbody.gpp-8.gpp_run 50000000" c++ n-body
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_nbody.gpp-8.gpp_run 50000000" c++ n-body
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

run:
	./nbody.gpp-8.gpp_run 50000000

run_optimized:
	./optimized_nbody.gpp-8.gpp_run 50000000
mem:
	/usr/bin/time -v ./nbody.gpp-8.gpp_run 50000000

valgrind:
	valgrind --tool=massif --stacks=yes ./nbody.gpp-8.gpp_run 50000000


