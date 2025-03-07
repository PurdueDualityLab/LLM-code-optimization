package jnt.scimark2;

public class SparseCompRowOptimized {
	/* multiple iterations used to make Kernel have roughly
		same granulairty as other Scimark kernels. */

    public static double num_flops(int N, int nz, long num_iterations) {
		/* Note that if nz does not divide N evenly, then the
		   actual number of nonzeros used is adjusted slightly.
		*/
        int actual_nz = (nz / N) * N;
        return ((double) actual_nz) * 2.0 * ((double) num_iterations);
    }


	/* computes  a matrix-vector multiply with a sparse matrix
		held in compress-row format.  If the size of the matrix
		in MxN with nz nonzeros, then the val[] is the nz nonzeros,
		with its ith entry in column col[i].  The integer vector row[]
		is of size M+1 and row[i] points to the begining of the
		ith row in col[].  
	*/

    public static void matmult(double[] y, double[] val, int[] row,
							   int[] col, double[] x, long NUM_ITERATIONS) {
        int M = row.length - 1;

        for (long reps = 0; reps < NUM_ITERATIONS; reps++) {

            for (int r = 0; r < M; r++) {
                double sum = 0.0;
                int rowR = row[r];
                int rowRp1 = row[r + 1];
                for (int i = rowR; i < rowRp1; i++)
                    sum += x[col[i]] * val[i];
                y[r] = sum;
            }
        }
    }

}
