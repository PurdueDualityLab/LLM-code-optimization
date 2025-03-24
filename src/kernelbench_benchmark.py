from benchmark import Benchmark

class KernelbenchBenchmark(Benchmark):
	def __init__(self, program: str):
		super(KernelbenchBenchmark, self).__init__(program)
		self.program = program
		self.compilation_error = None
		self.energy_data = {}
		self.evaluator_feedback_data = {}
		self.expect_test_output = None
		self.original_code = None
		self.optimization_iteration = 0