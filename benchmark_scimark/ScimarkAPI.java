package jnt.scimark2;

public class ScimarkAPI {

    public static BenchmarkResult runBenchmark(){
        return runBenchmark(false);
    }

    public static BenchmarkResult runBenchmark(int seed){
        return runBenchmark(seed, false);
    }

    public static BenchmarkResult runBenchmark(boolean bigDataset){
        return runBenchmark(Constants.RANDOM_SEED, bigDataset);
    }

    public static BenchmarkResult runBenchmark(int seed, boolean bigDataset){
        int FFT_size, SOR_size, Sparse_size_M, Sparse_size_nz, LU_size;
        double resolutionDefault = Constants.RESOLUTION_DEFAULT;

        if(bigDataset){
            FFT_size = Constants.LG_FFT_SIZE;
            SOR_size = Constants.LG_SOR_SIZE;
            Sparse_size_M = Constants.LG_SPARSE_SIZE_M;
            Sparse_size_nz = Constants.LG_SPARSE_SIZE_nz;
            LU_size = Constants.LG_LU_SIZE;
        } else {
            FFT_size = Constants.FFT_SIZE;
            SOR_size = Constants.SOR_SIZE;
            Sparse_size_M = Constants.SPARSE_SIZE_M;
            Sparse_size_nz = Constants.SPARSE_SIZE_nz;
            LU_size = Constants.LU_SIZE;
        }
        return runBenchmark(seed, resolutionDefault, FFT_size, SOR_size, Sparse_size_M, Sparse_size_nz, LU_size);
    }

    public static BenchmarkResult runBenchmark(int seed, double min_time, int FFT_size, int SOR_size, int Sparse_size_M, int Sparse_size_nz, int LU_size){
        Random R = new Random(seed);
        String javaVendor = System.getProperty("java.vendor");
        String javaVersion = System.getProperty("java.version");
        String osArch = System.getProperty("os.arch");
        String osName = System.getProperty("os.name");
        String osVersion = System.getProperty("os.version");
        var result =  new BenchmarkResult(
                seed,
                FFT_size,
                SOR_size,
                Sparse_size_M,
                Sparse_size_nz,
                LU_size,
                min_time,
                Kernel.measureFFT(FFT_size, min_time, R),
                Kernel.measureSOR(SOR_size, min_time, R),
                Kernel.measureMonteCarlo(min_time, R),
                Kernel.measureSparseMatmult(Sparse_size_M, Sparse_size_nz, min_time, R),
                Kernel.measureLU(LU_size, min_time, R),
                javaVendor, javaVersion, osArch, osName, osVersion);
        result.validate();
        return result;
    }

    public static class BenchmarkResult {
        private final int randomSeed, fft_size, sor_size, sparse_size_m, sparse_size_n, lu_size;
        private final double min_time, FFTScore, SORScore, MonteCarloScore, SparseMatmultScore, LUScore;
        private final String javaVendor, javaVersion, osArch, osName, osVersion;

        public BenchmarkResult(int randomSeed, int fft_size, int sor_size, int sparse_size_m, int sparse_size_n, int lu_size, double min_time, double fftScore, double sorScore, double monteCarloScore, double sparseMatmultScore, double luScore, String javaVendor, String javaVersion, String osArch, String osName, String osVersion) {
            this.randomSeed = randomSeed;
            this.fft_size = fft_size;
            this.sor_size = sor_size;
            this.sparse_size_m = sparse_size_m;
            this.sparse_size_n = sparse_size_n;
            this.lu_size = lu_size;
            this.min_time = min_time;
            FFTScore = fftScore;
            SORScore = sorScore;
            MonteCarloScore = monteCarloScore;
            SparseMatmultScore = sparseMatmultScore;
            LUScore = luScore;
            this.javaVendor = javaVendor;
            this.javaVersion = javaVersion;
            this.osArch = osArch;
            this.osName = osName;
            this.osVersion = osVersion;
        }

        public double getFFTScore() {
            return FFTScore;
        }

        public double getSORScore() {
            return SORScore;
        }

        public double getMonteCarloScore() {
            return MonteCarloScore;
        }

        public double getSparseMatmultScore() {
            return SparseMatmultScore;
        }

        public double getLUScore() {
            return LUScore;
        }

        public double getScore(){
            return (FFTScore + SORScore + MonteCarloScore + SparseMatmultScore + LUScore) / 5;
        }

        public int getRandomSeed() {
            return randomSeed;
        }

        public int getFft_size() {
            return fft_size;
        }

        public int getSor_size() {
            return sor_size;
        }

        public int getSparse_size_m() {
            return sparse_size_m;
        }

        public int getSparse_size_n() {
            return sparse_size_n;
        }

        public int getLu_size() {
            return lu_size;
        }

        public double getMin_time() {
            return min_time;
        }

        public String getJavaVendor() {
            return javaVendor;
        }

        public String getJavaVersion() {
            return javaVersion;
        }

        public String getOsArch() {
            return osArch;
        }

        public String getOsName() {
            return osName;
        }

        public String getOsVersion() {
            return osVersion;
        }

        public void validate(){
            // Same validations as existing CommandLine
            if(FFTScore == 0){
                throw new BenchmarkException("Invalid FFT Score");
            }
            if(LUScore == 0){
                throw new BenchmarkException("Invalid LU Score");
            }
        }
    }

    public static class BenchmarkException extends RuntimeException{
        public BenchmarkException(String reason){
            super(reason);
        }
    }
}
