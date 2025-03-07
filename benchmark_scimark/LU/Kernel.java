// package jnt.scimark2;

// public class Kernel {
//     // each measurement returns approx Mflops

//     public static double measureLU(int N, double min_time, Random R) {
//         // compute approx Mlfops, or O if LU yields large errors

//         double[][] A = RandomMatrix(N, N, R);
//         double[][] lu = new double[N][N];
//         int[] pivot = new int[N];

//         Stopwatch Q = new Stopwatch();

//         long cycles = 1;
//         while (true) {
//             Q.start();
//             for (int i = 0; i < cycles; i++) {
//                 CopyMatrix(lu, A);
//                 LUOptimized.factor(lu, pivot);
//             }
//             Q.stop();
//             if (Q.read() >= min_time) break;

//             cycles *= 2;
//         }


//         // verify that LU is correct
//         double[] b = RandomVector(N, R);
//         double[] b2 = NewVectorCopy(b);

//         double[] x = NewVectorCopy(b);
//         double[] x2 = NewVectorCopy(b);


//         LU.solve(lu, pivot, x);
//         LUOptimized.solve(lu, pivot, x2);

//         double LUerror = normabs(b, matvec(A, x));
//         double LUOptimizedError = normabs(b2, matvec(A, x2));

//         System.out.println( "LU error: " + LUerror);
//         System.out.println( "LUOptimized error: "+ LUOptimizedError);
//         if (Math.abs(LUerror - LUOptimizedError) > 0) {
//             System.out.println("Regression test failed for LUOptimized");
//             return 0.0;
//         }

//         final double EPS = 1.0e-12;
//         if (normabs(b, matvec(A, x)) / N > EPS)
//             return 0.0;


//         // else return approx Mflops
//         //
//         return LU.num_flops(N) * cycles / Q.read() * 1.0e-6;
//     }


//     private static double[] NewVectorCopy(double[] x) {
//         int N = x.length;

//         double[] y = new double[N];
//         System.arraycopy(x, 0, y, 0, N);

//         return y;
//     }

//     private static double normabs(double[] x, double[] y) {
//         int N = x.length;
//         double sum = 0.0;

//         for (int i = 0; i < N; i++)
//             sum += Math.abs(x[i] - y[i]);

//         return sum;
//     }

//     private static void CopyMatrix(double[][] B, double[][] A) {
//         int M = A.length;
//         int N = A[0].length;

//         int remainder = N & 3;         // N mod 4;

//         for (int i = 0; i < M; i++) {
//             double[] Bi = B[i];
//             double[] Ai = A[i];
//             System.arraycopy(Ai, 0, Bi, 0, remainder);
//             for (int j = remainder; j < N; j += 4) {
//                 Bi[j] = Ai[j];
//                 Bi[j + 1] = Ai[j + 1];
//                 Bi[j + 2] = Ai[j + 2];
//                 Bi[j + 3] = Ai[j + 3];
//             }
//         }
//     }

//     // private static double[][] RandomMatrix(int M, int N, Random R) {
//     //     double[][] A = new double[M][N];

//     //     for (int i = 0; i < N; i++)
//     //         for (int j = 0; j < N; j++)
//     //             A[i][j] = R.nextDouble();
//     //     return A;
//     // }

//     // private static double[] RandomVector(int N, Random R) {
//     //     double[] A = new double[N];

//     //     for (int i = 0; i < N; i++)
//     //         A[i] = R.nextDouble();
//     //     return A;
//     // }

//     // private static double[] matvec(double[][] A, double[] x) {
//     //     int N = x.length;
//     //     double[] y = new double[N];

//     //     matvec(A, x, y);

//     //     return y;
//     // }

//     // private static void matvec(double[][] A, double[] x, double[] y) {
//     //     int M = A.length;
//     //     int N = A[0].length;

//     //     for (int i = 0; i < M; i++) {
//     //         double sum = 0.0;
//     //         double[] Ai = A[i];
//     //         for (int j = 0; j < N; j++)
//     //             sum += Ai[j] * x[j];

//     //         y[i] = sum;
//     //     }
//     // }

// }
