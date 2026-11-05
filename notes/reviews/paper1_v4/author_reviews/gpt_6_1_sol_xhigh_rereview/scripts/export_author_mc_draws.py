"""Export the author's exact LHS CSV without rerunning searches/Sobol analyses.

Uses the unchanged author Runner on a reproduction copy; all writes are under
--out. This wrapper is a convenience, not an alternative mathematical model.
It has NOT been run on the million-draw case merely by being included here.
"""
import argparse
from pathlib import Path
import sys, time, gzip, shutil, json, hashlib, platform
sys.dont_write_bytecode = True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--repo',required=True,type=Path,help='Reproduction copy containing code/mc_claims.py and required inputs')
    ap.add_argument('--out',required=True,type=Path,help='New output folder outside the baseline snapshot')
    ap.add_argument('--workers',type=int,default=11)
    ap.add_argument('--n',type=int,default=1000000)
    ap.add_argument('--seed',type=int,default=20261102)
    a=ap.parse_args()
    repo,out=a.repo.resolve(),a.out.resolve()
    if out==repo or repo in out.parents:
        raise SystemExit('--out must be outside the baseline/reproduction repository to keep it untouched')
    sys.path.insert(0,str(repo/'code'))
    import mc_claims as mc
    argv=['--n',str(a.n),'--seed',str(a.seed),'--workers',str(a.workers),
          '--chunk','200','--corners','100000','--sobol-n','65536',
          '--amin-n','100000','--search-budget','6000','--out',str(out)]
    args=mc.parse_args(argv)
    run=mc.Runner(args)
    t=time.perf_counter()
    run.setup()
    run.start_pool(max(1,a.workers))
    try:
        run.run_draws()
        csv=out/'draws_lhs.csv'
        run.write_draws_csv(str(csv))
    finally:
        run.stop_pool()
    gz=out/'draws_lhs.csv.gz'
    with open(csv,'rb') as src,open(gz,'wb') as target:
        with gzip.GzipFile(filename='',fileobj=target,mode='wb',mtime=0) as dst:
            shutil.copyfileobj(src,dst)
    result={'scope':'Author Runner LHS/corner phase and exact CSV export only. Searches, Sobol, sub-box and report not rerun.',
            'n_lhs':a.n,'n_corners':len(run.U)-run.n_lhs,'seed':a.seed,'author_config_hash':run.cfg,
            'elapsed_s':time.perf_counter()-t,'python':platform.python_version(),
            'argv':argv,'author_script_sha256':hashlib.sha256((repo/'code/mc_claims.py').read_bytes()).hexdigest(),
            'csv_sha256':hashlib.sha256(csv.read_bytes()).hexdigest(),
            'gzip_sha256':hashlib.sha256(gz.read_bytes()).hexdigest(),
            'gzip_note':'mtime=0; compressed bytes may differ from an author gzip even when CSV content matches.',
            'outputs':[str(csv),str(gz)]}
    (out/'export_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    main()
