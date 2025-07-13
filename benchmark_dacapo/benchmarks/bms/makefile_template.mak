TEST ?= org.biojava.nbio.core.sequence.JoiningSequenceReaderTest

compile:
	mvn compile -q	

test:
	mvn test -Dtest=$(TEST)