package jnt.scimark2;

import java.util.Random;
import java.util.concurrent.ForkJoinPool;
import java.util.concurrent.RecursiveAction;

public class SparseCompRowOptimized {
    private static final ForkJoinPool forkJoinPool = new ForkJoinPool();

    
    public static void matmultParallel(double[] y, double[] val, int[] row,
                                       int[] col, double[] x, long NUM_ITERATIONS) {
        int M = row.length - 1;
        for (long reps = 0; reps < NUM_ITERATIONS; reps++) {
            forkJoinPool.invoke(new ParallelMatMultTask(y, val, row, col, x, 0, M));
        }
    }

    private static class SparseCompRowOptimized extends RecursiveAction {
        private final double[] y, val, x;
        private final int[] row, col;
        private final int start, end;

        ParallelMatMultTask(double[] y, double[] val, int[] row, int[] col, double[] x, int start, int end) {
            this.y = y;
            this.val = val;
            this.row = row;
            this.col = col;
            this.x = x;
            this.start = start;
            this.end = end;
        }

        @Override
        protected void compute() {
            if (end - start <= 10) { 
                for (int r = start; r < end; r++) {
                    double sum = 0.0;
                    int rowStart = row[r];
                    int rowEnd = row[r + 1];
                    for (int i = rowStart; i < rowEnd; i++) {
                        sum += x[col[i]] * val[i];
                    }
                    y[r] = sum;
                }
            } else {
                int mid = start + (end - start) / 2;
                invokeAll(new ParallelMatMultTask(y, val, row, col, x, start, mid),
                          new ParallelMatMultTask(y, val, row, col, x, mid, end));
            }
        }
    }

    
    private static double[] randomVector(int N, Random R) {
        double[] A = new double[N];
        for (int i = 0; i < N; i++) {
            A[i] = R.nextDouble();
        }
        return A;
    }

    
    private static double normabs(double[] a, double[] b) {
        double sum = 0.0;
        for (int i = 0; i < a.length; i++) {
            sum += Math.abs(a[i] - b[i]);
        }
        return sum;
    }

    public static void main(String[] args) {
        int N = 1000;
        int nz = 10000;
        long cycles = 524288;
        double regressionThreshold = 1.0e-10;
        long seed = 101010;

        Random rand1 = new Random(seed);
        Random rand2 = new Random(seed + 1);

        double[] x = randomVector(N, rand1);

        int nr = nz / N;
        int anz = nr * N;
        double[] val = randomVector(anz, rand2);
        int[] col = new int[anz];
        int[] row = new int[N + 1];
        row[0] = 0;
        for (int r = 0; r < N; r++) {
            int rowr = row[r];
            row[r + 1] = rowr + nr;
            int step = Math.max(r / nr, 1);
            for (int i = 0; i < nr; i++) {
                col[rowr + i] = i * step;
            }
        }

        double[] yTest = new double[N];
        double[] yRef = new double[N];

        matmultParallel(yTest, val, row, col, x, cycles);
        matmultParallel(yRef, val, row, col, x, 1);

        double difference = normabs(yTest, yRef);

        System.out.println(difference);
    }
}