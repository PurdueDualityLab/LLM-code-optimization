package jnt.scimark2;

public class SparseCompRowBenchmark {
    public static void main(String[] args) {
        int N = 1000; // Given constant
        int nz = 5000; // Givent constant
        double mintime = 2.0; // Given constant
        Random R = new Random(101010);

        double result = Kernel.measureSparseMatmult(N, nz, mintime, R);
        System.out.format("Sparse CompRow Benchmark Result: %.2f Mflops%n", result);
    }
}