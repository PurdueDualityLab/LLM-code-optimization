package jnt.scimark2;

public class LUOptimized {
    private final double[][] LU_;
    private final int[] pivot_;

    public static void main(String[] args) {
        Random R = new Random(101010);
        int N = 1000;
        
        double[][] A = RandomMatrix(N, N, R);
        double[][] lu = new double[N][N];
        int[] pivot = new int[N];

        CopyMatrix(lu, A);

        int status = factor(lu, pivot);
        if (status != 0) {
            System.err.println("LU factorization failed due to singular matrix.");
            return;
        }
        
        double[] b = RandomVector(N, R);
        double[] x = NewVectorCopy(b);

        solve(lu, pivot, x);
        System.out.println(normabs(b, matvec(A, x)) / N);
    }

    public LUOptimized(double[][] A) {
        int M = A.length;
        int N = A[0].length;

        LU_ = new double[M][N];

        insert_copy(LU_, A);

        pivot_ = new int[M];

        factor(LU_, pivot_);
    }

    private static double[] NewVectorCopy(double[] x) {
        int N = x.length;

        double[] y = new double[N];
        System.arraycopy(x, 0, y, 0, N);

        return y;
    }

    private static double[][] RandomMatrix(int M, int N, Random R) {
        double[][] A = new double[M][N];

        for (int i = 0; i < M; i++) {
            for (int j = 0; j < N; j++) {
                A[i][j] = R.nextDouble();
            }
        }
        return A;
    }

    private static double[] RandomVector(int N, Random R) {
        double[] A = new double[N];

        for (int i = 0; i < N; i++) {
            A[i] = R.nextDouble();
        }
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
            for (int j = 0; j < N; j++) {
                sum += Ai[j] * x[j];
            }
            y[i] = sum;
        }
    }

    private static double normabs(double[] x, double[] y) {
        int N = x.length;
        double sum = 0.0;

        for (int i = 0; i < N; i++) {
            sum += Math.abs(x[i] - y[i]);
        }

        return sum;
    }

    private static void CopyMatrix(double[][] B, double[][] A) {
        int M = A.length;
        int N = A[0].length;

        for (int i = 0; i < M; i++) {
            System.arraycopy(A[i], 0, B[i], 0, N);
        }
    }

    protected static double[] new_copy(double[] x) {
        int N = x.length;
        double[] T = new double[N];
        System.arraycopy(x, 0, T, 0, N);
        return T;
    }

    protected static double[][] new_copy(double[][] A) {
        int M = A.length;
        int N = A[0].length;

        double[][] T = new double[M][N];

        for (int i = 0; i < M; i++) {
            System.arraycopy(A[i], 0, T[i], 0, N);
        }

        return T;
    }

    public static int[] new_copy(int[] x) {
        int N = x.length;
        int[] T = new int[N];
        System.arraycopy(x, 0, T, 0, N);
        return T;
    }

    protected static void insert_copy(double[][] B, double[][] A) {
        int M = A.length;
        int N = A[0].length;

        for (int i = 0; i < M; i++) {
            System.arraycopy(A[i], 0, B[i], 0, N);
        }
    }

    public static int factor(double[][] A, int[] pivot) {
        int N = A.length;
        int M = A[0].length;

        int minMN = Math.min(M, N);

        for (int j = 0; j < minMN; j++) {
            int jp = j;
            double max = Math.abs(A[j][j]);

            for (int i = j + 1; i < M; i++) {
                double ab = Math.abs(A[i][j]);
                if (ab > max) {
                    jp = i;
                    max = ab;
                }
            }

            pivot[j] = jp;

            if (A[jp][j] == 0) return 1;

            if (jp != j) {
                double[] temp = A[j];
                A[j] = A[jp];
                A[jp] = temp;
            }

            if (j < M - 1) {
                double recp = 1.0 / A[j][j];
                for (int k = j + 1; k < M; k++) {
                    A[k][j] *= recp;
                }
            }

            for (int i = j + 1; i < M; i++) {
                double[] Ai = A[i];
                double[] Aj = A[j];
                double Aij = Ai[j];
                for (int k = j + 1; k < N; k++) {
                    Ai[k] -= Aij * Aj[k];
                }
            }
        }
        return 0;
    }

    public static void solve(double[][] LU, int[] pvt, double[] b) {
        int M = LU.length;
        int N = LU[0].length;
        int ii = 0;

        for (int i = 0; i < M; i++) {
            int ip = pvt[i];
            double sum = b[ip];
            b[ip] = b[i];
            if (ii == 0) {
                for (int j = ii; j < i; j++) {
                    sum -= LU[i][j] * b[j];
                }
            } else if (sum == 0.0) {
                ii = i;
            }
            b[i] = sum;
        }

        for (int i = N - 1; i >= 0; i--) {
            double sum = b[i];
            for (int j = i + 1; j < N; j++) {
                sum -= LU[i][j] * b[j];
            }
            b[i] = sum / LU[i][i];
        }
    }

    public double[][] getLU() {
        return new_copy(LU_);
    }

    public double[] solve(double[] b) {
        double[] x = new_copy(b);

        solve(LU_, pivot_, x);
        return x;
    }
}
