import com.github.javaparser.StaticJavaParser;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.MethodDeclaration;
import com.github.javaparser.ast.stmt.BlockStmt;

import java.io.File;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Optional;

public class JavaCodeExtraction {

    public static String getMethodSourceCode(String filePath, String methodName) throws IOException {
        File file = new File(filePath);
        CompilationUnit cu = StaticJavaParser.parse(file);
        Optional<MethodDeclaration> methodOpt = cu.findFirst(
                MethodDeclaration.class,
                m -> m.getNameAsString().equals(methodName)
        );
        return methodOpt.map(MethodDeclaration::toString).orElse(null);
    }

    public static void replaceMethodBodyFromFile(String filePath, String methodName, String blockFilePath) throws IOException {
        File file = new File(filePath);
        CompilationUnit cu = StaticJavaParser.parse(file);
        Optional<MethodDeclaration> methodOpt = cu.findFirst(
                MethodDeclaration.class,
                m -> m.getNameAsString().equals(methodName)
        );

        String blockCode = Files.readString(Paths.get(blockFilePath), StandardCharsets.UTF_8);

        BlockStmt newBody;
        try {
            newBody = StaticJavaParser.parseBlock(blockCode);
        } catch (Exception e) {
            System.err.println("Failed to parse block from file: " + blockFilePath);
            throw e;
        }

        methodOpt.ifPresent(method -> {
            method.setBody(newBody);
            try {
                Files.write(file.toPath(), cu.toString().getBytes(StandardCharsets.UTF_8));
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 3) {
            System.err.println("Usage:\n" +
                "  java JavaCodeExtraction print   <filePath> <methodName>\n" +
                "  java JavaCodeExtraction replace <filePath> <methodName> (uses optimized_java.txt)");
            System.exit(1);
        }

        String operation = args[0];
        String filePath = args[1];
        String methodName = args[2];

        switch (operation.toLowerCase()) {
            case "print":
                String source = getMethodSourceCode(filePath, methodName);
                System.out.println(source == null ? "Method not found" : source);
                break;

            case "replace":
                String blockPath = "/home/hpeng/E2COOL/src/runtime_logs/optimized_java.txt";
                System.out.println("=== Original Method Source ===");
                System.out.println(getMethodSourceCode(filePath, methodName));

                replaceMethodBodyFromFile(filePath, methodName, blockPath);

                System.out.println("=== Replaced Method Source ===");
                System.out.println(getMethodSourceCode(filePath, methodName));
                break;

            default:
                System.err.println("Unknown operation: " + operation);
                System.exit(1);
        }
    }
}
