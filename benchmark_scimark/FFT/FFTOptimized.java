package jnt.scimark2;

public class FFTOptimized {

    public static void transform(double[] data) {
        int n = data.length;
        double[] real = new double[n];
        double[] imag = new double[n];

        for (int i = 0; i < n; i++) {
            real[i] = data[i];
        }

        fft(real, imag);
    }

    public static void inverse(double[] data) {
        int n = data.length;
        double[] real = new double[n];
        double[] imag = new double[n];

        for (int i = 0; i < n; i++) {
            real[i] = data[i];
        }

        ifft(real, imag);
    }

    private static void fft(double[] real, double[] imag) {
        int n = real.length;
        if (n <= 1) {
            return;
        }

        double[] realEven = new double[n / 2];
        double[] imagEven = new double[n / 2];
        double[] realOdd = new double[n / 2];
        double[] imagOdd = new double[n / 2];

        for (int i = 0; i < n / 2; i++) {
            realEven[i] = real[2 * i];
            imagEven[i] = imag[2 * i];
            realOdd[i] = real[2 * i + 1];
            imagOdd[i] = imag[2 * i + 1];
        }

        fft(realEven, imagEven);
        fft(realOdd, imagOdd);

        for (int k = 0; k < n / 2; k++) {
            double twiddleReal = Math.cos(2 * Math.PI * k / n);
            double twiddleImag = -Math.sin(2 * Math.PI * k / n);

            double tempReal = realOdd[k] * twiddleReal - imagOdd[k] * twiddleImag;
            double tempImag = realOdd[k] * twiddleImag + imagOdd[k] * twiddleReal;

            real[k] = realEven[k] + tempReal;
            imag[k] = imagEven[k] + tempImag;
            real[n / 2 + k] = realEven[k] - tempReal;
            imag[n / 2 + k] = imagEven[k] - tempImag;
        }
    }

    private static void ifft(double[] real, double[] imag) {
        int n = real.length;

        for (int i = 0; i < n / 2; i++) {
            double tempReal = real[i];
            double tempImag = imag[i];

            real[i] = real[n - 1 - i];
            imag[i] = -imag[n - 1 - i];

            real[n - 1 - i] = tempReal;
            imag[n - 1 - i] = -tempImag;
        }

        fft(real, imag);

        for (int i = 0; i < n; i++) {
            real[i] /= n;
            imag[i] /= n;
        }
    }

    public static void main(String[] args) {
        double[] x = {1, 2, 3, 4, 5, 6, 7, 8};
        transform(x); 
        inverse(x); 

        for (double value : x) {
            System.out.print(value + " ");
        }
    }
}
