using Microsoft.AspNetCore.Mvc;
using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Scripting;
using Basic.Reference.Assemblies;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Scripting;
using ReflectYourself.Views.Main;

namespace ReflectYourself;

[Route("/")]
[Controller]
public class MainController : Controller
{
    [HttpGet]
    public IActionResult Index()
    {
        return View(new IndexModel());
    }

    [HttpPost]
    public async Task<IActionResult> IndexAsync(IndexModel model)
    {
        try
        {
            var tree = CSharpSyntaxTree.ParseText(model.Code);
            var root = tree.GetCompilationUnitRoot();
            var children = root.ChildNodes().ToList();
            if (children.Count > 1)
            {
                model.Error = "You didn't provide a statement";
                return PartialView(model);
            }

            var child = children[0];
            if (!child.IsKind(SyntaxKind.GlobalStatement))
            {
                model.Error = "You didn't provide a statement";
                return PartialView(model);
            }

            if (ContainsBlock(child))
            {
                model.Error = "Statement contains block. Why would I make it easy for you?";
                return PartialView(model);
            }

            var compilation = CSharpCompilation.Create("Script")
                .AddReferences(Net100.References.All)
                .AddSyntaxTrees(tree);
            var semanticModel = compilation.GetSemanticModel(tree);

            var invocations = root.DescendantNodes().OfType<InvocationExpressionSyntax>();
            foreach (var invocation in invocations)
            {
                if (invocation is not { Expression: MemberAccessExpressionSyntax member })
                {
                    continue;
                }

                var parent = semanticModel.GetTypeInfo(member.Expression);
                var isProcess = parent.Type?.Equals(
                    compilation.GetTypeByMetadataName("System.Diagnostics.Process"),
                    SymbolEqualityComparer.Default
                ) ?? false;
                if (isProcess)
                {
                    model.Error = "No System.Diagnostics.Process access for you :)";
                    return PartialView(model);
                }
            }

            var result = await CSharpScript.EvaluateAsync(model.Code);
            model.Result = result?.ToString();
        }
        catch (CompilationErrorException e)
        {
            model.Error = string.Join(Environment.NewLine, e.Diagnostics);
        }
        catch (Exception e)
        {
            model.Error = e.Message;
        }

        return PartialView(model);
    }

    public bool ContainsBlock(SyntaxNode node)
    {
        foreach (var child in node.ChildNodes())
        {
            if (child.IsKind(SyntaxKind.Block))
            {
                return true;
            }

            if (ContainsBlock(child))
            {
                return true;
            }
        }

        return false;
    }
}
