package jnt.scimark2;

public class MonteCarloBenchmark {
    public static void main(String[] args) {
        double mintime = 2.0; // Given constant
        Random R = new Random(101010);

        double result = Kernel.measureMonteCarlo(mintime, R);
        System.out.format("Monte Carlo Benchmark Result: %.2f Mflops%n", result);
    }
}