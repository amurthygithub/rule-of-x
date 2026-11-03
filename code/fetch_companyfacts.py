"""Retrieve the SEC XBRL companyfacts extract used in the paper (data/companyfacts_extract.json).

The paper's extract was retrieved on 28-29 October 2026 by running retrieval_browser.js in a web browser
(the author's), because the compute environment could not reach sec.gov. This script implements the same
extraction in Python for replication: for each CIK in data/companyfacts_ciks.txt it downloads
https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json and keeps, for the 35 US-GAAP elements in CON,
every USD fact filed on an annual-report form (FORMS), recording [element index, filing index, start, end, value]
and, per filing, [accession number, filing date, form].

The SEC requires a descriptive User-Agent with contact details and limits request rates (fair-access policy);
pass it as the first argument. Facts filed after the retrieval date will make a new extract differ slightly from
the one distributed with the paper.

Usage: python3 fetch_companyfacts.py "Your Name your.email@example.com"
"""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exclusions import is_excluded  # noqa: E402  registrants excluded at the author's request

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CON = ['Revenues', 'RevenueFromContractWithCustomerExcludingAssessedTax', 'RevenueFromContractWithCustomerIncludingAssessedTax',
       'SalesRevenueNet', 'SalesRevenueServicesNet', 'OperatingIncomeLoss', 'NetCashProvidedByUsedInOperatingActivities',
       'NetCashProvidedByUsedInOperatingActivitiesContinuingOperations', 'PaymentsToAcquirePropertyPlantAndEquipment',
       'PaymentsToAcquireProductiveAssets', 'PaymentsForCapitalImprovements', 'PaymentsToAcquireOtherPropertyPlantAndEquipment',
       'PaymentsForSoftware', 'PaymentsToDevelopSoftware', 'RightOfUseAssetObtainedInExchangeForFinanceLeaseLiability',
       'FinanceLeasePrincipalPayments', 'ShareBasedCompensation', 'AllocatedShareBasedCompensationExpense',
       'SellingAndMarketingExpense', 'SellingGeneralAndAdministrativeExpense', 'GeneralAndAdministrativeExpense', 'GrossProfit',
       'CostOfRevenue', 'CostOfGoodsAndServicesSold', 'DepreciationDepletionAndAmortization', 'DepreciationAndAmortization',
       'Goodwill', 'PropertyPlantAndEquipmentNet', 'PaymentsToAcquireBusinessesNetOfCashAcquired', 'PaymentsToAcquireBusinessesGross',
       'BusinessAcquisitionsProFormaRevenue', 'IncomeLossFromDiscontinuedOperationsNetOfTax',
       'IncomeLossFromDiscontinuedOperationsNetOfTaxAttributableToReportingEntity', 'NetIncomeLoss', 'ResearchAndDevelopmentExpense']
FORMS = {'10-K', '10-K/A', '10-KT', '10-KT/A', '20-F', '20-F/A', '40-F'}


def extract(j):
    g = (j.get('facts') or {}).get('us-gaap') or {}
    acc, accl, out = {}, [], []
    for i, c in enumerate(CON):
        units = (g.get(c) or {}).get('units') or {}
        for f in units.get('USD', []):
            if f.get('form') not in FORMS:
                continue
            a = acc.get(f['accn'])
            if a is None:
                a = len(accl)
                acc[f['accn']] = a
                accl.append([f['accn'], f.get('filed'), f.get('form')])
            out.append([i, a, f.get('start', ''), f['end'], f['val']])
    return {'acc': accl, 'f': out}


def main(user_agent):
    ciks = [int(x) for x in open(f'{BASE}/data/companyfacts_ciks.txt').read().split() if not is_excluded(x)]
    data, errors = {}, []
    for n, cik in enumerate(ciks):
        url = f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json'
        req = urllib.request.Request(url, headers={'User-Agent': user_agent, 'Accept-Encoding': 'identity'})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data[str(cik)] = extract(json.load(r))
        except Exception as e:  # missing filers return 404
            errors.append([cik, str(e)])
        time.sleep(0.15)
        if n % 50 == 0:
            print(f'{n}/{len(ciks)}', file=sys.stderr)
    json.dump(data, open(f'{BASE}/data/companyfacts_extract.json', 'w'))
    print(f'firms: {len(data)}; errors: {len(errors)}; facts: {sum(len(v["f"]) for v in data.values()):,}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
