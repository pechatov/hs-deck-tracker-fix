using System;
using System.Reflection;

class RunRegressionTests
{
    [STAThread]
    static int Main(string[] args)
    {
        var assembly = Assembly.LoadFrom(args[0]);
        int count = 0;
        foreach (var name in new[] {
            "HDTTests.Battlegrounds.BattlegroundsSessionRecentGamesTest",
            "HDTTests.Battlegrounds.GuidesTabsOverlayCompatibilityTest",
            "HDTTests.Battlegrounds.BattlegroundsSessionViewModelTest"
        })
        {
            var type = assembly.GetType(name, true);
            foreach (var method in type.GetMethods(BindingFlags.Public | BindingFlags.Instance | BindingFlags.DeclaredOnly))
            {
                if (method.GetParameters().Length != 0 || method.ReturnType != typeof(void)) continue;
                try
                {
                    method.Invoke(Activator.CreateInstance(type), null);
                    Console.WriteLine("PASS " + name + "." + method.Name);
                    count++;
                }
                catch (Exception error)
                {
                    Console.Error.WriteLine("FAIL " + method.Name + ": " + (error.InnerException ?? error));
                    return 1;
                }
            }
        }
        Console.WriteLine(count + " regression tests passed.");
        return count == 15 ? 0 : 2;
    }
}
