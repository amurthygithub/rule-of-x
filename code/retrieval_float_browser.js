// Browser retrieval of dei:EntityPublicFloat values from SEC XBRL frames, 3 Nov 2026 (built-in browser on the author's computer).
// Core v3 registrants (CIKs delta-encoded in base 36); registrants whose SHA-256 of the decimal CIK is excluded are dropped.
const enc='1x7.7ksh.7n2f.pa.47g.u6v.8sh.f52.5ng.ddd.2dt.emw.ajq.5va.1jt.1bp.3qf.86d.h0.uv.44n.1xf.3wl.4ns.11.am8.itq.cq.8jz.1n3.15f4.3l.13e.5st.1ju.1wc.5n.2qi.8z9.3rk.ark.524.4gm.17y.1im.38x.wo.1hu.h6.4qc.1vf.1px.1q.cv.199.sh.2r.3lm.10a.zq.4dq.1k8.274.ul.p1.ix.b4.1av.84.l6.2cp.1ug.2xs.14y.e5.1bl.7eh.kn0.2at.4cd.2j.9s1.w9c.ai5.cv5.5c2.eg5.4rb.dg3.19m.7kc.525.6dk.dy.5ab.2h0.qr.539.2i9.9r.19r.1wn.44v.2yx.17h.y.4o3.un.qx.o9.7ye.5jl.6no.hd.3n.1pn.nk.3rl.1a3.4o9.16d.it.f8.298.3rz.2o8.ti.37h.fx.2we.3p.2ox.1to.ar.xy.3i0.3rm.e0.61.21b.4an.sz.13t.579.dp.ar.7zn.1ek.cj.1u.6w.4v3.3to.2hw.m5.2iv.l7.gv.1ls.1cf.2a7.i.k.6l.3ru.4io.e3.ab.4pl.44.418.2ft.gu.6ac.2om.383.xz.ey.2rz.1v1.yl.3p2.1ki.kp.h0.1tc.2e8.k6.5lb.kn.2eb.2jt.3s9.3bb.1f5.12d.1x.cj.33f.2tx.5bx.mh.b7.4h.nf.8gp.ox.bs.2eq.132.4e9.x2.1hc.54s.42.45e.d8.1ir.69x.2ro.7sh.7nf.xe.j8.4n9.aya.203.s.dj.2sv.4nm.410.2x3.33r.d95.2ku.11t.2wb.zw.2i6.175.2yr.2cb.21j.3lk.no.4qw.1pk.24w.wy.329.5pf.x5.3gk.q0.1qt.f.1kc.23m.21k.6.ok.8f.45.3p.sa.1wa.1tp.2he.8s.1qe.2mz.1ni.142.1bz.1hz.2qa.7l.st.2in.7d.1n.1ly.3q.3vz.9zj.2d2.9ux.5pq.q1p.18v9.m68.p0f';
const ciks=[]; let a=0; for(const x of enc.split('.')){a+=parseInt(x,36); ciks.push(a);}
const EXCLUDED=new Set(['98a09ebecd587b52c233f1dda385c92194cf862e9caf6d436716baddf1c022f3']);
async function sha(s){const b=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(s));return Array.from(new Uint8Array(b),x=>x.toString(16).padStart(2,'0')).join('');}
const keep=new Set(); for(const c of ciks){ if(!EXCLUDED.has(await sha(String(c)))) keep.add(c); }
const periods=[]; for(let y=2010;y<=2026;y++) for(let q=1;q<=4;q++){ if(y===2026&&q>3) break; periods.push(`CY${y}Q${q}I`); }
window.__PF={done:false,rows:[],err:[],bytes:0,count:0,total:periods.length,ciks:keep.size};
(async()=>{ const sleep=ms=>new Promise(r=>setTimeout(r,ms)); let k=0;
 async function worker(){ while(k<periods.length){ const p=periods[k++];
   try{ const r=await fetch(`https://data.sec.gov/api/xbrl/frames/dei/EntityPublicFloat/USD/${p}.json`);
     if(r.status!==200){window.__PF.err.push([p,r.status]);} else { const t=await r.text(); window.__PF.bytes+=t.length; const j=JSON.parse(t);
       for(const d of (j.data||[])){ if(keep.has(d.cik)) window.__PF.rows.push([d.cik,d.end,d.val,d.accn,p]); } } }
   catch(e){window.__PF.err.push([p,String(e)]);}
   window.__PF.count++; await sleep(200); } }
 await Promise.all([worker(),worker(),worker()]); window.__PF.done=true; })();
'started '+periods.length+' frames for '+keep.size+' registrants'
