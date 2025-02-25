BENCHMARK ?= fop

compile:
	ant $(BENCHMARK)
measure:
	sudo modprobe msr
	sudo RAPL/main "java -jar dacapo-evaluation-git-unknown$$\{git.dirty\}.jar $(BENCHMARK)" Java $(BENCHMARK) 