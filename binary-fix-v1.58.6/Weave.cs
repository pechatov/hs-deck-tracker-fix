using Mono.Cecil;
using Mono.Cecil.Cil;
using System.Text.Json;
using System.Text.RegularExpressions;

sealed class Weave
{
    readonly ModuleDefinition target, donor;
    readonly Dictionary<string, TypeDefinition> originalTypes;
    readonly Dictionary<TypeDefinition, TypeDefinition> types = new();
    readonly Dictionary<MethodDefinition, MethodDefinition> methods = new();
    readonly Dictionary<FieldDefinition, FieldDefinition> fields = new();
    readonly Dictionary<GenericParameter, GenericParameter> parameters = new();
    readonly HashSet<TypeDefinition> pendingTypes = new();
    readonly HashSet<MethodDefinition> pendingMethods = new();
    readonly HashSet<FieldDefinition> newFields = new();
    readonly List<string> changed = new();
    const string Prefix = "Hearthstone_Deck_Tracker.";
    static readonly Dictionary<string,string[]> Plan = new() {
        ["Windows.OverlayWindow"] = new[]{"InitializeCollections","DetectMouseOver","SetTopmost","UpdatePosition","Window_Closing",".cctor"},
        ["Controls.AnimatedCard"] = new[]{".ctor","EnsureTile","get_CardTooltipPlacement","set_CardTooltipPlacement"},
        ["Controls.AnimatedCardList"] = new[]{".ctor","GetAnimatedCard","get_CardTooltipPlacement","set_CardTooltipPlacement"},
        ["Controls.Overlay.Battlegrounds.Session.BattlegroundsSession"] = new[]{"System.Windows.Markup.IComponentConnector.Connect"},
        ["Controls.Overlay.Battlegrounds.Session.BattlegroundsSessionViewModel"] = new[]{"UpdateLatestGames","DeleteOldGames","GetMostRecentGames","GetExpiredGames","UpdateDisplayedGames","ToggleRecentGames","get_ToggleRecentGamesCommand","get_ShowMoreGamesButtonText","get_ShowMoreGamesButtonVisibility","set_ShowMoreGamesButtonVisibility"},
        ["Controls.Overlay.Battlegrounds.Guides.BattlegroundsCompsGuidesViewModel"] = new[]{"GetCompGuides","GetPremiumCompGuides","OnMatchStart"},
        ["Utility.Overlay.OverlayOpacityMask"] = new[]{"CreateOpacityMask"}
    };
    public Weave(ModuleDefinition target, ModuleDefinition donor) {
        this.target=target; this.donor=donor;
        originalTypes=target.Types.SelectMany(Program.Types).ToDictionary(t=>t.FullName);
        foreach(var name in Plan.Keys) types[donor.GetType(Prefix+name)]=originalTypes[Prefix+name];
    }
    static string Canonical(string s) {
        s=Regex.Replace(s,@"(<[^<>]+>d__)\d+","$1N");
        return Regex.Replace(s,@"(__DisplayClass|b__|<>9__)\d+_","$1N_");
    }
    public static string SemanticBody(MethodDefinition m) {
        var s=Canonical(Program.Body(m));
        return Regex.Replace(s,@"ldstr ""[^\n]+Hearthstone Deck Tracker\\\\","ldstr \"ROOT\\\\");
    }
    TypeReference T(TypeReference t) {
        if(t is GenericParameter gp) {
            if(parameters.TryGetValue(gp,out var np))return np;
            if(gp.Owner is TypeReference owner) {
                var dest=T(owner).GetElementType();
                return dest.GenericParameters[gp.Position];
            }
            if(gp.Owner is MethodReference method) return M(method).GenericParameters[gp.Position];
            throw new Exception("Unmapped generic parameter "+gp.FullName);
        }
        if(t is GenericInstanceType gi) {
            var n=new GenericInstanceType(T(gi.ElementType));
            foreach(var a in gi.GenericArguments)n.GenericArguments.Add(T(a));
            return n;
        }
        if(t is ArrayType ar) {var n=new ArrayType(T(ar.ElementType),ar.Rank);for(int i=0;i<ar.Dimensions.Count;i++)n.Dimensions[i]=ar.Dimensions[i];return n;}
        if(t is ByReferenceType br)return new ByReferenceType(T(br.ElementType));
        if(t is PointerType pt)return new PointerType(T(pt.ElementType));
        if(t is PinnedType pn)return new PinnedType(T(pn.ElementType));
        if(t is RequiredModifierType rm)return new RequiredModifierType(T(rm.ModifierType),T(rm.ElementType));
        if(t is OptionalModifierType om)return new OptionalModifierType(T(om.ModifierType),T(om.ElementType));
        if(t.Scope==donor || t is TypeDefinition td0 && td0.Module==donor) {
            var td=t as TypeDefinition ?? donor.GetType(t.FullName);
            if(td==null)throw new Exception("Missing donor type "+t.FullName);
            if(types.TryGetValue(td,out var n))return n;
            if(td.IsNested && td.Name.StartsWith("<") && Plan.Keys.Any(k=>td.FullName.StartsWith(Prefix+k+"/")))return CloneType(td);
            if(originalTypes.TryGetValue(td.FullName,out n)){types[td]=n;return n;}
            throw new Exception("Unexpected new top-level donor type "+td.FullName);
        }
        return target.ImportReference(t);
    }
    TypeDefinition CloneType(TypeDefinition t) {
        if(types.TryGetValue(t,out var old))return old;
        var n=new TypeDefinition(t.Namespace,t.Name+"__HdtWine",t.Attributes);
        types[t]=n;
        ((TypeDefinition)T(t.DeclaringType)).NestedTypes.Add(n);
        foreach(var gp in t.GenericParameters){var g=new GenericParameter(gp.Name,n){Attributes=gp.Attributes};n.GenericParameters.Add(g);parameters[gp]=g;}
        n.BaseType=t.BaseType==null?null:T(t.BaseType);
        foreach(var gp in t.GenericParameters)foreach(var c in gp.Constraints)parameters[gp].Constraints.Add(new GenericParameterConstraint(T(c.ConstraintType)));
        foreach(var i in t.Interfaces)n.Interfaces.Add(new InterfaceImplementation(T(i.InterfaceType)));
        foreach(var f in t.Fields)F(f);
        foreach(var m in t.Methods)CreateMethod(m,n,m.Name);
        foreach(var p in t.Properties){var np=new PropertyDefinition(p.Name,p.Attributes,T(p.PropertyType));n.Properties.Add(np);if(p.GetMethod!=null)np.GetMethod=methods[p.GetMethod];if(p.SetMethod!=null)np.SetMethod=methods[p.SetMethod];}
        foreach(var ca in t.CustomAttributes)n.CustomAttributes.Add(Attribute(ca));
        pendingTypes.Add(t);
        return n;
    }
    FieldReference F(FieldReference f) {
        if(f.DeclaringType is GenericInstanceType)return new FieldReference(f.Name,T(f.FieldType),T(f.DeclaringType));
        if(f.DeclaringType.Scope==donor || f is FieldDefinition fd0 && fd0.Module==donor) {
            var td=donor.GetType(f.DeclaringType.FullName);
            var fd=f as FieldDefinition ?? td.Fields.Single(x=>x.Name==f.Name);
            if(fields.TryGetValue(fd,out var nf))return nf;
            var nt=(TypeDefinition)T(fd.DeclaringType);
            nf=nt.Fields.SingleOrDefault(x=>x.Name==fd.Name);
            if(nf==null){nf=new FieldDefinition(fd.Name,fd.Attributes,T(fd.FieldType));if(fd.HasConstant)nf.Constant=fd.Constant;nt.Fields.Add(nf);newFields.Add(nf);}
            fields[fd]=nf;return nf;
        }
        return target.ImportReference(f);
    }
    MethodDefinition CreateMethod(MethodDefinition m,TypeDefinition owner,string name) {
        if(methods.TryGetValue(m,out var exist))return exist;
        var n=new MethodDefinition(name,m.Attributes,target.TypeSystem.Void){ImplAttributes=m.ImplAttributes,CallingConvention=m.CallingConvention};
        owner.Methods.Add(n);methods[m]=n;
        foreach(var gp in m.GenericParameters){var g=new GenericParameter(gp.Name,n){Attributes=gp.Attributes};n.GenericParameters.Add(g);parameters[gp]=g;}
        n.ReturnType=T(m.ReturnType);
        foreach(var p in m.Parameters){var np=new ParameterDefinition(p.Name,p.Attributes,T(p.ParameterType));if(p.HasConstant)np.Constant=p.Constant;n.Parameters.Add(np);}
        foreach(var gp in m.GenericParameters)foreach(var c in gp.Constraints)parameters[gp].Constraints.Add(new GenericParameterConstraint(T(c.ConstraintType)));
        foreach(var ca in m.CustomAttributes)n.CustomAttributes.Add(Attribute(ca));
        foreach(var o in m.Overrides)n.Overrides.Add(M(o));
        pendingMethods.Add(m);return n;
    }
    MethodReference M(MethodReference m) {
        if(m is GenericInstanceMethod gi){var n=new GenericInstanceMethod(M(gi.ElementMethod));foreach(var a in gi.GenericArguments)n.GenericArguments.Add(T(a));return n;}
        if(m.DeclaringType is not GenericInstanceType && (m.DeclaringType.Scope==donor || m is MethodDefinition md0 && md0.Module==donor)) {
            var td=donor.GetType(m.DeclaringType.FullName);
            var md=m as MethodDefinition ?? td.Methods.Single(x=>x.FullName==m.FullName);
            if(methods.TryGetValue(md,out var n))return n;
            var nt=(TypeDefinition)T(md.DeclaringType);
            if(methods.TryGetValue(md,out n))return n;
            n=nt.Methods.SingleOrDefault(x=>x.FullName==md.FullName);
            if(n==null && md.Name.StartsWith("<"))n=nt.Methods.SingleOrDefault(x=>Canonical(x.FullName)==Canonical(md.FullName));
            if(n!=null){methods[md]=n;return n;}
            if(md.Name.StartsWith("<"))return CreateMethod(md,nt,md.Name+"__HdtWine");
            throw new Exception("Unplanned new donor method: "+md.FullName);
        }
        var mr=new MethodReference(m.Name,target.TypeSystem.Void,T(m.DeclaringType)){HasThis=m.HasThis,ExplicitThis=m.ExplicitThis,CallingConvention=m.CallingConvention};
        foreach(var gp in m.GenericParameters){var ng=new GenericParameter(gp.Name,mr){Attributes=gp.Attributes};mr.GenericParameters.Add(ng);parameters[gp]=ng;}
        mr.ReturnType=T(m.ReturnType);
        foreach(var p in m.Parameters)mr.Parameters.Add(new ParameterDefinition(T(p.ParameterType)));
        return target.ImportReference(mr);
    }
    CustomAttribute Attribute(CustomAttribute a) {
        var n=new CustomAttribute(M(a.Constructor));
        CustomAttributeArgument Arg(CustomAttributeArgument v) => new(T(v.Type),v.Value is TypeReference tr?T(tr):v.Value is CustomAttributeArgument[] ar?ar.Select(Arg).ToArray():v.Value);
        foreach(var x in a.ConstructorArguments)n.ConstructorArguments.Add(Arg(x));
        foreach(var x in a.Fields)n.Fields.Add(new CustomAttributeNamedArgument(x.Name,Arg(x.Argument)));
        foreach(var x in a.Properties)n.Properties.Add(new CustomAttributeNamedArgument(x.Name,Arg(x.Argument)));
        return n;
    }
    void CopyBody(MethodDefinition m,MethodDefinition n) {
        if(!m.HasBody)return;
        var body=new MethodBody(n){InitLocals=m.Body.InitLocals,MaxStackSize=m.Body.MaxStackSize};n.Body=body;
        foreach(var v in m.Body.Variables)body.Variables.Add(new VariableDefinition(T(v.VariableType)));
        var ins=m.Body.Instructions.ToDictionary(i=>i,i=>Instruction.Create(OpCodes.Nop));
        foreach(var i in m.Body.Instructions){var ni=ins[i];ni.OpCode=i.OpCode;body.Instructions.Add(ni);}
        object? Operand(object? o)=>o switch {
            Instruction i=>ins[i],Instruction[] a=>a.Select(i=>ins[i]).ToArray(),VariableDefinition v=>body.Variables[v.Index],ParameterDefinition p=>n.Parameters[p.Index],
            TypeReference t=>T(t),MethodReference mr=>M(mr),FieldReference fr=>F(fr),CallSite=>throw new Exception("Unsupported call site"),_=>o};
        foreach(var i in m.Body.Instructions)ins[i].Operand=Operand(i.Operand);
        Instruction? I(Instruction? x)=>x==null?null:ins[x];
        foreach(var e in m.Body.ExceptionHandlers)body.ExceptionHandlers.Add(new ExceptionHandler(e.HandlerType){CatchType=e.CatchType==null?null:T(e.CatchType),TryStart=I(e.TryStart),TryEnd=I(e.TryEnd),HandlerStart=I(e.HandlerStart),HandlerEnd=I(e.HandlerEnd),FilterStart=I(e.FilterStart)});
    }
    public void Run(ModuleDefinition baseline,string output) {
        // Validate the exact methods and async state machines before replacing them.
        foreach(var (name,names) in Plan) {
            var dt=donor.GetType(Prefix+name);var tt=originalTypes[Prefix+name];var bt=baseline.GetType(Prefix+name);
            foreach(var m in dt.Methods.Where(m=>names.Contains(m.Name))) {
                var old=tt.Methods.SingleOrDefault(x=>x.FullName==m.FullName);
                var bm=bt.Methods.SingleOrDefault(x=>x.FullName==m.FullName);
                if(old!=null && bm!=null && SemanticBody(old)!=SemanticBody(bm))throw new Exception("Official method differs from public baseline: "+m.FullName);
                if(bm!=null) {
                    var ba=bm.CustomAttributes.FirstOrDefault(a=>a.AttributeType.FullName=="System.Runtime.CompilerServices.AsyncStateMachineAttribute");
                    var oa=old?.CustomAttributes.FirstOrDefault(a=>a.AttributeType.FullName=="System.Runtime.CompilerServices.AsyncStateMachineAttribute");
                    if(ba!=null && oa!=null) {
                        var bs=(TypeReference)ba.ConstructorArguments[0].Value;var os=(TypeReference)oa.ConstructorArguments[0].Value;
                        var bsm=baseline.GetType(bs.FullName).Methods.Single(x=>x.Name=="MoveNext");
                        var osm=target.GetType(os.FullName).Methods.Single(x=>x.Name=="MoveNext");
                        if(SemanticBody(bsm)!=SemanticBody(osm))throw new Exception("Official async method differs: "+m.FullName);
                    }
                }
                if(old!=null){methods[m]=old;pendingMethods.Add(m);changed.Add(old.FullName);}
                else CreateMethod(m,tt,m.Name);
            }
        }
        // Materialize root fields and properties needed by bindings and new methods.
        foreach(var name in Plan.Keys) {
            var dt=donor.GetType(Prefix+name);var tt=types[dt];
            foreach(var f in dt.Fields)if(!tt.Fields.Any(x=>x.Name==f.Name))F(f);
            foreach(var p in dt.Properties)if(!tt.Properties.Any(x=>x.Name==p.Name)) {
                var np=new PropertyDefinition(p.Name,p.Attributes,T(p.PropertyType));tt.Properties.Add(np);
                if(p.GetMethod!=null)np.GetMethod=(MethodDefinition)M(p.GetMethod);
                if(p.SetMethod!=null)np.SetMethod=(MethodDefinition)M(p.SetMethod);
            }
        }
        var done=new HashSet<MethodDefinition>();
        while(pendingMethods.Except(done).FirstOrDefault() is MethodDefinition method) {
            var dest=methods[method];CopyBody(method,dest);
            var async=method.CustomAttributes.FirstOrDefault(a=>a.AttributeType.FullName=="System.Runtime.CompilerServices.AsyncStateMachineAttribute");
            if(async!=null){foreach(var a in dest.CustomAttributes.Where(a=>a.AttributeType.FullName==async.AttributeType.FullName).ToList())dest.CustomAttributes.Remove(a);dest.CustomAttributes.Add(Attribute(async));}
            done.Add(method);
        }
        // Preserve the official 1.58.6 account-update subscriptions in this constructor.
        var st=donor.GetType(Prefix+"Controls.Overlay.Battlegrounds.Session.BattlegroundsSessionViewModel");
        var sc=st.Methods.Single(m=>m.IsConstructor&&!m.IsStatic);
        var tc=types[st].Methods.Single(m=>m.IsConstructor&&!m.IsStatic);
        var additions=new List<Instruction>();
        for(int i=0;i<sc.Body.Instructions.Count;i++) {
            var x=sc.Body.Instructions[i];
            if(x.OpCode!=OpCodes.Stfld || x.Operand is not FieldDefinition fd || !fields.TryGetValue(fd,out var nf)||!newFields.Contains(nf))continue;
            int first=i-1;while(first>=0&&sc.Body.Instructions[first].OpCode!=OpCodes.Ldarg_0)first--;
            if(first<0)throw new Exception("Cannot isolate initializer "+fd.FullName);
            for(int j=first;j<=i;j++) {
                var old=sc.Body.Instructions[j];var ni=Instruction.Create(OpCodes.Nop);ni.OpCode=old.OpCode;
                ni.Operand=old.Operand switch{FieldReference f=>F(f),MethodReference m=>M(m),TypeReference t=>T(t),_=>old.Operand};additions.Add(ni);
            }
        }
        if(additions.Count!=6)throw new Exception("Unexpected recent-game initializers: "+additions.Count);
        for(int i=0;i<additions.Count;i++)tc.Body.Instructions.Insert(i,additions[i]);
        tc.Body.MaxStackSize=Math.Max(tc.Body.MaxStackSize,2);changed.Add(tc.FullName);
        target.Attributes &= ~ModuleAttributes.StrongNameSigned;
        target.Write(output);
        File.WriteAllText(output+".audit.json",JsonSerializer.Serialize(new {changedMethods=changed,addedMethods=done.Where(x=>!changed.Contains(methods[x].FullName)).Select(x=>methods[x].FullName).ToArray(),addedFields=newFields.Select(x=>x.FullName).ToArray(),addedTypes=pendingTypes.Select(x=>types[x].FullName).ToArray()},new JsonSerializerOptions{WriteIndented=true}));
    }
}
