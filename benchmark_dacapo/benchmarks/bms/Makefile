BENCHMARK ?= fop
TEST_GROUP ?= pdf
TEST_CLASS ?= PDFNumsArray

compile:
ifeq ($(BENCHMARK),fop)
	cd fop/build/fop-2.8/fop-core && sudo mvn test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase
endif

measure:
ifeq ($(BENCHMARK),fop)
	sudo modprobe msr
	sudo ${USER_PREFIX}/RAPL/main "cd $(shell pwd)/fop/build/fop-2.8/fop-core && mvn surefire:test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase" java fop_$(TEST_GROUP)_$(TEST_CLASS)
	sudo chmod -R 777 ${USER_PREFIX}/src/runtime_logs/java.csv
endif

test:
ifeq ($(BENCHMARK),fop)
	cd fop/build/fop-2.8/fop-core && sudo mvn surefire:test -Dtest=org.apache.fop.$(TEST_GROUP).$(TEST_CLASS)TestCase
endif

	