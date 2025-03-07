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
        int nd = data.length;
        int n = nd / 2;
        double norm = 1.0 / n;
        for (int i = 0; i < nd; i++) {
            data[i] *= norm;
        }
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
        for (int i = 0; i < nd; i++) {
            data[i] = Math.random();
        }
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
        if (n <= 0 || (n & (n - 1)) != 0) throw new IllegalArgumentException("FFT: Data length is not a power of 2!: " + n);
        return Integer.numberOfTrailingZeros(n);
    }

    protected static void transform_internal(double[] data, int direction) {
        if (data.length == 0) return;

        int n = data.length / 2;
        int logn = log2(n);

        bitreverse(data);

        double[] cosTable = new double[n / 2];
        double[] sinTable = new double[n / 2];
        for (int i = 0; i < n / 2; i++) {
            double angle = 2 * Math.PI * i / n;
            cosTable[i] = Math.cos(angle);
            sinTable[i] = Math.sin(angle);
        }

        int dual = 1;
        for (int bit = 0; bit < logn; bit++, dual *= 2) {
            for (int b = 0; b < n; b += 2 * dual) {
                for (int j = 0; j < dual; j++) {
                    int i = 2 * (b + j), k = 2 * (b + j + dual);
                    int index = j * (n / (2 * dual));
                    double cos = cosTable[index];
                    double sin = direction * sinTable[index];

                    double tempReal = cos * data[k] - sin * data[k + 1];
                    double tempImag = sin * data[k] + cos * data[k + 1];

                    data[k] = data[i] - tempReal;
                    data[k + 1] = data[i + 1] - tempImag;
                    data[i] += tempReal;
                    data[i + 1] += tempImag;
                }
            }
        }
    }

    protected static void bitreverse(double[] data) {
        int n = data.length / 2;
        int j = 0;
        for (int i = 0; i < n; i++) {
            if (i < j) {
                int swapIndex = j << 1;
                int currentIndex = i << 1;
                swap(data, swapIndex, currentIndex);
            }
            int m = n >> 1;
            while (j >= m && m > 0) {
                j -= m;
                m >>= 1;
            }
            j += m;
        }
    }

    private static void swap(double[] data, int a, int b) {
        double tempReal = data[a];
        double tempImag = data[a + 1];
        data[a] = data[b];
        data[a + 1] = data[b + 1];
        data[b] = tempReal;
        data[b + 1] = tempImag;
    }
}