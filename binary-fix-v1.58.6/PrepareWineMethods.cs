using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Runtime.CompilerServices;

class PrepareWineMethods
{
    [STAThread]
    static int Main(string[] args)
    {
        var assembly=Assembly.LoadFrom(args[0]);int count=0;
        var plan=new[] {
            "Hearthstone_Deck_Tracker.Windows.OverlayWindow|InitializeCollections,DetectMouseOver,SetTopmost,UpdatePosition,Window_Closing,.cctor",
            "Hearthstone_Deck_Tracker.Controls.AnimatedCard|.ctor,EnsureTile,get_CardTooltipPlacement,set_CardTooltipPlacement",
            "Hearthstone_Deck_Tracker.Controls.AnimatedCardList|.ctor,GetAnimatedCard,get_CardTooltipPlacement,set_CardTooltipPlacement",
            "Hearthstone_Deck_Tracker.Controls.Overlay.Battlegrounds.Session.BattlegroundsSession|System.Windows.Markup.IComponentConnector.Connect",
            "Hearthstone_Deck_Tracker.Controls.Overlay.Battlegrounds.Session.BattlegroundsSessionViewModel|.ctor,UpdateLatestGames,DeleteOldGames,GetMostRecentGames,GetExpiredGames,UpdateDisplayedGames,ToggleRecentGames,get_ToggleRecentGamesCommand,get_ShowMoreGamesButtonText,get_ShowMoreGamesButtonVisibility,set_ShowMoreGamesButtonVisibility",
            "Hearthstone_Deck_Tracker.Controls.Overlay.Battlegrounds.Guides.BattlegroundsCompsGuidesViewModel|GetCompGuides,GetPremiumCompGuides,OnMatchStart",
            "Hearthstone_Deck_Tracker.Utility.Overlay.OverlayOpacityMask|CreateOpacityMask"
        };
        foreach(var entry in plan)
        {
            var parts=entry.Split('|');var type=assembly.GetType(parts[0],true);var names=parts[1].Split(',');
            var flags=BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static|BindingFlags.DeclaredOnly;
            foreach(var m in type.GetMethods(flags).Cast<MethodBase>().Concat(type.GetConstructors(flags)).Where(m=>names.Contains(m.Name)))
            {
                try {RuntimeHelpers.PrepareMethod(m.MethodHandle);Console.WriteLine("JIT PASS "+type.FullName+"::"+m.Name);count++;}
                catch(Exception e){Console.Error.WriteLine("JIT FAIL "+m+" "+e);return 1;}
            }
        }
        foreach(var t in assembly.GetTypes().Where(t=>t.Name.EndsWith("__HdtWine")))
        {
            foreach(var m in t.GetMethods(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static|BindingFlags.DeclaredOnly).Cast<MethodBase>().Concat(t.GetConstructors(BindingFlags.Public|BindingFlags.NonPublic|BindingFlags.Instance|BindingFlags.Static)))
            {
                try {RuntimeHelpers.PrepareMethod(m.MethodHandle);count++;}
                catch(Exception e){Console.Error.WriteLine("JIT FAIL "+t.FullName+"::"+m.Name+" "+e);return 2;}
            }
        }
        Console.WriteLine(count+" patched methods and helpers prepared successfully.");return 0;
    }
}
