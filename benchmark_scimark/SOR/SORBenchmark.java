package jnt.scimark2;

public class SORBenchmark {
    public static void main(String[] args) {
        // Define matrix size and number of iterations
        int N = 100;              // Matrix dimension (N x N)
        long num_iterations = 100;  // Number of iterations to run
        double omega = 1.25;        // Relaxation factor

        // Initialize the matrix with a fixed value (for example, 1.0)
        double[][] G = new double[N][N];
        double[][] G_Optimized = new double[N][N];

        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                G[i][j] = 1.0;
                G_Optimized[i][j] = 1.0;
            }
        }

        // Optional warm-up to allow JIT optimizations (executed only once)
        SOR.execute(omega, G, 1);
        SOROptimized.execute(omega, G_Optimized, 1);

        // Time the SOR execution over the specified number of iterations
        long startTime = System.nanoTime();
        SOROptimized.execute(omega, G, num_iterations);
        long endTime = System.nanoTime();

        // Compute the elapsed time in seconds
        double elapsedTime = (endTime - startTime) / 1e9;

        // Calculate the total number of floating-point operations
        double flops = SOR.num_flops(N, N, num_iterations);

        // Compute performance in millions of flops per second (MFLOPS)
        double mflops = flops / (elapsedTime * 1e6);

        double regressionThreshold = 1.0e-12;
        double error = 0.0;
        for (int i = 0; i < N; i++) {
            for (int j = 0; j < N; j++) {
                error += Math.abs(G[i][j] - G_Optimized[i][j]);
            }
        }
        System.out.println("Error: " + error);
        if (error > regressionThreshold) {
            System.out.println("Regression test failed, difference: " + error);
            return;
        }

        // Print the benchmark result
        System.out.format("SOR (%d x %d, %d iterations): %.2f Mflops%n", N, N, num_iterations, mflops);
    }
}