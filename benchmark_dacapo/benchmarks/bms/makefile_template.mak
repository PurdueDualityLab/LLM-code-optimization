BENCHMARK ?= fop
TEST_GROUP ?= pdf
TEST_CLASS ?= PDFNumsArray
TEST_FOLDER ?= core

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
	sudo modprobe msr
	sudo /home/rishi/E2COOL/RAPL/main "mvn surefire:test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase" java fop_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 /home/rishi/E2COOL/src/runtime_logs/java.csv
endif
ifeq ($(BENCHMARK),spring)
	sudo modprobe msr
	sudo /home/rishi/E2COOL/RAPL/main "mvn surefire:test -Dtest=org.springframework.samples.petclinic.$(TEST_GROUP).$(TEST_CLASS)Tests" java spring_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 /home/rishi/E2COOL/src/runtime_logs/java.csv
endif
ifeq ($(BENCHMARK), biojava)
	sudo modprobe msr
	sudo /home/rishi/E2COOL/RAPL/main "mvn surefire:test -Dtest=org.biojava.nbio.$(TEST_FOLDER).$(TEST_GROUP).$(TEST_CLASS)Test" java biojava_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 /home/rishi/E2COOL/src/runtime_logs/java.csv
endif
ifeq ($(BENCHMARK), pmd)
	sudo modprobe msr
	sudo /home/rishi/E2COOL/RAPL/main "mvn surefire:test -Dtest=net.sourceforge.pmd.$(TEST_GROUP).$(TEST_CLASS)Test" java pmd_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 /home/rishi/E2COOL/src/runtime_logs/java.csv
endif

test:
ifeq ($(BENCHMARK),fop)
	sudo mvn surefire:test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase
endif
ifeq ($(BENCHMARK),spring)
	sudo mvn surefire:test -Dtest=org.springframework.samples.petclinic.$(TEST_GROUP).$(TEST_CLASS)Tests
endif
ifeq ($(BENCHMARK), biojava)
	sudo mvn surefire:test -Dtest=org.biojava.nbio.$(TEST_FOLDER).$(TEST_GROUP).$(TEST_CLASS)Test
endif
ifeq ($(BENCHMARK), pmd)
	sudo mvn surefire:test -Dtest=net.sourceforge.pmd.$(TEST_GROUP).$(TEST_CLASS)Test
endif