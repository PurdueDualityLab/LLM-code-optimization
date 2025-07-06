TEST ?= org.biojava.nbio.core.sequence.JoiningSequenceReaderTest

compile:
	mvn compile -q	

measure:
	mvn test -Dtest=$(TEST)
	modprobe msr
	${USER_PREFIX}/MEASURE/main "sudo mvn surefire:test -Dtest=$(TEST)" java $(TEST)
	chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv

test:
	mvn test -Dtest=$(TEST)