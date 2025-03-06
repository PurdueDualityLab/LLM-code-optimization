package jnt.scimark2;

public class FFTBenchmark {
    public static void main(String[] args) {
        int N = 1024;        // FFT size (adjust as needed)
        double mintime = 1.0;  // Minimum run time (seconds) before measuring performance
        // Random R = Random.getInstance();
        Random R = new Random(101010);
        Boolean optimized = args.length > 0 && Boolean.parseBoolean(args[0]);
        double result = Kernel.measureFFT(N, mintime, optimized, R);
        System.out.format("FFT (1024): %.2f Mflops%n", result);
    }
}