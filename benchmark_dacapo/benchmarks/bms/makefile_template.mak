TEST ?= org.biojava.nbio.core.sequence.JoiningSequenceReaderTest

compile:
	mvn compile -q	

measure:
	sudo mvn test -Dtest=$(TEST)
	sudo modprobe msr
	sudo /home/hpeng/E2COOL/MEASURE/main "sudo mvn surefire:test -Dtest=$(TEST)" java $(TEST)
	sudo chmod -R 777 /home/hpeng/E2COOL/src/runtime_logs/java.csv

test:
	mvn test -Dtest=$(TEST)