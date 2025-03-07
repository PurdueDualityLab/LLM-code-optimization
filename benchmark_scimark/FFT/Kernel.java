package jnt.scimark2;
import java.io.*;

import jnt.scimark2.FFTOptimized;

public class Kernel {
    private static final String FILE_NAME = "vector.txt";
    private static double[] x;
    public static void main(String[] args) {
        Random R = new Random(101010);

        x = loadVector();

        if (x == null) {
            x = RandomVector(2 * 1024, R);
            saveVector(FILE_NAME, x);
        }
    }

    public static void saveVector(String fileName, double[] vector) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(fileName))) {
            for (double v : vector) {
                writer.write(v + "\n");
            }
        } catch (IOException e) {
            System.err.println("Error saving vector: " + e.getMessage());
        }
    }

    public static double[] loadVector() {
        File file = new File(FILE_NAME);
        if (!file.exists()) {
            return null; 
        }
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            return reader.lines().mapToDouble(Double::parseDouble).toArray();
        } catch (IOException e) {
            System.err.println("Error loading vector: " + e.getMessage());
            return null;
        }
    }

    public static double measureFFT(int N, double mintime, boolean optimized, Random R) {
        // initialize FFT data as complex (N real/img pairs)
        double[] x = RandomVector(2 * N, R);
        double[] oldx = NewVectorCopy(x);
        long cycles = 1;
        Stopwatch Q = new Stopwatch();

        while (true) {
            Q.start();
            for (int i = 0; i < cycles; i++) {
                if (optimized){
                    FFTOptimized.transform(x);    // forward transform
                    FFTOptimized.inverse(x);        // backward transform
                } else {
                    FFT.transform(x);    // forward transform
                    FFT.inverse(x);        // backward transform
                }
            }
            Q.stop();
            if (Q.read() >= mintime)
                break;

            cycles *= 2;
        }
        // approx Mflops

        final double EPS = 3.0e-17;
        if (optimized){               
            if (FFTOptimized.test(x) / N > EPS)
                return 0.0;
            return FFTOptimized.num_flops(N) * cycles / Q.read() * 1.0e-6;
        }

        if (FFT.test(x) / N > EPS)
            return 0.0;
        return FFT.num_flops(N) * cycles / Q.read() * 1.0e-6;
    }

    private static double[] NewVectorCopy(double[] x) {
        int N = x.length;

        double[] y = new double[N];
        System.arraycopy(x, 0, y, 0, N);

        return y;
    }

    private static double normabs(double[] x, double[] y) {
        int N = x.length;
        double sum = 0.0;

        for (int i = 0; i < N; i++)
            sum += Math.abs(x[i] - y[i]);

        return sum;
    }

    private static void CopyMatrix(double[][] B, double[][] A) {
        int M = A.length;
        int N = A[0].length;

        int remainder = N & 3;         // N mod 4;

        for (int i = 0; i < M; i++) {
            double[] Bi = B[i];
            double[] Ai = A[i];
            System.arraycopy(Ai, 0, Bi, 0, remainder);
            for (int j = remainder; j < N; j += 4) {
                Bi[j] = Ai[j];
                Bi[j + 1] = Ai[j + 1];
                Bi[j + 2] = Ai[j + 2];
                Bi[j + 3] = Ai[j + 3];
            }
        }
    }

    private static double[][] RandomMatrix(int M, int N, Random R) {
        double[][] A = new double[M][N];

        for (int i = 0; i < N; i++)
            for (int j = 0; j < N; j++)
                A[i][j] = R.nextDouble();
        return A;
    }

    private static double[] RandomVector(int N, Random R) {
        double[] A = new double[N];

        for (int i = 0; i < N; i++)
            A[i] = R.nextDouble();
        return A;
    }

    private static double[] matvec(double[][] A, double[] x) {
        int N = x.length;
        double[] y = new double[N];

        matvec(A, x, y);

        return y;
    }

    private static void matvec(double[][] A, double[] x, double[] y) {
        int M = A.length;
        int N = A[0].length;

        for (int i = 0; i < M; i++) {
            double sum = 0.0;
            double[] Ai = A[i];
            for (int j = 0; j < N; j++)
                sum += Ai[j] * x[j];

            y[i] = sum;
        }
    }

}
