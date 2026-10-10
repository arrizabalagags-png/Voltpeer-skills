"""Reproducible teaching plates. Input values are never inferred from pictures.

demo creates explicit mathematical models; render replays declared CSV inputs.
For author experiments use voltpeer-plot's fixed import/mapping route first.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import re
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

KINDS = ('cycling', 'solvation', 'operando')
STYLE = {'font.family':'sans-serif','font.sans-serif':['DejaVu Sans','Arial'],
         'font.size':7.5,'axes.labelsize':8,'xtick.labelsize':7,'ytick.labelsize':7,
         'legend.fontsize':7,'axes.linewidth':.65,'lines.linewidth':1.1,
         'pdf.fonttype':42,'svg.fonttype':'none','savefig.facecolor':'white'}
plt.rcParams.update(STYLE)

def dump(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def table(path, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    if not rows: raise ValueError('Empty CSV: '+str(path))
    return rows

def array(rows,key):
    a=np.asarray([float(r[key]) for r in rows])
    if not np.isfinite(a).all(): raise ValueError('Nonfinite input: '+key)
    return a

def increasing(a):
    if len(a)<2 or not np.all(np.diff(a)>0): raise ValueError('Axis must increase without duplicate records')

def model(kind,folder):
    """All teaching values are original analytic models, not paper measurements."""
    folder.mkdir(parents=True,exist_ok=False)
    cfg={'schema':1,'kind':kind,'evidence_state':'synthetic_model',
         'sample_names':['Model A','Model B'],'series':['#245885','#C75A42'],
         'conditions':{'temperature_C':25,'capacity_basis':'positive-active-mass',
             'voltage_window_V':[2.8,4.3],'cycling_rate_C':.5},
         'data_files':{},'source_note':'Original analytic teaching inputs; not digitized or measured data.'}
    def put(name,rows):
        table(folder/(name+'.csv'),rows);cfg['data_files'][name]=name+'.csv'
    if kind=='cycling':
        cfg.update(cell_configuration='illustrative_full_cell',reference_cycle=5,
            capacity_unit='mAh g-1',protocol='Constant-current model; CE = Q_dis / Q_chg')
        rows=[];profiles=[];rates=[]
        for s,(q0,k) in enumerate([(180,.00065),(176,.00125)]):
            for n in range(1,301):
                q=q0*(1-.018*np.exp(-n/3))*np.exp(-k*(n-1))
                ce=99.7-.65*np.exp(-n/4)+.012*np.sin(n*.23+s)
                rows.append(dict(sample=s,cycle=n,q_charge=q/(ce/100),q_discharge=q))
            for n in (5,100,300):
                q=next(r['q_discharge'] for r in rows if r['sample']==s and r['cycle']==n)
                for u in np.linspace(0,1,101):
                    v=4.3-.65*u-.85*u**5
                    profiles.append(dict(sample=s,cycle=n,capacity=q*u,voltage=v))
            for n in range(1,61):
                rate=[.2,.5,1,2,5,.2][(n-1)//10]
                q=q0/(1+.085*rate**.8)*np.exp(-.0004*n)
                rates.append(dict(sample=s,cycle=n,rate_C=rate,capacity=q))
        put('cycling',rows);put('profiles',profiles);put('rate',rates)
    elif kind=='solvation':
        cfg.update(density_nm3=8.0,cutoff_nm=.35,
            scope='Two generic spectral components and a mathematical RDF. No chemical peak assignment, MD or evidence of a real electrolyte.')
        rows=[];rdf=[]
        r=np.linspace(.01,1.2,601)
        for s in (0,1):
            for x in np.linspace(680,820,561):
                p=(.75 if s==0 else .4)*np.exp(-.5*((x-730)/5)**2)
                p+=(.35 if s==0 else .8)*np.exp(-.5*((x-752)/7)**2)
                rows.append(dict(sample=s,shift_cm1=x,intensity=p+.025))
            g=(1-np.exp(-(r/.19)**12))+(4.2+s*1.5)*np.exp(-.5*((r-.245)/.025)**2)
            g+=.6*np.exp(-.5*((r-.48)/.07)**2)
            integral=np.r_[0,np.cumsum(.5*(g[1:]*r[1:]**2+g[:-1]*r[:-1]**2)*np.diff(r))]
            cn=4*np.pi*cfg['density_nm3']*integral
            rdf.extend(dict(sample=s,r_nm=x,g=y,coordination=z) for x,y,z in zip(r,g,cn))
        put('spectra',rows);put('rdf',rdf)
    else:
        cfg.update(wavelength_A=1.5406,hkl=[[1,1,1],[2,0,0],[2,2,0]],
            scope='FCC lattice model; illustrative cell voltage. Not a material assignment, phase identification or measured operando experiment.')
        x=np.linspace(40,80,2001);rows=[];states=[]
        for step in range(81):
            soc=step/40 if step<=40 else (80-step)/40
            a=3.60+.08*soc
            voltage=3.0+1.1*soc+(.06 if step<=40 else -.06)*np.sin(np.pi*soc)
            states.append(dict(step=step,time_h=step/20,soc=soc,voltage=voltage,a_A=a))
            peaks=2*np.degrees(np.arcsin(cfg['wavelength_A']*np.sqrt([3,4,8])/(2*a)))
            y=np.full_like(x,.01)
            for pos,amp in zip(peaks,[1,.5,.3]):y+=amp*np.exp(-.5*((x-pos)/.16)**2)
            rows.extend(dict(step=step,two_theta_deg=t,intensity=i) for t,i in zip(x,y))
        put('states',states);put('diffraction',rows)
    dump(folder/'config.json',cfg)
    return folder/'config.json'

def validate(config_path):
    cfg=json.loads(config_path.read_text(encoding='utf-8-sig'))
    if cfg.get('schema')!=1 or cfg.get('kind') not in KINDS:raise ValueError('Unsupported schema or kind')
    if cfg.get('evidence_state') not in ('synthetic_model','author_confirmed_measurements'):raise ValueError('Declare evidence_state')
    names=cfg['sample_names'];colours=cfg['series']
    if len(names)!=2 or len(colours)<2 or any(not matplotlib.colors.is_color_like(c) for c in colours):raise ValueError('Two named samples and distinct valid colours required')
    if colours[0].lower()==colours[1].lower():raise ValueError('Samples need different colours')
    data={}
    for key,filename in cfg['data_files'].items():
        path=(config_path.parent/filename).resolve()
        if path.parent!=config_path.parent.resolve():raise ValueError('CSV must sit beside config')
        data[key]=read(path)
    if cfg['kind']!='operando':
        for rows in data.values():
            if any(r.get('sample') not in ('0','1') for r in rows):raise ValueError('This two-sample contract accepts only sample 0 and 1; never silently discard other samples')
    metrics={}
    if cfg['kind']=='cycling':
        for k in ('temperature_C','capacity_basis','voltage_window_V','cycling_rate_C'):
            if k not in cfg['conditions']:raise ValueError('Missing actual condition: '+k)
        if not cfg.get('reference_cycle') or cfg.get('capacity_unit')!='mAh g-1':raise ValueError('Explicit baseline and supported unit required')
        for s in (0,1):
            rows=[r for r in data['cycling'] if int(r['sample'])==s]
            x=array(rows,'cycle');increasing(x)
            qc,qd=array(rows,'q_charge'),array(rows,'q_discharge')
            if np.any(qc<=0) or np.any(qd<=0) or np.any(qd>qc):raise ValueError('Capacity/CE outside this demo contract; audit protocol instead of clipping')
            ref=[float(r['q_discharge']) for r in rows if float(r['cycle'])==cfg['reference_cycle']]
            if len(ref)!=1:raise ValueError('Retention needs one measured positive reference capacity')
            for n in sorted({int(r['cycle']) for r in data['profiles'] if int(r['sample'])==s}):
                pr=[r for r in data['profiles'] if int(r['sample'])==s and int(r['cycle'])==n]
                increasing(array(pr,'capacity'))
                match=[float(r['q_discharge']) for r in rows if float(r['cycle'])==n]
                if len(match)!=1 or not np.isclose(max(array(pr,'capacity')),match[0],rtol=1e-6):raise ValueError('Profile endpoint differs from cycling capacity')
                vv=array(pr,'voltage');window=cfg['conditions']['voltage_window_V']
                if np.any(vv<float(window[0])-1e-6) or np.any(vv>float(window[1])+1e-6):raise ValueError('Voltage outside declared cell window')
            rate=[r for r in data['rate'] if int(r['sample'])==s];increasing(array(rate,'cycle'))
            if np.any(array(rate,'rate_C')<=0) or np.any(array(rate,'capacity')<=0):raise ValueError('Positive rate and capacity required')
            metrics[names[s]]={'reference_cycle':cfg['reference_cycle'],'reference_capacity':ref[0],'minimum_ce_percent':float((100*qd/qc).min())}
    elif cfg['kind']=='solvation':
        rho=float(cfg['density_nm3']);cut=float(cfg['cutoff_nm'])
        if not np.isfinite(rho) or rho<=0:raise ValueError('Positive species density required')
        for s in (0,1):
            rows=[r for r in data['rdf'] if int(r['sample'])==s]
            x,g,cn=[array(rows,k) for k in ('r_nm','g','coordination')];increasing(x)
            if np.any(x<0) or np.any(g<0) or not x[0]<=cut<=x[-1]:raise ValueError('RDF/cutoff outside declared domain')
            expected=4*np.pi*rho*np.r_[0,np.cumsum(.5*(g[1:]*x[1:]**2+g[:-1]*x[:-1]**2)*np.diff(x))]
            if not np.allclose(cn,expected,rtol=1e-5,atol=1e-5):raise ValueError('Coordination integral inconsistent with RDF/density')
            spectra=[r for r in data['spectra'] if int(r['sample'])==s];increasing(array(spectra,'shift_cm1'))
            if np.any(array(spectra,'intensity')<0):raise ValueError('Negative spectrum intensity')
            metrics[names[s]]={'coordination_at_cutoff':float(np.interp(cut,x,cn))}
    else:
        states=data['states'];x=array(states,'step');increasing(x);increasing(array(states,'time_h'))
        if np.any(array(states,'a_A')<=0) or not float(cfg['wavelength_A'])>0:raise ValueError('Invalid lattice or wavelength')
        scans=[]
        for row in states:
            rr=[r for r in data['diffraction'] if float(r['step'])==float(row['step'])]
            xx=array(rr,'two_theta_deg');yy=array(rr,'intensity');increasing(xx)
            if np.any(yy<0) or (scans and not np.array_equal(scans[0][0],xx)):raise ValueError('Diffraction grid/intensities inconsistent')
            scans.append((xx,yy))
        if len(data['diffraction'])!=sum(len(s[0]) for s in scans):raise ValueError('Orphan/duplicate diffraction states')
        if np.any(array(states,'soc')<0) or np.any(array(states,'soc')>1):raise ValueError('SOC outside declared fraction')
        metrics={'state_count':len(states),'same_map_and_slices':True,'wavelength_A':cfg['wavelength_A']}
    return cfg,data,metrics

def render(config_path,out,palette_lock=None):
    cfg,data,metrics=validate(config_path)
    if palette_lock:
        lock=json.loads(palette_lock.read_text(encoding='utf-8-sig'))
        path=(palette_lock.parent/lock['asset_path']).resolve()
        if path.parent!=palette_lock.parent.resolve() or hashlib.sha256(path.read_bytes()).hexdigest()!=lock['sha256']:raise ValueError('Palette location or SHA256 mismatch')
        asset=json.loads(path.read_text(encoding='utf-8-sig'))
        if asset['id']!=lock['asset_id'] or asset['version']!=lock['asset_version'] or asset['category']!='style' or asset['background'].upper()!='#FFFFFF':raise ValueError('Palette identity or background mismatch')
        if not 2<=len(asset['series'])<=8 or any(not re.fullmatch(r'#[0-9A-Fa-f]{6}',c) for c in asset['series']):raise ValueError('Palette requires 2–8 valid HEX colours')
        cfg['series']=asset['series'];cfg['palette_provenance']=lock
    out.mkdir(parents=True,exist_ok=False);panels=out/'panels';panels.mkdir()
    kind=cfg['kind'];names=cfg['sample_names'];cs=cfg['series']
    rows=[43,38,52] if kind=='cycling' else [55,55]
    # 180 mm canvas. Each source is drawn at the final allocated physical size.
    positions=[(0,0,2),(1,0,2),(2,0,1),(2,1,1)] if kind=='cycling' else [(0,0,1),(0,1,1),(1,0,1),(1,1,1)]
    if kind=='operando':positions=[(0,0,1),(0,1,3),(1,0,2),(1,2,2)];rows=[76,51]
    manifest={'version':1,'figure_id':'VoltPeer '+kind,'claim':cfg['source_note'],
        'width_mm':180,'margin_mm':2.5,'gutter_mm':2.5,'label_band_mm':4,
        'row_heights_mm':rows,'col_weights':[41.875,35.875,44.875,44.875] if kind=='operando' else [80.25,92.25] if kind=='cycling' else [1,1],
        'dpi':300,'output_purpose':'showcase','layout_mode':'fixed','panels':[]}
    # Guides concern actual axes, including rows with different column spans.
    # Right-hand CE labels/colourbars reserve space outside one common data ruler.
    if kind in ('cycling','operando'):
        manifest['alignment_guides']=[
            {'id':'outer-left','edge':'left','panels':['a','b','c'] if kind=='cycling' else ['a','c']},
            {'id':'outer-right','edge':'right','panels':['a','b','d'] if kind=='cycling' else ['b','d']},
            {'id':'lower-top','edge':'top','panels':['c','d']},
            {'id':'lower-bottom','edge':'bottom','panels':['c','d']},
            {'id':'lower-width','edge':'width','panels':['c','d']}]
        if kind=='operando':
            manifest['alignment_guides'] += [{'id':'process-top','edge':'top','panels':['a','b']},
                                            {'id':'process-bottom','edge':'bottom','panels':['a','b']}]
    else:
        manifest['alignment_guides']=[{'id':name,'edge':edge,'panels':labels} for name,edge,labels in
            [('left-column','left',['a','c']),('left-column-right','right',['a','c']),
             ('right-column','left',['b','d']),('right-column-right','right',['b','d']),
             ('upper-top','top',['a','b']),('upper-bottom','bottom',['a','b']),
             ('lower-top','top',['c','d']),('lower-bottom','bottom',['c','d'])]]
    checks=[]
    def make(i,role,fn):
        row,col,span=positions[i];weights=manifest['col_weights'];available=180-5-2.5*(len(weights)-1)
        width=available*sum(weights[col:col+span])/sum(weights)+2.5*(span-1)
        # Available column width is canvas - 2 margins - one gutter = 172.5.
        h=rows[row]-4
        fig=plt.figure(figsize=(width/25.4,h/25.4),dpi=300)
        left=15
        right=15 if (kind=='cycling' and i in (0,1,3)) or (kind=='operando' and i in (1,3)) else 3
        bottom=12;top=4
        ax=fig.add_axes([left/width,bottom/h,(width-left-right)/width,(h-bottom-top)/h])
        fn(fig,ax)
        fig.canvas.draw()
        for aa in fig.axes:
            aa.tick_params(direction='out',length=2.5,pad=2)
            for spine in aa.spines.values():spine.set_visible(True)
        fig.canvas.draw();renderer=fig.canvas.get_renderer()
        for aa in fig.axes:
            bounds=aa.get_tightbbox(renderer)
            if bounds.x0<-.5 or bounds.y0<-.5 or bounds.x1>fig.bbox.x1+.5 or bounds.y1>fig.bbox.y1+.5:raise ValueError('Axis label outside canvas: '+role)
        label=chr(97+i);stem=panels/label
        for ext in ('pdf','svg','png'):fig.savefig(stem.with_suffix('.'+ext),dpi=300,metadata={'Creator':'VoltPeer'} if ext=='pdf' else None)
        p=ax.get_position().bounds;box=[p[0],1-p[1]-p[3],p[0]+p[2],1-p[1]]
        for aa in fig.axes:
            for line in aa.lines:
                if line.get_label().startswith('cycle:') and line.get_linestyle() not in ('None','none',''):raise ValueError('Per-cycle input connected by lines')
        manifest['panels'].append({'label':label,'path':'panels/'+label+'.pdf','editable_svg_path':'panels/'+label+'.svg',
            'row':row,'col':col,'colspan':span,'role':role,'source_id':'original:analytic-'+kind,
            'rights_status':'original','alignment_intent':'compare' if kind=='cycling' and i<2 else 'independent',
            'alignment_group':'cycle-axis' if kind=='cycling' and i<2 else None,
            'alignment_reason':'Different measurement coordinates or shape; process association is checked in source CSV.',
            'plot_box_fraction':box})
        checks.append({'panel':label,'role':role,'width_mm':width,'height_mm':h,'axes':len(fig.axes),'plot_box_fraction':box})
        plt.close(fig)
    if kind=='cycling':
        def cycle(fig,ax):
            twin=ax.twinx()
            for s,c in enumerate(cs[:2]):
                r=[r for r in data['cycling'] if int(r['sample'])==s];x=array(r,'cycle');qc=array(r,'q_charge');qd=array(r,'q_discharge')
                ax.plot(x,qd,ls='none',marker='o',ms=1.7,color=c,label='cycle:'+names[s])
                twin.plot(x,100*qd/qc,ls='none',marker='o',mfc='none',mew=.5,ms=1.7,color=c)
            ax.set(xlabel='Cycle number',ylabel='Discharge capacity\n(mAh g⁻¹)',xlim=(0,305),ylim=(100,190))
            twin.set(ylabel='Coulombic efficiency\n(%)',ylim=(97,100.2));ax.legend(frameon=False,loc='lower left',labels=names)
            ax.text(.98,.09,'Capacity: filled  /  CE: open',ha='right',transform=ax.transAxes,fontsize=6.5)
        def retention(fig,ax):
            for s,c in enumerate(cs[:2]):
                rr=[r for r in data['cycling'] if int(r['sample'])==s];q=array(rr,'q_discharge');ref=metrics[names[s]]['reference_capacity']
                ax.plot(array(rr,'cycle'),100*q/ref,ls='none',marker='o',ms=1.7,color=c,label='cycle:'+names[s])
            ax.set(xlabel='Cycle number',ylabel='Capacity retention\n(%)',xlim=(0,305),ylim=(60,103))
            ax.text(.02,.08,'Reference: cycle '+str(cfg['reference_cycle']),transform=ax.transAxes,fontsize=7)
        def profiles(fig,ax):
            for n,alpha in zip((5,100,300),(.45,.7,1)):
                for s,c in enumerate(cs[:2]):
                    rr=[r for r in data['profiles'] if int(r['sample'])==s and int(r['cycle'])==n]
                    ax.plot(array(rr,'capacity'),array(rr,'voltage'),color=c,alpha=alpha,label=(str(n) if s==0 else '_nolegend_'))
            ax.set(xlabel='Capacity (mAh g⁻¹)',ylabel='Voltage (V)',ylim=(2.75,4.4));ax.legend(title='Cycle',frameon=False,fontsize=6)
        def rate(fig,ax):
            for s,c in enumerate(cs[:2]):
                rr=[r for r in data['rate'] if int(r['sample'])==s]
                ax.plot(array(rr,'cycle'),array(rr,'capacity'),ls='none',marker='o',ms=2.4,color=c,label='cycle:'+names[s])
            ax.set(xlabel='Cycle number',ylabel='Capacity (mAh g⁻¹)',ylim=(115,185))
            for n,rate in zip((5,15,25,35,45,55),('.2','.5','1','2','5','.2')):ax.text(n,180,rate+' C',ha='center',fontsize=6)
        for i,(role,fn) in enumerate([('capacity and same-cycle CE',cycle),('declared-baseline retention',retention),('matched voltage profiles',profiles),('rate and recovery',rate)]):make(i,role,fn)
    elif kind=='solvation':
        def plot(key,x,y,xlabel,ylabel,xlim=None):
            def draw(fig,ax):
                for s,c in enumerate(cs[:2]):
                    r=[r for r in data[key] if int(r['sample'])==s];ax.plot(array(r,x),array(r,y),color=c,label=names[s])
                ax.set(xlabel=xlabel,ylabel=ylabel);ax.legend(frameon=False)
                if xlim:ax.set_xlim(*xlim)
            return draw
        def coordination(fig,ax):
            for s,c in enumerate(cs[:2]):
                r=[r for r in data['rdf'] if int(r['sample'])==s];ax.plot(array(r,'r_nm'),array(r,'coordination'),color=c)
            maximum=max(float(np.interp(.4,array([r for r in data['rdf'] if int(r['sample'])==s],'r_nm'),array([r for r in data['rdf'] if int(r['sample'])==s],'coordination'))) for s in (0,1))
            ax.set(xlabel='r (nm)',ylabel='Coordination number',xlim=(.01,.4),ylim=(0,maximum*1.2))
            ax.text(.03,.94,'ρ = '+str(cfg['density_nm3'])+' nm⁻³',transform=ax.transAxes,va='top')
        def summary(fig,ax):
            ax.bar(names,[metrics[n]['coordination_at_cutoff'] for n in names],color=cs[:2],width=.55)
            ax.set(ylabel='Coordination number');ax.text(.04,.93,'Cutoff: '+str(cfg['cutoff_nm'])+' nm',transform=ax.transAxes,va='top')
        make(0,'generic spectral components',plot('spectra','shift_cm1','intensity','Raman shift (cm⁻¹)','Intensity (a.u.)'))
        make(1,'analytic radial distribution',plot('rdf','r_nm','g','r (nm)','g(r)',(.01,.8)))
        make(2,'same-RDF integral',coordination);make(3,'declared-cutoff summary',summary)
    else:
        states=data['states'];time=array(states,'time_h');soc=array(states,'soc')
        xx=array([r for r in data['diffraction'] if int(r['step'])==int(states[0]['step'])],'two_theta_deg')
        yy=np.asarray([array([r for r in data['diffraction'] if int(r['step'])==int(st['step'])],'intensity') for st in states])
        def voltage(fig,ax):
            ax.plot(array(states,'voltage'),time,color=cs[0]);ax.set(xlabel='Voltage (V)',ylabel='Time (h)',ylim=(time[-1],time[0]));ax.set_xticks([3,4])
        def diffraction(fig,ax):
            mesh=ax.pcolormesh(xx,time,yy,shading='nearest',cmap='viridis',rasterized=True,vmin=0,vmax=1.05)
            ax.set(xlabel='2θ (°)',ylim=(time[-1],time[0]));ax.set_yticks([])
            # The data frame shares its right guide with panel d. The bar sits
            # in a separate physical margin and never resizes that frame.
            pos=ax.get_position();width=fig.get_figwidth()*25.4
            cax=fig.add_axes([pos.x1+3/width,pos.y0,1.8/width,pos.height])
            fig.colorbar(mesh,cax=cax,label='Intensity (a.u.)',ticks=[0,.5,1])
        def slices(fig,ax):
            peak=int(np.argmax(soc));selected=(0,peak//2,peak)
            for i,c in zip(selected,[cs[0],cs[2] if len(cs)>2 else '#528B79',cs[1]]):ax.plot(xx,yy[i],color=c,label=f'SOC {soc[i]:.1f}')
            ax.set(xlabel='2θ (°)',ylabel='Intensity (a.u.)',xlim=(42,44.5));ax.legend(frameon=False,fontsize=6)
        def peaks(fig,ax):
            a=array(states,'a_A');pos=2*np.degrees(np.arcsin(float(cfg['wavelength_A'])*np.sqrt(3)/(2*a)))
            ax.plot(time,pos,color=cs[0]);ax.set(xlabel='Time (h)',ylabel='Model (111) 2θ (°)');ax.text(.02,.93,'λ = '+str(cfg['wavelength_A'])+' Å',transform=ax.transAxes,va='top')
        make(0,'illustrative voltage / same process',voltage);make(1,'same-state diffraction intensity map',diffraction)
        make(2,'slices of the same map',slices);make(3,'Bragg-consistent peak position',peaks)
    dump(out/'manifest.json',manifest);dump(out/'science-check.json',{'scope':'input consistency; not independent scientific certification','metrics':metrics,'panels':checks,'evidence_state':cfg['evidence_state'],'palette_provenance':cfg.get('palette_provenance'),'input_sha256':{name:hashlib.sha256((config_path.parent/filename).read_bytes()).hexdigest() for name,filename in cfg['data_files'].items()}})
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__);sp=p.add_subparsers(dest='command',required=True)
    d=sp.add_parser('demo');d.add_argument('--kind',choices=KINDS,required=True);d.add_argument('--output',type=Path,required=True)
    r=sp.add_parser('render');r.add_argument('--config',type=Path,required=True);r.add_argument('--output',type=Path,required=True);r.add_argument('--palette-lock',type=Path)
    args=p.parse_args()
    if args.command=='demo':
        args.output.mkdir(parents=True,exist_ok=False);cfg=model(args.kind,args.output/'inputs');out=args.output/'rendered'
    else:cfg=args.config;out=args.output
    render(cfg,out,getattr(args,'palette_lock',None))
    print(str(out/'manifest.json'))

if __name__=='__main__':main()
