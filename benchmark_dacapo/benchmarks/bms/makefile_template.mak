BENCHMARK ?= fop
TEST_GROUP ?= pdf
TEST_CLASS ?= PDFNumsArray
TEST_FOLDER ?= core
TEST ?= org.biojava.nbio.core.sequence.JoiningSequenceReaderTest

compile:
ifeq ($(BENCHMARK),fop)
	sudo mvn compile -q
endif
ifeq ($(BENCHMARK),spring)
	sudo mvn compile -q
endif
ifeq ($(BENCHMARK), biojava)
	sudo mvn compile -q
endif
ifeq ($(BENCHMARK), pmd)
	sudo mvn compile -q
endif

measure:
ifeq ($(BENCHMARK),fop)
	sudo mvn test -Dtest=$(TEST)
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "sudo mvn surefire:test -Dtest=$(TEST)" java fop_$(TEST)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv
endif
ifeq ($(BENCHMARK),spring)
	sudo mvn test -Dtest=$(TEST)
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "sudo mvn surefire:test -Dtest=org.springframework.samples.petclinic.$(TEST_GROUP).$(TEST_CLASS)Tests" java spring_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv
endif
ifeq ($(BENCHMARK), biojava)
	sudo mvn test -Dtest=$(TEST)
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "sudo mvn surefire:test -Dtest=$(TEST)" java biojava_$(TEST)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv
endif
ifeq ($(BENCHMARK), pmd)
	sudo mvn test -Dtest=$(TEST)
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "sudo mvn surefire:test -Dtest=net.sourceforge.pmd.$(TEST_GROUP).$(TEST_CLASS)Test" java pmd_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv
endif

test:
ifeq ($(BENCHMARK),fop)
	sudo mvn test -Dtest=$(TEST)
endif
ifeq ($(BENCHMARK),spring)
	sudo mvn test -Dtest=org.springframework.samples.petclinic.$(TEST_GROUP).$(TEST_CLASS)Tests
endif
ifeq ($(BENCHMARK), biojava)
	sudo mvn test -Dtest=$(TEST)
endif
ifeq ($(BENCHMARK), pmd)
	sudo mvn test -Dtest=net.sourceforge.pmd.$(TEST_GROUP).$(TEST_CLASS)Test
endif