package jnt.scimark2;

public class Kernel {
    // each measurement returns approx Mflops

    public static double measureSparseMatmult(int N, int nz,
                                              double min_time, Random R) {
        // initialize vector multipliers and storage for result
        // y = A*y;

        double[] x = RandomVector(N, R);
        double[] y = new double[N];

        // initialize square sparse matrix
        //
        // for this test, we create a sparse matrix wit M/nz nonzeros
        // per row, with spaced-out evenly between the begining of the
        // row to the main diagonal.  Thus, the resulting pattern looks
        // like
        //             +-----------------+
        //             +*                +
        //             +***              +
        //             +* * *            +
        //             +** *  *          +
        //             +**  *   *        +
        //             +* *   *   *      +
        //             +*  *   *    *    +
        //             +*   *    *    *  +
        //             +-----------------+
        //
        // (as best reproducible with integer artihmetic)
        // Note that the first nr rows will have elements past
        // the diagonal.

        int nr = nz / N;        // average number of nonzeros per row
        int anz = nr * N;   // _actual_ number of nonzeros


        double[] val = RandomVector(anz, R);
        int[] col = new int[anz];
        int[] row = new int[N + 1];

        row[0] = 0;
        for (int r = 0; r < N; r++) {
            // initialize elements for row r

            int rowr = row[r];
            row[r + 1] = rowr + nr;
            int step = r / nr;
            if (step < 1) step = 1;   // take at least unit steps


            for (int i = 0; i < nr; i++)
                col[rowr + i] = i * step;

        }

        Stopwatch Q = new Stopwatch();

        long cycles = 1;
        while (true) {
            Q.start();
            SparseCompRow.matmult(y, val, row, col, x, cycles);
            Q.stop();
            if (Q.read() >= min_time) break;

            cycles *= 2;
        }
        // approx Mflops
        return SparseCompRow.num_flops(N, nz, cycles) / Q.read() * 1.0e-6;
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
