"""Render seven previews from fixed CSVs; recolouring never generates new data."""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

KINDS=('line','scatter','bar','cycling','eis','raman','xrd')

def records(root,name):
    with (root/'data'/(name+'.csv')).open(encoding='utf-8-sig',newline='') as f:
        result=list(csv.DictReader(f))
    if not result:raise ValueError('Empty supplied CSV: '+name)
    return result

def values(rows,key):
    result=np.asarray([float(row[key]) for row in rows])
    if not np.isfinite(result).all():raise ValueError('Nonfinite '+key)
    return result

def draw(kind,root,series):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':7.5,'axes.labelsize':8,
        'xtick.labelsize':7,'ytick.labelsize':7,'legend.fontsize':7,'axes.linewidth':.65,
        'svg.fonttype':'none','pdf.fonttype':42,'lines.linewidth':1.15})
    fig=plt.figure(figsize=(180/25.4,86/25.4));axes=[]
    if kind=='eis':
        for i in range(3):axes.append(fig.add_axes([.075+i*.32,.21,.225,.70]))
    else:axes=[fig.add_axes([.105,.21,.79,.70])]
    ax=axes[0]
    if kind in ('line','scatter','bar'):
        rr=records(root,'appearance')
        for s,c in enumerate(series):
            rows=[r for r in rr if int(r['sample'])==s]
            x,y=values(rows,'x'),values(rows,'y')
            if kind=='bar':ax.bar(s,float(np.mean(y)),color=c,width=.65,label=f'Series {s+1}')
            elif kind=='scatter':ax.plot(x[::4],y[::4],ls='none',marker='o',ms=3,color=c,label=f'Series {s+1}')
            else:ax.plot(x,y,color=c,label=f'Series {s+1}')
        ax.set(xlabel='Series' if kind=='bar' else 'Coordinate (a.u.)',ylabel='Response (a.u.)')
        if kind=='bar':ax.set_xticks(range(len(series)),[str(s+1) for s in range(len(series))])
        ax.legend(frameon=False,ncol=2,fontsize=6.5)
    elif kind=='cycling':
        rr=records(root,'cycling');twin=ax.twinx();axes.append(twin)
        for s,c in enumerate(series[:2]):
            rows=[r for r in rr if int(r['sample'])==s];x=values(rows,'cycle');qc=values(rows,'q_charge');qd=values(rows,'q_discharge')
            if np.any(qc<=0) or np.any(qd<0) or np.any(qd>qc):raise ValueError('CE contract failed')
            ax.plot(x,qd,ls='none',marker='o',ms=2,color=c,label=f'Model {s+1}')
            twin.plot(x,100*qd/qc,ls='none',marker='o',mfc='none',mew=.6,ms=2,color=c)
        ax.set(xlabel='Cycle number',ylabel='Discharge capacity\n(mAh g⁻¹)',ylim=(100,190));twin.set(ylabel='CE (%)',ylim=(97,100.2))
        ax.legend(frameon=False,loc='lower left');ax.text(.98,.07,'Filled: capacity  /  open: CE',ha='right',transform=ax.transAxes)
    elif kind=='eis':
        rr=records(root,'eis')
        for s,c in enumerate(series[:2]):
            rows=[r for r in rr if int(r['sample'])==s];freq=values(rows,'frequency_Hz');re=values(rows,'z_real_ohm');im=values(rows,'z_imag_ohm')
            if np.any(freq<=0) or not np.all(np.diff(freq)>0):raise ValueError('EIS frequency must increase')
            z=re+1j*im
            axes[0].plot(re,-im,color=c,label=f'Model {s+1}');axes[1].semilogx(freq,np.abs(z),color=c);axes[2].semilogx(freq,np.angle(z,deg=True),color=c)
        axes[0].set(xlabel="Z′ (Ω)",ylabel="−Z″ (Ω)");axes[1].set(xlabel='Frequency (Hz)',ylabel='|Z| (Ω)');axes[2].set(xlabel='Frequency (Hz)',ylabel='Phase (°)');ax.legend(frameon=False,fontsize=6)
    elif kind=='raman':
        rr=records(root,'spectra')
        for s,c in enumerate(series[:2]):
            rows=[r for r in rr if int(r['sample'])==s];ax.plot(values(rows,'shift_cm1'),values(rows,'intensity'),color=c,label=f'Model {s+1}')
        ax.set(xlabel='Raman shift (cm⁻¹)',ylabel='Intensity (a.u.)');ax.legend(frameon=False)
    else:
        rr=records(root,'diffraction')
        for step,c in zip((0,40),series[:2]):
            rows=[r for r in rr if int(r['step'])==step];ax.plot(values(rows,'two_theta_deg'),values(rows,'intensity'),color=c,label='SOC '+str(step/40))
        ax.set(xlabel='2θ (°)',ylabel='Intensity (a.u.)',xlim=(40,80));ax.legend(frameon=False)
    for axis in axes:
        for spine in axis.spines.values():spine.set_visible(True)
        axis.tick_params(direction='out')
    fig.canvas.draw();renderer=fig.canvas.get_renderer()
    for axis in axes:
        box=axis.get_tightbbox(renderer)
        if box.x0<-.5 or box.y0<-.5 or box.x1>fig.bbox.x1+.5 or box.y1>fig.bbox.y1+.5:raise ValueError('Axis label outside canvas: '+kind)
    return fig

def render(config,out,kind=None):
    root=config.parent;asset=json.loads(config.read_text(encoding='utf-8'))
    if asset['palette_kind']!='categorical' or not 2<=len(asset['series'])<=8:raise ValueError('2–8 categorical colours required')
    out.mkdir(parents=True,exist_ok=False)
    for value in ((kind,) if kind else KINDS):
        fig=draw(value,root,asset['series'])
        for ext in ('png','svg','pdf'):fig.savefig(out/(value+'.'+ext),dpi=180)
        plt.close(fig)
    (out/'render-report.json').write_text(json.dumps({'data_source':'fixed supplied CSV','series':asset['series'],'kinds':[kind] if kind else list(KINDS),'continuous_signals':'solid / unmarked','per_cycle':'points / no line','four_borders':True,'cvd':'not_certified'},indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=Path(__file__).resolve().parent/'palette.json');p.add_argument('--output',type=Path,required=True);p.add_argument('--kind',choices=KINDS)
    a=p.parse_args();render(a.config,a.output,a.kind)
