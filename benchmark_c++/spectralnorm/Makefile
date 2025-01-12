include ../../.env

compile:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native -mfpmath=sse -msse2 -fopenmp -mfpmath=sse -msse2 spectralnorm.gpp-6.c++ -o spectralnorm.gpp-6.c++.o &&  /usr/bin/g++ spectralnorm.gpp-6.c++.o -o spectralnorm.gpp-6.gpp_run -fopenmp

compile_optimized:
	/usr/bin/g++ -c -pipe -fomit-frame-pointer -march=native -mfpmath=sse -msse2 -fopenmp -mfpmath=sse -msse2 optimized_spectralnorm.gpp-6.c++ -o optimized_spectralnorm.gpp-6.c++.o &&  /usr/bin/g++ optimized_spectralnorm.gpp-6.c++.o -o optimized_spectralnorm.gpp-6.gpp_run -fopenmp

measure:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./spectralnorm.gpp-6.gpp_run 5500" c++ spectral-norm
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

measure_optimized:
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "./optimized_spectralnorm.gpp-6.gpp_run 5500" c++ spectral-norm
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/c++/c++.csv

run:
	./spectralnorm.gpp-6.gpp_run 5500

run_optimized:
	./optimized_spectralnorm.gpp-6.gpp_run 5500

mem:
	/usr/bin/time -v ./spectralnorm.gpp-6.gpp_run 5500

valgrind:
	valgrind --tool=massif --stacks=yes ./spectralnorm.gpp-6.gpp_run 5500
