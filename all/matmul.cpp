#include <cassert>
#include <iostream>
#include <random>
#include <vector>
#include <string>
#include <unordered_set>

using namespace std;
using vector_type = std::vector<double>;
using matrix_type = std::vector<std::vector<double>>;

vector_type fast_mul(const matrix_type &A, const vector_type &b) {
    auto rows = A.size();
    auto cols = A[0].size();
    assert(cols == b.size());
    vector_type c(rows);
    for (decltype(rows) i = 0; i != rows; ++i) {
        for (decltype(cols) j = 0; j != cols; ++j) {
            c[i] += A[i][j] * b[j];
        }
    }
    return c;
}

vector_type slow_mul(const matrix_type &A, const vector_type &b) {
    auto rows = A.size();
    auto cols = A[0].size();
    assert(cols == b.size());
    vector_type c(rows);
    for (decltype(cols) j = 0; j != cols; ++j) {
        for (decltype(rows) i = 0; i != rows; ++i) {
            c[i] += A[i][j] * b[j];
        }
    }
    return c;
}

int main(int argc, char **argv) {
    unordered_set<string> options{"--fast", "--slow"};
    if (argc < 3 || options.find(argv[2]) == options.cend()) {
        cout << "Usage: size [--fast] [--slow]" << endl;
        return EXIT_FAILURE;
    }

    size_t sz = strtoull(argv[1], nullptr, 10);
    matrix_type A(sz, vector_type(sz));
    vector_type b(sz);
    if (string(argv[2]) == "--fast") {
        fast_mul(A, b);
    } else if (string(argv[2]) == "--slow") {
        slow_mul(A, b);
    } else {
        assert(false);
    }

    return EXIT_SUCCESS;
}