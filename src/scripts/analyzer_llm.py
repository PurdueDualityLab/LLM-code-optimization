from dotenv import load_dotenv  
from pydantic import BaseModel  
import sys  
import os  
import json  
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import LLMAgent

# Setup environment  
load_dotenv()  
USER_PREFIX = os.getenv('USER_PREFIX')  
openai_key = os.getenv('API_KEY')
genai_api_key = os.getenv('GenAI_API_KEY')

class AnalysisResult(BaseModel):  
    description: str
    comparison: str
    optimization_pattern: str
  
def analyze_optimization(original_code, optimized_code, llm_assistant):  
    
    print("Analyzing code optimization...")

    prompt = f"""  
I have two versions of a program: an original implementation and a final optimized version. Please analyze the differences between them with the following goals:

1. **Code Function Explanation**: Briefly explain what the code is doing—what problem it solves and how it works.

2. **Optimization Comparison**: Compare the original and optimized versions to identify:
   - **Algorithmic changes**: Any differences in logic, algorithm design, or problem-solving approach.
   - **Performance improvements**: Enhancements related to time complexity, space efficiency, or runtime behavior.
   - **Redundant code removal**: Elimination of unnecessary logic, method calls, or control structures.
   - **Other noteworthy changes**: Any structural or stylistic differences that could impact performance or readability.
   
3. **Optimization Pattern Classification**:
   Based on the overall nature of the optimized code, assign the following. Return No Meaningful Change if no meaningful change is made.
   - **Exactly one high-level optimization pattern** from the list below  
   - **One most representative sub-pattern** within that high-level category
   
   ### High-Level Optimization Patterns Taxonomy:
   - **Algorithm-Level Optimizations**
        - Select Computationally Efficient Algorithms
        - Select Algorithm Based on Instruction Speed
        - Structure Algorithm to Support ILP
        - Select Space Efficient Algorithm
        - Inheritance over Delegation for Energy Efficiency
   - **Control-Flow and Branching Optimizations**
        - Make Conditional Branches More Predictable
        - Remove Branches with min/max Instructions
        - Remove Branches by Doing Extra Work
        - Remove Branching with Masking
        - Rearranging Branches
        - Combining Branches
   - **Memory and Data Locality Optimizations**
        - Access Data with Appropriate Type
        - Increase Cache Efficiency via Locality
        - Arrange Data for Optimal Prefetching
        - Avoid Cache Capacity Issues
        - Increase Workload to Hide Latency
        - Use Smaller Data Types
        - Caching, Buffering
        - Improve Data Structure Locality
        - Optimize Object Use
        - Reduce RTSJ Immortal Memory Bloat
   - **Loop Transformations**
        - Remove Conditional by Loop Unrolling
        - Loop Distribution (Fission)
        - Loop Fusion, Peeling, Interchanging
        - Loop Invariant Branches
        - Loop Strip-mining
   - **I/O and Synchronization**
        - Selection of I/O Size
        - Polling
        - Non-Blocking I/O
   - **Data Structure Selection and Adaptation**
        - Choose Structure for Energy Efficiency
        - Darwinian Selection
        - Select via Method Calls
        - Cross-Library Comparison
   - **Code Smells and Structural Simplification**
        - Remove Optional Features
        - Remove Redundant Method Calls
        - Extract Long Methods
        - Remove Duplicates
        - Move Methods to Reduce Feature Envy
        - Minimize God Classes
        - Type Checking
         
Here are the two versions of the code:  
            
Original Code:  
{original_code}  

Final Optimized Code:  
{optimized_code}  

Output Structure:  
First provide a brief description of what the code is doing.  
Then provide a detailed comparison and highlight the specific optimizations or decisions made in the optimized version.  
Assign the **single most representative high-level optimization pattern** from the list above to the changes made in the optimized version. Or return "No Meaningful Change" if no meaningful change is made.
"""  
  
    # Send to LLM for analysis  
    llm_assistant.add_to_memory("user", prompt)  
    llm_assistant.generate_response(response_format=AnalysisResult)  
    response = llm_assistant.get_last_msg()  
      
    try:  
        content_dict = json.loads(response["content"])  
        return content_dict  
    except json.JSONDecodeError as e:  
        print(f"Failed to decode JSON: {e}")  
        return "Error: Failed to analyze code optimization."  

if __name__ == "__main__":
    original_code =   "package jnt.scimark2;\n\nimport java.util.Random;\n\npublic class SparseCompRowOptimized {\n    // Sparse matrix-vector multiply using compressed row storage.\n    public static void matmult(double[] y, double[] val, int[] row,\n                               int[] col, double[] x, long NUM_ITERATIONS) {\n        int M = row.length - 1;\n        for (long reps = 0; reps < NUM_ITERATIONS; reps++) {\n            for (int r = 0; r < M; r++) {\n                double sum = 0.0;\n                int rowStart = row[r];\n                int rowEnd = row[r + 1];\n                for (int i = rowStart; i < rowEnd; i++) {\n                    sum += x[col[i]] * val[i];\n                }\n                y[r] = sum;\n            }\n        }\n    }\n\n    // Helper method to generate a random vector.\n    private static double[] randomVector(int N, Random R) {\n        double[] A = new double[N];\n        for (int i = 0; i < N; i++) {\n            A[i] = R.nextDouble();\n        }\n        return A;\n    }\n\n    // Computes the sum of absolute differences between two vectors.\n    private static double normabs(double[] a, double[] b) {\n        double sum = 0.0;\n        for (int i = 0; i < a.length; i++) {\n            sum += Math.abs(a[i] - b[i]);\n        }\n        return sum;\n    }\n\n    public static void main(String[] args) {\n        // Parameters for the test.\n        int N = 1000;              // Size of the vector / number of rows.\n        int nz = 10000;            // Total number of nonzeros in the matrix.\n        long cycles = 524288;      // Fixed cycles\n        double regressionThreshold = 1.0e-10;\n        long seed = 101010;        \n\n        // Create random number generators.\n        Random rand1 = new Random(seed);\n        Random rand2 = new Random(seed + 1);\n\n        // Generate vector x.\n        double[] x = randomVector(N, rand1);\n\n        // Build the sparse matrix in compressed row format.\n        int nr = nz / N;       // Average nonzeros per row.\n        int anz = nr * N;      // Actual number of nonzeros.\n        double[] val = randomVector(anz, rand2);\n        int[] col = new int[anz];\n        int[] row = new int[N + 1];\n        row[0] = 0;\n        for (int r = 0; r < N; r++) {\n            int rowr = row[r];\n            row[r + 1] = rowr + nr;\n            int step = r / nr;\n            if (step < 1) step = 1;\n            for (int i = 0; i < nr; i++) {\n                col[rowr + i] = i * step;\n            }\n        }\n\n        // Prepare output arrays.\n        double[] yTest = new double[N];\n        double[] yRef = new double[N];\n\n        // Run the multiplication with a fixed number of cycles (simulate optimized run).\n        matmult(yTest, val, row, col, x, cycles);\n\n        // Run the multiplication with 1 iteration (reference run).\n        matmult(yRef, val, row, col, x, 1);\n\n        // Compare the two results.\n        double difference = normabs(yTest, yRef);\n\n        System.out.println(difference);\n    }\n}\n"
    optimized_code =  "package jnt.scimark2;\n\nimport java.util.Random;\nimport java.util.concurrent.ForkJoinPool;\nimport java.util.stream.IntStream;\n\npublic class SparseCompRowOptimized {\n    \n    public static void parallelMatmult(double[] y, double[] val, int[] row,\n                                       int[] col, double[] x, long NUM_ITERATIONS) {\n        int M = row.length - 1;\n        ForkJoinPool pool = new ForkJoinPool();\n        pool.submit(() -> IntStream.range(0, M).parallel().forEach(r -> {\n            double[] localY = new double[y.length]; \n            for (long reps = 0; reps < NUM_ITERATIONS; reps++) {\n                double sum1 = 0.0, sum2 = 0.0, sum3 = 0.0, sum4 = 0.0;\n                int rowStart = row[r];\n                int rowEnd = row[r + 1];\n                int i;\n                for (i = rowStart; i <= rowEnd - 4; i += 4) {\n                    sum1 += x[col[i]] * val[i];\n                    sum2 += x[col[i+1]] * val[i+1];\n                    sum3 += x[col[i+2]] * val[i+2];\n                    sum4 += x[col[i+3]] * val[i+3];\n                }\n                for (; i < rowEnd; i++) {\n                    sum1 += x[col[i]] * val[i];\n                }\n                localY[r] = sum1 + sum2 + sum3 + sum4;\n            }\n            y[r] = localY[r];\n        })).join();\n    }\n\n    private static double[] randomVector(int N, Random R) {\n        double[] A = new double[N];\n        for (int i = 0; i < N; i++) {\n            A[i] = R.nextDouble();\n        }\n        return A;\n    }\n\n    private static double normabs(double[] a, double[] b) {\n        double sum = 0.0;\n        for (int i = 0; i < a.length; i++) {\n            sum += Math.abs(a[i] - b[i]);\n        }\n        return sum;\n    }\n\n    public static void main(String[] args) {\n        int N = 1000;\n        int nz = 10000;\n        long cycles = 524288;\n        double regressionThreshold = 1.0e-10;\n        long seed = 101010;\n\n        Random rand1 = new Random(seed);\n        Random rand2 = new Random(seed + 1);\n\n        double[] x = randomVector(N, rand1);\n\n        int nr = nz / N;\n        int anz = nr * N;\n        double[] val = randomVector(anz, rand2);\n        int[] col = new int[anz];\n        int[] row = new int[N + 1];\n        row[0] = 0;\n        for (int r = 0; r < N; r++) {\n            int rowr = row[r];\n            row[r + 1] = rowr + nr;\n            int step = r / nr;\n            if (step < 1) step = 1;\n            for (int i = 0; i < nr; i++) {\n                col[rowr + i] = (i * step) % N;\n            }\n        }\n\n        double[] yTest = new double[N];\n        double[] yRef = new double[N];\n\n        parallelMatmult(yTest, val, row, col, x, cycles);\n        matmult(yRef, val, row, col, x, 1);\n\n        double difference = normabs(yTest, yRef);\n\n        System.out.println(difference);\n    }\n\n    \n    public static void matmult(double[] y, double[] val, int[] row,\n                               int[] col, double[] x, long NUM_ITERATIONS) {\n        int M = row.length - 1;\n        for (long reps = 0; reps < NUM_ITERATIONS; reps++) {\n            for (int r = 0; r < M; r++) {\n                double sum1 = 0.0, sum2 = 0.0, sum3 = 0.0, sum4 = 0.0;\n                int rowStart = row[r];\n                int rowEnd = row[r + 1];\n                int i;\n                for (i = rowStart; i <= rowEnd - 4; i += 4) {\n                    sum1 += x[col[i]] * val[i];\n                    sum2 += x[col[i+1]] * val[i+1];\n                    sum3 += x[col[i+2]] * val[i+2];\n                    sum4 += x[col[i+3]] * val[i+3];\n                }\n                for (; i < rowEnd; i++) {\n                    sum1 += x[col[i]] * val[i];\n                }\n                y[r] = sum1 + sum2 + sum3 + sum4;\n            }\n        }\n    }\n}"
    
    # Initialize LLM agent  
    analyzer_llm = LLMAgent(openai_api_key=openai_key, genai_api_key=genai_api_key,   
        model="gpt-4o-mini", use_genai_studio=False,   
        system_message="You are a code expert. Analyze code optimizations thoroughly.")  
    
    # Analyze code optimization  
    content_dict = analyze_optimization(original_code, optimized_code, analyzer_llm)
    content_dict["program_name"] = "SparseCompRowOptimized"  
    print("Analysis Result:")
    print(content_dict)

    with open("analysis_result.txt", "a") as f:  
        f.write(json.dumps(content_dict, indent=2))
    print("Analysis result saved to analysis_result.txt")