"""Deterministic checks of printed empirical arithmetic; no data-pipeline rerun."""
from pathlib import Path
import json
from math import sqrt

sample = {'E1_firm_years': 1732, 'affected': 457, 'adjusted': 57, 'unverified': 2}
e2 = sample['E1_firm_years'] - sample['affected'] + sample['adjusted'] - sample['unverified']
unaffected = sample['E1_firm_years'] - sample['affected'] - sample['unverified']
assert e2 == 1330
assert unaffected == 1273
assert 203 + 162 + 26 + 9 == 400
assert 270 + 187 == 457
assert 1732 - 1509 == 223
assert 1732 - 1495 == 237
assert 1277 + 455 == 1732
assert 191 + 116 + 148 == 455
assert 647 + 600 == 1247
assert 653 + 619 == 1272

# Cohen kappa implied by 293 descriptions, 49 both-positive and four disputes.
# Unknown distribution of the disputes between the readers is not imputed.
kappas=[]
for a in range(5):
    n=293
    reader_a=49+a
    reader_b=49+4-a
    po=289/n
    pe=(reader_a*reader_b+(n-reader_a)*(n-reader_b))/(n*n)
    kappas.append((po-pe)/(1-pe))

p=.075
se=sqrt(p*(1-p)/999)
result={
    'scope':'Printed-number arithmetic only; not independent reproduction of raw data, code or bootstrap.',
    'random_seed':'Not applicable: no random simulation',
    'sample_flow':{'E2':e2,'unaffected':unaffected},
    'valuation_match_counts':{'matched':1277,'unmatched':455,'total':1732},
    'kappa_range_consistent_with_unknown_dispute_split':[min(kappas),max(kappas)],
    'current_RW_binomial_style_MC_SE':se,
    'current_RW_approximate_MC_band_95':[p-1.96*se,p+1.96*se],
    'interest_income_printed_interval':[-35.9,-2.3],
    'interest_income_printed_interval_contains_zero':-35.9 <= 0 <= -2.3,
    'valuation_point_ratios_from_rounded_coefficients':{'cash':2.81/.58,'GAAP':2.87/.65},
}
(Path(__file__).parent/'empirical_arithmetic.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
