include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  --std=c++11 -pthread chameneosredux.gpp-5.c++ -o chameneosredux.gpp-5.c++.o && /usr/bin/g++ chameneosredux.gpp-5.c++.o -o chameneosredux.gpp-5.gpp_run -Wl,--no-as-needed -lpthread 

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native  --std=c++11 -pthread optimized_chameneosredux.gpp-5.c++ -o optimized_chameneosredux.gpp-5.c++.o && /usr/bin/g++ optimized_chameneosredux.gpp-5.c++.o -o optimized_chameneosredux.gpp-5.gpp_run -Wl,--no-as-needed -lpthread 

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./chameneosredux.gpp-5.gpp_run 6000000" c++ chameneosredux
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_chameneosredux.gpp-5.gpp_run 6000000" c++ chameneosredux
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++.csv
	
run:
	./chameneosredux.gpp-5.gpp_run 6000000

run_optimized:
	./optimized_chameneosredux.gpp-5.gpp_run 6000000
mem:
	/usr/bin/time -v ./chameneosredux.gpp-5.gpp_run 6000000

valgrind:
	valgrind --tool=massif --stacks=yes ./chameneosredux.gpp-5.gpp_run 6000000
