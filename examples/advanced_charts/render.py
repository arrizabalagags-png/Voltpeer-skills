# -*- coding: utf-8 -*-
"""Render one original reference chart from CSV; no network or data generation."""
from pathlib import Path
import argparse, csv, hashlib, json, sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Rectangle, Circle, Wedge, Polygon
from matplotlib.colors import TwoSlopeNorm
from scipy import stats
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.special import softmax
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.metrics import roc_curve, roc_auc_score, precision_recall_curve, average_precision_score, confusion_matrix
from catalogue import records
from figure_style import apply_figure_style

COLOURS=['#277DA8','#E66B4E','#259E91','#8A65B2','#D99A29','#52728F']
INK='#233740';NEUTRAL='#A5B1B7'

def read(root,name):
    with (root/name).open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f))

def numeric(rows,columns):return np.array([[float(r[c]) for c in columns] for r in rows])

def bh(p):
    p=np.asarray(p);order=np.argsort(p);n=len(p)
    q=np.minimum.accumulate((p[order]*n/np.arange(1,n+1))[::-1])[::-1]
    out=np.empty(n);out[order]=np.minimum(q,1);return out

def expression(root):
    rows=read(root,'expression.csv');a=numeric(rows,[f'A{i+1}' for i in range(6)]);b=numeric(rows,[f'B{i+1}' for i in range(6)])
    fc=b.mean(1)-a.mean(1);p=stats.ttest_ind(a,b,axis=1,equal_var=False).pvalue;q=bh(p)
    assert np.isfinite(p).all() and ((q>=p-1e-12)&(q<=1)).all()
    return rows,(a.mean(1)+b.mean(1))/2,fc,p,q

def base(title):
    width_in,height_in=np.array([180,120])/25.4
    fig=plt.figure(figsize=(width_in,height_in),facecolor='white')
    # Figure identity and synthetic status belong to the page, caption and
    # manifest. Keep the reusable plate to data labels and method information.
    ax=fig.add_axes([.13,.19,.76,.65])
    return fig,ax

def ribbon(x0,x1,y0,y1,h,colour,ax):
    d=(x1-x0)*.48
    pts=[(x0,y0),(x0+d,y0),(x1-d,y1),(x1,y1),(x1,y1+h),(x1-d,y1+h),(x0+d,y0+h),(x0,y0+h),(x0,y0)]
    ax.add_patch(PathPatch(MPath(pts,[1,4,4,4,2,4,4,4,79]),facecolor=colour,edgecolor='none',alpha=.32))

def draw(kind,root):
    record=next(a for a in records() if a['kind']==kind)
    fig,ax=base(record['title_en']);metrics={};alignment_axes=[ax]
    if kind=='sankey':
        rows=read(root,'flows.csv');flows={(r['source'],r['target']):int(r['count']) for r in rows}
        stages=[['Input A','Input B','Input C'],['Group 1','Group 2','Group 3'],['Output X','Output Y','Output Z']]
        ins=lambda n:sum(v for (s,t),v in flows.items() if t==n)
        outs=lambda n:sum(v for (s,t),v in flows.items() if s==n)
        assert all(ins(n)==outs(n) for n in stages[1]);total=sum(outs(n) for n in stages[0]);assert total==sum(ins(n) for n in stages[2])
        ax.set_position([.19,.16,.63,.68]);scale=.76/total;pos={};colours={};counts={}
        for c,names in enumerate(stages):
            y=.94
            for j,n in enumerate(names):
                count=outs(n) if c<2 else ins(n);h=count*scale;y-=h
                pos[n]=(c,y,h);counts[n]=count;colours[n]=COLOURS[j]
                ax.add_patch(Rectangle((c-.035,y),.07,h,facecolor=colours[n],edgecolor='none'))
                label=n.replace('Input ','').replace('Group ','G').replace('Output ','')
                ax.text(c-.08 if c==0 else c+.08,y+h/2,f'{label} · {count}',ha='right' if c==0 else 'left',va='center',fontsize=8,color=INK)
                y-=.055
        for c in [0,1]:
            offsets0={n:0. for n in stages[c]};offsets1={n:0. for n in stages[c+1]}
            for s in stages[c]:
                for t in stages[c+1]:
                    v=flows.get((s,t),0)
                    if not v:continue
                    ribbon(c+.035,c+1-.035,pos[s][1]+offsets0[s],pos[t][1]+offsets1[t],v*scale,colours[s],ax)
                    offsets0[s]+=v*scale;offsets1[t]+=v*scale
        for c,label in enumerate(['Input','Group','Output']):ax.text(c,1.06,label,ha='center',fontsize=9,color=INK)
        ax.set(xlim=(-.38,2.4),ylim=(-.02,1.15));ax.axis('off');metrics={'total_objects':total,'internal_conservation':True,'node_counts':counts}
    elif kind=='chord':
        rows=read(root,'chord.csv');names=sorted({r[k] for r in rows for k in ['source','target']});n=len(names);m=np.zeros((n,n))
        for r in rows:i,j=names.index(r['source']),names.index(r['target']);m[i,j]=m[j,i]=float(r['weight'])
        assert np.allclose(m,m.T) and (m>=0).all() and (m.sum(1)>0).all()
        totals=m.sum(1);unit=(360-6*n)/totals.sum();start=95;cursor=[];bounds=[]
        for i,w in enumerate(totals):
            stop=start+w*unit;bounds.append((start,stop));cursor.append(start)
            ax.add_patch(Wedge((0,0),1.0,start,stop,width=.055,facecolor=COLOURS[i],edgecolor='none'))
            a=np.deg2rad((start+stop)/2);x,y=1.42*np.cos(a),1.42*np.sin(a)
            ax.text(x,y,names[i].replace('Module ','')+' · '+str(int(w)),ha='left' if x>0 else 'right',va='bottom' if y>.5 else 'top' if y<-.5 else 'center',fontsize=9)
            start=stop+6
        def arc(a,b):
            t=np.deg2rad(np.linspace(a,b,16));return list(zip(.94*np.cos(t),.94*np.sin(t)))
        for i in range(n):
            for j in range(i+1,n):
                w=m[i,j]
                if not w:continue
                a=arc(cursor[i],cursor[i]+w*unit);b=arc(cursor[j],cursor[j]+w*unit);cursor[i]+=w*unit;cursor[j]+=w*unit
                pts=a+[(0,0),(0,0),b[0]]+b[1:]+[(0,0),(0,0),a[0]]+[a[0]]
                codes=[1]+[2]*(len(a)-1)+[4]*3+[2]*(len(b)-1)+[4]*3+[79]
                ax.add_patch(PathPatch(MPath(pts,codes),facecolor=COLOURS[i],alpha=.37,edgecolor='none'))
        ax.set_position([.17,.15,.66,.70]);ax.set(xlim=(-1.85,1.85),ylim=(-1.55,1.55),aspect='equal');ax.axis('off');metrics={'undirected_edges':len(rows),'node_strength':dict(zip(names,totals.tolist())),'sum_strength':float(totals.sum())}
    elif kind=='network':
        nodes=read(root,'nodes.csv');edges=read(root,'edges.csv');by={r['node']:r for r in nodes};groups=sorted({r['group'] for r in nodes});degrees={n:0 for n in by}
        for r in edges:
            a,b=by[r['source']],by[r['target']];w=float(r['weight']);assert w>=0
            ax.plot([float(a['x']),float(b['x'])],[float(a['y']),float(b['y'])],color='#B3C3CA',lw=.6+1.0*w,zorder=1)
            degrees[a['node']]+=1;degrees[b['node']]+=1
        for i,g in enumerate(groups):
            rows=[r for r in nodes if r['group']==g];x=np.array([float(r['x']) for r in rows]);y=np.array([float(r['y']) for r in rows])
            ax.scatter(x,y,s=[40+15*degrees[r['node']] for r in rows],c=COLOURS[i],edgecolor='white',linewidth=.6,zorder=2,label=g)
            center=np.array([x.mean(),y.mean()])
            for r in rows:
                # Identity labels are outside the node; all 18 nodes are retained.
                v=np.array([float(r['x']),float(r['y'])]);direction=v-center;v=center+direction/(np.linalg.norm(direction)+1e-9)*.50
                if r['node'] in ['N12','N14']:v[0]-=.20
                ax.text(*v,r['node'],ha='center',va='center',fontsize=8)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,1.13),ncol=3,fontsize=8,handletextpad=.2,columnspacing=.9)
        ax.set(xlim=(-1.10,1.40),ylim=(-1.15,1.2),aspect='equal');ax.axis('off');metrics={'nodes':len(nodes),'edges':len(edges),'degrees':degrees}
    elif kind in ['upset','venn']:
        rows=read(root,'sets.csv');cols=['Set A','Set B','Set C','Set D'];data=numeric(rows,cols).astype(int);assert np.isin(data,[0,1]).all()
        if kind=='upset':
            counts={tuple(bits):int(np.all(data==bits,axis=1).sum()) for bits in np.ndindex(*(2,)*4) if any(bits)}
            items=sorted(counts.items(),key=lambda kv:(-kv[1],kv[0]));patterns=np.array([k for k,v in items]);values=np.array([v for k,v in items])
            ax.set_position([.34,.47,.56,.36]);ax.bar(range(len(items)),values,color=COLOURS[0],width=.65);ax.set_ylabel('Intersection size');ax.set_xticks([]);ax.margins(y=.15)
            low=fig.add_axes([.34,.20,.56,.22]);side=fig.add_axes([.08,.20,.20,.22]);x=np.arange(len(items));low.scatter(np.repeat(x,4),np.tile(range(4),len(items)),s=16,color='#DBE1E5')
            for i,bits in enumerate(patterns):
                at=np.where(bits)[0];low.scatter(np.repeat(i,len(at)),at,s=25,color=INK);low.plot([i,i],[at.min(),at.max()],color=INK,lw=1.0)
            low.set(xlim=(-.6,len(items)-.4),ylim=(3.5,-.5));low.set_yticks([]);low.set_xticks([]);low.spines[:].set_visible(False)
            totals=data.sum(0);side.barh(range(4),totals,color=COLOURS[2],height=.6);side.set(ylim=(3.5,-.5));side.set_yticks(range(4));side.set_yticklabels(['A','B','C','D']);side.invert_xaxis();side.set_xlabel('Set size');side.spines[['right','top']].set_visible(False)
            metrics={'exclusive_intersections':{'/'.join(map(str,k)):v for k,v in items},'union_size':int(values.sum()),'set_sizes':totals.tolist(),'outside_union':int((data.sum(1)==0).sum())};alignment_axes=[ax,low]
        else:
            counts={bits:int(np.all(data[:,:3]==bits,axis=1).sum()) for bits in np.ndindex(2,2,2)}
            for center,c,label,labelpos in [((-.5,.30),COLOURS[0],'Set A',(-.75,1.28)),((.5,.30),COLOURS[1],'Set B',(.75,1.28)),((0,-.52),COLOURS[2],'Set C',(0,-1.48))]:
                ax.add_patch(Circle(center,.85,facecolor=c,alpha=.22,edgecolor=c,lw=.8));ax.text(*labelpos,label,ha='center',va='center',fontsize=9)
            positions={(1,0,0):(-1.02,.25),(0,1,0):(1.02,.25),(0,0,1):(0,-1.04),(1,1,0):(0,.63),(1,0,1):(-.43,-.45),(0,1,1):(.43,-.45),(1,1,1):(0,-.04)}
            for bits,p in positions.items():ax.text(*p,str(counts[bits]),ha='center',va='center',fontsize=10,color=INK)
            ax.set(xlim=(-1.65,1.65),ylim=(-1.60,1.45),aspect='equal');ax.axis('off');fig.text(.08,.10,'Circle areas are schematic; counts come from set operations.',fontsize=8,color='#53656E')
            metrics={'exclusive_regions':{'/'.join(map(str,k)):v for k,v in counts.items()},'union_size':sum(v for k,v in counts.items() if any(k))}
    elif kind in ['volcano','ma']:
        rows,mean,fc,p,q=expression(root);up=(q<.05)&(fc>=1);down=(q<.05)&(fc<=-1);other=~(up|down);xx=fc if kind=='volcano' else mean;yy=-np.log10(q) if kind=='volcano' else fc
        for mask,c,label in [(other,'#C4CDD1','Other'),(down,COLOURS[0],'Lower'),(up,COLOURS[1],'Higher')]:ax.scatter(xx[mask],yy[mask],s=9,c=c,label=label,alpha=.8,linewidth=0)
        if kind=='volcano':
            ax.axvline(-1,color=NEUTRAL,lw=.7,ls='--');ax.axvline(1,color=NEUTRAL,lw=.7,ls='--');ax.axhline(-np.log10(.05),color=NEUTRAL,lw=.7,ls='--');ax.set(xlabel='log₂ fold change (geometric means)',ylabel='−log₁₀ BH-adjusted p')
        else:ax.axhline(0,color=NEUTRAL,lw=.7);ax.set(xlabel='Mean log₂ abundance',ylabel='log₂ fold change (geometric means)')
        ax.legend(loc='upper center',bbox_to_anchor=(.5,1.16),ncol=3,fontsize=8,markerscale=1.3);ax.margins(.06)
        metrics={'features':len(rows),'samples_per_group':6,'higher':int(up.sum()),'lower':int(down.sum()),'test':'two-sided Welch t-test on log2 abundance','correction':'Benjamini-Hochberg across all 360 features','q_min':float(q.min())}
    elif kind in ['enrichment','gsea']:
        universe=read(root,'universe.csv');members=read(root,'memberships.csv');allids={r['object'] for r in universe};selected={r['object'] for r in universe if int(r['selected'])};sets={t:{r['object'] for r in members if r['set']==t} for t in sorted({r['set'] for r in members})}
        assert all(s<=allids for s in sets.values())
        if kind=='enrichment':
            names=list(sets);count=np.array([len(sets[t]&selected) for t in names]);sizes=np.array([len(sets[t]) for t in names]);p=stats.hypergeom.sf(count-1,len(allids),sizes,len(selected));q=bh(p);order=np.argsort(count/len(selected));y=np.arange(len(names))
            ax.set_position([.18,.19,.62,.65]);sc=ax.scatter(count[order]/len(selected),y,s=count[order]*10,c=-np.log10(q[order]),cmap='viridis',edgecolor='white',linewidth=.6)
            ax.set_yticks(y);ax.set_yticklabels(np.array(names)[order]);ax.set_xlabel('Gene ratio (overlap / selected)');ax.margins(x=.15,y=.07)
            cb=fig.colorbar(sc,cax=fig.add_axes([.86,.47,.022,.34]));cb.set_label('−log₁₀ BH-adjusted p');cb.ax.tick_params(labelsize=8)
            for size in [10,20,30]:ax.scatter([],[],s=size*10,facecolor='white',edgecolor=INK,label=str(size))
            ax.legend(title='Overlap count',loc='lower right',bbox_to_anchor=(1.32,-.1),fontsize=8,title_fontsize=8,labelspacing=1.1)
            metrics={'background':len(allids),'selected':len(selected),'tested_sets':len(names),'overlap':count.tolist(),'set_size':sizes.tolist(),'p':p.tolist(),'q':q.tolist()}
        else:
            rows=sorted(read(root,'ranked.csv'),key=lambda r:-float(r['score']));ids=[r['object'] for r in rows];scores=np.array([float(r['score']) for r in rows]);hit=np.array([i in sets['Set 01'] for i in ids]);assert set(ids)==allids and len(ids)==len(allids)
            weight=np.abs(scores)*hit;steps=weight/weight.sum()-(~hit)/(~hit).sum();running=np.r_[0,np.cumsum(steps)];es=running[np.argmax(np.abs(running))]
            ax.plot(np.arange(len(running)),running,color=COLOURS[2]);ax.axhline(0,color=NEUTRAL,lw=.7);ax.set(xlim=(0,len(rows)),ylabel='Running enrichment score');ax.set_position([.13,.42,.76,.42]);ax.set_xticks([])
            low=fig.add_axes([.13,.19,.76,.18]);low.plot(np.arange(1,len(rows)+1),scores,color=COLOURS[0],lw=.9);low.set(xlim=(0,len(rows)),xlabel='Rank in the complete list',ylabel='Rank score');low.eventplot(np.where(hit)[0]+1,lineoffsets=scores.max()+.4,linelengths=.45,colors=INK,linewidths=.6);low.margins(y=.12)
            fig.text(.65,.9,f'Raw ES = {es:.3f} · {hit.sum()} members',fontsize=8);metrics={'ranked_objects':len(rows),'members':int(hit.sum()),'raw_ES':float(es),'running_sum_end':float(running[-1]),'NES_p_FDR':'not calculated: no permutations'};alignment_axes=[ax,low]
    elif kind=='heatmap':
        rows=read(root,'heatmap.csv');cols=list(rows[0])[1:];m=numeric(rows,cols);z=(m-m.mean(1,keepdims=True))/m.std(1,keepdims=True,ddof=1)
        rowlink=linkage(z,method='average',metric='euclidean');collink=linkage(z.T,method='average',metric='euclidean')
        ax.set_position([.28,.22,.56,.54]);left=fig.add_axes([.10,.22,.13,.54]);top=fig.add_axes([.28,.79,.56,.10]);rorder=dendrogram(rowlink,orientation='left',no_labels=True,color_threshold=0,above_threshold_color='#677D86',ax=left)['leaves'];corder=dendrogram(collink,no_labels=True,color_threshold=0,above_threshold_color='#677D86',ax=top)['leaves'];left.axis('off');top.axis('off')
        # origin lower matches the left-oriented dendrogram leaf order.
        im=ax.pcolormesh(np.arange(len(cols)+1)-.5,np.arange(len(rows)+1)-.5,z[rorder][:,corder],cmap='RdBu_r',norm=TwoSlopeNorm(vmin=-2.5,vcenter=0,vmax=2.5),rasterized=False)
        ax.set(xlim=(-.5,len(cols)-.5),ylim=(-.5,len(rows)-.5))
        ax.set_yticks(range(len(rows)));ax.set_yticklabels([rows[i]['feature'] for i in rorder],fontsize=8);ax.set_xticks(range(len(cols)));ax.set_xticklabels(np.array(cols)[corder],rotation=45,ha='right',rotation_mode='anchor',fontsize=8);ax.tick_params(length=0)
        groups={r['sample']:r['group'] for r in read(root,'sample_groups.csv')};stripe=fig.add_axes([.28,.768,.56,.013]);stripe.pcolormesh(np.array([[ord(groups[cols[i]][-1])-65 for i in corder]]),cmap=matplotlib.colors.ListedColormap(COLOURS[:3]),vmin=0,vmax=2,rasterized=False);stripe.axis('off')
        cb=fig.colorbar(im,cax=fig.add_axes([.90,.44,.018,.29]));cb.set_label('Row z-score');cb.set_ticks([-2,0,2]);metrics={'features':len(rows),'samples':len(cols),'standardization':'per-row sample SD (ddof=1)','linkage':'average Euclidean','row_order':rorder,'column_order':corder,'colour_center':0}
    elif kind=='violin':
        rows=read(root,'observations.csv');groups=sorted({r['group'] for r in rows});vals=[np.array([float(r['value']) for r in rows if r['group']==g]) for g in groups]
        vs=ax.violinplot(vals,positions=np.arange(3),showextrema=False,widths=.7,bw_method='scott')
        for i,body in enumerate(vs['bodies']):body.set_facecolor(COLOURS[i]);body.set_edgecolor(COLOURS[i]);body.set_alpha(.2)
        for i,v in enumerate(vals):
            jitter=(np.arange(len(v))*.61803398875%1-.5)*.28;ax.scatter(i+jitter,v,s=7,c=COLOURS[i],alpha=.6,linewidth=0);lo,med,hi=np.quantile(v,[.25,.5,.75]);ax.plot([i,i],[lo,hi],color=INK,lw=3);ax.scatter([i],[med],s=28,c='white',edgecolor=INK,zorder=5)
        ax.set_xticks(range(3));ax.set_xticklabels([g+' (n=60)' for g in groups]);ax.set_ylabel('Value (arbitrary units)');ax.set_xlim(-.65,2.65);ax.margins(y=.08);metrics={'counts':[len(v) for v in vals],'median':[float(np.median(v)) for v in vals],'KDE_bandwidth':'Scott','center_spread':'median / interquartile range; points are all synthetic observations'}
    elif kind in ['pca','tsne']:
        rows=read(root,'features.csv');cols=list(rows[0])[2:];x=StandardScaler().fit_transform(numeric(rows,cols));groups=sorted({r['group'] for r in rows})
        if kind=='pca':
            fit=PCA(n_components=2,svd_solver='full');embedding=fit.fit_transform(x);variance=fit.explained_variance_ratio_;labels=[f'PC{i+1} ({variance[i]*100:.1f}%)' for i in range(2)];metrics={'explained_variance':variance.tolist(),'algorithm':'StandardScaler + full SVD PCA'}
        else:
            fit=TSNE(n_components=2,perplexity=30,learning_rate=200,init='pca',random_state=17,max_iter=1000);embedding=fit.fit_transform(x);labels=['t-SNE 1','t-SNE 2'];metrics={'perplexity':30,'seed':17,'iterations':1000,'learning_rate':200,'init':'PCA','KL_divergence':float(fit.kl_divergence_)}
        for i,g in enumerate(groups):
            mask=np.array([r['group']==g for r in rows]);ax.scatter(*embedding[mask].T,s=11,color=COLOURS[i],alpha=.8,label=g,linewidth=0)
        ax.legend(loc='upper center',bbox_to_anchor=(.5,1.16),ncol=4,fontsize=8);ax.set(xlabel=labels[0],ylabel=labels[1]);ax.set_xticks([]);ax.set_yticks([]);ax.margins(.08);metrics.update({'objects':len(rows),'input_features':len(cols),'embedding_sha256':hashlib.sha256(embedding.tobytes()).hexdigest()})
    elif kind in ['roc','pr','confusion','calibration']:
        rows=read(root,'predictions.csv');truth=np.array([int(r['truth']) for r in rows]);scores=numeric(rows,['score_a','score_b']);assert np.isin(truth,[0,1]).all() and ((scores>=0)&(scores<=1)).all()
        metrics={'objects':len(rows),'positives':int(truth.sum()),'negative':int((truth==0).sum()),'prevalence':float(truth.mean()),'dataset':'same predictions.csv across ROC, PR, confusion and calibration'}
        if kind in ['roc','pr']:
            for i,name in enumerate(['Model A','Model B']):
                if kind=='roc':
                    x,y,_=roc_curve(truth,scores[:,i],drop_intermediate=False);value=roc_auc_score(truth,scores[:,i]);metric='ROC AUC'
                else:
                    y,x,_=precision_recall_curve(truth,scores[:,i]);value=average_precision_score(truth,scores[:,i]);metric='AP'
                ax.step(x,y,where='post' if kind=='roc' else 'pre',color=COLOURS[i],lw=1.3,label=f'{name} · {metric} {value:.3f}');metrics[name]={metric:float(value)}
            if kind=='roc':ax.plot([0,1],[0,1],color=NEUTRAL,lw=.8,ls='--');ax.set(xlabel='False positive rate',ylabel='True positive rate')
            else:ax.axhline(truth.mean(),color=NEUTRAL,lw=.8,ls='--',label='Prevalence = 0.20');ax.set(xlabel='Recall',ylabel='Precision')
            ax.set(xlim=(-.015,1.015),ylim=(-.015,1.015));ax.legend(loc='lower right' if kind=='roc' else 'lower left',fontsize=8)
        elif kind=='confusion':
            cm=confusion_matrix(truth,scores[:,0]>=.5,labels=[0,1]);norm=cm/cm.sum(1,keepdims=True);im=ax.pcolormesh(np.arange(3)-.5,np.arange(3)-.5,norm,cmap='Blues',vmin=0,vmax=1,rasterized=False);ax.set(xlim=(-.5,1.5),ylim=(1.5,-.5),aspect='equal');ax.set_xticks([0,1]);ax.set_yticks([0,1]);ax.set_xticklabels(['Negative','Positive']);ax.set_yticklabels(['Negative','Positive']);ax.set(xlabel='Predicted label (Model A, threshold 0.5)',ylabel='Actual label');ax.tick_params(length=0)
            for i in range(2):
                for j in range(2):ax.text(j,i,f'{cm[i,j]}\n{norm[i,j]*100:.1f}% of row',ha='center',va='center',fontsize=9,color='white' if norm[i,j]>.55 else INK)
            cb=fig.colorbar(im,cax=fig.add_axes([.87,.27,.021,.45]));cb.set_label('Row fraction');metrics.update({'matrix':cm.tolist(),'threshold':.5,'model':'A','normalization':'per true-class row; all 600 objects retained'})
        else:
            for i,name in enumerate(['Model A','Model B']):
                pred=scores[:,i]>=.5;confidence=np.maximum(scores[:,i],1-scores[:,i]);correct=pred==truth;binidx=np.minimum(np.floor(confidence*10).astype(int),9);parts=[]
                for j in range(10):
                    mask=binidx==j
                    if not mask.any():continue
                    parts.append((int(mask.sum()),float(confidence[mask].mean()),float(correct[mask].mean())))
                ece=sum(n/len(truth)*abs(c-a) for n,c,a in parts);ax.plot([c for n,c,a in parts],[a for n,c,a in parts],marker='o',ms=4,color=COLOURS[i],lw=1.2,label=f'{name} · ECE {ece:.3f}');metrics[name]={'ECE':ece,'nonempty_bins':parts}
            ax.plot([.5,1],[.5,1],color=NEUTRAL,lw=.8,ls='--');ax.set(xlabel='Mean predicted-class confidence',ylabel='Accuracy within the same bin',xlim=(.48,1.02),ylim=(.45,1.02));ax.legend(loc='lower right',fontsize=8)
    elif kind=='forest':
        rows=read(root,'effects.csv');e=numeric(rows,['log_ratio']).ravel();se=numeric(rows,['se']).ravel();assert (se>0).all();w=1/se**2;pooled=np.dot(w,e)/w.sum();pse=1/np.sqrt(w.sum());y=np.arange(len(rows),0,-1);lo=np.exp(e-1.96*se);hi=np.exp(e+1.96*se);mid=np.exp(e)
        ax.set_position([.23,.19,.62,.65]);ax.hlines(y,lo,hi,color=COLOURS[0],lw=1.1);ax.scatter(mid,y,s=25+90*w/w.max(),marker='s',c=COLOURS[0]);ax.axvline(1,color=NEUTRAL,lw=.8,ls='--')
        pl,pm,ph=np.exp([pooled-1.96*pse,pooled,pooled+1.96*pse]);ax.add_patch(Polygon([(pl,0),(pm,.22),(ph,0),(pm,-.22)],facecolor=COLOURS[2],edgecolor='none'));ax.set_yticks([*y,0]);ax.set_yticklabels([r['study'] for r in rows]+['Pooled']);ax.set(xscale='log',xlabel='Ratio and normal-approximation 95% CI',ylim=(-.6,7));ax.set_xticks([.5,.75,1,1.5]);ax.set_xticklabels(['0.5','0.75','1','1.5']);ax.margins(x=.1)
        metrics={'log_estimates':e.tolist(),'standard_errors':se.tolist(),'pooled_log_ratio':float(pooled),'pooled_se':float(pse),'pooled_ratio':float(pm),'pooled_CI95':[float(pl),float(ph)],'weight':'fixed-effect inverse variance','uncertainty':'normal 95% CI, +/-1.96 SE; synthetic inputs'}
        ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    elif kind=='attention':
        qr=read(root,'queries.csv');kr=read(root,'keys.csv');cols=list(qr[0])[1:];q=numeric(qr,cols);k=numeric(kr,cols);assert [r['token'] for r in qr]==[r['token'] for r in kr];logits=q@k.T/np.sqrt(q.shape[1]);mask=np.triu(np.ones(logits.shape,dtype=bool),1);logits[mask]=-np.inf;a=softmax(logits,axis=1);assert np.allclose(a.sum(1),1)
        ax.set_position([.22,.19,.59,.65]);im=ax.pcolormesh(np.arange(len(q)+1)-.5,np.arange(len(q)+1)-.5,a,cmap='viridis',vmin=0,vmax=1,rasterized=False);ax.set(xlim=(-.5,len(q)-.5),ylim=(len(q)-.5,-.5),aspect='equal');ax.set_xticks(range(len(q)));ax.set_yticks(range(len(q)));ax.set_xticklabels([r['token'] for r in qr]);ax.set_yticklabels([r['token'] for r in qr]);ax.set(xlabel='Key position',ylabel='Query position');ax.tick_params(length=0)
        for i in range(len(q)):
            for j in range(len(q)):
                if mask[i,j]:ax.add_patch(Rectangle((j-.5,i-.5),1,1,facecolor='#EFF3F5',edgecolor='white',linewidth=.3));continue
                ax.text(j,i,f'{a[i,j]:.2f}',ha='center',va='center',fontsize=8,color=INK if a[i,j]>.5 else 'white')
        cb=fig.colorbar(im,cax=fig.add_axes([.87,.31,.02,.43]));cb.set_label('Attention weight');metrics={'tokens':len(q),'dimensions':q.shape[1],'row_sums':a.sum(1).tolist(),'causal_mask_max':float(a[mask].max()),'formula':'row softmax(QK^T / sqrt(d)), causal upper triangle masked'}
    elif kind=='pareto':
        rows=read(root,'benchmarks.csv');names=sorted({r['model'] for r in rows});means=[];std=[]
        for name in names:
            subset=[r for r in rows if r['model']==name];arr=numeric(subset,['latency_ms','accuracy']);assert len(subset)==5;means.append(arr.mean(0));std.append(arr.std(0,ddof=1))
        means=np.array(means);std=np.array(std);front=np.array([not np.any((means[:,0]<=x)&(means[:,1]>=y)&((means[:,0]<x)|(means[:,1]>y))) for x,y in means]);at=np.where(front)[0];at=at[np.argsort(means[at,0])]
        ax.plot(means[at,0],means[at,1]*100,color=COLOURS[2],lw=.9,ls='--',label='Non-dominated means')
        for i,name in enumerate(names):
            ax.errorbar(means[i,0],means[i,1]*100,xerr=std[i,0],yerr=std[i,1]*100,fmt='o' if front[i] else 's',ms=5,color=COLOURS[2] if front[i] else NEUTRAL,elinewidth=.8,capsize=2)
            ax.annotate(name.replace('Model ','') ,xy=(means[i,0],means[i,1]*100),xytext=(0,23 if i not in [4,6] else -22),textcoords='offset points',ha='center',fontsize=9)
        ax.set(xlabel='Latency (ms; synthetic, no hardware benchmark)',ylabel='Accuracy (%)');ax.margins(x=.1,y=.2);ax.legend(loc='lower right',fontsize=8)
        metrics={'seeds_per_model':5,'means':means.tolist(),'sample_SD':std.tolist(),'frontier_models':[names[i] for i in at],'uncertainty':'mean +/- one sample SD across 5 synthetic seeds'}
    else:raise ValueError(kind)
    return fig,metrics,alignment_axes

def render(kind,inputs,output,qa_scripts=None):
    if any((output/('figure.'+ext)).exists() for ext in ['svg','pdf','png']):
        raise FileExistsError('Use a new output folder; existing exports are not overwritten: '+str(output))
    output.mkdir(parents=True,exist_ok=True)
    apply_figure_style(frame='open',font='DejaVu Sans',sizes=(9,8,8))
    matplotlib.rcParams.update({'font.family':'sans-serif','font.sans-serif':['DejaVu Sans'],'svg.fonttype':'none','svg.hashsalt':'voltpeer-advanced-1.0.2','pdf.fonttype':42,'figure.dpi':150,'savefig.dpi':300,'savefig.bbox':None,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK})
    fig,metrics,axes=draw(kind,inputs)
    # Matplotlib automatically rasterizes long colorbar meshes. Preserve their
    # vector cells too, so the downloadable SVG contains no bitmap fragments.
    for axis in fig.axes:
        for artist in axis.collections:artist.set_rasterized(False)
    fig.canvas.draw()
    geometry=[dict(bounds_fraction=[float(v) for v in ax.get_position().bounds],role='main data or linked axis') for ax in axes]
    alignment={'status':'NOT APPLICABLE' if len(axes)==1 else 'MEASURED','plot_area_bounds_fraction':geometry,'reason':'Only data/linked axes; colourbars, annotation stripes and dendrograms are auxiliary.'}
    if qa_scripts:
        sys.path.insert(0,str(qa_scripts));from audit_panel_alignment import require_matplotlib_panel_alignment
        # Explicit groups for free-positioned linked axes. Auxiliary axes do not
        # encode comparable measurements and are excluded with the reason above.
        panel_ids=[chr(97+i) for i in range(len(axes))]
        alignment=require_matplotlib_panel_alignment(fig,axes=axes,panel_ids=panel_ids,column_groups=[panel_ids] if len(axes)>1 else [],strict=True,json_out=output/'figure.alignment.json')
    fig.savefig(output/'figure.svg',format='svg',metadata={'Date':None})
    fig.savefig(output/'figure.pdf',format='pdf',metadata={'CreationDate':None,'ModDate':None})
    fig.savefig(output/'figure.png',format='png',dpi=300)
    plt.close(fig)
    identity=next(a for a in records() if a['kind']==kind)
    report={'id':identity['id'],'version':identity['version'],'data_scope':identity['data_scope'],'metrics':metrics,'alignment':alignment,'inputs':{n:hashlib.sha256((inputs/n).read_bytes()).hexdigest() for n in identity['files']},'exports':{ext:hashlib.sha256((output/('figure.'+ext)).read_bytes()).hexdigest() for ext in ['svg','pdf','png']},'physical_size_mm':[180,120],'dpi':300,'editable_svg_text':True,'source_figure_reused':False,'library_versions':{'numpy':np.__version__,'matplotlib':matplotlib.__version__}}
    with (output/'render-report.json').open('w',encoding='utf-8',newline='\n') as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',choices=[r['kind'] for r in records()],required=True);p.add_argument('--inputs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--qa-scripts',type=Path);a=p.parse_args();report=render(a.kind,a.inputs,a.output,a.qa_scripts);print(json.dumps({'id':report['id'],'exports':list(report['exports'])}))
