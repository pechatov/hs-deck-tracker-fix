using Mono.Cecil;
using Mono.Cecil.Cil;
using System.Text.Json;

static class Program
{
    public static IEnumerable<TypeDefinition> Types(TypeDefinition t) => new[] {t}.Concat(t.NestedTypes.SelectMany(Types));
    public static string Body(MethodDefinition m)
    {
        if (!m.HasBody) return "NO BODY";
        var list=m.Body.Instructions;
        string Operand(object? o) => o switch {
            null => "", Instruction i => "#"+list.IndexOf(i), Instruction[] a => string.Join(",",a.Select(i=>"#"+list.IndexOf(i))),
            ParameterDefinition p => "arg:"+p.Index, VariableDefinition v => "local:"+v.Index+":"+v.VariableType.FullName,
            MemberReference r => r.FullName, string s => JsonSerializer.Serialize(s), _ => o.ToString()??""};
        return string.Join("\n",m.Body.Variables.Select(v=>"local:"+v.VariableType.FullName)) + "\n" +
            string.Join("\n",list.Select(i=>i.OpCode.Name+" "+Operand(i.Operand))) + "\n" +
            string.Join("\n",m.Body.ExceptionHandlers.Select(e=>$"EH {e.HandlerType} {e.CatchType?.FullName} {list.IndexOf(e.TryStart)} {list.IndexOf(e.TryEnd)} {list.IndexOf(e.HandlerStart)} {list.IndexOf(e.HandlerEnd)} {list.IndexOf(e.FilterStart)}"));
    }
    static AssemblyDefinition Read(string path) {
        var resolver=new DefaultAssemblyResolver();
        resolver.AddSearchDirectory(Path.GetDirectoryName(path)!);
        foreach(var dir in (Environment.GetEnvironmentVariable("HDT_CECIL_REFERENCE_DIRS")??"").Split(Path.PathSeparator,StringSplitOptions.RemoveEmptyEntries))resolver.AddSearchDirectory(dir);
        return AssemblyDefinition.ReadAssembly(path,new ReaderParameters{AssemblyResolver=resolver});
    }
    static void Main(string[] args)
    {
        if(args[0]=="weave") {
            var official=Read(args[1]);
            var donor=Read(args[2]);
            var baseline=Read(args[3]);
            new Weave(official.MainModule,donor.MainModule).Run(baseline.MainModule,args[4]);
            return;
        }
        if(args[0]=="resources") {
            var assembly=Read(args[1]);
            var res=(EmbeddedResource)assembly.MainModule.Resources.Single(r=>r.Name=="HearthstoneDeckTracker.g.resources");
            File.WriteAllBytes(args[2],res.GetResourceData());
            return;
        }
        if(args[0]=="attach") {
            var assembly=Read(args[1]);
            var r=assembly.MainModule.Resources.Single(r=>r.Name=="HearthstoneDeckTracker.g.resources");
            int i=assembly.MainModule.Resources.IndexOf(r);
            assembly.MainModule.Resources[i]=new EmbeddedResource(r.Name,r.Attributes,File.ReadAllBytes(args[2]));
            assembly.Write(args[3]);
            return;
        }
        var a=Read(args[0]);
        var methods=a.MainModule.Types.SelectMany(Types).SelectMany(t=>t.Methods).ToDictionary(m=>m.FullName,Body);
        File.WriteAllText(args[1],JsonSerializer.Serialize(methods,new JsonSerializerOptions{WriteIndented=true}));
        Console.WriteLine($"{methods.Count} method bodies exported.");
    }
}
