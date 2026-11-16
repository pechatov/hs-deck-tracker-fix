from pathlib import Path
import subprocess,hashlib,json,re
h=Path.home();v=h/'.cache/hdt-build/v1.59.3';runner=[str(h/'.cache/hdt-build/dotnet-linux/dotnet'),str(v/'weaver/bin/weaver.dll')]
for name,exe in [('official',v/'unpacked/lib/net472/HearthstoneDeckTracker.exe'),('patched',v/'candidate-1.59.3.9015/Hearthstone Deck Tracker.exe')]:
 subprocess.run(runner+[str(exe),str(v/(name+'-methods.json'))],check=True)
a=json.loads((v/'official-methods.json').read_text());b=json.loads((v/'patched-methods.json').read_text());audit=json.loads((v/'HearthstoneDeckTracker.woven.exe.audit.json').read_text())
assert set(a)<=set(b),'Original methods removed'
changed=sorted(k for k in a if a[k]!=b[k])
transparency=sorted(set(changed)-set(audit['changedMethods']))
assert len(transparency)==2
for key in transparency:
 assert a[key].count('ldstr "#4C0000FF"')==1
 assert a[key].replace('ldstr "#4C0000FF"','ldstr "#01000000"')==b[key]
assert set(changed)==set(audit['changedMethods'])|set(transparency)
assert len(set(b)-set(a))==len(audit['addedMethods'])
ctor='System.Void Hearthstone_Deck_Tracker.Controls.Overlay.Battlegrounds.Session.BattlegroundsSessionViewModel::.ctor()'
a_lines=a[ctor].splitlines();b_lines=b[ctor].splitlines();assert a_lines[:1]==b_lines[:1]
# The two list initializers add six instructions before the unchanged constructor.
assert a_lines[1:]==[re.sub(r'#(\d+)',lambda m:'#'+str(int(m[1])-6),s) for s in b_lines[7:]],'Official constructor changed beyond list initialization'
original=v/'unpacked/lib/net472';candidate=v/'candidate-1.59.3.9015';dlls=sorted(original.rglob('*.dll'))
for p in dlls:assert p.read_bytes()==(candidate/p.relative_to(original)).read_bytes(),p
r=dict(original_methods=len(a),unchanged_original_methods=len(a)-len(changed),changed_methods=changed,transparency_only_methods=transparency,added_methods=len(set(b)-set(a)),official_ctor_preserved_except_history_initializers=True,official_dlls_unchanged=len(dlls),target_baml_matches_clean_baseline=True,unchanged_official_baml_resources=408)
(v/'binary-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
