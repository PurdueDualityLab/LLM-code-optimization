TEST ?= org.biojava.nbio.core.sequence.JoiningSequenceReaderTest

compile:
	sudo mvn compile -q	

measure:
	sudo mvn test -Dtest=$(TEST)
	sudo modprobe msr
	sudo ${USER_PREFIX}/MEASURE/main "sudo mvn surefire:test -Dtest=$(TEST)" java $(TEST)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

test:
	sudo mvn test -Dtest=$(TEST)