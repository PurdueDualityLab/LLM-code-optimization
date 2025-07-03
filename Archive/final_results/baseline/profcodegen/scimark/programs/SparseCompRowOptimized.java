package jnt.scimark2;

import java.util.Random;

public class SparseCompRowOptimized {
    
    public static void matmult(double[] y, double[] val, int[] row,
                               int[] col, double[] x, long NUM_ITERATIONS) {
        int M = row.length - 1;
        for (long reps = 0; reps < NUM_ITERATIONS; reps++) {
            for (int r = 0; r < M; r++) {
                double sum = 0.0;
                int rowStart = row[r];
                int rowEnd = row[r + 1];
                for (int i = rowStart; i < rowEnd; i++) {
                    sum += x[col[i]] * val[i];
                }
                y[r] = sum;
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
        int len = a.length;
        for (int i = 0; i < len; i++) {
            sum += Math.abs(a[i] - b[i]);
        }
        return sum;
    }

    public static void main(String[] args) {
        
        int N = 1000;              
        int nz = 10000;            
        long cycles = 524288;      
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
            int step = (int) Math.sqrt(nr); 
            if (step < 1) step = 1;
            for (int i = 0; i < nr; i++) {
                col[rowr + i] = (i * step + r) % N; 
            }
        }

        
        double[] yTest = new double[N];
        double[] yRef = new double[N];

        
        matmult(yTest, val, row, col, x, cycles);

        
        matmult(yRef, val, row, col, x, 1);

        
        double difference = normabs(yTest, yRef);

        System.out.println(difference);
    }
}
