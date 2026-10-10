"""Build a separate Beta package revision from frozen transport and canonical Skills.

The 1.2.1 archives remain untouched. Current Skills, including the previously
completed assembly alignment fix, replace only their own package members. Raw
demo CSV and unaffected ZIP bytes are preserved. No model or desktop claim is made.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import re
import shutil
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from package_workbuddy import adapted_skill, ZH

ROOT=Path(__file__).resolve().parents[1]
REVISION='scientific-guidance-v1.2.2'
VERSION='0.12.0'
BASE=ROOT/'docs/downloads/v0.12.0-cycling-rule-v1.2.1'
NEW_REL=Path('downloads')/('v'+VERSION+'-'+REVISION)
STARTER_REL=Path('assets')/REVISION/'starter'

def digest(value):
    return hashlib.sha256(value).hexdigest()

def dump(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def files(root):
    return {p.relative_to(root).as_posix():p.read_bytes() for p in root.rglob('*')
        if p.is_file() and '__pycache__' not in p.parts and p.suffix not in {'.pyc','.pyo'}}

def revision_record(base_bytes, changes):
    return {'schema_version':1,'version':VERSION,'channel':'beta','package_revision':REVISION,
        'base_package_sha256':digest(base_bytes),'changed_members':changes,
        'source_scope':'Current canonical Skills; source bytes identify this revision. Existing assembly alignment code is included. Original demo inputs are unchanged.',
        'native_desktop_discovery_to_delivery':'NOT_RUN_CURRENT_TREE','full_model_behavior':'NOT_RUN_CURRENT_TREE'}

def rewrite(base_bytes, replacements, extra=None):
    extra=dict(extra or {})
    with ZipFile(io.BytesIO(base_bytes)) as old:
        names=set(old.namelist())
        missing=set(replacements)-names
        allowed_new={'voltpeer-assemble/scripts/batterycompose/svg_export.py',
                     'skills/voltpeer-assemble/scripts/batterycompose/svg_export.py'}
        if missing-allowed_new:
            raise ValueError('New canonical members need an explicit inventory review: '+str(sorted(missing-allowed_new)))
        changes=[]
        for name,value in replacements.items():
            if name in missing:
                extra[name]=value
                changes.append({'path':name,'before_sha256':None,'sha256':digest(value),'bytes':len(value),
                    'source':'Existing canonical SVG export module, referenced by the existing assembly CLI but missing from the historical transport.'})
                continue
            previous=old.read(name)
            if value!=previous:
                changes.append({'path':name,'before_sha256':digest(previous),'sha256':digest(value),'bytes':len(value)})
        if not changes and not extra:
            return base_bytes, []
        target=io.BytesIO()
        with ZipFile(target,'w',ZIP_DEFLATED) as out:
            for info in old.infolist():
                out.writestr(info,replacements.get(info.filename,old.read(info.filename)))
            for name,value in extra.items():
                if name in names:
                    raise ValueError('Extra member already exists: '+name)
                info=ZipInfo(name,date_time=(2026,10,10,0,0,0));info.compress_type=ZIP_DEFLATED
                out.writestr(info,value)
            info=ZipInfo('GUIDANCE_REVISION.json',date_time=(2026,10,10,0,0,0));info.compress_type=ZIP_DEFLATED
            out.writestr(info,(json.dumps(revision_record(base_bytes,changes),ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        return target.getvalue(),changes

def single_payload(path, workbuddy=False):
    with ZipFile(path) as z:
        roots={n.split('/')[0] for n in z.namelist() if n.endswith('/SKILL.md')}
        if len(roots)!=1:
            raise ValueError('Expected one canonical Skill root: '+str(path))
        identity=roots.pop()
        content=files(ROOT/'skills'/identity)
        if workbuddy:
            portable=content['SKILL.md'].decode('utf-8-sig').replace('\r\n','\n')
            content['SKILL.md']=adapted_skill(portable,ZH[identity]).encode('utf8')
        replacements={identity+'/'+name:value for name,value in content.items()}
    return rewrite(path.read_bytes(),replacements)

def starter(out):
    old_path=ROOT/'docs/assets/cycling-rule-v1.2.1/starter/VoltPeer-Plot-Starter-v0.12.0.zip'
    base_bytes=old_path.read_bytes()
    with ZipFile(io.BytesIO(base_bytes)) as z:
        replacements={'plot_starter/skills/voltpeer-plot/'+name:value for name,value in files(ROOT/'skills/voltpeer-plot').items()}
        manifest=json.loads(z.read('plot_starter/PACKAGE_MANIFEST.json'))
        for item in manifest['files']:
            name='plot_starter/'+item['path']
            item['sha256']=digest(replacements.get(name,z.read(name)))
        manifest['package_revision']=REVISION
        replacements['plot_starter/PACKAGE_MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8')
    payload,changes=rewrite(base_bytes,replacements)
    target=out/STARTER_REL/old_path.name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(payload)
    base_registry=json.loads((old_path.parent/'plot-starter.json').read_text(encoding='utf8'))
    row=base_registry['packs'][0]
    row.update(bytes=len(payload),sha256=digest(payload),package_revision=REVISION,
        validation='canonical Skill content and extracted runtime checked separately; native/model NOT_RUN')
    dump(target.parent/'plot-starter.json',base_registry)
    return {'path':target.relative_to(out).as_posix(),'bytes':len(payload),'sha256':digest(payload),'changes':changes}

def packages(out):
    dest=out/NEW_REL
    dest.mkdir(parents=True,exist_ok=True)
    index=json.loads((BASE/'download-index.json').read_text(encoding='utf8'))
    records=[]
    changed=[]
    # Independent archives are built first; collections reuse their exact bytes.
    for row in index['archives']:
        rel=row['file']
        if not rel.startswith(('single/','workbuddy/')):
            continue
        old=BASE/rel
        payload,changes=single_payload(old,rel.startswith('workbuddy/'))
        target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(payload)
        changed.append({'file':rel,'changed_members':changes,'base_sha256':digest(old.read_bytes())})
    for row in index['archives']:
        rel=row['file']
        if rel.startswith(('single/','workbuddy/')):
            continue
        old=BASE/rel
        if rel=='VoltPeer-v0.12.0.zip':
            replacements={'skills/'+name:value for name,value in files(ROOT/'skills').items()}
            with ZipFile(old) as z:
                names=set(z.namelist())
                for name in ['README.md','README.en.md','docs/COMPATIBILITY.md','docs/GETTING_STARTED.md',
                             'docs/RELEASE_v0.12.0.md','docs/RELEASE_STATUS.json']:
                    if name in names:
                        replacements[name]=(ROOT/name).read_bytes()
                provenance=json.loads(z.read('docs/SOURCE_PROVENANCE_v0.12.0.json'))
                skill_manifest=[{'path':name,'sha256':digest(value),'bytes':len(value)} for name,value in sorted(files(ROOT/'skills').items())]
                provenance['skill_tree']={'sha256':digest(json.dumps(skill_manifest,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode('utf8')),'files':skill_manifest}
                provenance['scope']='Frozen transport provenance is historical. The complete Skill manifest identifies the effective current scientific-guidance-v1.2.2 source; native desktop and model behavior remain NOT_RUN.'
                provenance['package_revision']=REVISION
                replacements['docs/SOURCE_PROVENANCE_v0.12.0.json']=(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n').encode('utf8')
            payload,changes=rewrite(old.read_bytes(),replacements)
        else:
            with ZipFile(old) as z:
                replacements={name:(dest/'workbuddy'/name).read_bytes() for name in z.namelist() if name.endswith('.zip')}
            payload,changes=rewrite(old.read_bytes(),replacements)
        (dest/rel).write_bytes(payload)
        changed.append({'file':rel,'changed_members':changes,'base_sha256':digest(old.read_bytes())})
    for row in index['archives']:
        path=dest/row['file']
        records.append({**row,'url':(NEW_REL/row['file']).as_posix(),'bytes':path.stat().st_size,'sha256':digest(path.read_bytes())})
    index.update(package_revision=REVISION,base_url=NEW_REL.as_posix()+'/',
        publication='FROZEN_LOCAL_BETA_CANDIDATE; Github publication and ECS deployment are separate events',
        base_package_revision='cycling-rule-v1.2.1',archives=records,skill_count=16,
        current_native_desktop_e2e='NOT_RUN_CURRENT_TREE',full_model_behavior='NOT_RUN_CURRENT_TREE')
    dump(dest/'download-index.json',index)
    (dest/'distribution-sha256.txt').write_text(''.join(r['sha256']+'  '+r['file']+'\n' for r in records),encoding='utf8')
    return {'archives':records,'changes':changed,'download_index':(NEW_REL/'download-index.json').as_posix()}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-docs',type=Path,required=True,help='New staging docs root; never reuse a previously frozen destination.')
    parser.add_argument('--starter-only',action='store_true')
    args=parser.parse_args();out=args.output_docs.resolve()
    if (out/NEW_REL).exists() or (out/STARTER_REL).exists():
        raise FileExistsError('Use a fresh destination; frozen bytes are immutable.')
    first=starter(out)
    if args.starter_only:
        print(json.dumps(first,ensure_ascii=False));return
    result=packages(out)
    result.update(starter=first,revision=REVISION,version=VERSION,channel='beta',skill_count=16)
    pointer=json.loads((ROOT/'docs/assets/cycling-rule-v1.0.0/skill-downloads.json').read_text(encoding='utf8'))
    old_base='downloads/v0.12.0-cycling-rule-v1.2.1/'
    old_starter='assets/cycling-rule-v1.2.1/starter/'
    encoded=json.dumps(pointer,ensure_ascii=False).replace(old_base,NEW_REL.as_posix()+'/').replace(old_starter,STARTER_REL.as_posix()+'/')
    pointer=json.loads(encoded)
    pointer.update(package_revision=REVISION,archives=result['archives'],
        download_manifest=result['download_index'],starter_registry=(STARTER_REL/'plot-starter.json').as_posix(),
        distribution_sha256=(NEW_REL/'distribution-sha256.txt').as_posix())
    pointer['starter_archive']=(STARTER_REL/'VoltPeer-Plot-Starter-v0.12.0.zip').as_posix()
    # Existing record schema contains aliases and a Starter object; keep them current.
    for key,value in list(pointer.items()):
        if key in {'starter_bytes','starter_archive_bytes'}:pointer[key]=first['bytes']
        if key in {'starter_sha256','starter_archive_sha256'}:pointer[key]=first['sha256']
        if key=='starter' and isinstance(value,dict):value.update(bytes=first['bytes'],sha256=first['sha256'])
    dump(out/'assets'/REVISION/'skill-downloads.json',pointer)
    dump(out/NEW_REL/'revision-record.json',result)
    print(json.dumps({'revision':REVISION,'archives':len(result['archives']),'starter_bytes':first['bytes'],'starter_sha256':first['sha256']},ensure_ascii=False))

if __name__=='__main__':
    main()
