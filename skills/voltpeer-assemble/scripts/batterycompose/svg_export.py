"""Assemble explicitly paired native SVG sources, preserving editable text.

Optional sidecars are author assertions; check their visible contents against
the PDF sources. Never vectorize microscopy or fetch external SVG resources.
"""
from pathlib import Path
import math
import re
import xml.etree.ElementTree as ET
from .assets import _safe_svg
from .layout import ComposeError

NS='http://www.w3.org/2000/svg'
ET.register_namespace('',NS)
ET.register_namespace('xlink','http://www.w3.org/1999/xlink')

def export_svg(manifest, report, destination):
    base=Path(manifest['_manifest_path']).parent
    dest=Path(destination)
    if dest.exists():raise ComposeError('SVG destination already exists: '+str(dest))
    root=ET.Element('{'+NS+'}svg',{'width':str(report['width_mm'])+'mm','height':str(report['height_mm'])+'mm',
        'viewBox':f"0 0 {report['width_mm']} {report['height_mm']}"})
    ET.SubElement(root,'{'+NS+'}rect',{'width':'100%','height':'100%','fill':'white'})
    records={p['label']:p for p in report['panels']}
    for panel in manifest['panels']:
        source=panel.get('editable_svg_path') or (panel['path'] if str(panel['path']).lower().endswith('.svg') else None)
        if not source:raise ComposeError('Panel '+panel['label']+' has no explicitly paired SVG')
        if panel.get('crop_px') or panel.get('crop_box_fraction'):raise ComposeError('SVG export requires uncropped native panels; regenerate cropped sources')
        path=(base/source).resolve();svg=ET.fromstring(_safe_svg(path))
        if svg.tag!='{'+NS+'}svg':raise ComposeError('Sidecar must have an SVG root: '+panel['label'])
        try:box=list(map(float,svg.attrib['viewBox'].replace(',',' ').split()))
        except (KeyError,ValueError) as exc:raise ComposeError('SVG needs a numeric viewBox: '+panel['label']) from exc
        if len(box)!=4 or not all(math.isfinite(v) for v in box) or min(box[2:])<=0:raise ComposeError('SVG viewBox must have finite positive dimensions')
        record=records[panel['label']];x,y,w,h=record['placed_mm']
        if not all(math.isfinite(v) for v in (x,y,w,h)) or min(w,h)<=0:raise ComposeError('SVG placement must have finite positive dimensions')
        if abs(w/h-box[2]/box[3])>.002:raise ComposeError('SVG/PDF aspect ratio differs: '+panel['label'])
        prefix='panel-'+panel['label']+'-'
        ids={e.attrib['id']:prefix+e.attrib['id'] for e in svg.iter() if 'id' in e.attrib}
        for e in svg.iter():
            for key,val in list(e.attrib.items()):
                if key=='id':e.set(key,ids[val]);continue
                val=re.sub(r'url\(#([^\)]+)\)',lambda m:'url(#'+ids.get(m[1],m[1])+')',val)
                if key.endswith('href') and val.startswith('#'):val='#'+ids.get(val[1:],val[1:])
                e.set(key,val)
        group=ET.SubElement(root,'{'+NS+'}g',{'transform':f'translate({x} {y}) scale({w/box[2]}) translate({-box[0]} {-box[1]})'})
        for child in svg:group.append(child)
        if manifest.get('draw_labels',True):
            slot=record['slot_mm'];t=ET.SubElement(root,'{'+NS+'}text',{'x':str(slot[0]),'y':str(slot[1]+2.8),'font-family':'Arial, sans-serif','font-size':'2.8222','font-weight':'bold','fill':'#111111'})
            t.text=panel['label']
    dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
    return str(dest)
