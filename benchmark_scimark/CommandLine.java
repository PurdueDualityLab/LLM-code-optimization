package jnt.scimark2;

/**
 * SciMark2: A Java numerical benchmark measuring performance
 * of computational kernels for FFTs, Monte Carlo simulation,
 * sparse matrix computations, Jacobi SOR, and dense LU matrix
 * factorizations.
 */
public class CommandLine {
    private static final String[] DUMP_PROPERTIES = new String[]{
            "java.vendor",
            "java.version",
            "os.arch",
            "os.name",
            "os.version"
    };

    public static void main(String[] args) {
        // default to the (small) cache-contained version

        System.out.println();
        System.out.println("SciMark " + CommandLine.class.getPackage().getImplementationVersion());
        System.out.println();

        double min_time = Constants.RESOLUTION_DEFAULT;

        int FFT_size = Constants.FFT_SIZE;
        int SOR_size = Constants.SOR_SIZE;
        int Sparse_size_M = Constants.SPARSE_SIZE_M;
        int Sparse_size_nz = Constants.SPARSE_SIZE_nz;
        int LU_size = Constants.LU_SIZE;

        // look for runtime options

        if (args.length > 0) {

            if (args[0].equalsIgnoreCase("-h") ||
                    args[0].equalsIgnoreCase("-help")) {
                System.out.println("Usage: [-large] [minimum_time]");
                return;
            }

            int current_arg = 0;
            if (args[current_arg].equalsIgnoreCase("-large")) {
                FFT_size = Constants.LG_FFT_SIZE;
                SOR_size = Constants.LG_SOR_SIZE;
                Sparse_size_M = Constants.LG_SPARSE_SIZE_M;
                Sparse_size_nz = Constants.LG_SPARSE_SIZE_nz;
                LU_size = Constants.LG_LU_SIZE;

                current_arg++;
            }

            if (args.length > current_arg)
                min_time = Double.parseDouble(args[current_arg]);
        }


        // run the benchmark

        double[] res = new double[6];
        Random R = new Random(Constants.RANDOM_SEED);

        res[1] = Kernel.measureFFT(FFT_size, min_time, R);
        res[2] = Kernel.measureSOR(SOR_size, min_time, R);
        res[3] = Kernel.measureMonteCarlo(min_time, R);
        res[4] = Kernel.measureSparseMatmult(Sparse_size_M,
                Sparse_size_nz, min_time, R);
        res[5] = Kernel.measureLU(LU_size, min_time, R);


        res[0] = (res[1] + res[2] + res[3] + res[4] + res[5]) / 5;



        // print out results
        System.out.format("Composite Score: %.2f%n", res[0]);
        System.out.format("FFT (%s): %.2f%n", FFT_size, res[1]);
        System.out.format("SOR (%s x %s): %.2f%n", SOR_size, SOR_size, res[2]);
        System.out.format("Monte Carlo: %.2f%n", res[3]);
        System.out.format("Sparse matmult (N=%s, nz=%s): %.2f%n", Sparse_size_M, Sparse_size_nz, res[4]);
        System.out.format("LU (%s x %s ): %.2f%n", LU_size, LU_size, res[5]);

        // print out System info
        System.out.println();
        for(var property: DUMP_PROPERTIES){
            System.out.println(property + ": " + System.getProperty(property));
        }
    }
}
