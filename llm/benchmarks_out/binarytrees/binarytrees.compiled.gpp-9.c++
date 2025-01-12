#include <iostream>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <omp.h>
#include <apr_pools.h> // Assume APR environment is correctly setup

const size_t LINE_SIZE = 64;

class Apr {
public:
    Apr() { apr_initialize(); }
    ~Apr() { apr_terminate(); }
};

struct Node {
    Node *l, *r;
    int check() const { return l ? l->check() + 1 + r->check() : 1; }
};

class NodePool {
public:
    NodePool() { apr_pool_create_unmanaged(&pool); }
    ~NodePool() { apr_pool_destroy(pool); }

    Node* alloc() { return (Node *)apr_palloc(pool, sizeof(Node)); }
    void clear() { apr_pool_clear(pool); }

private:
    apr_pool_t* pool;
};

Node* make(int depth, NodePool &store, std::unordered_map<int, Node*>& memo) {
    if (auto it = memo.find(depth); it != memo.end()) {
        return it->second;
    }

    Node* node = store.alloc();
    if (depth > 0) {
        node->l = make(depth - 1, store, memo);
        node->r = make(depth - 1, store, memo);
    } else {
        node->l = node->r = nullptr;
    }

    memo[depth] = node;
    return node;
}

void runTreeOperations(int min_depth, int max_depth) {
    NodePool long_lived_store;
    std::unordered_map<int, Node*> memo;

    Node *long_lived_tree = make(max_depth, long_lived_store, memo);

    std::vector<std::string> results((max_depth/2) + 1);
    std::stringstream resultStream;

    #pragma omp parallel for schedule(dynamic)
    for (int d = min_depth; d <= max_depth; d += 2) {
        int checksum = 0;
        NodePool thread_store;  

        #pragma omp parallel
        {
            std::unordered_map<int, Node*> thread_memo;
            int iterations = 1 << (max_depth - d + min_depth);
            
            #pragma omp for reduction(+:checksum)
            for (int i = 0; i < iterations; ++i) {
                Node* tree = make(d, thread_store, thread_memo);
                checksum += tree->check();
                thread_store.clear();
            }
        }

        std::ostringstream oss;
        oss << (1 << (max_depth - d + min_depth)) << "\t trees of depth " << d << "\t check: " << checksum << "\n";
        #pragma omp critical
        results[d/2] = oss.str();
    }

    Node *stretch_tree = make(max_depth + 1, long_lived_store, memo);
    std::cout << "stretch tree of depth " << max_depth + 1 << "\t check: " << stretch_tree->check() << std::endl;

    for (const auto &result : results) {
        std::cout << result;
    }

    std::cout << "long lived tree of depth " << max_depth << "\t check: " << (long_lived_tree->check()) << "\n";
}

int main(int argc, char *argv[]) {
    Apr apr;
    int min_depth = 4;
    int max_depth = std::max(min_depth + 2, (argc == 2 ? atoi(argv[1]) : 10));

    runTreeOperations(min_depth, max_depth);

    return 0;
}
