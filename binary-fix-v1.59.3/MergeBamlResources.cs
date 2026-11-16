using System;
using System.IO;
using System.Linq;
using System.Collections;
using System.Collections.Generic;
using System.Resources;
using System.Security.Cryptography;

class MergeBamlResources
{
    static Dictionary<string, Tuple<string, byte[]>> Read(string path)
    {
        var result=new Dictionary<string,Tuple<string,byte[]>>();
        using(var r=new ResourceReader(path))
        {
            var e=r.GetEnumerator();
            while(e.MoveNext()) {string type;byte[] data;var name=(string)e.Key;r.GetResourceData(name,out type,out data);result.Add(name,Tuple.Create(type,data));}
        }
        return result;
    }
    static int Main(string[] args)
    {
        var old=Read(args[0]);var donor=Read(args[1]);
        var replace=new HashSet<string>(new[]{
            "controls/overlay/battlegrounds/minions/battlegroundscardsgroup.baml",
            "controls/overlay/battlegrounds/session/battlegroundssession.baml",
            "controls/tooltips/cardtooltip.baml"
        });
        var baseline=Read(args[3]);
        foreach(var key in replace)
        {
            if(old[key].Item1!=baseline[key].Item1 || !old[key].Item2.SequenceEqual(baseline[key].Item2))
                throw new Exception("Official BAML differs from public baseline: "+key);
        }
        Console.WriteLine("All three target BAML resources match the clean baseline.");
        using(var w=new ResourceWriter(args[2]))
            foreach(var pair in old) {var value=replace.Contains(pair.Key)?donor[pair.Key]:pair.Value;w.AddResourceData(pair.Key,value.Item1,value.Item2);}
        var result=Read(args[2]);int changed=0;
        if(old.Count!=result.Count)throw new Exception("Resource count changed");
        foreach(var pair in old)
        {
            var n=result[pair.Key];var same=pair.Value.Item1==n.Item1&&pair.Value.Item2.SequenceEqual(n.Item2);
            if(!same){if(!replace.Contains(pair.Key))throw new Exception("Unexpected resource change: "+pair.Key);changed++;Console.WriteLine("Patched "+pair.Key);}
        }
        if(changed!=3)throw new Exception("Expected exactly three changed BAML resources");
        Console.WriteLine((old.Count-changed)+" official resources preserved byte-for-byte.");
        return 0;
    }
}
