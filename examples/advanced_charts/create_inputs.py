# -*- coding: utf-8 -*-
"""Make deterministic, explicitly synthetic fixtures; never runs in redraw mode."""
from pathlib import Path
import argparse, csv
import numpy as np

def write(path, headers, rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f,lineterminator='\n');w.writerow(headers);w.writerows(rows)

def create(folder):
    if folder.exists() and any(folder.glob('*.csv')):
        raise FileExistsError('Fixture generation needs an empty folder: '+str(folder))
    folder.mkdir(parents=True,exist_ok=True)
    rng=np.random.RandomState(260107)
    write(folder/'flows.csv',['source','target','count'],[
        ('Input A','Group 1',65),('Input A','Group 2',35),('Input B','Group 1',25),('Input B','Group 2',35),('Input B','Group 3',40),('Input C','Group 2',25),('Input C','Group 3',35),
        ('Group 1','Output X',55),('Group 1','Output Y',35),('Group 2','Output X',40),('Group 2','Output Y',35),('Group 2','Output Z',20),('Group 3','Output Y',25),('Group 3','Output Z',50)])
    weights=np.array([[0,18,5,2,0,7],[18,0,15,4,9,0],[5,15,0,22,3,6],[2,4,22,0,11,5],[0,9,3,11,0,16],[7,0,6,5,16,0]])
    write(folder/'chord.csv',['source','target','weight'],[(f'Module {chr(65+i)}',f'Module {chr(65+j)}',weights[i,j]) for i in range(6) for j in range(i+1,6) if weights[i,j]])
    nodes=[];edges=[]
    for g in range(3):
        center=np.array([np.cos(2*np.pi*g/3),np.sin(2*np.pi*g/3)])*.65
        for j in range(6):
            x,y=center+.28*np.array([np.cos(2*np.pi*j/6),np.sin(2*np.pi*j/6)])
            nodes.append((f'N{g*6+j+1:02}',f'Module {chr(65+g)}',x,y))
            edges.append((f'N{g*6+j+1:02}',f'N{g*6+(j+1)%6+1:02}',float(rng.uniform(.4,1))))
            if j<3:edges.append((f'N{g*6+j+1:02}',f'N{g*6+j+4:02}',float(rng.uniform(.4,1))))
    edges += [('N01','N07',.28),('N07','N13',.32),('N13','N01',.25)]
    write(folder/'nodes.csv',['node','group','x','y'],nodes);write(folder/'edges.csv',['source','target','weight'],edges)
    sets=(rng.uniform(size=(280,4))<np.array([.52,.48,.39,.27])).astype(int)
    write(folder/'sets.csv',['object','Set A','Set B','Set C','Set D'],[(f'O{i+1:03}',*r) for i,r in enumerate(sets)])
    mu=rng.uniform(4,12,360);effect=np.r_[rng.normal(1.7,.35,45),rng.normal(-1.5,.4,45),rng.normal(0,.13,270)]
    x=rng.normal(mu[:,None],.65,(360,6));y=rng.normal(mu[:,None]+effect[:,None],.65,(360,6))
    write(folder/'expression.csv',['feature',*[f'A{i+1}' for i in range(6)],*[f'B{i+1}' for i in range(6)]],[(f'Feature {i+1:03}',*x[i],*y[i]) for i in range(360)])
    selected=set(rng.choice(140,60,replace=False).tolist())
    write(folder/'universe.csv',['object','selected'],[(f'G{i+1:03}',int(i in selected)) for i in range(400)])
    memberships=[]
    for t in range(10):
        size=40+t*3
        ids=rng.choice(400 if t>5 else 140,size,replace=False)
        memberships.extend((f'G{i+1:03}',f'Set {t+1:02}') for i in ids)
    write(folder/'memberships.csv',['object','set'],memberships)
    hit=set(o for o,t in memberships if t=='Set 01')
    scores=np.array([rng.normal(1.7 if f'G{i+1:03}' in hit else 0,1) for i in range(400)])
    write(folder/'ranked.csv',['object','score'],[(f'G{i+1:03}',scores[i]) for i in range(400)])
    matrix=rng.normal(0,.4,(18,12))
    for i in range(18): matrix[i,(i//6)*4:(i//6+1)*4]+=2
    write(folder/'heatmap.csv',['feature',*[f'S{i+1:02}' for i in range(12)]],[(f'F{i+1:02}',*r) for i,r in enumerate(matrix)])
    write(folder/'sample_groups.csv',['sample','group'],[(f'S{i+1:02}',f'Group {chr(65+i//4)}') for i in range(12)])
    observations=[(f'Group {chr(65+g)}',f'O{g*60+i+1:03}',float(rng.normal([1.2,2.1,2.5][g],[.22,.3,.55][g]))) for g in range(3) for i in range(60)]
    write(folder/'observations.csv',['group','object','value'],observations)
    centers=rng.normal(0,2.5,(4,8));features=np.vstack([rng.normal(centers[g],.8,(60,8)) for g in range(4)])
    write(folder/'features.csv',['object','group',*[f'F{i+1}' for i in range(8)]],[(f'O{i+1:03}',f'Group {chr(65+i//60)}',*r) for i,r in enumerate(features)])
    labels=np.r_[np.ones(120,dtype=int),np.zeros(480,dtype=int)];rng.shuffle(labels)
    a=1/(1+np.exp(-rng.normal(np.where(labels==1,1.2,-1.4),1.3)))
    b=1/(1+np.exp(-rng.normal(np.where(labels==1,.7,-1),1.5)))
    write(folder/'predictions.csv',['object','truth','score_a','score_b'],[(f'O{i+1:03}',labels[i],a[i],b[i]) for i in range(600)])
    write(folder/'effects.csv',['study','log_ratio','se'],[(f'Study {i+1}',e,s) for i,(e,s) in enumerate(zip([-.25,.03,-.42,-.16,-.37,.1],[.14,.17,.11,.12,.2,.15]))])
    q=rng.normal(0,1,(8,5));k=rng.normal(0,1,(8,5))
    for name,m in [('queries',q),('keys',k)]:write(folder/(name+'.csv'),['token',*[f'D{i+1}' for i in range(5)]],[(f'T{i+1}',*r) for i,r in enumerate(m)])
    rows=[]
    for m,c,a in [('Model A',8,.77),('Model B',15,.83),('Model C',26,.85),('Model D',40,.89),('Model E',55,.875),('Model F',70,.90),('Model G',90,.895)]:
        for seed in range(5): rows.append((m,seed,c+float(rng.normal(0,c*.035)),a+float(rng.normal(0,.006))))
    write(folder/'benchmarks.csv',['model','seed','latency_ms','accuracy'],rows)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);args=p.parse_args();create(args.output)
