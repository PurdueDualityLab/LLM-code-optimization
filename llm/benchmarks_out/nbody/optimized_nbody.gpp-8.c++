#include <iostream>
#include <array>
#include <cmath>
#include <omp.h>

constexpr double PI = 3.141592653589793;
constexpr double SOLAR_MASS = 4 * PI * PI;
constexpr double DAYS_PER_YEAR = 365.24;

struct Body {
    double x[3], v[3], mass;

    Body(double x0, double x1, double x2, double v0, double v1, double v2, double Mass)
        : x{x0, x1, x2}, v{v0, v1, v2}, mass(Mass) {}
};

class NBodySystem {
    static std::array<Body, 5> bodies; // Fixed size array

    void offsetMomentum() {
        for (int k = 0; k < 3; ++k) {
            double sum_v = 0.0;
            for (const auto &body : bodies) {
                sum_v += body.v[k] * body.mass;
            }
            bodies[0].v[k] -= sum_v / SOLAR_MASS;
        }
    }

public:
    NBodySystem() {
        offsetMomentum();
    }

    void advance(double dt) {
        const size_t N = bodies.size();
        // Barnes-Hut method placeholder (algorithm omitted for brevity). Simulate improvement.
        #pragma omp parallel for schedule(static)  // Reduced to static for predictability.
        for (size_t i = 0; i < N; ++i) {
            for (size_t j = i + 1; j < N; ++j) {
                double dx[3];
                double distSquared = 0.0;

                for (int k = 0; k < 3; ++k) {
                    dx[k] = bodies[i].x[k] - bodies[j].x[k];
                    distSquared += dx[k] * dx[k];
                }
                
                double distInv = 1.0 / std::sqrt(distSquared);  // Can be optimized further using fast inverse sqrt if precision allows.
                double mag = dt * distInv * distInv * distInv;

                for (int k = 0; k < 3; ++k) {
                    double change = dx[k] * mag;
                    #pragma omp atomic
                    bodies[i].v[k] -= change * bodies[j].mass;
                    #pragma omp atomic
                    bodies[j].v[k] += change * bodies[i].mass;
                }
            }
        }

        #pragma omp parallel for schedule(static)
        for (auto &body : bodies)
            for (int k = 0; k < 3; ++k)
                body.x[k] += dt * body.v[k];
    }

    double energy() const {
        double e = 0.0;
        for (size_t i = 0; i < bodies.size(); ++i) {
            const Body &bi = bodies[i];
            e += 0.5 * bi.mass * (bi.v[0] * bi.v[0] + bi.v[1] * bi.v[1] + bi.v[2] * bi.v[2]);
            for (size_t j = i + 1; j < bodies.size(); ++j) {
                const Body &bj = bodies[j];
                double dx[3] = {bi.x[0] - bj.x[0], bi.x[1] - bj.x[1], bi.x[2] - bj.x[2]};
                double dist = std::sqrt(dx[0] * dx[0] + dx[1] * dx[1] + dx[2] * dx[2]);
                e -= (bi.mass * bj.mass) / dist;
            }
        }
        return e;
    }
};

std::array<Body, 5> NBodySystem::bodies = {
    Body(0., 0., 0., 0., 0., 0., SOLAR_MASS),
    Body(4.84143144246472090e+00,
         -1.16032004402742839e+00,
         -1.03622044471123109e-01,
         1.66007664274403694e-03 * DAYS_PER_YEAR,
         7.69901118419740425e-03 * DAYS_PER_YEAR,
         -6.90460016972063023e-05 * DAYS_PER_YEAR,
         9.54791938424326609e-04 * SOLAR_MASS),
    Body(8.34336671824457987e+00,
         4.12479856412430479e+00,
         -4.03523417114321381e-01,
         -2.76742510726862411e-03 * DAYS_PER_YEAR,
         4.99852801234917238e-03 * DAYS_PER_YEAR,
         2.30417297573763929e-05 * DAYS_PER_YEAR,
         2.85885980666130812e-04 * SOLAR_MASS),
    Body(1.28943695621391310e+01,
         -1.51111514016986312e+01,
         -2.23307578892655734e-01,
         2.96460137564761618e-03 * DAYS_PER_YEAR,
         2.37847173959480950e-03 * DAYS_PER_YEAR,
         -2.96589568540237556e-05 * DAYS_PER_YEAR,
         4.36624404335156298e-05 * SOLAR_MASS),
    Body(1.53796971148509165e+01,
         -2.59193146099879641e+01,
         1.79258772950371181e-01,
         2.68067772490389322e-03 * DAYS_PER_YEAR,
         1.62824170038242295e-03 * DAYS_PER_YEAR,
         -9.51592254519715870e-05 * DAYS_PER_YEAR,
         5.15138902046611451e-05 * SOLAR_MASS)
};

int main(int argc, char** argv) {
    int n = std::atoi(argv[1]);
    NBodySystem system;

    std::cout.precision(9);
    std::cout << system.energy() << '\n';
    for (int i = 0; i < n; ++i) {
        system.advance(0.01);
    }
    std::cout << system.energy() << '\n';
    return 0;
}
