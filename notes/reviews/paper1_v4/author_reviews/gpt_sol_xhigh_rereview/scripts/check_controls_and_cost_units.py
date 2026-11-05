"""Deterministic checks of printed control examples and source unit conversion.
No repository code or data are used. Seed: not applicable.
"""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
N=24
human=lambda n: .002+.998*.05**n
ai=lambda n: .005+.995*.02**n
annual=lambda p: 1-(1-p)**N
out={"seed":None,"scope":"Independent deterministic printed-formula checks, not repository reproduction", "control":{
"three_human_annual_escape":annual(human(3)),
"one_human_one_AI_annual_escape":annual(human(1)*ai(1)),
"one_human_two_AI_annual_escape":annual(human(1)*ai(2)),
"three_AI_independent_opportunities_annual_escape":annual(ai(3)),
"three_AI_period_persistent_common_mode_escape":.005+.995*annual(.02**3),
"per_objective_threshold_for_ten_independent_objectives_at_firm_five_percent":1-.95**.1},
"epoch_source_units":{"upfront_servers_USDm":21188,"annualized_servers_USDm":5021,"annual_total_TCO_USDm":8514,
"source_implied_server_CRF":5021/21188,"source_implied_server_K_over_economic_TCO":21188/8514,
"paper_implied_K_over_TCO":.6*5.5,"paper_implied_server_K_USDm":.6*5.5*8514,
"cash_replacement_at_paper_5point5yr_life_USDm":21188/5.5,
"cash_replacement_share_of_source_economic_TCO_at_5point5yr_life":21188/5.5/8514},
"acquisition_case":{"revenue_2024_USD_thousand":671053,"revenue_2025_USD_thousand":1306404,
"CFO_2025_USD_thousand":290600,"SBC_2025_USD_thousand":55523,"PPE_cash_2025_USD_thousand":501,
"simple_growth_2025_percent":100*(1306404/671053-1),
"panel_basis_cash_score_2025":100*(1306404/671053-1+(290600-55523-501)/1306404),
"SBC_share_2024_percent":100*25855/671053,"SBC_share_2025_percent":100*55523/1306404},
"successful_run_cost_identity":"expected total cost per success = c_success + ((1-p)/p)*c_failure"}
(root/'results'/'controls_cost_units.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
