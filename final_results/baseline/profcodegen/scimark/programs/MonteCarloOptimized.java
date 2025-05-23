package jnt.scimark2;

import java.util.concurrent.ThreadLocalRandom;

public class MonteCarloOptimized {
    final static int SEED = 113;

    public static void main(String[] args) {
        int cycles = 1073741824;
        double result = integrate(cycles);
        System.out.println(result);
    }

    public static double integrate(long Num_samples) {

        
        long under_curve = 0;
        for (long count = 0; count < Num_samples; count++) {
            double x = ThreadLocalRandom.current().nextDouble();
            double y = ThreadLocalRandom.current().nextDouble();

            if (x * x + y * y <= 1.0)
                under_curve++;
        }

        return ((double) under_curve / Num_samples) * 4.0;
    }
}
