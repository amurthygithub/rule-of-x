#!/usr/bin/env bash
# Rebuild every Part II data contract file. Re-run after new raw files land in data/raw/.
set -euo pipefail
cd "$(dirname "$0")"
for s in 00_onet_mysql_to_csv.py 01_functions.py 02_occupations.py 03_activities.py 04_industry_staffing.py 05_function_priors.py \
         07_processes.py 08_params.py \
         11_nonsoftware_priors.py 12_task_statements.py 09_checksums.py 10_validate.py; do
  echo "== $s"; python3 -I "$s"
done
# 11_nonsoftware_priors.py must run after 05_function_priors.py, which rewrites industry_function_shares.csv
# with the software rows only; 11 re-appends the non-software rows and leaves the software rows unchanged.
# 06_capability.py (METR refit, about 3 minutes with the bootstrap) only needs re-running if the METR clone changes:
#   python3 -I 06_capability.py && python3 -I 08_params.py
