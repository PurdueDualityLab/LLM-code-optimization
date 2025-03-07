package jnt.scimark2;

public class LUBenchmark {
    public static void main(String[] args) {
        double min_time = 2.0; // Given constant
        Random R = new Random(101010); // Given constant
        int LU_size = 100; // Given constant

        double result = Kernel.measureLU(LU_size, min_time, R);
        System.out.format("LU Benchmark Result (%s x %s): %.2f Mflops%n", LU_size, LU_size, result);
    }
}
