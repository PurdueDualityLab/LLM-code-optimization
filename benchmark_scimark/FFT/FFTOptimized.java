
package jnt.scimark2;

import java.util.stream.IntStream;

public class FFTOptimized {

    public static double num_flops(int N) {
        double logN = log2(N);
        return (5.0 * (double) N - 2) * logN + 2 * ((double) N + 1);
    }

    public static void transform(double[] data) {
        transform_internal(data, -1);
    }

    public static void inverse(double[] data) {
        transform_internal(data, +1);
        int n = data.length / 2;
        double norm = 1.0 / n;
        for (int i = 0; i < data.length; i++)
            data[i] *= norm;
    }

    public static double test(double[] data) {
        int nd = data.length;
        double[] copy = new double[nd];
        System.arraycopy(data, 0, copy, 0, nd);
        transform(data);
        inverse(data);
        double diff = 0.0;
        for (int i = 0; i < nd; i++) {
            double d = data[i] - copy[i];
            diff += d * d;
        }
        return Math.sqrt(diff / nd);
    }

    public static double[] makeRandom(int n) {
        int nd = 2 * n;
        double[] data = new double[nd];
        for (int i = 0; i < nd; i++)
            data[i] = Math.random();
        return data;
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            int n = 1024;
            System.out.println("n=" + n + " => RMS Error=" + test(makeRandom(n)));
        }
        for (String arg : args) {
            int n = Integer.parseInt(arg);
            System.out.println("n=" + n + " => RMS Error=" + test(makeRandom(n)));
        }
    }

    protected static int log2(int n) {
        int log = 0;
        for (int k = 1; k < n; k *= 2, log++);
        if (n != (1 << log))
            throw new Error("FFT: Data length is not a power of 2!: " + n);
        return log;
    }

    protected static void transform_internal(double[] data, int direction) {
        if (data.length == 0) return;
        int n = data.length / 2;
        if (n == 1) return;
        int logn = log2(n);

        
        bitreverse(data);

        
        double[] precomputed_cos = new double[n / 2];
        double[] precomputed_sin = new double[n / 2];
        for (int i = 0; i < n / 2; i++) {
            double angle = 2.0 * Math.PI * i / n;
            precomputed_cos[i] = Math.cos(angle);
            precomputed_sin[i] = Math.sin(angle);
        }

        for (int bit = 0, dual = 1; bit < logn; bit++, dual *= 2) {
            double theta = direction * 2.0 * Math.PI / (2.0 * dual);
            double w_real = 1.0;
            double w_imag = 0.0;
            double s = Math.sin(theta);
            double t = Math.sin(theta / 2.0);
            double s2 = 2.0 * t * t;

            for (int b = 0; b < n; b += 2 * dual) {
                int i = 2 * b;
                int j = 2 * (b + dual);

                double wd_real = data[j];
                double wd_imag = data[j + 1];

                data[j] = data[i] - wd_real;
                data[j + 1] = data[i + 1] - wd_imag;
                data[i] += wd_real;
                data[i + 1] += wd_imag;
            }

            for (int a = 1; a < dual; a++) {
                
                int index = a * n / (2 * dual);
                w_real = precomputed_cos[index];
                w_imag = precomputed_sin[index];
                
                for (int b = 0; b < n; b += 2 * dual) {
                    int i = 2 * (b + a);
                    int j = 2 * (b + a + dual);

                    double z1_real = data[j];
                    double z1_imag = data[j + 1];

                    double wd_real = w_real * z1_real - w_imag * z1_imag;
                    double wd_imag = w_real * z1_imag + w_imag * z1_real;

                    data[j] = data[i] - wd_real;
                    data[j + 1] = data[i + 1] - wd_imag;
                    data[i] += wd_real;
                    data[i + 1] += wd_imag;
                }
            }
        }
    }

    protected static void bitreverse(double[] data) {
        int n = data.length / 2;
        int j = 0;
        for (int i = 0; i < n; i++) {
            if (i < j) { 
                int ii = i << 1;
                int jj = j << 1;
                double tmp_real = data[ii];
                double tmp_imag = data[ii + 1];
                data[ii] = data[jj];
                data[ii + 1] = data[jj + 1];
                data[jj] = tmp_real;
                data[jj + 1] = tmp_imag;
            }
            int m = n >> 1;
            while (m >= 1 && j >= m) {
                j -= m;
                m >>= 1;
            }
            j += m;
        }
    }
}
