

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.net.URI;
import java.nio.file.FileSystem;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.nio.file.WatchEvent.Kind;
import java.nio.file.WatchEvent.Modifier;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import com.github.javaparser.TokenRange;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.expr.VariableDeclarationExpr;
import org.json.*;

import com.github.javadocparser.ParseException;
import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.*;
import com.github.javaparser.ast.comments.Comment;
import com.github.javaparser.ast.comments.JavadocComment;
import com.github.javaparser.ast.stmt.BlockStmt;
import com.github.javaparser.ast.stmt.Statement;
import com.github.javaparser.ast.type.Type;
import com.github.javaparser.utils.ParserCollectionStrategy;
import com.github.javaparser.utils.ProjectRoot;
import com.github.javaparser.utils.SourceRoot;

import static com.github.javaparser.StaticJavaParser.parseBodyDeclaration;


public class JavaParserTest {

    public static void main(String[] args) throws IOException {
    	parseProject(Paths.get("/Users/facade/Documents/GitHub/nextcloud/android/src"));
//      parseProject(Paths.get("C:\\Users\\PranayDev\\Documents\\UMN\\ASE\\project\\test_apps\\focus-android-master\\app\\src"));
//      parseProject(Paths.get("C:\\Users\\PranayDev\\Documents\\UMN\\ASE\\project\\test_apps\\k-9-master\\app\\k9mail\\src"));

        System.out.println("Parsed Successfully");
    }

    private static void parseProject(Path root) throws IOException {
        final ProjectRoot projectRoot =
                new ParserCollectionStrategy()
                        .collect(root);

        JSONObject results = new JSONObject();
        List<SourceRoot> roots = projectRoot.getSourceRoots();
        for(SourceRoot sourceRoot : roots) {
            String rootPath = sourceRoot.getRoot().toString();
            List<ParseResult<CompilationUnit>> parseResults = sourceRoot.tryToParse();
            JSONObject analyzedClasses= new JSONObject();
            for(ParseResult<CompilationUnit> result : parseResults) {
                analyzeMethods(result, analyzedClasses);
            }

            results.put(rootPath, analyzedClasses);
        }

        writeResult(results);

    }

    private static JSONObject analyzeMethods(ParseResult<CompilationUnit> result, JSONObject analyzedClasses) {
        if(!result.isSuccessful()) {
            return new JSONObject();
        }

        CompilationUnit cu = result.getResult().get();
        String packageName = "";
        if(cu.getPackageDeclaration().isPresent()) {
            packageName = cu.getPackageDeclaration().get().getNameAsString();
        }

        List<TypeDeclaration<?>> types = cu.getTypes();
        for (TypeDeclaration type : types) {
            String classOrInterfaceName = type.getNameAsString();
            List<BodyDeclaration> members = type.getMembers();
//            System.out.println("###############################");
//            System.out.println(packageName+"."+classOrInterfaceName);
            JSONObject analyzedMethods = new JSONObject();
            for (BodyDeclaration member : members) {
                if (member instanceof MethodDeclaration) {
                    MethodDeclaration method = (MethodDeclaration) member;
                    analyzeMethod(method, analyzedMethods);
                }
            }

            String classKey = packageName != null ? packageName+"."+classOrInterfaceName : classOrInterfaceName;
            analyzedClasses.put(classKey, analyzedMethods);
        }

        return analyzedClasses;
    }

    private static void analyzeMethod(MethodDeclaration method, JSONObject analyzedMethods) {
        List<String> allComments = new ArrayList<>();
        List<String> arguments = new ArrayList<>();
        List<String> localVariables = new ArrayList<>();

        BodyDeclaration methodBody = parseBodyDeclaration(method.toString());
        methodBody.walk(VariableDeclarationExpr.class, e -> {
            for(VariableDeclarator v : e.getVariables()) {
                localVariables.add(v.getName().asString());
            }
        });

        for (Parameter p : method.getParameters()) {
            arguments.add(p.getName().asString());
        }

        for (Comment cmnt : method.getAllContainedComments()) {
            allComments.add(cmnt.toString());
        }

        // Building JSON object
        analyzedMethods.put(method.getNameAsString(),
                            new JSONObject().put("attributes", arguments)
                            .put("comments", allComments)
                            .put("variables", localVariables)
                            .put("methodName", method.getNameAsString()));
    }

    private static void writeResult(JSONObject results) {
        FileWriter file = null;

        try {
            // Constructs a FileWriter given a file name, using the platform's default charset
            file = new FileWriter("result.json");
            file.write(results.toString());

        } catch (IOException e) {
            e.printStackTrace();

        } finally {

            try {
                file.flush();
                file.close();
            } catch (IOException e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
        }
    }
}
