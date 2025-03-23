BENCHMARK ?= fop
TEST_GROUP ?= pdf
TEST_CLASS ?= PDFNumsArray

compile:
ifeq ($(BENCHMARK),fop)
	sudo mvn compile -q
endif

measure:
ifeq ($(BENCHMARK),fop)
	sudo modprobe msr
	sudo /home/hpeng/E2COOL/RAPL/main "mvn surefire:test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase" java fop_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 /home/hpeng/E2COOL/src/runtime_logs/java.csv
endif

test:
ifeq ($(BENCHMARK),fop)
	sudo mvn surefire:test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase
endif

	