package jnt.scimark2;

public class FFTOptimized {

    public static void transform(double[] data) {
        transform_internal(data, -1);
    }

    public static void inverse(double[] data) {
        transform_internal(data, +1);
        
        int nd = data.length;
        int n = nd / 2;
        double norm = 1 / ((double) n);
        for (int i = 0; i < nd; i++)
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
        int n = 1048576; 
        double[] randomData = makeRandom(n);
        if (args.length == 0) {
            System.out.println(test(randomData) / 1048576);
        }
        for (int i = 0; i < args.length; i++) {
            n = Integer.parseInt(args[i]);
            System.out.println(test(randomData) / 1048576);
        }
    }

    protected static int log2(int n) {
        return (31 - Integer.numberOfLeadingZeros(n));
    }

    protected static void transform_internal(double[] data, int direction) {
        if (data.length == 0) return;
        int n = data.length / 2;
        if (n == 1) return;         
        int logn = log2(n);

        
        bitreverse(data);

        
        
        for (int bit = 0, dual = 1; bit < logn; bit++, dual *= 2) {
            double w_real = 1.0;
            double w_imag = 0.0;

            double theta = 2.0 * direction * Math.PI / (2.0 * (double) dual);
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
                
                {
                    double tmp_real = w_real - s * w_imag - s2 * w_real;
                    double tmp_imag = w_imag + s * w_real - s2 * w_imag;
                    w_real = tmp_real;
                    w_imag = tmp_imag;
                }
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
        int nm1 = n - 1;
        int i = 0;
        int j = 0;
        for (; i < nm1; i++) {

            
            int ii = i << 1;

            
            int jj = j << 1;

            
            int k = n >> 1;

            if (i < j) {
                double tmp_real = data[ii];
                double tmp_imag = data[ii + 1];
                data[ii] = data[jj];
                data[ii + 1] = data[jj + 1];
                data[jj] = tmp_real;
                data[jj + 1] = tmp_imag;
            }

            while (k <= j) {
                
                j -= k;

                
                k >>= 1;
            }
            j += k;
        }
    }
}
