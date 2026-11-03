"""params.yaml: engine parameters with central values, ranges, sources and source-quality flags.

Convention for every leaf parameter block:
  value: central value used by default
  range: [low, high] for sensitivity and Monte Carlo
  quality: one of
    peer_reviewed            journal article or peer-reviewed conference paper
    working_paper            research working paper (NBER, Census CES, arXiv preprint) not yet refereed
    government               statute, regulation or official statistics
    company_filing           SEC filing (read directly or through a named secondary summary)
    vendor_price_list        published list price
    vendor_documentation     vendor's own published policy or documentation page (dated), e.g. model-deprecation policy
    company_statement        a company's own press release about its results; not audited or independently verified
    primary_data_fit         fitted by our script from a primary dataset (script named)
    practitioner_survey_disclosed     consultancy or vendor survey with sample and method stated
    practitioner_survey_undisclosed   consultancy or vendor survey without enough method to judge
    practitioner_dataset_disclosed    practitioner count of events in a stated population (e.g. index constituents), not a survey
    prediction               analyst forecast, not a measurement
    secondary                figure taken from a summary of a primary source we could not open
    assumed                  our assumption (assumed: true)
  source: short citation; full entries, URLs and retrieval dates are in notes/data_sources_part2.md
  assumed: true whenever the value is not taken from a source
  grounding: spec Section 21.1 class (added by the assumptions audit, 29 Oct 2026):
    a  sourced (peer-reviewed, government, standards body, audited or regulatory filing, practitioner data with a stated method)
    b  grounded by stated precedent: an analogous documented estimate, analogy stated in `analogy`, range widened
    c  calibrated from our own data (SEC panel, O*NET, BLS, AEI, METR runs) by a named script
    d  free scenario parameter: a scenario dimension only, never a baseline point estimate; claims that use it are conditional
    ref  a recorded reference, rejection or absence that the engine does not use as a value
  Blocks without an explicit `grounding` get one from their quality flag in set_grounding() at the end of this script;
  every class set by hand is justified in notes/assumptions_register.md.

Round 2 of Paper 1 (2 Nov 2026). The round-2 edits were first made by hand in data/tasks/params.yaml (notes/r2_propagation.md
items 1, 2, 4 and 5; notes/r2_code_changes.md B1, B2, B9, C3) and were ported into this script afterwards (Follow-up 5,
notes/r2_code_changes.md), so that this script again reproduces the committed params.yaml byte for byte. Strings whose
hand-set line breaks differ from the emitter's wrapping are written as Hand(...) with their lines as they stand in the file.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # this folder (python3 -I does not add it), also in a scratch copy
import datetime
import math
import re
import yaml
from common import BASE, load_meta

cap = load_meta('capability')
TODAY = '2026-10-29'
R2_READ = '2026-11-02'   # read date of the sources added in round 2 of Paper 1 (KPMG by revenue size, accelerated-filer fee)


def P(value, rng, quality, source, unit=None, note=None, assumed=None):
    d = {'value': value, 'range': rng, 'quality': quality, 'source': source}
    if unit:
        d['unit'] = unit
    if note:
        d['note'] = note
    d['assumed'] = bool(assumed) if assumed is not None else (quality == 'assumed')
    return d


def r(x, n=4):
    return float(round(x, n))


class Hand(str):
    """A string whose line breaks in params.yaml were set by hand (round-2 edits of 2 Nov 2026, made in the file).

    The value is the lines joined by single spaces, which is exactly what YAML line folding loads from the file. _Dumper
    writes the lines as given instead of re-wrapping them at the emitter's width, so the build reproduces the committed
    file byte for byte. quoted=True keeps the single-quoted style of a hand edit where the emitter would choose plain style.
    Lines hold the value's text: a quote inside a single-quoted line is written once here and doubled by the dumper.
    """
    def __new__(cls, *lines, quoted=False):
        self = super().__new__(cls, ' '.join(lines))
        self.lines, self.style = lines, ("'" if quoted else None)
        return self


class _Dumper(yaml.SafeDumper):
    """yaml.SafeDumper, except that a Hand string is written line by line (plain or single-quoted style)."""
    def write_plain(self, text, split=True):
        if not (isinstance(text, Hand) and split):
            return super().write_plain(text, split)
        for i, line in enumerate(text.lines):
            if i:
                self.write_indent()
            super().write_plain(line, split=False)

    def write_single_quoted(self, text, split=True):
        if not (isinstance(text, Hand) and split):
            return super().write_single_quoted(text, split)
        self.write_indicator("'", True)
        for i, line in enumerate(text.lines):
            if i:
                self.write_indent()
            data = line.replace("'", "''")
            self.column += len(data)
            self.stream.write(data.encode(self.encoding) if self.encoding else data)
        self.write_indicator("'", False)


_Dumper.add_representer(Hand, lambda dumper, s: dumper.represent_scalar('tag:yaml.org,2002:str', s, style=s.style))


# ------------------------------------------------------------------ payroll loading (BLS ECEC, June 2026)
ECEC = {  # $ per hour worked: total compensation, wages and salaries, paid leave (Tables 1 and 4, release of 9 Sep 2026)
    'private_industry': (46.89, 32.82, 3.54),
    'civilian': (49.46, 33.85, 3.71),
    'management_professional_private': (78.88, 54.06, 7.37),
    'professional_business_services_private': (59.80, 41.55, 5.20),
    'information_private': (84.28, 54.46, 8.63),
}
load_hw = {k: r(t / w - 1) for k, (t, w, l) in ECEC.items()}
load_aw = {k: r((t - w - l) / (w + l)) for k, (t, w, l) in ECEC.items()}
hours = {k: r(2080 / (1 + l / w), 1) for k, (t, w, l) in ECEC.items()}
ecec_src = 'BLS, Employer Costs for Employee Compensation, June 2026 (news release USDL, 9 Sep 2026), Tables 1 and 4'

# ------------------------------------------------------------------ list prices and inference cost per human-hour
PRICES = {  # USD per million tokens: input, output, cache hit; platform.claude.com pricing page, retrieved 2026-10-29
    'frontier_tier (Claude Mythos 5.1 / Fable 5.1)': (10.0, 50.0, 0.25),
    'claude_opus_5_5': (4.0, 20.0, 0.20),
    'claude_sonnet_5_5': (2.0, 10.0, 0.10),
    'claude_haiku_5_5 (prompts up to 100k tokens)': (0.10, 0.50, 0.01),
}
MIX = dict(input_share=0.90, cache_hit_share_of_input=0.80, output_share=0.10)


def blended(i, o, c):
    inp = (1 - MIX['cache_hit_share_of_input']) * i + MIX['cache_hit_share_of_input'] * c
    return MIX['input_share'] * inp + MIX['output_share'] * o


import numpy as np
import pandas as pd
from common import METR, read_sec_panel
_runs = pd.read_json(f'{METR}/reports/time-horizon-1-1/data/raw/runs.jsonl', lines=True)
FRONTIER = ['Claude Opus 4.6 (Inspect)', 'Claude Opus 4.5 (Inspect)', 'GPT-5.2', 'GPT-5.3-Codex', 'Gemini 3 Pro', 'GPT-5 (Inspect)']
_fr = _runs[_runs.alias.isin(FRONTIER) & (_runs.tokens_count > 0)].copy()
_ok = _fr[_fr.score_binarized == 1]
tok_hr = float((_ok.tokens_count / (_ok.human_minutes / 60)).median() / 1e6)   # million tokens per human-hour
_fr['bin'] = pd.cut(_fr.human_minutes, [0, 1, 4, 16, 64, 256, 960, 3000])
_g = _fr.groupby('bin', observed=True).agg(t=('tokens_count', 'median'), m=('human_minutes', 'median'))
tok_bins = (_g.t / (_g.m / 60) / 1e6)
tok_rng = [r(tok_bins.min(), 3), r(tok_bins.max(), 3)]
tok_elast = float(np.polyfit(np.log(_fr.human_minutes), np.log(_fr.tokens_count), 1)[0])
blend = {k: r(blended(*v)) for k, v in PRICES.items()}
cost_hr = {k: r(v * tok_hr, 3) for k, v in blend.items()}

# METR Time Horizon 1.0 runs record generation_cost (USD) for most agents: observed inference cost per human-hour of task,
# with no assumed token mix (assumptions audit, 29 Oct 2026). Successful runs only, as for tokens_per_human_hour.
_r10 = pd.read_json(f'{METR}/reports/time-horizon-1-0/data/raw/runs.jsonl', lines=True)
_g10 = _r10[(_r10.generation_cost > 0) & (_r10.score_binarized == 1)].copy()
_g10['cph'] = _g10.generation_cost / (_g10.human_minutes / 60)
_g10['ratio'] = _g10.generation_cost / _g10.human_cost
_g10['ppm'] = _g10.generation_cost / _g10.tokens_count * 1e6
OBS_AGENTS = ['Claude Opus 4.5', 'Claude 4.1 Opus', 'Claude Sonnet 4.5', 'GPT-5', 'o3', 'Gemini 2.5 Pro Preview']
obs = {a: dict(n_successful_runs=int(len(d)), usd_per_human_hour_median=r(d.cph.median(), 3),
               usd_per_human_hour_iqr=[r(d.cph.quantile(.25), 3), r(d.cph.quantile(.75), 3)],
               share_of_human_baseline_cost_median=r(d.ratio.median(), 5),
               effective_usd_per_mtok_median=(r(d.ppm.median(), 2) if d.ppm.notna().any() else None))
       for a, d in _g10[_g10.alias.isin(OBS_AGENTS)].groupby('alias')}
LIST_OLD = {'Claude Opus 4.5': (5.0, 25.0), 'Claude 4.1 Opus': (15.0, 75.0)}   # same pricing page as PRICES (see list_prices note)
out_share_obs = {a: r((obs[a]['effective_usd_per_mtok_median'] - i) / (o - i), 3) for a, (i, o) in LIST_OLD.items()}
ANCHOR = 'Claude Opus 4.5'          # most recent agent with recorded cost; its list price has the same 1:5 input:output ratio as every current tier
cph_anchor = obs[ANCHOR]['usd_per_human_hour_median']
iqr_mult = [r(obs[ANCHOR]['usd_per_human_hour_iqr'][0] / cph_anchor, 3), r(obs[ANCHOR]['usd_per_human_hour_iqr'][1] / cph_anchor, 3)]
cost_hr_obs = {k: r(cph_anchor * v[0] / LIST_OLD[ANCHOR][0], 3) for k, v in PRICES.items()}

tr = cap['trend']
front = cap['frontier']
chi = {k: r(v, 2) for k, v in cap['chi_reliability_factor'].items()}

params = {
    'meta': {
        'version': '1.0', 'built': TODAY, 'built_by': 'code/data_part2/08_params.py',
        'conventions': 'value = default; range = [low, high]; quality flag as listed in the script docstring; '
                       'assumed: true when not sourced. Monetary values in 2026 USD unless stated.',
        'source_log': 'notes/data_sources_part2.md',
    },

    # ============================================================== labour cost
    'payroll_loading': {
        'tau_L_per_hour_worked': P(load_hw['private_industry'], [load_hw['private_industry'], load_hw['information_private']],
                                   'government', ecec_src,
                                   note='(total compensation / wages and salaries) - 1, per hour worked. Use when t is measured in '
                                        'hours worked and w is the OEWS hourly rate (annual / 2080). Range spans private industry '
                                        'to the information industry.'),
        'tau_L_on_annual_wage': P(load_aw['private_industry'], [load_aw['professional_business_services_private'], load_aw['information_private']],
                                  'government', ecec_src,
                                  note='(total compensation - wages - paid leave) / (wages + paid leave): loading on an OEWS annual '
                                       'wage, which already pays for leave. Annual FTE cost = OEWS annual wage x (1 + this).'),
        'worked_hours_per_fte_year': P(hours['private_industry'], [hours['information_private'], hours['private_industry']],
                                       'government', ecec_src,
                                       note='2080 paid hours / (1 + paid leave per hour worked / wages per hour worked).'),
        'by_group': {k: {'tau_L_per_hour_worked': load_hw[k], 'tau_L_on_annual_wage': load_aw[k],
                         'worked_hours_per_fte_year': hours[k],
                         'ecec_usd_per_hour_worked': dict(total=ECEC[k][0], wages=ECEC[k][1], paid_leave=ECEC[k][2])}
                     for k in ECEC},
    },

    # ============================================================== capability path (Section 6)
    'capability_path': {
        'H0_hours_p50': P(r(front['p50_hours'], 2), [r(front['p50_hours'] * 0.75, 2), r(front['p50_hours'] * 1.25, 2)],
                          'primary_data_fit',
                          'METR Time Horizon 1.1 run data (github.com/METR/eval-analysis-public), refit by 06_capability.py',
                          unit='human hours at 50% success',
                          note=f"frontier agent {front['agent']}; METR reports measurements above 16 h as unreliable with the "
                               'current task suite. Software tasks only.'),
        'H0_hours_p80': P(r(front['p80_hours'], 2), [r(front['p80_hours'] * 0.75, 2), r(front['p80_hours'] * 1.25, 2)],
                          'primary_data_fit', 'as H0_hours_p50', unit='human hours at 80% success'),
        't0': P(front['release_date'], None, 'primary_data_fit', 'release date of the frontier agent, METR release_dates.yaml'),
        'T_d_days': P(143, [102, 240], 'peer_reviewed',
                      'Kwa et al. (2025), Measuring AI Ability to Complete Long Software Tasks, arXiv:2503.14499, NeurIPS 2025: '
                      '207 days (95% CI 166-240) for 2019-2025, 143 days for 2024-onward models',
                      unit='days per doubling of the 50% horizon',
                      note='Default 143 (published, 2024-onward). Our refits, reported alongside: '
                           f"TH1.0 data 2019+ {r(cap['th10_point_estimates']['2019-01-01']['doubling_days'], 1)} d, "
                           f"TH1.0 2024+ {r(cap['th10_point_estimates']['2024-01-01']['doubling_days'], 1)} d; "
                           f"TH1.1 data 2023+ {r(tr['2023-01-01']['doubling_days'], 1)} d (95% CI {r(tr['2023-01-01']['ci95'][0], 1)}-{r(tr['2023-01-01']['ci95'][1], 1)}), "
                           f"TH1.1 2024+ {r(tr['2024-01-01']['doubling_days'], 1)} d (95% CI {r(tr['2024-01-01']['ci95'][0], 1)}-{r(tr['2024-01-01']['ci95'][1], 1)}). "
                           'Low end of range = fastest refit; high end = upper CI of the published long-run estimate.'),
        'T_d_scenarios_days': {'slow': 207, 'base': 143, 'fast': r(tr['2024-01-01']['doubling_days'], 0),
                               'source': 'slow and base published (Kwa et al. 2025); fast = TH1.1 2024+ refit'},
        'logistic_slope_b': P(r(cap['logistic_slope_median_2025plus'], 3), [0.41, 0.69], 'primary_data_fit',
                              'METR TH1.1 refit: |coefficient| of success on log2(human minutes), median over agents released 2025+',
                              note='P(success | task length d) = 1 / (1 + (d / H50)^b). Range = min and max over those agents.'),
        'chi_reliability_factor': {
            'value': chi, 'quality': 'primary_data_fit', 'assumed': False,
            'source': 'derived from logistic_slope_b: H50 / H_r = 2^(logit(r) / b)',
            'note': 'Anchored empirically at r = 0.8 (Kwa et al. report 80% horizons 4-6x shorter; our refit 5.0). Values '
                    'above 0.8 extrapolate the logistic form and are not validated by METR data.'},
        'domain_transfer_factor': dict(P(1.0, [0.5, 9.5], 'practitioner_dataset_disclosed',
                                    'Anthropic Economic Index report, 15 Jan 2026 (anthropic.com/research/economic-index-primitives, re-read '
                                    '29 Oct 2026): Claude "50% successful at tasks that take ... around 3.5 hours" on the API and "around 19 '
                                    'hours" on Claude.ai, for Claude Sonnet 4.5, which METR measures at 50% success on 2-hour tasks; the '
                                    'report says its method differs from METR\'s (user-guided task breakdown, selection)',
                                    note='multiplies H for non-software or in-product tasks. Upper bound 19/2 = 9.5 (Claude.ai), API 3.5/2 = 1.75; '
                                         'Kwa et al. (2025) find lower success on messier tasks, so values below 1 are allowed. Central 1 '
                                         'lies between the API ratio (biased up by user selection) and the messiness penalty.', assumed=False),
                                       grounding='b', analogy='user-guided Claude tasks (API and Claude.ai) relative to METR software tasks '
                                                             'for the same model; transfer to enterprise processes is the stated analogy',
                                       conditional='the range spans log2(19) = 4.2 horizon doublings (1.6 to 2.4 years at T_d = 143 to 207 '
                                                   'days), so feasibility dates must be reported over the range'),
        'physical_lag_years': dict(P(5, [2, 10], 'assumed', 'assumed: lag before world models make physical activities feasible'),
                                   grounding='d', note='no credible estimate of a world-model lag exists; scenario dimension'),
        'context_engine_multiplier_kappa_ctx': dict(P(1.0, [1.0, 3.0], 'assumed',
                                                 'assumed: multiplier on effective horizon from organisational context engines'),
                                                    grounding='d'),
    },

    # ============================================================== inference prices and energy (Section 6)
    'inference_price': {
        'decline_factor_per_year_fixed_capability': P(10, [5, 40], 'peer_reviewed',
                                                      'Gundlach et al. (2025) arXiv:2511.23455: 5-10x a year at fixed benchmark performance; '
                                                      'Cottier et al. (2025), Epoch AI: 9-900x a year by threshold, 40x for GPT-4-level GPQA',
                                                      note='delta_pi = ln(factor) per year (continuous). Extreme range for stress tests: [5, 900]. '
                                                           'Gundlach is a working paper (arXiv); Epoch is a data insight. Applies at fixed task '
                                                           'difficulty only.'),
        'delta_pi_continuous': P(r(math.log(10), 3), [r(math.log(5), 3), r(math.log(40), 3)], 'peer_reviewed', 'ln of the factor above'),
        'frontier_price_change_factor_per_year': P(1.0, [1.0, 18.0], 'working_paper',
                                                   'Gundlach et al. (2025): the price of running frontier models rises 3-18x a year',
                                                   note='for activities that need the current frontier model; default 1 (flat) because list '
                                                        'prices of a given tier have fallen (see list_prices).', assumed=True),
        'list_prices_usd_per_mtok': {
            'value': {k: dict(input=v[0], output=v[1], cache_hit=v[2]) for k, v in PRICES.items()},
            'quality': 'vendor_price_list', 'assumed': False,
            'source': f'Anthropic, Claude API pricing, platform.claude.com/docs/en/about-claude/pricing, retrieved {TODAY}',
            'note': 'Batch API: 50% discount on input and output. Same page lists Opus 4.1 at $15/$75 and Opus 4.5 at $5/$25.'},
    },
    'energy_share_s_E': P(0.07, [0.02, 0.10], 'secondary',
                          'Michael and Cottier (2026), Epoch AI data insight: energy about 7% of annualised TCO of a 1 GW AI data '
                          'center (servers 60%); Cottier et al. (2024) arXiv:2405.21015: energy 9% of amortised hardware plus energy, '
                          '2-6% of total model development cost',
                          note='share of compute cost, not of API price (prices include margins, so the share of price is lower).'),

    # ============================================================== AI mode cost (Section 3)
    'ai_cost': {
        'tokens_per_human_hour_mtok': P(r(tok_hr), tok_rng, 'primary_data_fit',
                                        'METR TH1.1 runs, frontier agents (Opus 4.5/4.6, GPT-5/5.2/5.3-Codex, Gemini 3 Pro): median '
                                        'tokens_count per human-hour, successful runs; range = medians by task-length bin',
                                        note=f'tokens scale with task length with elasticity {r(tok_elast, 2)}. METR does not state whether tokens_count '
                                             'includes cached input; software tasks only.'),
        'token_mix_assumed': {'value': MIX, 'quality': 'assumed', 'assumed': True, 'grounding': 'd',
                              'source': 'assumed agentic workload mix; cross-check only since the audit of 29 Oct 2026',
                              'range': 'cache_hit_share 0.0-0.95; output_share 0.05-0.25',
                              'metr_observed': {'output_share_no_cache': out_share_obs, 'cache_hit_share': 0.0,
                                                'basis': 'effective USD per Mtok in METR TH1.0 runs, (p_eff - p_in)/(p_out - p_in) at the '
                                                         'list prices of Claude Opus 4.5 ($5/$25) and Opus 4.1 ($15/$75); an effective price '
                                                         'above the input price means METR priced runs without cache discounts'},
                              'note': 'output_share 0.10 is consistent with METR (0.075-0.09, class c); the 0.80 cache-hit share is a '
                                      'deployment scenario with no measured source and halves the cost relative to METR\'s observed cost'},
        'blended_price_usd_per_mtok': {'value': blend, 'quality': 'assumed', 'assumed': True, 'grounding': 'd',
                                       'source': 'list prices x assumed token mix (cross-check)'},
        'inference_cost_usd_per_human_hour': {
            'value': cost_hr_obs, 'range_multiplier': [0.3, 3.0], 'quality': 'primary_data_fit', 'assumed': False, 'grounding': 'c',
            'source': f'METR Time Horizon 1.0 runs (github.com/METR/eval-analysis-public, reports/time-horizon-1-0/data/raw/runs.jsonl): '
                      f'recorded generation_cost / task human-hours, successful runs, {ANCHOR} median ${cph_anchor}/h '
                      f'(IQR {obs[ANCHOR]["usd_per_human_hour_iqr"]}) at its list price $5/$25 per Mtok, scaled to each current tier by '
                      f'input list price (every tier has the same 1:5 input:output price ratio); built by 08_params.py',
            'note': 'pi*n per activity-hour for cognitive digital work within the capability horizon; multiply by 1/success probability '
                    f'for retries. IQR multiplier {iqr_mult}, widened to [0.3, 3.0]. Observed cost for other agents: '
                    + '; '.join(f"{a} ${v['usd_per_human_hour_median']}/h" for a, v in obs.items()) +
                    f'. Cross-check (former default, assumed): tokens_per_human_hour x blended price under the assumed mix = {cost_hr}. '
                    'METR software tasks only; agent scaffolds, not production deployments.',
            'metr_observed_by_agent': obs},
        'activity_class_multiplier': {
            'value': {'information_input (GWA 4.A.1)': 0.5, 'mental_processes (4.A.2)': 1.0, 'digital_work_output (4.A.3.b)': 1.0,
                      'interacting_with_others (4.A.4)': 1.5, 'physical_work_output (4.A.3.a)': None},
            'range': [0.3, 3.0], 'quality': 'assumed', 'assumed': True, 'grounding': 'd',
            'source': 'assumed multipliers on inference_cost_usd_per_human_hour by GWA class; physical work uses capital (capital_per_unit)'},
        'review_fraction_psi_A': {
            'value': {'readiness_high_low_stakes': 0.05, 'readiness_high_high_stakes': 0.25, 'readiness_low_low_stakes': r(1 / 1.74, 3),
                      'readiness_low_high_stakes': 1.0},
            'range': {'readiness_high_low_stakes': [0.0, 0.10], 'readiness_high_high_stakes': [0.10, 0.60],
                      'readiness_low_low_stakes': [0.37, 0.91], 'readiness_low_high_stakes': [0.60, 1.20]},
            'quality': 'peer_reviewed', 'assumed': False, 'grounding': 'b',
            'source': 'full-review cells: machine-translation post-editing, the longest-studied case of people correcting machine drafts. '
                      'Plitt and Masselot (2010), Prague Bulletin of Mathematical Linguistics 93 (ufal.mff.cuni.cz/pbml/93/'
                      'art-plitt-masselot.pdf): 12 translators, 4 languages, throughput +74% on average (time ratio 1/1.74 = 0.575), '
                      'individual gains 20-131%; Ahsan, Mujadia and Sharma (2021, arXiv:2112.09841) review: time savings 15-20% '
                      '(Laubli et al. 2013), 9-60% (Laubli et al. 2019), 63% (their English-Hindi study), slowdowns of 3-5x with poor '
                      'MT (Shah et al. 2015). High-stakes cell: Agarwal, Moehring, Rajpurkar and Salz (NBER w31422; MIT copy read): '
                      '180 radiologists, AI predictions add about 4% to time per case (human still does the whole task, ratio 1.04); '
                      'Becker et al. (2025) +19%',
            'analogy': 'reviewing and correcting an AI draft of a digital work product, as translators post-edit MT output',
            'note': 'share of in-house human time w t spent reviewing and correcting AI output. Full-review cells (low readiness) are '
                    'class b; the partial-review cells (high readiness: sampled review) have no measured source and are class d. '
                    'Values above 1 are possible (Becker et al. 2025; Shah et al. 2015 via Ahsan et al.).',
            'cell_grounding': {'readiness_high_low_stakes': 'd', 'readiness_high_high_stakes': 'd', 'readiness_low_low_stakes': 'b',
                               'readiness_low_high_stakes': 'b'}},
        'review_time_ratio_rho_rev': dict(P(r(1 / 1.74, 3), [0.37, 1.19], 'peer_reviewed',
                                            'Plitt and Masselot (2010): post-editing raised throughput 74% (time ratio 0.575); range: '
                                            'lowest time ratio in the post-editing studies reviewed by Ahsan et al. (2021), 0.37, to '
                                            'Becker et al. (2025, arXiv:2507.09089), 1.19 (AI slowed experienced developers by 19%)',
                                            unit='review-and-correct hours per hour of doing the unit unaided',
                                            note='for the engine key review.rho_rev (t_R / t), today 0.8 [0.3, 1.2] unlinked; added by the '
                                                 'assumptions audit, 29 Oct 2026'),
                                          grounding='b', analogy='as review_fraction_psi_A'),
        'raw_error_rate_e': {
            'full_readiness_e1': dict(P(0.033, [0.01, 0.14], 'practitioner_dataset_disclosed',
                                        'Vectara, next-generation hallucination leaderboard (blog, 19 Nov 2025; vectara.com/blog/'
                                        'introducing-the-next-generation-of-vectaras-hallucination-leaderboard): summaries of 7,700+ '
                                        'supplied articles (up to 32k tokens) scored by the HHEM model; best model 3.3%, Gemini-3-pro '
                                        '13.6%, Claude Sonnet 4.5 and GPT-5 above 10%',
                                        note='grounded summarization is the closest measured analog of full readiness (all inputs '
                                             'supplied). HHEM is the vendor\'s own classifier; the dataset is not public (flag). '
                                             'For the engine key capability.e1, today 0.01 [0.005, 0.03] unlinked'),
                                      grounding='b', analogy='answering from fully supplied, machine-readable inputs'),
            'low_readiness_e0': dict(P(0.25, [0.10, 0.45], 'peer_reviewed',
                                       'Magesh, Surani, Dahl, Suzgun, Manning and Ho (2025), Hallucination-Free? Assessing the Reliability '
                                       'of Leading AI Legal Research Tools, Journal of Empirical Legal Studies 22(2), 216-242, doi:10.1111/'
                                       'jels.12413: preregistered test; retrieval-based legal research tools "each hallucinate between 17% '
                                       'and 33% of the time"',
                                       note='central = midpoint of 17-33%; range widened for transfer from legal research to other '
                                            'activities. For the engine key capability.e0, today 0.20 [0.10, 0.45] unlinked'),
                                     grounding='b', analogy='retrieval over a large, partly structured corpus (case law) as a stand-in for '
                                                           'low data readiness'),
        },
        'error_rate_epsilon_A': {
            'value': 'model: epsilon(d) = 1 - 1 / (1 + (d / H50(t))^b) before review',
            'residual_after_review_factor': dict(P(0.2, [0.05, 0.5], 'assumed', 'assumed share of errors that survive human review'),
                                                 grounding='d', note='no verified measure of the share of AI errors human reviewers miss'),
            'quality': 'primary_data_fit', 'assumed': False, 'source': 'logistic form and slope from capability_path'},
        'augmentation_gain_beta_U': P(0.25, [-0.16, 1.27], 'peer_reviewed',
                                      'Noy and Zhang (2023) Science: writing time -40% (beta 0.67); Brynjolfsson, Li and Raymond (2025) QJE: '
                                      '+14% resolutions per hour (0.14); Cui et al. (2024): +26% tasks (0.26); Dell\'Acqua et al. (2026) '
                                      'Organization Science: +12.2% tasks, 25.1% faster; Peng et al. (2023): 55.8% faster (1.27, lab task); '
                                      'Becker et al. (2025): +19% time (-0.16)',
                                      note='c_U = w t / (1 + beta_U). Central = between the field estimates (0.14-0.26) and lab estimates.'),
        'build_fixed_cost_F_A': {
            'value': {'llm_workflow_per_process_usd': 500000},
            'range': {'llm_workflow_per_process_usd': [100000, 2000000]},
            'quality': 'working_paper', 'assumed': False, 'grounding': 'b',
            'source': 'precedent: Svanberg et al. (2024) computer-vision system, bare-bones $165,000 to full $1,765,000 implementation '
                      '(reference_points); $500,000 lies inside that band; range widened to $0.1M-2M',
            'analogy': 'implementing one AI system for one workflow at one firm (computer vision there, LLM workflow here)',
            'reference_points': {
                'computer_vision_system': {'implementation_usd': 1765000, 'maintenance_usd_per_year': 242840,
                                           'bare_bones_implementation_usd': 165000, 'bare_bones_maintenance_usd_per_year': 122840,
                                           'lifespan_years': 5, 'real_discount_rate': 0.05,
                                           'quality': 'working_paper',
                                           'source': 'Svanberg, Li, Fleming, Goehring and Thompson (2024), Beyond AI Exposure, MIT FutureTech'},
                'gartner_genai_transformation_deployments_usd': {'range': [5000000, 20000000], 'quality': 'prediction',
                                                                 'source': 'Gartner press release, 29 Jul 2024'}}},
        'amortization_years_T_A': dict(P(4, [3, 5], 'assumed',
                                         'precedent: book useful life of internal-use software, 3 to 5 years in practice (not read at a '
                                         'filing in this pass). ASC 350-40 prescribes no life: amortisation is generally straight line '
                                         'over a life that reflects obsolescence, technology, competition and other economic factors '
                                         '(350-40-35-4 to 35-6, read via PwC Viewpoint; notes/ref_verification_accounting.md); hosted '
                                         'implementation costs are amortised over the hosting term including reasonably certain renewals '
                                         '(350-40-35-13, 35-14, ASU 2018-15)',
                                         note='T_A is an economic and book amortisation horizon, not a tax life. Tax: software development '
                                              'is research or experimental expenditure (26 U.S.C. 174A(d)(3), 174(c)(3)); domestic '
                                              'expenditure is deducted when paid or incurred for taxable years beginning after 31 Dec 2024 '
                                              '(174A(a)); foreign expenditure is amortised over 15 years from the midpoint of the taxable '
                                              'year (174(a)). See depreciation.rnd_tax_treatment. The 36-month rule of 26 CFR '
                                              '1.167(a)-14(b)(1) applies only to off-the-shelf software under 167(f)(1) and is not a '
                                              'precedent for this horizon.'),
                                       grounding='b', analogy='an LLM workflow build is amortised like internal-use software'),
    },

    # ============================================================== outsourcing (Section 3)
    'outsourcing': {
        'price_ratio_pO_over_wt': {
            'value': {'F05 customer support': 0.55, 'F11 finance and accounting': 0.65, 'F12 human resources (admin)': 0.70,
                      'F15 IT and security': 0.65, 'F02 product and engineering': 0.75, 'F07 professional services': 0.80,
                      'F13 legal (process outsourcing)': 0.60, 'F17 facilities': 0.85, 'F09 logistics': 0.85,
                      'F03 marketing (content and operations)': 0.75, 'F04 sales (SDR and inside sales)': 0.80},
            'range': {'F05 customer support': [0.35, 0.80], 'F11 finance and accounting': [0.45, 0.85],
                      'F12 human resources (admin)': [0.50, 0.90], 'F15 IT and security': [0.45, 0.90],
                      'F02 product and engineering': [0.50, 1.00], 'F07 professional services': [0.60, 1.00],
                      'F13 legal (process outsourcing)': [0.40, 0.85], 'F17 facilities': [0.70, 1.00],
                      'F09 logistics': [0.70, 1.00], 'F03 marketing (content and operations)': [0.50, 1.00],
                      'F04 sales (SDR and inside sales)': [0.60, 1.00]},
            'quality': 'government', 'assumed': False, 'grounding': 'b',
            'source': 'level grounded by precedent: GAO-01-20 (DOD Competitive Sourcing: Results of A-76 Studies Over the Past 5 Years, '
                      'Dec 2000; govinfo.gov): for 286 studies (138 cost comparisons, 148 direct conversions, FY1995-1999) DOD reported '
                      'costs "reduced by about 39 percent"; GAO calls the estimate imprecise (baselines largely personnel costs; study '
                      'and implementation costs not deducted). All-in cost ratio 0.61 implies p_O/(w t) of about 0.48 at the default '
                      'kappa_O and zeta_O, the low end of these ranges. No public dataset of BPO prices relative to in-house cost was found',
            'analogy': 'government support services opened to competition (in-house or contractor) as a stand-in for outsourcing an '
                       'enterprise function; function-level differences inside the band are assumed',
            'note': 'the A-76 savings include in-house winners that reorganised, so they bound the outsourcing saving from above'},
        'coordination_overhead_kappa_O': dict(P(0.10, [0.05, 0.15], 'assumed', 'assumed retained-organisation and vendor-management share of w t'),
                                              grounding='d'),
        'risk_premium_zeta_O': dict(P(0.03, [0.0, 0.10], 'assumed', 'assumed share of w t for IP, data protection and rework risk'),
                                    grounding='d'),
        'vendor_price_decline_per_year': dict(P(0.05, [0.0, 0.15], 'assumed', 'assumed: vendors pass through part of their own AI savings'),
                                              grounding='d'),
    },

    # ============================================================== regulation (Section 5)
    'regulatory_oversight_floor_psi_min': {
        'value': {'none': 0.0, 'high_risk_eu': 0.25, 'licensed': 0.30},
        'range': {'none': [0.0, 0.05], 'high_risk_eu': [0.10, 1.00], 'licensed': [0.15, 0.60]},
        'quality': 'assumed', 'assumed': True, 'grounding': 'd',
        'source': 'EU AI Act (Regulation (EU) 2024/1689) Article 14 is qualitative: high-risk systems must allow natural persons to '
                  'oversee, override and stop them; it sets no numeric review share. Annex III point 1(a) remote biometric '
                  'identification requires verification by at least two natural persons (Art. 14(5)).',
        'note': 'floors are shares of in-house time w t spent on mandatory review. For biometric identification set the floor to '
                'at least two reviews per decision.'},

    # ============================================================== Section 13.1 capital per unit of work
    'capital_per_unit': {
        'api_inference': dict(P(0.0, [0.0, 0.0], 'assumed', 'inference bought as a service is opex: K = 0'), grounding='a',
                              note='definitional (a purchased service is an operating expense), so no empirical grounding is needed'),
        'owned_compute_capex_per_usd_annual_compute_cost': P(3.0, [2.0, 4.0], 'assumed',
                                                             'derived: servers are about 60% of annualised AI data-center TCO '
                                                             '(Michael and Cottier 2026, Epoch AI) times a 5-6 year server life',
                                                             note='upfront capex per $1 a year of compute it replaces; K_A = this x '
                                                                  'inference cost per unit.'),
        'robotics_and_devices_usd_per_displaced_fte': P(250000, [100000, 600000], 'assumed',
                                                        'assumed installed system cost per FTE-equivalent of physical work, '
                                                        'including integration', note='no verified public source in this build'),
        'capitalized_share_of_build_cost': P(0.5, [0.3, 0.7], 'assumed',
                                             'assumed share of F_A capitalised as internal-use software (application development stage)'),
    },
    'depreciation': {
        'servers_book_life_years': P(5.5, [5.0, 6.0], 'company_filing',
                                     'Meta FY2025 10-K: most servers and network assets 5.5 years from Jan 2025; Amazon FY2025 10-K: a '
                                     'subset of servers cut from 6 to 5 years from Jan 2025 ("increased pace of technology development"); '
                                     'earlier Amazon changes 4 to 5 (2022) and 5 to 6 (2024)',
                                     note='read through secondary summaries (hudson-labs.com, altss.com) that quote the filings; the full '
                                          '10-K pages were too long to fetch. delta_K = 1 / life.'),
        'accelerators_economic_delta_K': P(0.25, [0.20, 0.33], 'assumed',
                                           'Part I Remark rem:assumptions(c): compute fleets depreciate about 20-33% a year',
                                           note='economic obsolescence is faster than book life when price-performance improves fast'),
        'internal_use_software_book_life_years': P(4, [3, 5], 'assumed', 'assumed common GAAP practice (ASC 350-40)'),
        'software_tax_life_months': P(36, [36, 36], 'government',
                                      '26 CFR 1.167(a)-14(b)(1): software under section 167(f)(1) amortised straight line over 36 months',
                                      note='scope: off-the-shelf (purchased) computer software only. It does not apply to software the '
                                           'firm develops, including AI builds, which is research or experimental expenditure under '
                                           '26 U.S.C. 174A (domestic, deducted when paid or incurred) and 174 (foreign, 15 years); use '
                                           'rnd_tax_treatment for builds. Qualified property, including off-the-shelf software, acquired '
                                           'after 19 Jan 2025 may instead take the 100% additional first-year allowance (IRS Notice '
                                           '2026-11).'),
        'rnd_tax_treatment': {
            'domestic_psi': P(1.0, [1.0, 1.0], 'government',
                              '26 U.S.C. 174A(a), (d)(3) (Pub. L. 119-21, sec. 70302(a)): domestic research or experimental '
                              'expenditure, including software development, deducted when paid or incurred for taxable years '
                              'beginning after 31 Dec 2024; election to amortise over at least 60 months under 174A(c)',
                              note='text via Legal Information Institute (Cornell); refs key usc2026sec174a'),
            'foreign_amortization_years': P(15, [15, 15], 'government',
                                            '26 U.S.C. 174(a) as amended by Pub. L. 119-21, sec. 70302(b)(1): expenditure attributable '
                                            'to foreign research charged to capital and amortised ratably over 15 years beginning with '
                                            'the midpoint of the taxable year; no deduction on disposition or abandonment (174(d))',
                                            note='refs key usc2026sec174'),
            'foreign_psi_15': P(r((1 + 1.1 ** -15) / 30 + (1 - 1.1 ** -14) / (0.10 * 15)), [0.44, 0.63], 'government',
                                'computed: psi_T = [1 + (1+r)^-T]/(2T) + [1 - (1+r)^-(T-1)]/(rT) at T = 15, r = 0.10 '
                                '(midpoint convention; verify_part2_accounting.py check 3b); range for r from 0.07 to 0.14',
                                note='0.518 with continuous straight-line deductions'),
            'psi_split_rule': {'value': 'psi = 1 - s_for (1 - psi_15)', 'quality': 'government', 'assumed': False,
                               'source': 'prop:acct-tax (part2/theory_accounting.tex); s_for = share of the build attributable '
                                         'to foreign research (26 U.S.C. 41(d)(4)(F)); firm input, default 0'},
            'prior_law_2022_2024_psi_5yr': P(0.796, [0.796, 0.796], 'government',
                                             'domestic R&E amortised over 5 years from the midpoint (pre-2025 26 U.S.C. 174); '
                                             'psi_5 = 0.796 at r = 0.10 (0.787 with continuous straight-line deductions); history only'),
        },
        'integration_build_life_years': P(4, [3, 5], 'assumed', 'assumed'),
        'robotics_equipment_life_years': P(7, [5, 10], 'assumed', 'assumed'),
    },

    # ============================================================== Section 13.2 transition costs
    'transition': {
        'parallel_run_T_par_years': {
            'value': {'erp_migration': 0.17, 'finance_close': 0.17, 'payroll': 0.08, 'support_platform': 0.08,
                      'outsourcing_transition': 0.25, 'ai_agent_shadow_mode': 0.17},
            'range': {'erp_migration': [0.08, 0.50], 'finance_close': [0.08, 0.25], 'payroll': [0.04, 0.12],
                      'support_platform': [0.04, 0.25], 'outsourcing_transition': [0.08, 0.50], 'ai_agent_shadow_mode': [0.04, 0.50]},
            'quality': 'practitioner_survey_undisclosed', 'assumed': False, 'grounding': 'b',
            'source': 'precedents by cell. payroll: "parallel runs will be carried out for two or three different payroll periods" '
                      '(SAPinsider, How to plan and manage a successful payroll parallel run; practitioner guidance, no data), i.e. 4-6 '
                      'weeks on biweekly pay; finance_close and erp_migration: the same practice applied to 1-3 monthly closes; '
                      'outsourcing_transition: FAR 52.237-3 (Continuity of Services), phase-in and phase-out for up to 90 days '
                      '(government); ai_agent_shadow_mode: the clinical-AI silent trial of Kwong et al. (2022), Frontiers in Digital '
                      'Health 4:929508, doi:10.3389/fdgth.2022.929508, ran about 5 months (Aug-Dec 2020; 523 kidneys) with clinicians '
                      'blinded, the high-stakes upper end; support_platform: weeks, by analogy with payroll cycles',
            'analogy': 'cycle-based parallel runs of payroll and finance systems; prospective silent trials of clinical AI for agents',
            'note': 'erp_migration and support_platform rest on analogy only (no ERP- or helpdesk-specific source found); GAO-24-106313 '
                    '(Marine Corps move to DAI) documents a 26-month slip to normal operations but no parallel-run length'},
        'duplication_premium_omega_par': dict(P(0.8, [0.5, 1.0], 'assumed', 'assumed share of full legacy cost kept during the parallel run'),
                                              grounding='d',
                                              note='in every precedent above (payroll, silent trial) the legacy process runs at full volume '
                                                   'during the parallel run; how that maps to omega_par depends on whether the ramp share '
                                                   'already counts legacy work (theory_core ass:tasks-transition; engine parallel_cost_flow). '
                                                   'Definitional question for the core theorist; scenario dimension until resolved'),
        'reconciliation_effort_nu_rec': dict(P(0.10, [0.05, 0.25], 'assumed', 'assumed, as a share of c_H v during the parallel run'),
                                             grounding='d'),
        'duplicate_license_months': dict(P(3, [0, 12], 'assumed', 'assumed months of legacy licence and infrastructure cost beyond cut-over'),
                                         grounding='d'),
        'severance_s_w_months': {
            'value': {'US': 3.0, 'DE': 2.0, 'FR': 1.0, 'UK': 0.9},
            'range': {'US': [1.0, 6.0], 'DE': [1.0, 6.0], 'FR': [1.0, 4.0], 'UK': [0.5, 3.0]},
            'quality': 'company_filing', 'assumed': False, 'grounding': 'b',
            'analogy': 'U.S. bound: WARN notice (2 months) below and the published formulas of two large software employers above '
                       '(16 weeks + 2 weeks per year of service = 5.5 months at 3.9 years of tenure); other countries: statute',
            'us_precedent': {'meta_2022': {'formula': '16 weeks of base pay plus two additional weeks for every year of service, no cap; '
                                                      'six months of healthcare',
                                           'severance_and_personnel_costs_usd': 975000000, 'employees': 11000,
                                           'usd_per_employee': r(975e6 / 11000, 0),
                                           'source': 'Meta Form 8-K, Exhibit 99.1, 9 Nov 2022 (sec.gov/Archives/edgar/data/1326801/'
                                                     '000132680122000116/nov092022exhibit991.htm); Meta Q4 2022 results release '
                                                     '(investor.atmeta.com): $975M severance and other personnel costs, about 11,000 employees'},
                             'alphabet_2023': {'severance_and_related_usd': 2088000000, 'roles': 12000,
                                               'usd_per_role': r(2088e6 / 12000, 0),
                                               'source': 'Alphabet Q4 2023 results, Form 8-K Exhibit 99.1 (sec.gov/Archives/edgar/data/1652044/'
                                                         '000165204424000014/googexhibit991q42023.htm): "employee severance and related '
                                                         'charges of $2.1 billion" ($2,088M) for 2023; about 12,000 roles and 16 weeks plus '
                                                         '2 weeks per additional year, at least 60 days notice, per HR Dive (20 Jan 2023, '
                                                         'secondary report of the CEO memo)'}},
            'source': 'U.S. precedent above (company filings) and statutory anchors (government) at median U.S. tenure of 3.9 years (BLS, CPS, Jan 2024): '
                      'DE KSchG s.1a(2): 0.5 month per year of service (= 1.95 months); FR Code du travail R1234-2: 1/4 month per '
                      'year up to 10 years, 1/3 thereafter (= 0.98 month minimum); UK statutory redundancy: 1 week per year aged '
                      '22-40 (0.5 under 22, 1.5 aged 41+), max 20 years, weekly cap GBP 719 from 6 Apr 2025 (GB, CIPP) and GBP 783 '
                      'from 6 Apr 2026 (NI, LRA) (= about 0.9 month); US: no federal severance requirement found; WARN requires '
                      '60 days notice for plant closings and mass layoffs by employers with 100+ employees (dol.gov), so pay in '
                      'lieu of notice is about 2 months. Central values above the statutory minimum are assumed (negotiated plans, '
                      'notice, benefits continuation, outplacement).'},
        'redeployment_share_rho_d': dict(P(0.25, [0.10, 0.50], 'assumed',
                                      'assumed share of affected FTE redeployed internally (symbol rho_d, not Part I rho)'),
                                         grounding='d', note='no measured internal redeployment rate found; scenario dimension'),
        'contract_break_fee_months': {
            'value': {'outsourcing_termination_for_convenience': 4, 'saas_or_license_remaining_term': 6},
            'range': {'outsourcing_termination_for_convenience': [2, 9], 'saas_or_license_remaining_term': [0, 24]},
            'quality': 'assumed', 'assumed': True, 'grounding': 'd',
            'source': 'assumed months of contract fees; subscription contracts are usually non-cancellable for the committed term, so '
                      'the break cost is the remaining committed fees'},
        'j_curve': {
            'dip_share_of_process_productivity': dict(grounding='d', **P(0.10, [0.01, 0.30], 'assumed',
                                                   'assumed; direction from McElheran, Yang, Kroff and Brynjolfsson (2025), The Rise of '
                                                   'Industrial AI in America, U.S. Census CES WP 25-27: short-run productivity and '
                                                   'profitability losses precede gains (manufacturing, 2017 and 2021 surveys)',
                                                   note='MIT Sloan summary reports a 1.33 percentage point short-run drop with controls '
                                                        'and a much larger figure after selection correction (secondary; units unclear, '
                                                        'not used numerically).')),
            'dip_duration_years': dict(grounding='d', **P(1.0, [0.25, 3.0], 'assumed',
                                    'assumed; McElheran et al. observe adopters over a four-year window (2017-2021), with pre-2017 '
                                    'adopters growing faster by 2021; McAfee (2002, POM) finds operational performance worsened right '
                                    'after an enterprise-system go-live and surpassed its prior level within several months (abstract, as '
                                    'recorded in ref_verification_part2.md); lower bound widened to 0.25 years by the audit of 29 Oct 2026')),
            'macro_mismeasurement_reference': {'value': {'tfp_gap_2004': 0.113, 'tfp_gap_2017': 0.159}, 'quality': 'peer_reviewed',
                                               'assumed': False,
                                               'source': 'Brynjolfsson, Rock and Syverson (2021), AEJ: Macroeconomics 13(1), 333-372: '
                                                         'intangible-adjusted TFP 11.3% (2004) and 15.9% (2017) above official measures',
                                               'note': 'aggregate measurement effect, not a firm-level dip; for context only'}},
        'rollback_probability_p_fail': dict(P(0.10, [0.03, 0.30], 'assumed',
                                         'assumed; see project_outcomes for the overrun evidence it is calibrated against'),
                                            grounding='d', note='surveys give abandonment before production (project_outcomes), not '
                                                                'rollback after cut-over; scenario dimension'),
    },

    # ============================================================== Section 14 project outcomes, learning, decisions
    'project_outcomes': {
        'it_cost_overrun_mean': P(0.27, [0.27, 0.39], 'peer_reviewed',
                                  'Flyvbjerg and Budzier (2011), Why Your IT Project May Be Riskier Than You Think, Harvard Business '
                                  'Review 89(9) (SSRN 2229735; arXiv:1304.0265): 1,471 IT projects, mean cost overrun 27%',
                                  note='HBR is a practitioner journal; the underlying database analysis is also in Flyvbjerg et al. '
                                       '(2022), JMIS 39(3), 607-639 (5,392 projects; overruns follow a power law with a fat tail). '
                                       'Upper range value 0.39 is assumed headroom for a fatter tail, not a sourced mean.'),
        'it_black_swan_share': P(r(1 / 6, 3), [0.12, 0.20], 'peer_reviewed',
                                 'Flyvbjerg and Budzier (2011): one in six projects had a cost overrun of 200% on average and a '
                                 'schedule overrun of almost 70%'),
        'it_black_swan_cost_overrun': P(2.0, [1.5, 3.0], 'peer_reviewed', 'Flyvbjerg and Budzier (2011)'),
        'it_black_swan_schedule_overrun': P(0.70, [0.5, 1.0], 'peer_reviewed', 'Flyvbjerg and Budzier (2011)'),
        'overrun_tail': {'value': 'power law', 'quality': 'peer_reviewed', 'assumed': False,
                         'source': 'Flyvbjerg, Budzier, Lee, Keil, Lunn and Bester (2022), The Empirical Reality of IT Project Cost '
                                   'Overruns: Discovering a Power-Law Distribution, JMIS 39(3), 607-639',
                         'note': 'tail exponent not read from the paper; the engine should sample overruns from a fat-tailed '
                                 'distribution (e.g. lognormal-Pareto mixture) matched to mean 0.27 and P(>2.0) = 1/6'},
        'digital_transformation_success_rate_survey': P(0.30, [0.20, 0.80], 'practitioner_survey_disclosed',
                                                         'BCG (29 Oct 2020), Flipping the Odds of Digital Transformation Success: '
                                                         '825 senior executives, self-rated; 30% met or exceeded target value with '
                                                         'sustainable change; 80% when six factors were present',
                                                         note='self-reported survey by a consultancy; success defined by respondents.'),
        'change_failure_70_percent': {'value': None, 'quality': 'unsupported', 'assumed': False,
                                      'source': 'Hughes (2011), Do 70 Per Cent of All Organizational Change Initiatives Really Fail?, '
                                                'Journal of Change Management 11(4), 451-464, doi:10.1080/14697017.2011.630506: no valid '
                                                'and reliable empirical evidence supports the 70% figure',
                                      'note': 'do not use the popular 70% failure figure. Standish CHAOS rates are also not used '
                                              '(method not disclosed; criticised by Eveleens and Verhoef, IEEE Software, 2010).'},
        'genai_poc_to_production_rate': P(0.54, [0.05, 0.70], 'practitioner_survey_disclosed',
                                          'S&P Global Market Intelligence survey (more than 1,000 respondents, North America and Europe, '
                                          'reported by CIO Dive 14 Mar 2025): the average organisation scrapped 46% of AI proofs of concept '
                                          'before production; 42% of companies abandoned most AI initiatives (17% a year earlier)',
                                          note='value = 1 - 0.46. Read through a trade-press summary (secondary). Low end of the range '
                                               'reflects the MIT NANDA figure below. Cross-check (audit, 29 Oct 2026): Gartner survey of 644 '
                                               'respondents in the U.S., Germany and the U.K. (Q4 2023), "only 48% of AI projects make it into '
                                               'production", about 8 months from prototype to production (reported by mi-3.com.au, 9 May 2024; '
                                               'secondary). This is pilot attrition before production, not the failure of a funded '
                                               'migration (assumptions round 2, Section 1.1). Since the params commit of 29 Oct 2026 '
                                               'the engine success logit (success.a0) is calibrated so a reference process reaches '
                                               'production with probability about 0.50 (Gartner 48%, S&P 54%), because the engine\'s '
                                               'b_bar (transformation_value_realized_share) now carries the realization haircut.'),
        # ---- assumptions round 2 (notes/assumptions_round2.md Sections 0, 1.1, 1.3-1.4), adopted 29 Oct 2026
        'transformation_attempt_creates_value_varpi': dict(
            P(0.70, [0.54, 0.80], 'practitioner_survey_disclosed',
              'BCG (29 Oct 2020), Flipping the Odds of Digital Transformation Success (bcg.com/publications/2020/'
              'increasing-odds-of-success-in-digital-transformation; read 29 Oct 2026): 825 senior executives, self-rated; '
              '30% win zone + 44% worry zone = 74% of transformations created value; 80% with all six success factors. Low end: '
              'S&P Global pilot attrition (genai_poc_to_production_rate, 0.54)',
              # round 2 (B9, notes/r2_propagation.md item 4): varpi is the share of attempts that create some value,
              # not a success rate; the calibration target is the per-attempt yield varpi x b_bar (P1 YieldModel)
              unit='share of funded attempts that create some value (not a success rate; Paper 1 round 2, B9, 2 Nov 2026)',
              note=Hand('central = 74% rounded down for self-report bias; the calibration target is the per-attempt yield '
                        'varpi x b_bar',
                        '= 0.70 x 0.67 = 0.47 (Paper 1 macro YieldModel), close to McKinsey\'s unconditional 0.46; high end = '
                        'BCG six-factor rate 0.80. Used as P1 varpi (code/calibrate_horizons.py',
                        'PACE). Because varpi and b_bar come from outcome surveys, which already include leadership changes and '
                        'strategy shifts,',
                        'the disruption haircut exp(-nu_D T_emb) is not applied to q; nu_D stays for the shock-timing results '
                        '(prop:ext-shocks).')),
            grounding='b', analogy='whole-transformation outcomes (self-reported) as the share of funded AI migrations that '
                                   'create value', read=TODAY, adopted='params commit 2026-10-29 (assumptions round 2, 1.1)'),
        'transformation_value_realized_share_b_bar': dict(
            P(0.67, [0.37, 0.85], 'practitioner_survey_disclosed',
              'McKinsey Global Survey, Losing from day one: Why even successful transformations fall short (7 Dec 2021; '
              'mckinsey.com/capabilities/people-and-organizational-performance/our-insights/successful-transformations; read '
              '29 Oct 2026): 1,034 participants, fielded 18 May-29 Jun 2021; successful transformations realized 67% of the '
              'maximum financial benefits, all others 37% on average; top-quartile listed firms capture 74% of value within 12 months',
              unit='share of targeted value realized given success',
              note='flag: self-reported consultancy survey, but the only source that measures realization rather than attrition. '
                   'Low end = the "all others" mean; high end = top quartile. Product varpi x b_bar = 0.47 [0.20, 0.68], against '
                   'McKinsey\'s unconditional mean 0.30 x 0.67 + 0.70 x 0.37 = 0.46. Replaces the unsourced 0.85 (P1 bbar, engine '
                   'success.b_bar).'),
            grounding='a', flag='survey (self-reported)', read=TODAY, adopted='params commit 2026-10-29 (assumptions round 2, 1.4)'),
        'genai_weak_figures': {
            'mit_nanda_2025': {'claim': '95% of organisations get zero measurable return from generative AI; about 5% of pilots '
                                        'reach production with P&L impact',
                               'method': 'about 52-53 interviews, 153 survey responses and a review of public deployments over about '
                                         'six months; authors call it a directionally accurate snapshot',
                               'quality': 'practitioner_survey_undisclosed', 'assumed': False,
                               'source': 'MIT NANDA, The GenAI Divide: State of AI in Business 2025, via getdx.com/blog/the-ai-divide',
                               'flag': 'weak methodology; read through a summary; not used as a default'},
            'gartner_2024': {'claim': 'at least 30% of generative AI projects will be abandoned after proof of concept by end of 2025',
                             'quality': 'prediction', 'assumed': False, 'source': 'Gartner press release, 29 Jul 2024',
                             'flag': 'forecast, not a measured rate; not used as a default'}},
    },
    'learning': {
        'progress_ratio_per_doubling_of_completed_waves': P(0.85, [0.70, 1.00], 'assumed',
                                                            'assumed; learning curves in software development are documented '
                                                            'by Boh, Slaughter and Espinosa (2007), Management Science 53(8), '
                                                            '1315-1331, which reports no single rate usable here',
                                                            note='applied to wave cost and duration; 1.00 = no learning'),
        'success_logit_gain_per_prior_success': P(0.2, [0.0, 0.5], 'assumed', 'assumed experience effect on pi_p'),
        'correlated_failure_rho_common_shock': P(0.3, [0.0, 0.6], 'assumed',
                                                 'assumed correlation of outcomes for waves on a shared platform or data layer'),
        'pilot_cost_share_of_F_A': P(0.15, [0.05, 0.30], 'assumed', 'assumed'),
    },
    'decision_capacity': {
        'approval_latency_weeks_major_initiative': dict(P(12, [6, 78], 'peer_reviewed',
                                                          'Eisenhardt (1989), Making Fast Strategic Decisions in High-Velocity Environments, '
                                                          'Academy of Management Journal 32(3), 543-576, Table 2: ten strategic decisions in eight '
                                                          'microcomputer firms took 1.5-18 months from first deliberate action to commitment; '
                                                          'fast firms averaged 2.8 months, slow firms 14 months (as stated in the text)',
                                                          note='central = fast-firm mean (2.8 months = 12 weeks); range = shortest (1.5 months) to '
                                                               'longest (18 months) decision. Raised from the assumed 8 weeks [2, 26] by the '
                                                               'audit of 29 Oct 2026'),
                                                        grounding='b', analogy='approval of a major transformation wave treated as a strategic '
                                                                               'decision (alliances, new products, strategy) in a fast-moving industry'),
        'latency_weeks_per_governance_layer': dict(P(r(10 / 3, 1), [r(4.5 / 3, 1), r(59 / 3, 1)], 'peer_reviewed',
                                                     'derived: (approval latency - the engine\'s 2-week base) / 3 governance layers (engine prior), '
                                                     'at Eisenhardt\'s fast-firm mean (12 weeks); range from her shortest decision (6.5 weeks) '
                                                     'to the slow-firm mean (61 weeks)'),
                                                   grounding='b', analogy='as approval_latency_weeks_major_initiative; the split into a base '
                                                                          'and equal per-layer delays is the model\'s own assumption'),
        'concurrent_major_initiatives_capacity_Phi': dict(P(5, [3, 10], 'assumed', 'assumed per executive team'), grounding='d'),
        'decision_units_per_initiative_launch_and_gate': dict(P(1.0, [0.5, 2.0], 'assumed', 'assumed (normalisation)'), grounding='d'),
        'congestion_elasticity_of_success': dict(P(0.5, [0.2, 1.0], 'assumed',
                                              'assumed: q(L/Phi) = min(1, (Phi/L)^elasticity) for L > Phi'), grounding='d'),
        'ai_decision_support_bandwidth_gain': dict(P(0.2, [0.0, 0.5], 'assumed', 'assumed proportional increase in Phi from AI analysis support'),
                                                   grounding='d'),
        'fast_to_slow_latency_ratio_reference': {'value': r(2.8 / 14, 2), 'quality': 'peer_reviewed', 'assumed': False, 'grounding': 'ref',
                                                 'source': 'Eisenhardt (1989): 2.8 / 14 months',
                                                 'note': 'bounds the regime latency multipliers (PE 0.5, family 0.7, public 1.0), which stay '
                                                         'assumed: the fastest decision makers took about a fifth of the time of the slowest'},
    },
    # ============================================================== Section 15 leadership change, reorganizations, context loss
    'leadership_and_context': {
        'ceo_turnover_hazard_h_L': P(0.168, [0.126, 0.168], 'peer_reviewed',
                                     'Kaplan and Minton (2012), How Has CEO Turnover Changed?, International Review of Finance 12(1), '
                                     '57-87, doi:10.1111/j.1468-2443.2011.01135.x: total annual CEO turnover in large U.S. firms 15.8% '
                                     '(1992-2007) and 16.8% since 2000 (implied tenure under 6 years); about 12.6% in 1992-1999',
                                     unit='per year', note='includes external turnover (takeover, bankruptcy). Expected tenure = 1 / h_L.'),
        'ceo_expected_tenure_years': P(r(1 / 0.168, 1), [r(1 / 0.168, 1), r(1 / 0.126, 1)], 'peer_reviewed', 'derived from h_L above'),
        'ceo_departing_tenure_years_2025': P(8.5, [8.1, 10.3], 'practitioner_dataset_disclosed',
                                             'Spencer Stuart, 2025 S&P 1500 CEO Transitions (Feb 2026): departing CEOs averaged 8.5 years '
                                             'in 2025 (9.2 in 2024; low 8.1 in 2019; peak 10.3 in 2021); 168 new S&P 1500 CEOs in 2025 '
                                             '(about 11% of 1,500, our calculation); sector turnover 8-14%',
                                             note='tenure of completed spells, longer than 1/h_L because it excludes short spells still running '
                                                  'and takeovers; for context only.'),
        'ceo_forced_share_of_departures': P(0.21, [0.21, 0.30], 'peer_reviewed',
                                            'Gentry, Harrison, Quigley and Boivie (2021), A database of CEO turnover and dismissal in S&P '
                                            '1500 firms, 2000-2018, Strategic Management Journal 42(5), 968-991, doi:10.1002/smj.3278 '
                                            '(data: doi:10.5281/zenodo.4543893): 870 of 4,141 departures dismissed for performance, 1,023 '
                                            'all dismissals, 2,193 retirements',
                                            note='our shares from the paper\'s Table 3 counts; 0.30 excludes other and missing codes.'),
        'ceo_forced_turnover_multiplier_bad_industry': P(2.0, [1.5, 2.5], 'peer_reviewed',
                                                         'Jenter and Kanaan (2015), CEO Turnover and Relative Performance Evaluation, '
                                                         'Journal of Finance 70(5), 2155-2184: 3,365 turnovers 1993-2009; a fall in industry '
                                                         'performance from the 90th to the 10th percentile doubles the probability of forced turnover',
                                                         note='range assumed around the point estimate'),
        'c_suite_tenure_years': {
            'value': {'CEO': 6.9, 'CFO': 4.7, 'CIO': 4.6, 'CHRO': 3.7, 'CMO': 3.5, 'all_c_suite': 4.9,
                      'CDO': 2.5, 'CAIO': 2.5},
            'range': {'CIO': [4.3, 4.6], 'CDO': [1.9, 2.5], 'CAIO': [1.5, 4.0]},
            'quality': 'practitioner_dataset_disclosed', 'assumed': False,
            'source': 'CEO to CMO and all_c_suite: Korn Ferry Institute, Age and Tenure in the C-Suite (press release 21 Jan 2020; '
                      'top 1,000 U.S. companies by revenue, late 2019; 2017 release: CIO 4.3 years); CDO: 2.5 years attributed to '
                      'Harvard Business Review (Aug 2021) by Becker\'s Hospital Review (secondary, method not stated) and 1.9 years in '
                      'Europe per DataIQ (Oct 2025, method not stated); CAIO: assumed (role too new for tenure data)',
            'note': 'CDO values: practitioner_survey_undisclosed / secondary; CAIO: assumed: true. Sponsor hazard default uses all_c_suite.'},
        'sponsor_change_hazard_h_L_exec': P(r(1 / 4.9, 3), [0.15, 0.30], 'practitioner_dataset_disclosed',
                                            '1 / Korn Ferry all-C-suite average tenure (4.9 years); range assumed',
                                            note='for a CIO, CDO or CAIO sponsor use 1 / that role\'s tenure'),
        'vision_overhaul_hazard_h_V': P(0.15, [0.05, 0.30], 'assumed', 'assumed baseline rate of change in the strategic objective'),
        'vision_overhaul_multiplier_after_leadership_change': P(3.0, [1.5, 6.0], 'assumed',
                                                                'assumed size; direction from Zhu, Hu and Shen (2020), Strategic Management '
                                                                'Journal 41(10), 1933-1951 (outsider new CEOs make more strategic change than '
                                                                'insiders), which gives no probability usable here',
                                                                note='applies for 2 years after the change; use the high end for outsider successors'),
        'new_leader_program_outcome': {'value': {'keep_kappa_keep': 0.60, 'rescope': 0.25, 'cancel': 0.15},
                                       'range': {'keep_kappa_keep': [0.30, 0.85]}, 'quality': 'assumed', 'assumed': True,
                                       'source': 'assumed; no credible estimate found'},
        'reorganization_hazard_h_R': P(0.46, [0.30, 0.60], 'practitioner_survey_undisclosed',
                                       'derived from Aronowitz, De Smet and McGinty (2015), Getting organizational redesign right, '
                                       'McKinsey Quarterly (1 Jun 2015): almost 60% of surveyed executives had a redesign within the past '
                                       'two years, 25% three or more years ago; h_R = -ln(1 - 0.6) / 2 assuming Poisson arrivals',
                                       note='self-reported executive survey, sample size not given. The same article reports fewer than a '
                                            'quarter of redesigns succeed (self-reported).'),
        'reorg_freeze_T_freeze_years': dict(P(0.25, [0.08, 1.0], 'practitioner_survey_disclosed',
                                              'precedent for the length of reorganization disruption: McKinsey Global Survey, Taking '
                                              'organizational redesigns from plan to practice (fielded 9-19 Nov 2010; 2,525 executives, '
                                              '1,890 with a redesign in the past five years): expected durations split roughly into thirds, '
                                              'six months or less, six to twelve months, more than a year; 43% underestimated the time. '
                                              'McKinsey Global Survey, The secrets of successful organizational redesigns (10-20 Sep 2013; '
                                              '2,063 executives): nearly 30% of fully implemented redesigns lasted more than 12 months',
                                              note='self-reported surveys (flag). A freeze of in-flight work is shorter than the whole '
                                                   'redesign, so central 0.25 years stays; the upper bound is widened from 0.5 to 1.0 '
                                                   '(median redesign of 6-12 months) by the audit of 29 Oct 2026'),
                                            grounding='b', analogy='duration of an organizational redesign as the outer bound of the '
                                                                   'freeze it imposes on in-flight initiatives'),
        'reorg_decision_bandwidth_factor': P(0.5, [0.3, 0.8], 'assumed', 'assumed share of Phi available during a freeze'),
        'reorg_process_owner_turnover_share': P(0.3, [0.1, 0.6], 'assumed', 'assumed'),
        'key_person_departure_hazard_h_K': dict(P(0.15, [0.08, 0.30], 'assumed',
                                             'assumed; anchor: median tenure with current employer 3.9 years (BLS, CPS, Jan 2024), '
                                             'i.e. about 0.26 a year if exits were memoryless; critical roles are assumed stickier. '
                                             'Upper anchor (audit, 29 Oct 2026): BLS JOLTS, August 2026 (preliminary; bls.gov/news.release/'
                                             'jolts.htm): total separations 2.5% a month in the information industry, 1 - 0.975^12 = 0.26 a '
                                             'year for all employees'),
                                                grounding='d', note='the stickiness of critical roles relative to all employees is '
                                                                    'unmeasured; the upper bound is grounded, the central value is not'),
        'context_lost_per_departure': P(0.5, [0.2, 0.8], 'assumed', 'assumed share of a role\'s tacit process context lost when it leaves'),
        'context_stock_depreciation_per_year': dict(P(0.20, [0.0, 0.50], 'assumed',
                                                 'assumed; Argote, Beckman and Epple (1990), Management Science 36(2), 140-154, find '
                                                 'production knowledge "depreciates rapidly" (rate not read; not used numerically). '
                                                 'Contrary precedent (audit, 29 Oct 2026): Thompson (2007), How Much Did the Liberty '
                                                 'Shipbuilders Forget?, Management Science 53(6), 908-918, doi:10.1287/mnsc.1060.0678, rebuilds '
                                                 'the same shipyard data from archives and finds forgetting "much smaller than previously '
                                                 'reported, and may well be zero" (abstract, ideas.repec.org)'),
                                                    grounding='d', note='the two precedents disagree on the same data; lower bound '
                                                                        'widened to 0; scenario dimension'),
        'documentation_protection_kappa_doc': P(0.5, [0.2, 0.8], 'assumed',
                                                'assumed reduction in context lost per departure from documented processes and context engines'),
        'reuse_fraction_vartheta_reuse': {
            'value': {'data_and_integration_platform': 0.80, 'process_automation_on_platform': 0.50, 'vision_specific_build': 0.20},
            'range': {'data_and_integration_platform': [0.60, 0.95], 'process_automation_on_platform': [0.30, 0.70],
                      'vision_specific_build': [0.0, 0.40]},
            'quality': 'assumed', 'assumed': True, 'source': 'assumed share of value kept after a vision overhaul'},
        'replan_cost_C_replan_share_of_annual_program_budget': P(0.10, [0.05, 0.25], 'assumed', 'assumed'),
    },
    # ============================================================== Section 16 ownership regime presets
    'ownership_regimes': {
        'public': {
            'r_own_wacc': P(0.0934, [0.0700, 0.1066], 'practitioner_dataset_disclosed',
                            'Damodaran, Cost of Equity and Capital (US), January 2026, pages.stern.nyu.edu/~adamodar/New_Home_Page/'
                            'datafile/wacc.html: Software (System & Application) 9.34% (309 firms); Software (Internet) 10.66%; '
                            'Computer Services 7.83%; Information Services 7.00%; Business & Consumer Services 7.23%; total market 6.96%',
                            unit='per year, nominal', note='range = Information Services to Software (Internet)'),
            'horizon': {'value': 'going concern (infinite)', 'quality': 'assumed', 'assumed': True, 'source': 'spec 16.1'},
            'myopia_weight_theta_my': P(0.3, [0.0, 0.6], 'assumed',
                                        'assumed weight on near-term GAAP margin dips; evidence of pressure (survey): Graham, Harvey and '
                                        'Rajgopal (2005), Journal of Accounting and Economics 40(1-3), 3-73: of 401 financial executives, '
                                        '78% would give up economic value to smooth earnings and 55% would avoid initiating a very '
                                        'positive-NPV project if it meant missing the quarter\'s consensus; Asker, Farre-Mensa and '
                                        'Ljungqvist (2015), Review of Financial Studies 28(2), 342-390: public firms invest substantially '
                                        'less than similar private firms and respond less to investment opportunities',
                                        note='Graham et al. is a self-reported survey (flag); Asker et al. is peer-reviewed but gives the '
                                             'direction, not a weight'),
            'decision_latency_multiplier': P(1.0, [1.0, 1.5], 'assumed', 'assumed (baseline: board and disclosure cycles)'),
        },
        'pe_backed': {
            'target_gross_irr': P(0.22, [0.20, 0.25], 'practitioner_survey_disclosed',
                                  'Gompers, Kaplan and Mukharlyamov (2016), What do private equity firms say they do?, Journal of '
                                  'Financial Economics 121(3), 449-476: survey of 79 PE investors (more than $750 billion AUM, mostly '
                                  '2012); typical target IRR 22%, most between 20% and 25% (median reported as 25%)',
                                  note='self-reported survey published in a peer-reviewed journal'),
            'target_moic': P(2.5, [2.5, 2.85], 'practitioner_survey_disclosed',
                             'Gompers, Kaplan and Mukharlyamov (2016): median target multiple 2.5x, mean 2.85x, over a five-year horizon'),
            'net_excess_return_over_public_equity_per_year': P(0.03, [0.0, 0.04], 'peer_reviewed',
                                                               'Harris, Jenkinson and Kaplan (2014), Private Equity Performance: What Do We '
                                                               'Know?, Journal of Finance 69(5), 1851-1882: U.S. buyout funds (Burgiss data, '
                                                               'nearly 1,400 buyout and VC funds) beat the S&P 500 by 20-27% over fund life, '
                                                               'more than 3% a year; Kaplan and Schoar (2005), Journal of Finance 60(4), '
                                                               '1791-1823: average net returns approximately equal the S&P 500',
                                                               note='low end = Kaplan and Schoar; net of fees'),
            'carried_interest': P(0.20, [0.20, 0.20], 'peer_reviewed',
                                  'Kaplan and Stromberg (2009), Leveraged Buyouts and Private Equity, Journal of Economic Perspectives '
                                  '23(1), 121-146: carry "almost always equals 20 percent"; example management fee 2% of committed capital'),
            'management_fee': P(0.02, [0.015, 0.025], 'peer_reviewed', 'Kaplan and Stromberg (2009), example fee; range assumed'),
            'preferred_return_hurdle': P(0.08, [0.06, 0.08], 'secondary',
                                         'industry convention, stated by Carta (carta.com/learn/private-funds/management/carried-interest/'
                                         'hurdle-rate/): hurdle "often around 8%", "more than 50% of funds" (no data source named). Not '
                                         'found in Kaplan and Stromberg (2009) or in the Metrick and Yasuda (2010) abstract',
                                         note='flag: practitioner statement without a disclosed dataset'),
            'hold_period_T_hold_years': P(6.0, [4.0, 7.0], 'peer_reviewed',
                                          'Kaplan and Stromberg (2009): median holding period roughly six years; 42% of deals exited within '
                                          '60 months. Gompers, Kaplan and Mukharlyamov (2016): 96% of PE investors use a five-year forecast '
                                          'horizon. Practitioner (flag): Private Equity Info (19 Feb 2025), median hold 5.8 years, about '
                                          '6.0 for 2025 exits'),
            'entry_leverage_debt_to_ebitda': P(5.2, [4.2, 6.1], 'peer_reviewed',
                                               'Axelson, Jenkinson, Stromberg and Weisbach (2013), Borrow Cheap, Buy High?, Journal of '
                                               'Finance 68(6), 2223-2267: 1,157 buyouts 1980-2008, debt/EBITDA mean 5.6x, median 5.2x; '
                                               'median 6.1x in the lowest and 4.2x in the highest high-yield-spread quartile; debt/EV '
                                               'median 0.70; EV/EBITDA at entry median 7.6x (mean 8.2x)'),
            'entry_ev_to_ebitda_historical': dict(P(7.6, [7.6, 8.2], 'peer_reviewed', 'Axelson et al. (2013), all industries, 1980-2008',
                                                    note='audit, 29 Oct 2026: do not pair this all-industry 1980-2008 entry multiple with '
                                                         'the 2025 software exit multiple (14x) in a regime IRR; the gap would build in '
                                                         'multiple expansion that no operating change earns (Guo, Hotchkiss and Song 2011 '
                                                         'find much of buyout returns came from multiple expansion). Baseline: entry multiple '
                                                         '= exit multiple'),
                                                  grounding='ref'),
            'covenant_max_net_debt_to_ebitda': dict(P(7.0, [6.0, 8.0], 'government',
                                                 'lower bound: Interagency Guidance on Leveraged Lending (Federal Reserve, FDIC, OCC; SR 13-3, '
                                                 '21 Mar 2013; Federal Reserve Regulatory Service page read 29 Oct 2026): leverage "in excess '
                                                 'of 6X Total Debt/EBITDA raises concerns for most industries"; central = median entry '
                                                 'leverage 5.2x (Axelson et al. 2013) plus about 1.8x headroom (assumed). Chava and Roberts '
                                                 '(2008), Journal of Finance 63(5), 2085-2121, doi:10.1111/j.1540-6261.2008.01391.x, find '
                                                 'capital investment declines sharply after a covenant violation (direction only)',
                                                 note='trade-press headlines report that the OCC and FDIC later rescinded the guidance '
                                                      '(not verified); the 6x level is used as a supervisory precedent, not a binding limit'),
                                                    grounding='b', analogy='supervisory leverage concern level as the floor of a maintenance '
                                                                           'covenant'),
            'debt_rate_reference': {'value': {'treasury_2y_apr_2026': 0.038, 'treasury_10y_apr_2026': 0.0432}, 'quality': 'government',
                                    'assumed': False, 'grounding': 'ref',
                                    'source': 'Federal Reserve, Financial Stability Report, May 2026, accessible tables, Figure 1.1 '
                                              '(federalreserve.gov/publications/2026-may-financial-stability-report-accessibility-tables.htm): '
                                              '2-year 3.80%, 10-year 4.32% (April 2026); the same report says leveraged loan spreads '
                                              '"increased but remain below median levels" without a number',
                                    'note': 'floor for the engine key regime.debt_rate (0.08 [0.06, 0.11], assumed): spread over the floor is '
                                            'unverified, so the debt rate stays a scenario dimension'},
            'exit_multiple_M_exit_software_ev_to_ebitda': P(14.0, [10.0, 17.0], 'practitioner_dataset_disclosed',
                                                            'Silverpeak, Software M&A Report Q4 2025 (Jan 2026; Capital IQ and PitchBook): '
                                                            'software deal EV/EBITDA "within the historical 12-17x band", chart average '
                                                            '14.9x, 43 deals in 2025 with both multiples disclosed, down 3.4x year on year',
                                                            note='flag: small sample of disclosed deals, strategic and financial buyers '
                                                                 'mixed; lower bound 10x assumed for a stressed exit'),
            'decision_latency_multiplier': P(0.5, [0.3, 0.8], 'assumed', 'assumed (fast owner decisions)'),
        },
        'vc_backed': {
            'target_irr': P(0.31, [0.28, 0.35], 'practitioner_survey_disclosed',
                            'Gompers, Gornall, Kaplan and Strebulaev (2020), How do venture capitalists make decisions?, Journal of '
                            'Financial Economics 135(1), 169-190: survey of 889 VCs (Nov 2015 - Mar 2016); average required IRR 31%, '
                            'late-stage 28-29%, early stage higher (values read from the NBER conference version)',
                            note='self-reported survey published in a peer-reviewed journal; upper bound assumed'),
            'target_multiple': P(5.0, [5.0, 5.5], 'practitioner_survey_disclosed', 'Gompers et al. (2020): median 5x, mean about 5.5x'),
            'horizon_years': P(7, [5, 10], 'assumed', 'assumed'),
            'realized_performance_note': {'value': 'outperformed public equities in the 1990s, underperformed in the 2000s',
                                          'quality': 'peer_reviewed', 'assumed': False,
                                          'source': 'Harris, Jenkinson and Kaplan (2014)'},
        },
        'private_family': {
            'r_own_spread_over_public_wacc': P(-0.01, [-0.03, 0.02], 'assumed',
                                               'assumed; no verified estimate of family-firm discount rates found. Direction: Asker et '
                                               'al. (2015) find private firms invest more and respond more to investment opportunities'),
            'horizon_years': P(30, [10, 100], 'assumed', 'assumed (long or dynastic horizon)'),
            'employment_preference_b_share_of_wage': P(0.10, [0.0, 0.30], 'assumed',
                                                       'assumed owner utility per retained job, as a share of the loaded wage'),
            'decision_latency_multiplier': P(0.7, [0.4, 1.0], 'assumed', 'assumed'),
        },
        'hybrid_take_private_control_premium': P(0.30, [0.15, 0.50], 'peer_reviewed',
                                                  'Kaplan and Stromberg (2009): buyout premiums for public targets 15-50% over the '
                                                  'current stock price; central value assumed'),
        'hybrid_dual_class_myopia_weight': P(0.15, [0.0, 0.3], 'assumed', 'assumed: public disclosure with a controlling holder'),
    },
    'change_capacity': {
        'affected_fte_share_per_year': dict(P(0.10, [0.05, 0.22], 'practitioner_survey_disclosed',
                                              'central precedent (work changed): World Economic Forum, Future of Jobs Report 2025, digest '
                                              '(weforum.org/publications/the-future-of-jobs-report-2025/digest/; read 29 Oct 2026): over 1,000 '
                                              'employers, 14 million workers, 55 economies; 59 of 100 workers need training by 2030, about 12 a '
                                              'year. Exit-based bracket: single-year reductions in filings, Salesforce about 10% (Form 8-K, 4 Jan '
                                              '2023), Alphabet about 6% (about 12,000 roles, Jan 2023), Meta 22% of headcount in 2023 (67,317 at 31 '
                                              'Dec 2023; Q4 2023 results release); BLS JOLTS, August 2026: layoffs and discharges 1.0% a month '
                                              '(about 12% a year), total separations 3.2% a month',
                                              note='re-grounded by assumptions round 2 (Section 1.2): layoffs measure exits, the parameter '
                                                   'counts employees whose work changes; WEF measures that concept and lands on the same '
                                                   'value. Upper bound 0.20 -> 0.22 (Meta 2023).'),
                                            grounding='b', analogy='employers\' expected share of workers whose work changes (training, '
                                                                   'redeployment), bracketed by one-year reductions in filings',
                                            read=TODAY, adopted='params commit 2026-10-29 (assumptions round 2, 1.2)'),
        'embedding_time_T_emb_years': dict(P(1.25, [1.0, 2.0], 'company_filing',
                                             'Salesforce Form 8-K (4 Jan 2023; sec.gov/Archives/edgar/data/1108524/000110852423000003/'
                                             'crm-20230104.htm; read 29 Oct 2026) and FY2024 results (28 Feb 2024): the workforce reduction '
                                             'announced 4 Jan 2023 was "substantially completed" about 13 months later; McKinsey (2021): '
                                             'about half of transformation value within 18 months, top-quartile listed firms 74% within 12 '
                                             'months; Gartner (2024, secondary): about 8 months prototype to production',
                                             unit='years from a transition\'s start to embedded value (T_emb = T_pb in Part I)',
                                             note='replaces 2 [1, 3] (d). Used by code/calibrate_horizons.py PACE (Temb, Tpb).'),
                                           grounding='b', analogy='time from announcement to substantial completion of a disclosed '
                                                                  'restructuring, and to half of transformation value',
                                           read=TODAY, adopted='params commit 2026-10-29 (assumptions round 2, 1.3)'),
        'revealed_pace_reference_fy22_fy24': {
            'value': {'gaap_operating_margin_points': {'n': 149, 'p10': -7.8, 'p25': 2.1, 'median': 7.5, 'p75': 21.5, 'p90': 36.0},
                      'fcf_after_sbc_margin_points': {'n': 145, 'p10': -6.3, 'p25': 1.3, 'median': 9.5, 'p75': 23.5, 'p90': 35.4},
                      'gross_margin_less_ga_points': {'n': 129, 'p10': -2.8, 'p25': 0.4, 'median': 3.8, 'p75': 8.0, 'p90': 13.0},
                      'sm_share_points': {'n': 139, 'median': -3.7}, 'rd_share_points': {'n': 138, 'median': -1.2},
                      'ga_share_points': {'n': 140, 'median': -1.5}, 'sbc_share_points': {'n': 151, 'median': -0.9}},
            'quality': 'primary_data_fit', 'assumed': False, 'grounding': 'c', 'reference_only': True,
            'flag': 'to recompute on panel_v3: computed on data/panel_v2_all.csv, which the IM-1 sample audit is rebuilding',
            'source': 'assumptions round 2 (notes/assumptions_round2.md Section 1.5), own calculation on data/panel_v2_all.csv: SIC '
                      '7372, FY2022 revenue at least $100 million, firms reporting both FY2022 and FY2024; change FY2022 to FY2024',
            'unit': 'percentage points of revenue over two years',
            'note': 'class c reference, not used as a value: the median firm closed 7.5 points of GAAP operating margin in two years '
                    'with no AI program (cost programs remove cost on announcement); the model\'s central path is "AI migration '
                    'only". The lower quartile (about 5% of the gap a year) and the median (about 17%) bracket the cost-program pace.',
            'read': TODAY, 'adopted': 'params commit 2026-10-29 (assumptions round 2, 1.5)'},
    },
    # ============================================================== organization (spec 7), added by the assumptions audit
    'organization': {
        'span_of_control_oews': None,          # filled below from occupations.csv and industry_staffing.csv
        'ai_engineers_per_automated_process_run': None,
    },
}


# ================================================================== Section 17 AI product strategy (`product` block)
def LP(value, unit, source, url, note=None, retrieved=TODAY):
    """Vendor list price, verified on the vendor's own page on the retrieval date."""
    d = {'value': value, 'unit': unit, 'quality': 'vendor_price_list', 'source': source, 'url': url, 'retrieved': retrieved}
    if note:
        d['note'] = note
    d['assumed'] = False
    return d


_occ = pd.read_csv(f'{BASE}/data/tasks/occupations.csv', dtype={'soc': str})
_act = pd.read_csv(f'{BASE}/data/tasks/activities.csv')
_ifs = pd.read_csv(f'{BASE}/data/tasks/industry_function_shares.csv', dtype={'sic': str, 'naics': str})
CSR_WAGE = float(_occ.loc[_occ.soc == '43-4051', 'wage_median'].iloc[0])        # OEWS May 2025, customer service representatives
BLR_RPH = 1.7        # Brynjolfsson, Li and Raymond, arXiv:2304.11771: never-treated agents resolve 1.7 chats per hour
human_cost_per_resolution = CSR_WAGE / 2080 * (1 + load_hw['private_industry']) / BLR_RPH
SUPPORT_DWAS = {'4.A.4.a.8.c.2': 'Respond to customer inquiries', '4.A.4.a.8.c.3': 'Answer customer questions about goods or services',
                '4.A.4.a.3.c.8': 'Provide customers with general information or assistance',
                '4.A.4.b.6.b.2': 'Advise customers on technical or procedural issues'}
_sup = _act.set_index('dwa_id').loc[list(SUPPORT_DWAS)]
assert (_sup.dwa_title.str.rstrip('.') == pd.Series(SUPPORT_DWAS)).all(), 'support DWA titles changed'
assert _sup.est_task_hours_method.str.startswith('AEI').all()
aei_hours = {k: r(v, 3) for k, v in _sup.est_task_hours.items()}
tok_conv_anchor = [r(tok_hr * _sup.est_task_hours.min(), 3), r(tok_hr * _sup.est_task_hours.max(), 3)]
TOK_CONV = 0.05      # assumed million tokens per support conversation (agentic, with retrieval and tool calls)
cost_conv = {k: r(v * TOK_CONV, 4) for k, v in blend.items()}
_sw = _ifs[(_ifs.sic == '7372') & (_ifs.size_band == 'all') & (_ifs.cost_bucket == 'cogs')].iloc[0]

FIN_OWNER = ('owner: Fin (formerly Intercom), a Salesforce company since 10 Sep 2026 (Salesforce press release "Salesforce Completes Acquisition of Fin", 10 Sep 2026, https://www.salesforce.com/news/press-releases/2026/09/10/salesforce-completes-acquisition-of-fin/, read 29 Oct 2026).')
OUTCOME_PRICES = {
    'intercom_fin_per_outcome': LP(0.99, 'USD per outcome (one per conversation; a resolution is billed when no further help is requested '
                                         'after Fin\'s last answer)',
                                   'Fin (formerly Intercom), Fin AI Agent pricing on fin.ai/pricing and intercom.com/pricing, both read '
                                   '29 Oct 2026 in the author\'s browser',
                                   'https://fin.ai/pricing; https://www.intercom.com/pricing',
                                   note='the AI unit is per outcome ($0.99), not per resolution. Minimum 50 outcomes a month; qualifications '
                                        '$9.99 each; other billable outcomes: procedure handoffs, disqualifications, self-serve routings. '
                                        'Helpdesk seats (annual): Essential $29, Advanced $85, Expert $132 per seat per month. ' + FIN_OWNER),
    'salesforce_agentforce_per_conversation': LP(2.00, 'USD per conversation', 'Salesforce, Agentforce pricing page (Conversations option)',
                                                 'https://www.salesforce.com/agentforce/pricing/',
                                                 note='per-user alternatives on the same page: Agentforce add-ons $125 per user per month '
                                                      '(Sales, Service, Field Service); Agentforce 1 Editions from $550 per user per month '
                                                      'with 2.5M Flex Credits per org per year.'),
    'salesforce_agentforce_per_action': LP(0.10, 'USD per standard action (20 Flex Credits at $500 per 100,000 credits)',
                                           'Salesforce, Agentforce pricing page; Flex Credits rate card (updated 17 Jun 2026)',
                                           'https://www.salesforce.com/agentforce/pricing/; https://www.salesforce.com/en-us/wp-content/'
                                           'uploads/sites/4/assets/pdf/agentforce/Flex-Credits-Rate-Card-06.17.2026.pdf',
                                           note='rate card: standard and custom actions 20 credits, voice actions 30, Help Agent '
                                                'resolution 400 credits (= $2.00 at list).'),
    'hubspot_customer_agent_per_resolution': LP(0.50, 'USD per resolved conversation (50 HubSpot credits at $0.010 per credit)',
                                                'HubSpot company news (updated 13 Apr 2026): outcome-based pricing from 14 Apr 2026, '
                                                'previously $1.00 per conversation; HubSpot Credits page ($10 per 1,000 credits)',
                                                'https://www.hubspot.com/company-news/hubspots-customer-agent-and-prospecting-agent-now-you-'
                                                'pay-when-the-task-is-complete; https://www.hubspot.com/products/artificial-intelligence/credits',
                                                note='Prospecting Agent $1.00 per lead recommended for outreach (100 credits); voice 50 '
                                                     'credits per minute. A dated example of migration from per-conversation to '
                                                     'per-outcome pricing (price halved).'),
    'freshworks_freddy_ai_agent_per_session': LP(0.49, 'USD per session ($49 per 100 additional sessions; first 500 included)',
                                                 'Freshworks, Freshdesk pricing page', 'https://www.freshworks.com/freshdesk/pricing/',
                                                 note='the page does not define a session, so this is per use, not per resolution. Seats, '
                                                      'billed annually: Growth $19, Pro $55, Enterprise $89 per agent per month (Pro is '
                                                      'the middle paid tier and the low end of the product example seat range; '
                                                      'freshworks2026pricing, accessed 29 Oct 2026).'),
    'microsoft_copilot_studio_per_credit': LP(0.008, 'USD per Copilot Credit ($200 per pack of 25,000 credits per month)',
                                              'Microsoft, Copilot Studio plans and pricing page',
                                              'https://www.microsoft.com/en-us/copilot/pricing/copilot-studio',
                                              note='credits consumed per message or action not verified (the June 2026 licensing guide '
                                                   'PDF failed to load), so no per-task price is derived. Up to 20% off with pre-purchase.'),
}
# professional (middle) help-desk seat tiers, per agent a month, billed annually (product notes Section 6; author decision
# 29 Oct 2026: four vendors, named only as sources). Bib keys in part2/refs_product.bib; all accessed 29 Oct 2026.
SEAT_PRICES = {
    'freshworks_freshdesk_pro': dict(LP(55, 'USD per agent per month, billed annually',
                                        'Freshworks, Freshdesk pricing page: Pro, the middle of three paid plans',
                                        'https://www.freshworks.com/freshdesk/pricing/',
                                        note='"billed annually"; the page offers monthly billing but lists no monthly prices. Also '
                                             'Growth $19 and Enterprise $89.'), bib='freshworks2026pricing'),
    'intercom_advanced': dict(LP(85, 'USD per seat per month, billed annually',
                                 'Fin (formerly Intercom), intercom.com/pricing: Advanced, read 29 Oct 2026 in the author\'s browser',
                                 'https://www.intercom.com/pricing',
                                 note='also Essential $29 ($19 with a new-customer discount) and Expert $132. ' + FIN_OWNER),
                              bib='intercom2026pricing'),
    'hubspot_service_hub_professional': dict(LP(90, 'USD per seat per month, billed annually',
                                                'HubSpot, Service Hub Professional pricing page',
                                                'https://www.hubspot.com/pricing/service/professional',
                                                note='$100 per seat a month billed monthly. Also Starter $7 or $20 (the page does not '
                                                     'clearly label which is annual) and Enterprise $150.'),
                                             bib='hubspot2026servicepro'),
    'salesforce_service_cloud_pro_suite': dict(LP(100, 'USD per user per month, billed annually',
                                                  'Salesforce, Service Cloud pricing page: Pro Suite',
                                                  'https://www.salesforce.com/service/pricing/',
                                                  note='"starting price, billed annually, contract required"; fetched as '
                                                       'https://www.salesforce.com/service/pricing/?bc=HL (the bare URL was not on the '
                                                       'fetch allowlist). Also Starter Suite $25, Core $195, Advanced $395, Max $550.'),
                                               bib='salesforce2026servicepricing'),
}
_seat_annual = {k: 12 * v['value'] for k, v in SEAT_PRICES.items()}
_seat_sorted = sorted(_seat_annual.values())
_seat_median = float(np.median(_seat_sorted))          # even count: mean of the two middle values
SEAT_LABEL = {'freshworks_freshdesk_pro': 'Freshworks Freshdesk Pro', 'intercom_advanced': 'Fin (formerly Intercom) Advanced',
              'hubspot_service_hub_professional': 'HubSpot Service Hub Professional',
              'salesforce_service_cloud_pro_suite': 'Salesforce Service Cloud Pro Suite'}
_seat_name = {12 * v['value']: SEAT_LABEL[k] for k, v in SEAT_PRICES.items()}
assert len(_seat_name) == len(SEAT_PRICES), 'two vendors share an annual price; name lookup is ambiguous'
assert [min(_seat_sorted), max(_seat_sorted)] == [660, 1200] and _seat_median == 1050.0, (_seat_sorted, _seat_median)
SEAT_PRICES['annual_seat_price_professional_tier'] = dict(
    P(_seat_median, [min(_seat_sorted), max(_seat_sorted)], 'vendor_price_list',
      'our calculation from the four list prices above: 12 x monthly = ' + ', '.join(f'${v:,.0f}' for v in _seat_sorted) +
      ' a year; range = lowest to highest; central = median of the four annual prices, taken as the mean of the two middle '
      f'values (${_seat_sorted[1]:,.0f} {_seat_name[_seat_sorted[1]]} and ${_seat_sorted[2]:,.0f} {_seat_name[_seat_sorted[2]]}) = '
      f'${_seat_median:,.0f}',
      unit='USD per agent (seat) per year, billed annually',
      note=f'the lower and upper medians would be ${_seat_sorted[1]:,.0f} and ${_seat_sorted[2]:,.0f}. List prices, not '
           'transaction prices (discounts and multi-year terms are not public). Wider published span, not used for the '
           'range: under $25 to $550 a month (Starter and Max tiers).'),
    grounding='a')

_res_prices = {k: v['value'] for k, v in OUTCOME_PRICES.items()
               if k in ('intercom_fin_per_outcome', 'salesforce_agentforce_per_conversation', 'hubspot_customer_agent_per_resolution')}
theta_implied = {k: r(v / human_cost_per_resolution, 3) for k, v in _res_prices.items()}

product = {
    'bass_diffusion': {
        'p_innovation': P(0.027, [0.012, 0.03], 'peer_reviewed',
                          'Van den Bulte and Stremersch (2004), Social Contagion and Income Heterogeneity in New Product Diffusion: '
                          'A Meta-Analytic Test, Marketing Science 23(4), 530-544, doi:10.1287/mksc.1040.0054: 293 observations, '
                          '52 consumer durables, 28 countries, 46 publications; p mean 0.027, median 0.012 (p. 537)',
                          unit='per year', note='range = their median to the Sultan et al. mean. Consumer durables, annual data.'),
        'q_imitation': P(0.419, [0.38, 0.42], 'peer_reviewed',
                         'Van den Bulte and Stremersch (2004): q mean 0.419, median 0.420 (p. 537)', unit='per year',
                         note='low end of range = Sultan et al. (1990) mean'),
        'sultan_farley_lehmann_1990': {
            'value': {'p': 0.03, 'q': 0.38, 'n_applications': 213, 'n_articles': 15}, 'quality': 'secondary', 'assumed': False,
            'source': 'Sultan, Farley and Lehmann (1990), A Meta-Analysis of Applications of Diffusion Models, Journal of Marketing '
                      'Research 27 (February), 70-77 (citation and abstract verified at business.columbia.edu); mean p and q '
                      'read in Nam (2011, Rutgers working paper) and Orbach (2016), Innovative Marketing 12(1), p. 30, '
                      'doi:10.21511/im.12(1).2016.03',
            'note': 'the JMR original was not opened, so the averages are secondary; used only as a cross-check and range bound.'},
        'software_or_it_specific': {
            'value': None, 'quality': 'unsupported', 'assumed': False,
            'source': 'no verified software or IT category estimate found. Van den Bulte and Stremersch (2004) code PCs, VCRs and '
                      'cellular telephones as competing-standards products and find them more strongly S-shaped (higher q/p, '
                      'p. 541) but report no category p and q. Givon, Mahajan and Muller (1995), Journal of Marketing 59(1), 29-37, '
                      'estimate software diffusion in the UK; their PC parameters as quoted by Waters (2013, MPRA 46036) are on a '
                      'different time scale and are not used.'},
        'ai_feature_within_installed_base': {
            'p': P(0.05, [0.01, 0.15], 'assumed', 'assumed: an AI feature sold into an existing customer base (no new-logo '
                                                  'acquisition) diffuses faster than a new consumer durable'),
            'q': P(0.50, [0.25, 0.90], 'assumed', 'assumed; anchored above the meta-analytic mean'),
        },
    },
    'gross_margin': {
        'ai_product_gross_margin_by_year': {
            'value': {'2025': 0.45, '2026_projected': 0.53, '2027_projected': 0.59}, 'range': {'2025': [0.40, 0.50]},
            'quality': 'practitioner_survey_disclosed', 'assumed': False,
            'source': 'ICONIQ (2026), State of AI: The Builder\'s Economy, July 2026 (refs.bib: iconiq2026state), '
                      'https://www.iconiq.com/growth/reports/state-of-ai-2026, re-read 29 Oct 2026: "jumping from 45% in 2025 to a '
                      'projected 53% in 2026, and 59% in 2027"',
            'note': 'survey of about 300 executives at software companies building AI products (Q2 2026, 87% North America); '
                    '2026 and 2027 are respondent projections, not measurements. 2025 range assumed. Confirms ref_verification.md.'},
        'subscription_software_gross_margin_reference': P(r(1 - _sw.bucket_share_median, 3), [r(1 - _sw.bucket_share_mean, 3), r(1 - _sw.bucket_share_median, 3)],
                                                           'primary_data_fit',
                                                           f'1 - median cost-of-revenue share, SIC 7372, {int(_sw.n_firms)} firms, '
                                                           f'{_sw.years} (industry_function_shares.csv, SEC XBRL panel)',
                                                           note='use this, not the unsourced "75-80% for classic SaaS" '
                                                                '(not in ICONIQ; audit_report.md item 26). Range low = 1 - mean.'),
    },
    'outcome_and_usage_list_prices': OUTCOME_PRICES,
    'seat_list_prices': SEAT_PRICES,
    'outcome_pricing_not_public': {
        'value': ['Sierra (outcome-based, prices by quote)', 'Decagon (per conversation or resolution, by quote)'],
        'quality': 'unsupported', 'assumed': False,
        'source': 'no public list price on the vendors\' pages; not used'},
    'capture_share': {
        'human_cost_per_resolution_usd': P(r(human_cost_per_resolution, 2), [r(human_cost_per_resolution * 0.5, 2), r(human_cost_per_resolution * 1.5, 2)],
                                           'primary_data_fit',
                                           'our calculation: OEWS May 2025 median wage, customer service representatives (43-4051) '
                                           f'${CSR_WAGE:,.0f} / 2080 x (1 + tau_L per hour worked, ECEC private) / 1.7 resolutions per hour '
                                           '(never-treated agents, Brynjolfsson, Li and Raymond, arXiv:2304.11771; published QJE 140(2), '
                                           '889-942, 2025)',
                                           note='range +/-50% assumed (agents in the study handle concurrent chats at one Fortune 500 '
                                                'software firm; U.S. wage applied to their throughput).'),
        'implied_capture_share_theta_cap_at_list_price': {
            'value': theta_implied, 'range': [min(theta_implied.values()), max(theta_implied.values())],
            'quality': 'vendor_price_list', 'assumed': False,
            'source': 'our calculation: list price per outcome, resolution or conversation / human_cost_per_resolution_usd',
            'note': 'assumes one AI outcome or resolution displaces one human resolution. AI agents resolve the simpler contacts, '
                    'which take less human time, so the capture share of the cost actually displaced is higher than shown. '
                    'Not independent observations: Salesforce and Fin (formerly Intercom) share a parent since 10 Sep 2026, so two '
                    f'of the three list prices ({theta_implied["intercom_fin_per_outcome"]} and '
                    f'{theta_implied["salesforce_agentforce_per_conversation"]}) come from one corporate group.'},
        'theta_cap_default': dict(P(0.10, [0.03, 0.30], 'vendor_price_list',
                               'grounded by the list-price-implied shares above (HubSpot '
                               f'{theta_implied["hubspot_customer_agent_per_resolution"]}, Fin (formerly Intercom) {theta_implied["intercom_fin_per_outcome"]}, '
                               f'Salesforce {theta_implied["salesforce_agentforce_per_conversation"]}): central 0.10 near the upper list-price share; high end '
                               '0.30 allows for scarce-input rents (data, workflow, distribution, trust) and is not sourced'),
                                  grounding='b', analogy='published per-resolution prices of AI support agents relative to the loaded '
                                                         'cost of a human resolution, for labor-substituting products in general',
                                  note='the engine default product.theta_cap is 0.25 [0.1, 0.5], unlinked and above every list-price '
                                       'share; it should link here (audit, 29 Oct 2026)'),
    },
    'seat_compression': {
        'evidence_flag': {'value': 'thin', 'quality': 'unsupported', 'assumed': False,
                          'source': 'no peer-reviewed or disclosed-method estimate of the elasticity of software seats to customer '
                                    'automation was found; trade-press claims of "the end of per-seat pricing" are not used'},
        'bls_projection_csr_2025_35': P(r(-141800 / 2666000, 4), [-0.055, r(-141800 / 2666000, 4)], 'government',
                                        'BLS Occupational Outlook Handbook, Customer Service Representatives (modified 27 Aug 2026): '
                                        'employment 2,666,000 (2025) to 2,524,100 (2035), -141,800, "projected to decline 5 percent", '
                                        'as tasks "continue to be automated" and self-service spreads. BLS TED, 16 Jul 2026 (2024-34 '
                                        'projections): -5.5% (-153,700), with AI productivity gains expected to dampen labour demand',
                                        unit='share change over 10 years',
                                        note=f'about {r((2524100 / 2666000) ** 0.1 - 1, 4)} a year. An official projection, not a '
                                             'measurement; a lower bound on support-seat erosion at customers that adopt AI agents. '
                                             'Office and administrative support group: -4.0% (-752,100), 2025-35 (Employment '
                                             'Projections release, 27 Aug 2026).'),
        'klarna_2024_ai_assistant': {
            'value': {'fte_equivalent_work': 700, 'share_of_chats': 0.67, 'conversations_first_month': 2300000,
                      'resolution_minutes_before_after': [11, 2], 'repeat_inquiry_change': -0.25},
            'quality': 'company_statement', 'assumed': False,
            'source': 'Klarna press release, 27 Feb 2024, https://www.klarna.com/international/press/klarna-ai-assistant-handles-'
                      'two-thirds-of-customer-service-chats-in-its-first-month/',
            'note': 'one firm\'s unaudited claim (customer service is partly outsourced, so the 700 are not all Klarna seats); '
                    'illustration only'},
        'aei_automation_pattern_share_support_dwas': P(r(_sup.aei_automation_pct.mean() / 100, 3),
                                                       [r(_sup.aei_automation_pct.min() / 100, 3), r(_sup.aei_automation_pct.max() / 100, 3)],
                                                       'primary_data_fit',
                                                       'Anthropic Economic Index 2026-06-26, collaboration_bucket_automation_pct for DWAs '
                                                       + ', '.join(SUPPORT_DWAS), note='share of Claude.ai conversations on these activities '
                                                       'with a directive or automation pattern; a usage pattern, not displaced seats'),
        'seat_elasticity_epsilon_seat': dict(grounding='d', **P(1.0, [0.3, 1.2], 'assumed',
                                          'assumed: % change in seats per % change in customer FTE in the occupations the seats serve. '
                                          'Below 1 when seats are kept for supervisors, reviewers and escalations; above 1 when '
                                          'automation triggers licence consolidation. No public filing reports seat counts against '
                                          'customer headcount, so no elasticity can be computed (searched 29 Oct 2026); scenario dimension')),
        'seat_lag_years': P(1.0, [0.5, 2.0], 'assumed', 'assumed lag from customer automation to seat reduction (renewal cycle)'),
    },
    'inference_usage': {
        'aei_source_note': {'value': 'no token or cost facet in the local AEI files', 'quality': 'unsupported', 'assumed': False,
                            'source': 'release_2026_06_26 claude_ai file has time, autonomy, collaboration and artifact metrics '
                                      'only; the 1p_api file is not in data/raw/anthropic_aei/'},
        'tokens_per_support_conversation_mtok': P(TOK_CONV, [0.01, 0.20], 'assumed',
                                                  'assumed for an agentic support conversation with retrieval and tool calls',
                                                  unit='million tokens (input plus output)',
                                                  note=f'upper anchor {tok_conv_anchor[0]}-{tok_conv_anchor[1]} Mtok = ai_cost.tokens_per_human_hour '
                                                       f'x AEI human_only_time_mean for support DWAs ({aei_hours} hours); METR tokens are '
                                                       'from agentic software tasks, so the anchor is likely high for chat support'),
        'inference_cost_per_support_conversation_usd': {
            'value': cost_conv, 'range_multiplier': [0.2, 4.0], 'quality': 'assumed', 'assumed': True,
            'source': 'tokens_per_support_conversation_mtok x ai_cost.blended_price_usd_per_mtok (list prices x assumed token mix)'},
        'inference_share_of_outcome_price': P(r(cost_conv['claude_sonnet_5_5'] / 0.99, 3), [0.005, 0.40], 'assumed',
                                              'Sonnet 5.5-tier cost per conversation / Fin list price per outcome',
                                              note='excludes retrieval, hosting, evaluation and human escalation costs, which ICONIQ\'s '
                                                   '45% gross margin implies are large'),
        'conversations_per_resolution': P(1.4, [1.0, 2.5], 'assumed', 'assumed conversations billed or run per billable resolution'),
    },
    'pricing_migration': {
        'migration_cost_share_of_migrated_arr': P(0.05, [0.02, 0.15], 'assumed',
                                                  'assumed one-off cost: billing and metering build, contract renegotiation, sales '
                                                  'compensation redesign, customer communication'),
        'transition_revenue_dip_share': P(0.05, [0.0, 0.15], 'assumed', 'assumed share of migrated ARR lost during the transition'),
        'transition_dip_duration_years': P(1.0, [0.5, 2.0], 'assumed', 'assumed; links to transition.j_curve'),
        'churn_uplift_pp_during_migration': P(0.02, [0.0, 0.08], 'assumed', 'assumed addition to annual gross revenue churn'),
        'forecast_error_multiplier_usage_vs_seat': P(2.0, [1.2, 4.0], 'assumed',
                                                     'assumed ratio of revenue forecast error (sd) under usage or outcome pricing to seat pricing'),
        'price_cut_at_migration_share': P(0.0, [-0.5, 0.2], 'assumed',
                                          'assumed change in price per unit of value at migration; HubSpot halved its per-unit price '
                                          'when moving from per conversation to per resolution (see list prices)'),
        'migration_duration_years': P(1.5, [1.0, 3.0], 'assumed', 'assumed time to move the installed base (renewal cycles)'),
    },
}

# ================================================================== Section 18 security, maintenance and ancillary costs
D = pd.Timestamp
LIFE = [  # (vendor, model, release date, retirement or announced shutdown date, release-date source)
    ('Anthropic', 'claude-3-sonnet-20240229', '2024-03-04', '2025-07-21', 'METR'),
    ('Anthropic', 'claude-3-opus-20240229', '2024-03-04', '2026-01-05', 'METR'),
    ('Anthropic', 'claude-3-5-sonnet-20240620', '2024-06-20', '2025-10-28', 'METR'),
    ('Anthropic', 'claude-3-5-sonnet-20241022', '2024-10-22', '2025-10-28', 'METR'),
    ('Anthropic', 'claude-3-7-sonnet-20250219', '2025-02-24', '2026-02-19', 'METR'),
    ('Anthropic', 'claude-sonnet-4-20250514', '2025-05-22', '2026-06-15', 'METR'),
    ('Anthropic', 'claude-opus-4-20250514', '2025-05-22', '2026-06-15', 'METR'),
    ('Anthropic', 'claude-opus-4-1-20250805', '2025-08-05', '2026-08-05', 'METR'),
    ('Anthropic', 'claude-sonnet-4-5-20250929', '2025-09-29', '2026-11-30', 'METR'),
    ('OpenAI', 'gpt-4-0314', '2023-03-14', '2026-03-26', 'METR'),
    ('OpenAI', 'gpt-4-0613', '2023-06-13', '2026-10-23', 'METR'),
    ('OpenAI', 'gpt-4-turbo-2024-04-09', '2024-04-09', '2026-10-23', 'METR'),
    ('OpenAI', 'gpt-4o-2024-05-13', '2024-05-13', '2026-10-23', 'METR'),
    ('OpenAI', 'gpt-4o-mini-2024-07-18', '2024-07-18', '2027-01-14', 'METR'),
    ('OpenAI', 'o1-2024-12-17', '2024-12-05', '2026-10-23', 'METR'),
    ('OpenAI', 'o3-2025-04-16', '2025-04-16', '2026-12-11', 'METR'),
    ('OpenAI', 'o4-mini-2025-04-16', '2025-04-16', '2026-10-23', 'METR'),
    ('OpenAI', 'gpt-4.1-2025-04-14', '2025-04-14', '2027-01-14', 'snapshot date in model ID'),
    ('OpenAI', 'gpt-5-2025-08-07', '2025-08-07', '2026-12-11', 'METR'),
    ('OpenAI', 'gpt-5.1-2025-11-13', '2025-11-13', '2027-04-01', 'snapshot date in model ID'),
    ('OpenAI', 'gpt-5.3-codex', '2026-02-05', '2027-04-01', 'METR'),
    ('Google', 'gemini-2.0-flash', '2025-02-05', '2026-06-01', 'Gemini API deprecations page'),
    ('Google', 'gemini-2.0-flash-lite', '2025-02-25', '2026-06-01', 'Gemini API deprecations page'),
    ('Google', 'gemini-3.1-flash-lite', '2026-05-07', '2027-05-07', 'Gemini API deprecations page'),
]
_life = pd.DataFrame(LIFE, columns=['vendor', 'model', 'release', 'retire', 'release_source'])
_life['years'] = (_life.retire.map(D) - _life.release.map(D)).dt.days / 365.25
_recent = _life[_life.release.map(D) >= D('2025-01-01')]
life_med_all, life_med_recent = r(_life.years.median(), 2), r(_recent.years.median(), 2)
life_by_vendor = {v: r(g.years.median(), 2) for v, g in _life.groupby('vendor')}
NOTICE_ANTHROPIC = [('2026-09-30', '2026-11-30'), ('2026-06-05', '2026-08-05'), ('2026-04-14', '2026-06-15'), ('2026-02-19', '2026-04-20'),
                    ('2025-12-19', '2026-02-19'), ('2025-10-28', '2026-02-19'), ('2025-08-13', '2025-10-28'), ('2025-06-30', '2026-01-05'),
                    ('2025-01-21', '2025-07-21'), ('2024-09-04', '2024-11-06')]
notice_days = [(D(b) - D(a)).days for a, b in NOTICE_ANTHROPIC]
SVANBERG = dict(impl=1765000, maint=242840, bare_impl=165000, bare_maint=122840)
ATD = dict(usd_2025=846, usd_2024=1254, hours_2025=16.7)

security_and_maintenance = {
    'breach_cost': {
        'global_average_usd': P(4990000, [4440000, 11500000], 'practitioner_survey_disclosed',
                                'IBM and Ponemon Institute, Cost of a Data Breach Report 2026 (29 Jul 2026), ibm.com/reports/data-breach '
                                'and IBM newsroom: global average $4.99M, up 12%, a record; 602 organizations breached between Mar 2025 '
                                'and Feb 2026; 2025 edition: $4.44M (IBM X-Force, 30 Jul 2025)',
                                note='average over breached organizations, not a hazard or a per-process loss. Range: 2025 global '
                                     'average to the 2026 U.S. average. Detection and escalation plus lost business are 63% of cost.'),
        'us_average_usd': P(11500000, [4990000, 11500000], 'secondary',
                            'Baker Donelson, Ten takeaways from IBM\'s 2026 Cost of a Data Breach Report (30 Jul 2026): U.S. $11.5M, '
                            'up 11%', note='not on the IBM pages read; the same summary\'s financial-sector figure ($6.29M) matches '
                                           'IBM\'s own ($6.3M). Range low = global average.'),
        'by_industry_usd': {'value': {'financial_services': 6300000, 'energy': 5200000, 'healthcare': 6640000},
                            'quality': 'practitioner_survey_disclosed', 'assumed': False,
                            'source': 'IBM newsroom, 29 Jul 2026 (financial services $6.3M, energy $5.2M); healthcare $6.64M (highest) '
                                      'from the Baker Donelson summary (secondary)'},
        'mean_days_to_identify_and_contain': P(247, [241, 247], 'secondary',
                                               'Baker Donelson summary of the 2026 report: 247 days; IBM X-Force (30 Jul 2025): 241 days '
                                               'in the 2025 edition'),
        'savings_from_extensive_security_ai_usd': P(1930000, [1930000, 1930000], 'practitioner_survey_disclosed',
                                                    'IBM 2026: $1.93M lower breach cost with extensive AI and automation in security '
                                                    'operations vs none', note='cross-sectional comparison, not a causal estimate'),
        'per_process_loss_share_of_average_L_inc': P(0.30, [0.05, 1.0], 'assumed',
                                                     'assumed L_inc,j as a share of the average breach cost for an incident confined '
                                                     'to one automated process'),
    },
    'ai_specific_incidents': {
        'share_of_orgs_with_ai_related_breach': P(0.20, [0.13, 0.20], 'practitioner_survey_disclosed',
                                                  'IBM 2026: "roughly one in five" (newsroom: "more than 20%") of breached organizations '
                                                  'reported a breach of AI models or applications; 2025 edition: 13%',
                                                  note='share of breached organizations, not of all organizations'),
        'share_lacking_ai_access_controls': P(0.92, [0.92, 0.97], 'practitioner_survey_disclosed',
                                              'IBM 2026: 92% of organizations with an AI-related breach lacked proper AI access controls '
                                              '(2025: 97%); only 40% use access controls on AI models and data'),
        'avg_loss_prompt_injection_usd': P(5890000, [4990000, 6070000], 'practitioner_survey_disclosed',
                                           'IBM X-Force, 29 Jul 2026: prompt injection average loss $5.89M; model inversion $6.07M',
                                           note='small subsamples, not stated; range assumed between the global average and model inversion'),
        'avg_cost_ai_enabled_malicious_breach_usd': P(6000000, [5000000, 6100000], 'practitioner_survey_disclosed',
                                                      'IBM newsroom 29 Jul 2026: one in four malicious breaches AI-enabled (up 56%), '
                                                      'costing $6M on average, about $1M above the global average', note='range assumed'),
        'shadow_ai_cost_premium_usd': P(670000, [670000, 760000], 'practitioner_survey_disclosed',
                                        'IBM X-Force (30 Jul 2025): shadow AI added $670,000 to the average breach; 2026 per Baker '
                                        'Donelson (secondary): incidence 43% (20% in 2025), cost $5.39M vs $4.63M (+$760,000)'),
        'share_without_ai_governance_policy_2025': P(0.63, [0.63, 0.63], 'practitioner_survey_disclosed',
                                                     'IBM X-Force (30 Jul 2025): 63% of breached organizations had no AI governance policy'),
    },
    'exposure_and_hazard': {
        'incident_hazard_h_inc_per_process_year': P(0.02, [0.005, 0.10], 'assumed',
                                                    'assumed annual probability of a material incident for one automated process at '
                                                    'baseline exposure and security spend; IBM/Ponemon samples breached firms only and '
                                                    'gives no hazard'),
        'exposure_multipliers_e_j': {
            'value': {'data_sensitivity': {'public': 0.2, 'internal': 1.0, 'confidential': 2.0, 'regulated_pii_phi_pci': 4.0},
                      'autonomy': {'read_only': 0.5, 'draft_for_human': 1.0, 'write': 2.0, 'transact': 3.0},
                      'integration_breadth_elasticity': 0.5, 'external_untrusted_input': 2.0},
            'range': 'each multiplier x0.5 to x2', 'quality': 'assumed', 'assumed': True,
            'source': 'assumed; direction from spec 18.2. External untrusted input (indirect prompt injection; Greshake et al. 2023, '
                      'literature agent) doubles exposure. e_j = product of multipliers x (systems reachable)^elasticity'},
        'hazard_elasticity_to_security_spend': P(0.5, [0.2, 1.0], 'assumed',
                                                 'assumed elasticity of h_inc to s_sec; a Gordon-Loeb Class I form '
                                                 'S = v / (alpha z + 1)^beta can be fitted to it'),
    },
    'gordon_loeb_bound': P(r(1 / math.e, 4), [0.0, r(1 / math.e, 4)], 'peer_reviewed',
                           'Gordon and Loeb (2002), The Economics of Information Security Investment, ACM Transactions on Information '
                           'and System Security 5(4), 438-457, Proposition 3: optimal investment is at most (1/e) vL, "36.79% of the '
                           'loss" expected without investment (paper copy read; also UMD Smith School summary)',
                           unit='max security investment / expected loss without investment',
                           note='holds for breach-probability classes S_I = v/(alpha z + 1)^beta (beta >= 1) and S_II = v^(alpha z + 1); '
                                'assumes no incremental fixed costs of security.'),
    'security_spend': {
        'share_of_it_spend': P(0.099, [0.086, 0.119], 'practitioner_survey_disclosed',
                               'IANS Research and Artico Search, 2026 Security Budget Benchmark Report (more than 500 CISOs): 9.9% of '
                               'IT spend; 2025 edition (5 Aug 2025; 587 CISOs, data Apr-Aug 2025): 10.9%, from 11.9% in 2024 and 8.6% '
                               'in 2020', note='self-reported CISO survey, mostly larger firms; 2026 survey period not stated. Range = '
                                               '2020 low to 2024 high.'),
        'share_of_revenue': P(0.0069, [0.0069, 0.0069], 'practitioner_survey_disclosed', 'IANS 2025: 0.69% of revenue, flat'),
        'macro_ratio_reference': {'value': r(213 / 5577, 3), 'quality': 'prediction', 'assumed': False,
                                  'source': 'Gartner press releases: information security end-user spending $213B in 2025 (29 Jul 2025; '
                                            '$240B forecast for 2026) over worldwide IT spending $5,577B in 2025 (27 Jul 2026)',
                                  'note': 'worldwide forecasts of different vintages and scope; lower than the CISO-survey share because '
                                          'IT spending includes devices and telecom; context only'},
    },
    'model_lifecycle': {
        'anthropic_min_notice_days': P(60, [min(notice_days), max(notice_days)], 'vendor_documentation',
                                       'Anthropic, Model deprecations, platform.claude.com/docs/en/about-claude/model-deprecations '
                                       f'(read {TODAY}): "at least 60 days\' notice before model retirement for publicly released models"',
                                       note=f'observed notice in the deprecation history: {sorted(notice_days)} days. Active models list '
                                            '"not sooner than" retirement dates one year after launch (e.g. Opus 4.6, launched 5 Feb 2026: '
                                            'not sooner than 5 Feb 2027).'),
        'openai_min_notice_months': {'value': {'generally_available': 6, 'specialized_variant': 3, 'preview': 0.5},
                                     'quality': 'vendor_documentation', 'assumed': False,
                                     'source': f'OpenAI, Deprecations, developers.openai.com/api/docs/deprecations (read {TODAY}): '
                                               '"Generally available models: At least 6 months"; specialized variants "At least 3 '
                                               'months"; previews "may be retired with much shorter notice, such as 2 weeks"'},
        'azure_foundry_lifecycle_months': {'value': {'deprecated_for_new_customers': 12, 'retired': 18,
                                                     'retired_anthropic_deepseek_fireworks_mistral': 12, 'ga_notice_days': 60,
                                                     'preview_notice_days': 30},
                                           'quality': 'vendor_documentation', 'assumed': False,
                                           'source': 'Microsoft, Foundry Models lifecycle and support policy, learn.microsoft.com/en-us/'
                                                     'azure/foundry/openai/concepts/model-retirements (updated 24 Jul 2026)',
                                           'note': 'retirement dates not extendable; Standard deployments auto-upgrade, Provisioned do not'},
        'aws_bedrock_legacy_period_months': {'value': {'most_models': 6, 'short': 1.5}, 'quality': 'vendor_documentation', 'assumed': False,
                                             'source': 'AWS, Amazon Bedrock model lifecycle, docs.aws.amazon.com/bedrock/latest/userguide/'
                                                       'model-lifecycle.html (read 29 Oct 2026): Legacy (notice) period 6 months or 45 days; '
                                                       'per-model "EOL no sooner than" dates; applies to models launched on or after 7 Sep 2026'},
        'google_gemini_api_policy': {'value': 'no notice period stated', 'quality': 'vendor_documentation', 'assumed': False,
                                     'source': 'Google, Gemini deprecations, ai.google.dev/gemini-api/docs/deprecations (updated 22 Oct '
                                               '2026): listed shutdown dates are "the earliest possible dates"; exact dates communicated '
                                               '"with advance notice". The Vertex AI model-versions page could not be read'},
        'observed_ga_lifetime_years': {
            'value': {'median_all': life_med_all, 'median_released_2025_onward': life_med_recent, 'by_vendor_median': life_by_vendor,
                      'n_models': len(_life), 'n_released_2025_onward': len(_recent)},
            'range': [r(_life.years.min(), 2), r(_life.years.max(), 2)], 'quality': 'primary_data_fit', 'assumed': False,
            'source': 'our calculation, 08_params.py LIFE table: release dates from METR release_dates.yaml (two from snapshot dates in '
                      'the model ID, three from the Gemini page), retirement or announced shutdown dates from the vendor pages above',
            'note': 'GA text models only (previews excluded); models still active with no date are right-censored and excluded, '
                    'which biases the recent median down.'},
        'T_up_years': P(life_med_recent, [0.5, r(_recent.years.max(), 2)], 'primary_data_fit',
                        'median release-to-retirement time of GA models released from 2025 (observed_ga_lifetime_years)',
                        note='forced revalidation interval for API builds; low end 0.5 assumed for firms that upgrade voluntarily '
                             'when a better model ships.'),
        'revalidation_cost_C_reval_share_of_F_A': P(0.10, [0.03, 0.30], 'assumed',
                                                    'assumed: rerun evaluation suites, prompt and agent rework, regression fixes, sign-off'),
    },
    'maintenance': {
        'mu_m_share_of_F_A_per_year': dict(P(0.17, [0.10, 0.40], 'working_paper',
                                        'precedents: Svanberg et al. (2024, MIT FutureTech working paper, see ai_cost.build_fixed_cost_F_A): '
                                        f"computer-vision system maintenance ${SVANBERG['maint']:,} a year on ${SVANBERG['impl']:,} "
                                        f"implementation = {r(SVANBERG['maint'] / SVANBERG['impl'], 3)}; bare-bones "
                                        f"{r(SVANBERG['bare_maint'] / SVANBERG['bare_impl'], 3)} (a fixed floor). Enterprise-software support "
                                        'fees: SAP Basic Support 17% and Enterprise Support 22% of the license price a year (CIO.com, 10 Apr '
                                        '2008, reporting SAP\'s Jan 2008 change; secondary)',
                                        note='central 0.17 = median of 0.138 (Svanberg), 0.17 and 0.22 (SAP). Covers prompt and agent upkeep, '
                                             'eval suites, monitoring, data-pipeline upkeep and drift. Sculley et al. (2015), Hidden Technical '
                                             'Debt in Machine Learning Systems, NIPS 28, find it "common to incur massive ongoing maintenance '
                                             'costs" but give no share. Raised from the assumed 0.15 by the audit of 29 Oct 2026.'),
                                           grounding='b', analogy='annual upkeep of a deployed AI system and vendor maintenance of licensed '
                                                                  'enterprise software, both as a share of the initial build or license'),
        'maintenance_increment_per_integration': P(0.05, [0.02, 0.10], 'assumed',
                                                   'assumed proportional increase in M_A per additional integrated system (coupling; '
                                                   'Sculley et al. 2015, qualitative)'),
        'vendor_maintenance_share_of_inhouse': P(0.30, [0.10, 0.60], 'assumed',
                                                 'assumed maintenance a SaaS or agent-platform customer bears, relative to an in-house build'),
        'switching_cost_months_of_contract': P(6, [2, 18], 'assumed', 'assumed lock-in cost: re-integration, data migration, revalidation'),
    },
    'compliance': {
        'soc2_type1_audit_fee_usd': P(15000, [5000, 60000], 'practitioner_survey_undisclosed',
                                      'Drata, How Much Does a SOC 2 Audit Cost? (25 Mar 2026): $7,500-15,000 small to midsize, '
                                      '$20,000-60,000 large; Secureframe SOC 2 audit cost page (undated, (c) 2026): about $5-20k',
                                      note='vendor estimates with no stated method; vendors sell compliance automation (flag)'),
        'soc2_type2_audit_fee_usd': P(30000, [12000, 150000], 'practitioner_survey_undisclosed',
                                      'Drata (25 Mar 2026): $12,000-20,000 small to midsize, $30,000-100,000+ large; Secureframe: $7k-150k, '
                                      'example firm quote $30,000 Type II', note='flag as above'),
        'soc2_first_year_total_usd': P(80000, [25000, 350000], 'practitioner_survey_undisclosed',
                                       'Drata: $25,000 (small startup) to over $200,000 (large enterprise) including readiness, tooling '
                                       'and staff time; Secureframe: $80-350k total including annual maintenance',
                                       note='internal staff time, "the largest hidden cost" (Drata), is not priced by either'),
        'soc2_annual_maintenance_usd': P(35000, [10000, 60000], 'practitioner_survey_undisclosed', 'Secureframe: $10-60k a year'),
        'iso42001_certification_audit_usd': P(13500, [5000, 20000], 'practitioner_survey_undisclosed',
                                              'Vanta, ISO 42001 certification costs (undated, (c) 2026): initial certification audit '
                                              '"typically $7,000-$20,000" ($5,000-20,000 in its summary table)',
                                              note='"based on anecdotal data"; ISO publishes no cost benchmarks (Vanta)'),
        'iso42001_surveillance_audit_usd_per_year': P(6000, [2500, 9000], 'practitioner_survey_undisclosed',
                                                      'Vanta: surveillance audits $3,500-9,000; illustrative table $2,500-3,500'),
        'iso42001_readiness_and_implementation_usd': P(30000, [13000, 50000], 'practitioner_survey_undisclosed',
                                                       'Vanta: gap analysis $3,000-10,000+, implementation $10,000-40,000+; initial '
                                                       'certification overall "several thousand dollars to $75,000+"'),
        'sox404_compliance_cost_usd_reference': {
            'value': {'mean_post_reform': 2330000, 'median_post_reform': 1040000, 'mean_non_accelerated': 690000},
            'quality': 'government', 'assumed': False, 'grounding': 'ref',
            'source': 'SEC Office of Economic Analysis (Sept 2009), Study of the Sarbanes-Oxley Act of 2002 Section 404 Internal Control '
                      'over Financial Reporting Requirements (copy at dair.nps.edu, SEC809-SMP-09-0052.pdf): 2,907 responding firms; '
                      'Section 404(b) firms mean $2.87M before and $2.33M after the 2007 reforms, median $1.19M and $1.04M; '
                      'non-accelerated filers mean $690,000; costs scaled by assets fall with size',
            # round 2 (C3, notes/r2_propagation.md item 5): superseded in the direct cost of accountability
            'note': Hand('firm-level accountability cost, a component of Part I\'s a_min (see part1_ceiling.a_min); 2007-08 '
                         'dollars. Superseded',
                         'in the direct cost of accountability by Paper 1 round 2 (C3, 2 Nov 2026), which uses the KPMG 2025 SOX '
                         'program budget',
                         'by revenue size plus the accelerated-filer audit fee (audit_fee_accelerated_filer_reference); kept as '
                         'a reference', quoted=True)},
        # ---- assumptions round 2, Sections 5.3 and 5.5 (adopted 29 Oct 2026); by_revenue_size added in Paper 1 round 2 (C3)
        'sox_program_cost_kpmg_2025_reference': {
            'value': {'budget_usd': 2300000, 'hours': 15581, 'key_controls': 546, 'itgc_controls': 149, 'itac_controls': 78,
                      'in_scope_systems': 40, 'test_hours_per_control': 16, 'usd_per_in_scope_system': r(2.3e6 / 40, 0),
                      'itgc_usd_per_in_scope_system': r(2.3e6 / 40 * 149 / 546, 0), 'usd_per_key_control': r(2.3e6 / 546, 0)},
            'quality': 'practitioner_survey_disclosed', 'assumed': False, 'grounding': 'ref',
            'source': 'KPMG, The 2025 SOX Survey (kpmg.com/kpmg-us/content/dam/kpmg/pdf/2025/the-2025-sox-survey.pdf; read 29 Oct 2026): '
                      'web survey Apr-Jun 2025 of 146 U.S. SOX 404 program owners, FY2024 results; average budget $2.3M and 15,581 '
                      'hours; 546 key controls (319 business process, 149 ITGC, 78 ITAC); 40 in-scope systems; 16 testing hours per '
                      'control. Derived: about $57,500 of SOX program cost per in-scope system a year, about $16,000 on the ITGC share',
            'note': 'precedent for icfr_line_per_in_scope_ai_application_usd and regulated_build_multiplier', 'read': TODAY,
            # round 2 (C3 and the lead agent's KPMG ruling, notes/r2_code_changes.md "Follow-up 2 Nov" item 3): the SOX
            # program budget by revenue class, the direct cost of the accountability floor (under $5B: $1.5M)
            'by_revenue_size': {
                'value': {'under_5b_usd': 1500000, '5b_to_25b_usd': 2700000, '25b_and_above_usd': 4700000},
                'source': 'KPMG, The 2025 SOX Survey, archived copy (https://web.archive.org/web/20260318224741/https://kpmg.com/'
                          'kpmg-us/content/dam/kpmg/pdf/2025/the-2025-sox-survey.pdf, p. 12; bib key kpmg2025sox): chart "By '
                          'revenue size (average budget in $ M)", large ($25B+), mid ($5-25B) and small (under $5B); budget '
                          '"including both internal and external resources" (co-source providers, not the auditor\'s fee)',
                'flag': 'values read from a text extraction; chart layout and labels verified (lead agent, 2 Nov 2026; the '
                        'kpmg.com URL returned 404)',
                'used_in': Hand('Paper 1 code/paper1_macros.py KPMG_SIZE (direct cost of the accountability floor, round 2 C3); '
                                'engine',
                                'accounting.sox_program_by_size; Paper 2 code/verify_part2_accounting.py (a_min band)'),
                'read': R2_READ}},
        'icfr_line_per_in_scope_ai_application_usd': dict(
            P(80000, [16000, 350000], 'practitioner_survey_disclosed',
              'KPMG 2025 SOX Survey (sox_program_cost_kpmg_2025_reference): $57,500 per in-scope system a year all-in, $16,000 on '
              'the ITGC share; the survey prices testing and administration, not change evidence, interface controls or '
              'operations monitoring, so it is a floor for a new, frequently changing AI application; upper case: the accounting '
              'example\'s invoice application line before the params commit ($347,000)',
              unit='USD a year per in-scope AI application (sum of the eq:acct-itgc lines)',
              note='target total of the round-2 proposal (Section 5.5). Engine unit costs moved as that section lists '
                   '(accounting.itgc_c_chg 5k -> 2.5k, itgc_c_ops 30k -> 20k, itgc_c_ifc 15k -> 10k; itgc_setup 25k and itgc_c_acc '
                   'kept); the upgrade retest accounting.C_val/T_up (100k/1.22 = 82k a year) is not among the listed lines and is '
                   'unchanged, so lines computed from the engine units do not reach this total (see notes/params_commit_2026-10-29.md)'),
            grounding='b', analogy='an AI application performing in-scope steps is one more in-scope system', read=TODAY,
            adopted='params commit 2026-10-29 (assumptions round 2, 5.5)'),
        'regulated_build_multiplier': dict(
            P(1.5, [1.1, 2.0], 'practitioner_survey_disclosed',
              'derived from the KPMG 2025 SOX Survey: $16,000-57,500 a year per in-scope system is 13-46% of an amortized $500,000 '
              'build ($125,000 a year over four years), an equivalent multiplier of 1.1-1.5 if the ICFR running cost were folded '
              'into the build; first-year testing alone about 160 hours (16 hours x about 10 controls)',
              unit='multiplier on AI-engineering build effort for a regulated activity',
              note='covers only the one-time premium on the build (documentation, validation, test evidence). It excludes the ICFR '
                   'lines, which the engine charges separately (accounting.itgc_* lines a year, itgc_setup and '
                   'interface_control_setup once, icfr_redesign_cost per process, C_val per forced upgrade): build.regulated_mult '
                   'multiplies build months only (engine economics.py), so the lines are not counted twice'),
            grounding='b', analogy='SOX program cost of one more in-scope system, read as a build premium', read=TODAY,
            adopted='params commit 2026-10-29 (assumptions round 2, 5.3)'),
        'audit_fee_per_musd_revenue_reference': {
            'value': 343, 'quality': 'practitioner_dataset_disclosed', 'assumed': False, 'grounding': 'ref',
            'source': 'Ideagen Audit Analytics, audit fee trends of the S&P 500 (ideagen.com blog): FY2022 average audit fee $10,776,916, '
                      '$343 of audit fees per $1 million of revenue',
            'unit': 'USD per USD 1 million of revenue',
            # round 2 (C3, lead-agent ruling 4): the S&P 500 ratio is the low bound of the audit fee
            'note': Hand('the LOW bound of the audit fee in the direct cost of accountability since Paper 1 round 2 (C3, 2 Nov '
                         '2026); the',
                         'central fee is audit_fee_accelerated_filer_reference', quoted=True)},
        # round 2 (lead-agent ruling 4, notes/r2_code_changes.md "Follow-up 2 Nov"): central audit fee of the direct cost
        'audit_fee_accelerated_filer_reference': {
            'value': 1492375, 'large_accelerated_filer': 5327646, 'quality': 'practitioner_dataset_disclosed', 'assumed': False,
            'grounding': 'a',
            'source': 'Ideagen Audit Analytics, Audit Fee Trends 2003-2022 (July 2023), p. 14 (bib key auditanalytics2023fees): "In '
                      'FY2022, average audit fees paid by accelerated filers increased 31% from FY2021 to $1,492,375"; large '
                      'accelerated filers $5,327,646 (read in the PDF by the lead agent, 2 Nov 2026)',
            'unit': 'USD a year',
            'note': Hand('central audit fee of the direct cost of accountability for a firm of about $1 billion of revenue (Paper '
                         '1 round 2,',
                         'lead-agent ruling 4); the large-accelerated average is the high case and the S&P 500 ratio '
                         '(audit_fee_per_musd_revenue_reference)',
                         'the low bound. Consumers: code/paper1_macros.py (AUDIT_FEE), engine accounting.audit_fee and '
                         'audit_fee_high, code/verify_part2_accounting.py', quoted=True),
            'read': R2_READ},
        'nist_ai_rmf_alignment_fte_months_initial': P(3, [1, 12], 'assumed',
                                                      'assumed effort to map, measure and manage under the NIST AI RMF 1.0 (voluntary; no '
                                                      'certification exists)'),
        'nist_ai_rmf_ongoing_fte': P(0.25, [0.1, 1.0], 'assumed', 'assumed ongoing governance effort per firm'),
        'privacy_impact_assessment_usd_per_process': P(10000, [3000, 40000], 'assumed', 'assumed'),
        'ai_red_team_usd_per_system_per_year': P(30000, [10000, 150000], 'assumed', 'assumed external or internal AI red-teaming'),
        'cyber_insurance_premium_share_of_revenue': P(0.001, [0.0003, 0.003], 'assumed', 'assumed; no premium dataset read'),
        'security_review_bandwidth_Phi_sec_reviews_per_reviewer_quarter': P(10, [5, 20], 'assumed',
                                                                            'assumed security and privacy design reviews per reviewer FTE per quarter'),
        'security_review_latency_weeks': P(3, [1, 8], 'assumed', 'assumed queue-free review time per deployment'),
    },
    'people_and_ancillary': {
        'training_cost_per_employee_usd_per_year': P(ATD['usd_2025'], [ATD['usd_2025'], ATD['usd_2024']], 'practitioner_survey_disclosed',
                                                     'ATD, 2026 State of the Industry (TD blog, 11 and 19 May 2026): average direct learning '
                                                     'expenditure $846 per employee in 2025 (340 organizations), down from $1,254 in 2024; '
                                                     '16.7 formal learning hours per employee (13.7 in 2024 per the 2025 report, 539 organizations)',
                                                     note='the fall from 2024 may partly reflect a different sample; range spans both years. '
                                                          'Full report is members-only and was not read.'),
        'training_cost_per_learning_hour_usd': P(r(ATD['usd_2025'] / ATD['hours_2025'], 1),
                                                 [r(ATD['usd_2025'] / ATD['hours_2025'], 1), r(ATD['usd_2024'] / 13.7, 1)],
                                                 'practitioner_survey_disclosed', 'our calculation: ATD expenditure / formal hours, 2025 and 2024',
                                                 note='direct expenditure only; excludes the learner\'s time, which is priced at w'),
        'ai_reskilling_hours_per_affected_fte': P(20, [8, 60], 'assumed', 'assumed formal training per FTE whose work changes'),
        'change_management_cost_per_affected_fte_usd': P(2000, [500, 8000], 'assumed',
                                                         'assumed: communications, change agents, process redesign workshops; the '
                                                         'productivity dip is in transition.j_curve, not here'),
        'legal_and_contract_review_usd_per_vendor': P(15000, [5000, 50000], 'assumed', 'assumed (AI terms, data processing, IP)'),
        'eval_dataset_build_usd_per_process': P(20000, [5000, 100000], 'assumed', 'assumed labelling and evaluation set creation'),
        'vendor_management_share_of_vendor_spend': P(0.03, [0.01, 0.06], 'assumed', 'assumed'),
        'finops_share_of_inference_spend': P(0.03, [0.01, 0.08], 'assumed', 'assumed monitoring and optimisation of inference spend'),
        'incident_response_retainer_usd_per_year': P(50000, [20000, 200000], 'assumed', 'assumed'),
        'scaling_note': {'value': {'fixed_per_firm': ['SOC 2', 'ISO 42001', 'NIST AI RMF', 'insurance', 'IR retainer'],
                                   'per_process': ['PIA', 'red team', 'eval datasets', 'revalidation', 'security review'],
                                   'per_unit': ['FinOps', 'expected incident loss'], 'per_fte': ['training', 'change management']},
                         'quality': 'assumed', 'assumed': True, 'source': 'classification by spec 18.4'},
    },
}
params['product'] = product
params['security_and_maintenance'] = security_and_maintenance

# ================================================================== organization (spec 7): span of control, run-mode AI engineers
_st = pd.read_csv(f'{BASE}/data/tasks/industry_staffing.csv', dtype={'naics': str, 'soc': str})
_mgr = _occ.soc.str.startswith('11-') & (_occ.soc != '11-9013')            # management occupations, less farm and ranch managers
_sup = _occ.title.str.startswith('First-Line Supervisors')
_M, _S, _T = (float(_occ.loc[_mgr, 'employment'].sum()), float(_occ.loc[_sup, 'employment'].sum()), float(_occ.employment.sum()))
span = {'all_industries': r((_T - _M - _S) / (_M + _S), 2)}
_ttl = _occ.set_index('soc').title
for n, lab in [('5132', 'software_publishers_5132'), ('5415', 'computer_systems_design_5415'), ('5182', 'data_processing_hosting_5182')]:
    x = _st[_st.naics == n]
    m = float(x.loc[x.soc.str.startswith('11-'), 'emp_share'].sum())
    s = float(x.loc[x.soc.map(_ttl).fillna('').str.startswith('First-Line Supervisors'), 'emp_share'].sum())
    span[lab] = r((1 - m - s) / (m + s), 2)
params['organization']['span_of_control_oews'] = {
    'value': span['software_publishers_5132'], 'range': [span['software_publishers_5132'], span['all_industries']],
    'by_industry': span, 'quality': 'primary_data_fit', 'assumed': False, 'grounding': 'c',
    'source': 'our calculation from BLS OEWS May 2025 (occupations.csv, industry_staffing.csv): workers outside management '
              '(SOC 11, less 11-9013) and first-line supervisor occupations per worker in them',
    'unit': 'non-managerial workers per manager or supervisor',
    'note': 'OEWS management occupations include roles without direct reports (e.g. 11-9199 managers, all other, which holds '
            'product and program managers), so these spans are lower bounds. For the engine key org.span_base, today 7.0 [5, 10] '
            'unlinked: 7.0 matches the all-industry figure, not a software firm.'}
_dev_loaded = float(_occ.loc[_occ.soc == '15-1252', 'wage_median'].iloc[0]) * (1 + load_aw['private_industry'])
_mu = params['security_and_maintenance']['maintenance']['mu_m_share_of_F_A_per_year']
_FA = params['ai_cost']['build_fixed_cost_F_A']['value']['llm_workflow_per_process_usd']
params['organization']['ai_engineers_per_automated_process_run'] = {
    'value': r(_mu['value'] * _FA / _dev_loaded, 2), 'range': [r(_mu['range'][0] * _FA / _dev_loaded, 2), r(_mu['range'][1] * _FA / _dev_loaded, 2)],
    'quality': 'primary_data_fit', 'assumed': False, 'grounding': 'b',
    'source': 'derived: maintenance share mu_m x build cost F_A / loaded cost of a software developer (OEWS May 2025 median for '
              f'15-1252, ${_dev_loaded:,.0f} with the ECEC loading on annual wages)',
    'analogy': 'run-mode upkeep of an automated process is staffed by software engineers at the maintenance budget',
    'unit': 'FTE per automated process', 'note': 'for the engine key org.e_mnt, today 0.25 [0.1, 0.5] unlinked, which is below the '
                                                  'engine\'s own maintenance budget (security.delta_M 0.15 x F_A)'}

# ================================================================== Part I ceiling (Cor ceiling, tab:ceiling) and calibration
# Recorded here so the engine (finance.tau, fees_f, a_min_fixed) and the paper can cite one place. Values are the paper's;
# grounding, bounds and the threshold sensitivities are the audit's (29 Oct 2026). model.tex and calibrate_horizons.py are unchanged.
_ga = read_sec_panel('panel_v2_all.csv', low_memory=False)          # without excluded registrants (code/exclusions.py)
_ga = _ga[(_ga.year >= 2023) & (_ga.year <= 2025) & (_ga.rev > 0)]
_ga = _ga.assign(ga_s=_ga.ga / _ga.rev)
ga_floor = {}
for lo, hi, lab in [(1e9, 1e10, 'rev_1b_10b'), (1e10, 1e15, 'rev_over_10b')]:
    f_ = _ga[(_ga.rev >= lo) & (_ga.rev < hi)].groupby('cik').ga_s.mean().dropna()
    f_ = f_[(f_ > 0) & (f_ < 2)]
    ga_floor[lab] = {'n_firms': int(len(f_)), 'p5': r(f_.quantile(.05), 3), 'p10': r(f_.quantile(.10), 3), 'median': r(f_.median(), 3)}


def gstar(tau, cc, f, amin):
    return r(1 - (1 - tau) * (1 - cc - f - amin), 4)


# Compute share at full automation (assumptions round 2, Section 2; adopted 29 Oct 2026). Explicit path
#   c_c(H) = s_L [omega_H kappa_front + (1 - omega_H) kappa_fixed(H)],  kappa_fixed(H) = max(kappa_2025 / D^(H - 2025),
#   floor_share kappa_2025); central inputs below reproduce the proposal's centrals 0.06 (2025 prices), 0.12, 0.08, 0.05.
CC_PATH = dict(s_L=0.60, s_L_range=[0.50, 0.65], kappa_2025=0.10, kappa_2025_range=[0.01, 0.35], D=5.0, D_range=[3.0, 10.0],
               floor_share=0.005, kappa_front=0.33, kappa_front_range=[0.10, 0.50],
               omega={'2028': 0.6, '2031': 0.4, '2036': 0.25},
               omega_range={'2028': [0.3, 0.9], '2031': [0.2, 0.7], '2036': [0.1, 0.5]})


def cc_path(H, s_L=CC_PATH['s_L'], k25=CC_PATH['kappa_2025'], D=CC_PATH['D'], floor=CC_PATH['floor_share'],
            kf=CC_PATH['kappa_front'], omega=None):
    if H is None:
        return s_L * k25
    om = CC_PATH['omega'][str(H)] if omega is None else omega
    kfix = max(k25 / D ** (H - 2025), floor * k25)
    return s_L * (om * kf + (1 - om) * kfix)


CC_BY_H = {'2028': (0.12, [0.02, 0.30]), '2031': (0.08, [0.01, 0.25]), '2036': (0.05, [0.01, 0.20])}
assert abs(cc_path(None) - 0.06) < 1e-12 and all(abs(cc_path(int(h)) - v) < 0.005 for h, (v, _) in CC_BY_H.items()), \
    'compute-share path no longer reproduces the round-2 centrals'
CENT = dict(tau=0.18, cc=0.06, f=0.025, amin=0.03)
sens = {k: [gstar(**{**CENT, k: lo}), gstar(**{**CENT, k: hi})]
        for k, (lo, hi) in dict(tau=(0.15, 0.21), cc=(0.01, 0.20), f=(0.02, 0.03), amin=(0.015, 0.06)).items()}
params['part1_ceiling'] = {
    'meta': {'formula': 'G* = 1 - (1 - tau)(1 - c_c - f - a_min): market growth at which R_max = 1 with k = 0, X = 1, psi = 0',
             'central_threshold': gstar(**CENT), 'one_at_a_time_threshold_range': sens,
             'used_in': 'sections/model.tex Cor ceiling and tab:ceiling (31/39/48/55% thresholds); intro.tex; '
                        'code/calibrate_horizons.py (TAU, M0_CAP); engine finance.tau, fees_f, a_min_fixed'},
    'tau_cash_tax_rate': {
        'value': 0.18, 'range': [0.15, 0.21], 'quality': 'government', 'assumed': False, 'grounding': 'b',
        'source': 'bounds: 21% federal rate, 26 U.S.C. 11(b) ("21 percent of taxable income", uscode.house.gov); 15% corporate '
                  'alternative minimum tax on adjusted financial statement income for corporations with average annual AFSI above '
                  '$1 billion, tax years beginning after 31 Dec 2022 (IRS, Inflation Reduction Act CAMT page). Wider evidence: '
                  'GAO-23-105384 (2023): average effective rate of profitable large corporations fell from 16% (2014) to 9% (2018)',
        'analogy': 'a mature, profitable firm at the ceiling is large enough for the CAMT floor; state taxes are excluded, as in the paper',
        'note': 'central 0.18 is the midpoint, not an estimate. The widest credible range is [0.09, 0.21] plus state tax; '
                'the 9% GAO average predates the CAMT.'},
    'a_min_accountability_floor': {
        'value': 0.03, 'range': [0.005, 0.046], 'quality': 'primary_data_fit', 'assumed': False, 'grounding': 'b',
        # lower bound since Paper 1 round 2 (C3, notes/r2_propagation.md item 5): KPMG budget by size + accelerated-filer
        # fee; value and band unchanged. The upper-bound figures are computed from the panel (ga_floor above).
        'source': Hand('lower bound: direct accountability costs, since Paper 1 round 2 (C3, 2 Nov 2026) the KPMG 2025 SOX '
                       'program budget',
                       'of a firm under $5B of revenue ($1.5M; security_and_maintenance.compliance.'
                       'sox_program_cost_kpmg_2025_reference.by_revenue_size)',
                       'plus the accelerated-filer average audit fee ($1,492,375; audit_fee_accelerated_filer_reference), 0.30% '
                       'of revenue',
                       'for a $1B firm (0.18% with the S&P 500 fee ratio of $343 per $1M, 0.68% with the large-accelerated fee); '
                       'before round',
                       '2, the S&P 500 ratio plus the SEC OEA 2009 median Section 404 cost ($1.04M), 0.14%. With the cheapest '
                       'admissible control',
                       'design the bottom-up floor is about 0.37-0.38% (Paper 1 macros AminFloor, AminFloorOne), below the '
                       'band\'s 0.5%. Upper bound: our calculation from the SEC XBRL',
                       'panel (data/panel_v2_all.csv, SIC 7370-7374, FY2023-25 firm means): total G&A share p5 '
                       f"{ga_floor['rev_1b_10b']['p5']} and p10 {ga_floor['rev_1b_10b']['p10']} for revenue",
                       f"$1B-10B ({ga_floor['rev_1b_10b']['n_firms']} firms), p5 {ga_floor['rev_over_10b']['p5']} and p10 "
                       f"{ga_floor['rev_over_10b']['p10']} above $10B ({ga_floor['rev_over_10b']['n_firms']} firms)"),
        'analogy': 'the accountability floor after full automation cannot exceed the whole G&A of today\'s leanest software firms, '
                   'and cannot fall below the audit and control costs the law requires',
        'ga_share_by_size': ga_floor,
        'note': 'the paper\'s central 3% equals the p10 G&A share of software firms above $10B (all of today\'s G&A kept); the '
                'favorable 1.5% lies inside the band; the conservative 6% lies above the p5 G&A share of $1B-10B firms and outside '
                'the band. G&A includes SBC.'},
    'c_c_compute_share': {
        'value': r(cc_path(None), 4), 'range': [0.01, 0.20], 'quality': 'working_paper', 'assumed': False, 'grounding': 'b',
        'basis': '2025 prices, no price path (b-anchored)',
        'source': 'c_c = s_L x kappa (assumptions round 2, Section 2; read 29 Oct 2026). kappa at 2025 prices 0.10 [0.01, 0.35] (b): '
                  'METR agent runs (ai_cost.inference_cost_usd_per_human_hour: median '
                  f"{r(min(v['share_of_human_baseline_cost_median'] for v in obs.values()) * 100, 2)}-"
                  f"{r(max(v['share_of_human_baseline_cost_median'] for v in obs.values()) * 100, 2)}% of the human baseline cost "
                  f'across {len(obs)} recent agents, METR TH1.0; c); Stevens (2026), Payrolls to Prompts, arXiv:2602.00139: about $0.03 '
                  'of AI spend per $1 of displaced freelance labor (a, preprint); AI-native products, inference 13-23% of revenue at '
                  '2025 prices (ICONIQ 2026 via SaaStr, secondary; the revenue mapping is the auditor\'s calculation); central 0.10 = '
                  'geometric middle of the field analogs. s_L 0.60 [0.50, 0.65] (c): labor cost the ceiling automates, share of revenue',
        'by_horizon': {h: {'value': v, 'range': rg, 'grounding': 'd', 'model': r(cc_path(int(h)), 4)} for h, (v, rg) in CC_BY_H.items()},
        'path': dict(CC_PATH, formula='c_c(H) = s_L [omega_H kappa_front + (1 - omega_H) max(kappa_2025 / D^(H - 2025), '
                                      'floor_share kappa_2025)]',
                     # round 2 (B2, notes/r2_propagation.md item 2): the value test is kappa < 1, so c_c <= s_L; the
                     # factor 0.5 (1 - review share) had no source and the full-automation ceiling has no human review
                     sources=Hand('D = 5 [3, 10] a year: Gundlach, Lynch, Mertens and Thompson (2026), arXiv:2511.23455v2, '
                                  'fixed-performance',
                                  'price down 5-10x a year (a); kappa_front = 0.33 [0.10, 0.50] (d), capped by the value test kappa '
                                  '< 1, so c_c <= s_L',
                                  '(Paper 1 round 2, B2: the earlier cap kappa < 1 - review share, c_c <= 0.5 s_L, had no source '
                                  'and the full-automation',
                                  'ceiling has no human review; frontier cost up 3-18x a year is capped by abandonment, not '
                                  'extrapolated); omega_H (d): share of automated labor',
                                  'cost in tasks reached within two years of H; floor_share = engine prices.floor_share (d)')),
        # round 2 (B2): within the value-test cap c_c <= s_L (code/calibrate_horizons.py CC_VALUE_TEST_FACTOR = 1.0), so the
        # high-compute case is feasible; the cap is s_L itself (0.60)
        'high_compute_case': {'value': 0.40, 'feasible_at_full_automation': True, 'value_test_cap': CC_PATH['s_L'],
                              'note': Hand('within the value-test cap c_c <= s_L = 0.60 (Paper 1 round 2, B2, 2 Nov 2026; '
                                           'code/calibrate_horizons.py',
                                           'CC_VALUE_TEST_FACTOR = 1.0), so feasible at full automation (G* 61.3%, Paper 1 macro '
                                           'GstarHigh). Before round 2 the',
                                           'cap was s_L x 0.5 = 0.30, a factor with no source, and the case was labelled '
                                           'infeasible. Credible range of c_c at',
                                           '2025 prices against the cap: 1-60% (G* 28-78%, Paper 1 macros GstarCcLo, GstarCcHi); '
                                           'the old cap 0.30 gives G* 52.8%',
                                           '(GstarCcOldCap)')},
        'previous': {'value': 0.20, 'range': [0.15, 0.25], 'scenario_bounds': [0.01, 0.55], 'grounding': 'd',
                     'note': 'horizon-invariant scenario value before the params commit of 29 Oct 2026'},
        'note': 'the horizon values are class d (the mix omega_H and the frontier cap are scenarios), with the 2025 anchor class b. '
                'Every threshold that uses c_c is conditional on it: dG*/dc_c = (1 - tau)(1 + s_fin) = 0.845 at the central tax and '
                'FinOps rates. Consumers: code/calibrate_horizons.py (FC, by horizon), engine finance.c_c_full_automation.',
        'read': TODAY, 'adopted': 'params commit 2026-10-29 (assumptions round 2, 2)'},
    'f_payment_fees': {
        'value': 0.025, 'range': [0.02, 0.03], 'quality': 'assumed', 'assumed': True, 'grounding': 'd',
        'source': 'paper: card processing for firms that bill directly; no processor price page could be read in this pass '
                  '(stripe.com not reachable), so the bracket is unverified',
        'note': 'smallest influence on G* (one-at-a-time range 0.8 points); invoiced B2B billing by bank transfer would cost less'},
    'calibration_horizons': {
        # round 2 (IM2-N10/N12, revision plan F5): class as used. The spend ratio identifies alpha(X - k), not alpha
        # (Paper 1 Section 5.4, decision D-1), so alpha is a scenario value: 0.25 and 0.45 bound the surplus scaling of the
        # tornado, 0.35 is the central path's value and 0.3 the levers table's
        'alpha_spend_elasticity': {'value': [0.25, 0.45], 'quality': 'assumed', 'assumed': True, 'grounding': 'd',
                                   'source': 'scenario range (class d): the Part I data identify only alpha(X - k) through '
                                             'the spend ratio (Section 5.4, decision D-1), not alpha itself; used as the '
                                             'bounds of the surplus scaling (central path alpha = 0.35; levers table 0.3)'},
        'TAU': {'value': 0.18, 'quality': 'government', 'assumed': False, 'grounding': 'b', 'source': 'as tau_cash_tax_rate'},
        'M0_CAP': {'value': r((1 - 0.15) * (1 - 0.15 - 0.02 - 0.015), 5), 'quality': 'assumed', 'assumed': True, 'grounding': 'd',
                   'source': 'third-revision favorable accountability-only margin term at c_c = 0.15 (class d); kept only for the '
                             '"previous" comparison block of code/calibrate_horizons.py (M0_CAP_OLD). The current favorable '
                             'full-cost terms are horizon-specific (c_c by horizon, params commit of 29 Oct 2026)'},
        'm0_paths': {'value': {'2028': [0.40, 0.62], '2031': [0.45, 0.65], '2036': [0.50, 'M0_CAP']}, 'quality': 'assumed',
                     'assumed': True, 'grounding': 'd',
                     'source': 'scenario; lower ends sit above the 2025 anchor IQR of m0 (0.35-0.50, upper-bound case; class c)'},
        'G_paths': {'value': {'2028': [0.10, 0.20], '2031': [0.08, 0.20], '2036': [0.05, 0.30]}, 'quality': 'assumed', 'assumed': True,
                    'grounding': 'd', 'source': 'scenario around the 2025 panel median of 12.9% (class c)'},
        'mu_pull_multiplier': {'value': {'2028': [1.0, 2.0], '2031': [0.75, 1.5], '2036': [0.5, 1.25]}, 'quality': 'assumed',
                               'assumed': True, 'grounding': 'd', 'source': 'scenario; Pi scales with mu^(1/(1-alpha)), up to 3.5x at '
                                                                            'mu = 2 and alpha = 0.45'},
        'k_cases': {'value': [0.0, 0.5], 'quality': 'assumed', 'assumed': True, 'grounding': 'd', 'source': 'scenario cases'},
    },
}

# Pass-through of unit-cost savings to output prices (assumptions round 2, Section 4; adopted 29 Oct 2026; restated in Paper 1
# round 2, B1, notes/r2_propagation.md item 1). The scenario value phi is the industry pass-through RATE: the share of a
# common unit-cost change that reaches the output price, applied to every unit-cost saving with margins at the post-cut
# price. dur = 1 - phi (1 - HHI) (theory_competition.tex cor:ext-game-engine, eq:ext-game-dur; engine formulas.game_shares)
# is the share of the dollar saving a firm keeps when every rival makes it, not a margin share, and is not used in the score.
# The anchor identical_inference (Demirer et al., "near 1") was removed in round 2 (A9, IO2-2): the -1.1 within-model
# elasticity measures substitution between providers, not pass-through; the note below says so.
params['pass_through'] = {
    'industry_pass_through_scenarios': {
        'value': [0.0, 0.5, 0.7], 'quality': 'peer_reviewed', 'assumed': False, 'grounding': 'b',
        'fixed_prices_case': 0.0,
        'anchors': {
            'software_short_run': {'value': [0.0, 0.1], 'source': 'Choi (Analysis Group, funded by Apple), What Happens to App '
                                   'Prices when Developers Pay Lower Commission Fees? Evidence from the European Union, Nov 2025 '
                                   '(developer.apple.com/download/files/DMA-Study-Nov-2025.pdf; read 29 Oct 2026): after a 10-point '
                                   'commission cut, prices fell on 9% of products (6% of transactions), median cut 2.5%; three months, '
                                   'no control group'},
            'industry_wide_medium_run': {'value': 0.7, 'source': 'Ganapati, Shapiro and Walker (2020), Energy Cost Pass-Through in '
                                         'US Manufacturing, AEJ: Applied 12(2), 303-342 (aeaweb.org/doi/10.1257/app.20180474; read 29 Oct '
                                         '2026): about 70% of energy-driven input cost changes pass through in the short to medium run'},
            'long_run_broad_vs_narrow': {'value': [0.3, 1.0], 'source': 'Benedek, de Mooij, Keen and Wingender, Estimating VAT Pass '
                                         'Through, IMF WP 15/214 (read 29 Oct 2026): about 100% for standard-rate changes, about 30% '
                                         'for reduced-rate changes'}},
        'source': 'scenario set with precedent (assumptions round 2, Section 4): 0 = fixed prices (the case Paper 1 reported '
                  'alone before the params commit, kept and reported beside the others), 0.5 central medium-run case, 0.7 '
                  'industry-wide cost shock',
        'unit': 'industry pass-through RATE phi, the share of a common unit-cost change that reaches the output price. Paper 1 '
                'round 2 (B1, 2 Nov 2026) applies it to every unit-cost saving (cost of revenue, compute and the '
                'non-discretionary floors; Prop. entry(d)), with margins at the post-cut price: the after-tax margin term is '
                '(1 - tau)(1 - f - K/(1 - phi S))',
        'note': Hand('consumers: code/calibrate_horizons.py (scenario dimension; rate on all unit-cost savings at the post-cut '
                     'price;',
                     'dur = 1 - phi (1 - HHI) at the engine\'s HHI is reported as the dollar-profit share and not used in the '
                     'score); engine',
                     'competition.phi_ind_scenarios (named scenarios pass_through_0, _50, _70), formulas.passthrough_terms '
                     '(score) and the',
                     'durable share (dollars). The central engine value is competition.phi_ind = 0.5; the derived Cournot '
                     'phi_ind = n_c/(n_c',
                     '+ 1 - e) is a benchmark. Removed anchor (Paper 1 round 2, A9 and IO2-2): Demirer, Fradkin, Tadelis and '
                     'Peng report a',
                     'preliminary within-model price elasticity of about -1.1 across providers of the same open model, which '
                     'measures',
                     'substitution between providers, not the pass-through of cost to price; it is not evidence of '
                     'pass-through near one.'),
        'read': TODAY, 'adopted': 'params commit 2026-10-29 (assumptions round 2, 4)'},
}


# ================================================================== grounding classes (spec 21.1)
DEFAULT_CLASS = {'peer_reviewed': 'a', 'government': 'a', 'company_filing': 'a', 'vendor_price_list': 'a', 'vendor_documentation': 'a',
                 'practitioner_survey_disclosed': 'a', 'practitioner_dataset_disclosed': 'a', 'working_paper': 'a',
                 'primary_data_fit': 'c', 'secondary': 'b', 'practitioner_survey_undisclosed': 'b', 'company_statement': 'b',
                 'prediction': 'ref', 'unsupported': 'ref', 'assumed': 'd'}


def set_grounding(d):
    """Give every parameter block a spec 21.1 class: explicit if set above, else d when assumed, else by quality flag."""
    if isinstance(d, dict) and 'quality' in d:
        if 'grounding' not in d:
            d['grounding'] = 'd' if d.get('assumed') else DEFAULT_CLASS.get(d['quality'], 'b')
        for v in d.values():
            set_grounding(v)
        return
    if isinstance(d, dict):
        for v in d.values():
            set_grounding(v)


# ------------------------------------------------------------------ permanent capital and acquirer limits (acquirer section)
# notes/acquirer_notes.md Sections 3-5 (formulas and grounding classes); disclosed values parsed from the lead's F-1 extract
# notes/case_bending_spoons_f1_extract.md (not typed here). Rates stay annual; the engine converts with ln(1 + r).
_F1_PATH = f'{BASE}/notes/case_bending_spoons_f1_extract.md'
_F1 = open(_F1_PATH, encoding='utf-8').read()
_F1_LINES = _F1.splitlines()


def _f1(pattern, cast=float):
    m = re.search(pattern, _F1)
    assert m, f'F-1 extract pattern not found: {pattern}'
    line = _F1[:m.start()].count('\n') + 1
    return [cast(g.replace(',', '')) for g in m.groups()], line


F1_CITE = ('Bending Spoons S.p.A., Form F-1 registration statement, filed with the SEC 8 June 2026 (CIK 2004711), '
           'https://www.sec.gov/Archives/edgar/data/0002004711/000110465926071170/tm2613674-7_f1.htm, read in the author\'s browser '
           '29 Oct 2026 (bib bendingspoons2026f1; original filing only: the F-1/A, accession 000110465926076487, and the final '
           'prospectus were not read); values parsed from notes/case_bending_spoons_f1_extract.md')
(_hur_l, _hur_u), _l_hur = _f1(r'hurdles of (\d+)% levered and (\d+)% unlevered')
(_ltv,), _l_ltv = _f1(r'lower of (\d+)% of enterprise value')
_words = {'five': 5}
_m = re.search(r'could repay within (\w+) years', _F1); _rep_years = _words[_m.group(1)]; _l_rep = _F1[:_m.start()].count('\n') + 1
_m = re.search(r'\*\*IRR method:\*\*\n  - (\w+) years of free cash flow', _F1); _irr_years = _words[_m.group(1)]
_l_irr = _F1[:_m.start()].count('\n') + 2
(_cov, _lev25, _levq1), _l_cov = _f1(r'covenant of at most ([\d.]+); the ratio was ([\d.]+) at end-2025 and ([\d.]+) at end-Q1 2026')
(_n23, _n24, _n25, _nq1), _l_nrr = _f1(r'Portfolio: (\d+)% \(2023\), (\d+)% \(2024\), (\d+)% \(2025\) and (\d+)% \(Q1 2026\)')
(_aol, _ev, _rem, _sy), _l_nrrb = _f1(r'AOL (\d+)%, Evernote (\d+)%, Remini (\d+)%, StreamYard (\d+)%')
_m = re.search(r'"assuming we\'ll never sell the acquired business"', _F1); assert _m; _l_hold = _F1[:_m.start()].count('\n') + 1
assert (_hur_l, _hur_u, _ltv, _rep_years, _irr_years, _cov) == (65, 25, 85, 5, 5, 4.0), 'F-1 extract values changed'
(_usd_b, _usd_cpn, _eur_m, _eur_cpn, _due), _l_notes = _f1(r'\$([\d.]+)B at ([\d.]+)% and €(\d+)M at ([\d.]+)%, due (\d{4})')
assert 'priced 28 Oct 2026' in _F1_LINES[_l_notes - 1], 'senior secured notes line changed'
(_nd_b, _ltd_b, _cash_m), _l_nd = _f1(r'Net debt \$([\d.]+)B \(long-term debt \$([\d.]+)B, cash \$(\d+)M\)')
(_levq2,), _l_levq2 = _f1(r'Leverage ratio ([\d.]+)×')
_l_q2 = next(i + 1 for i, l in enumerate(_F1_LINES) if l.startswith('- **Q2 2026 results**'))
assert _l_nd == _l_levq2 and _l_q2 < _l_nd and '6-K filed 13 Aug 2026' in _F1_LINES[_l_q2 - 1], 'Q2 2026 6-K section changed'
SIXK_CITE = ('Bending Spoons S.p.A., Form 6-K, Ex. 99.1, filed on EDGAR (CIK 2004711) on {date}, read 29 Oct 2026 in the '
             'author\'s browser; values parsed from notes/case_bending_spoons_f1_extract.md (section "Post-IPO filings"; the '
             'extract does not record the exhibit URL)')
_nrr_full = sorted([_n23 / 100, _n24 / 100, _n25 / 100])
_decay = {k: r(-math.log(v), 4) for k, v in zip(('high', 'central', 'low'), _nrr_full)}   # lowest NRR = fastest decay


def F1(value, rng, source, line, unit=None, note=None):
    d = P(value, rng, 'company_filing', f'{F1_CITE}, line {line}: {source}', unit=unit, note=note)
    d['grounding'] = 'a'
    return d


def SCN(neutral, domain, symbol, meaning, checked_in, unit=None):
    """class d scenario parameter: no value in the acquirer notes. neutral_value switches the limit off; verified_domain is
    the domain over which code/verify_part2_acquirer.py checks the proposition, not a calibration."""
    d = {'value': None, 'range': None, 'neutral_value': neutral, 'verified_domain': domain, 'scenario': True,
         'quality': 'assumed', 'assumed': True, 'grounding': 'd', 'symbol': symbol,
         'source': f'scenario (class d): notes/acquirer_notes.md Section 5 lists {symbol} among "scenario values, not grounded"; '
                   f'no value is given. {meaning} verified_domain: {checked_in}'}
    if unit:
        d['unit'] = unit
    return d


params['ownership_regimes']['permanent_capital'] = {
    'horizon': dict(F1('infinite (acquired businesses are never sold)', None, 'invests on expected returns "assuming we\'ll never '
                       'sell the acquired business"', _l_hold), range=None),
    'hurdle_unlevered_irr_annual': F1(_hur_u / 100, [_hur_u / 100, _hur_u / 100], f'unlevered IRR hurdle {_hur_u:.0f}% '
                                      '(acquisitions completed 2023 to Q1 2026)', _l_hur, unit='per year, annual',
                                      note=f'continuous ln(1 + r) = {r(math.log(1 + _hur_u / 100), 4)}; the engine converts'),
    'hurdle_levered_irr_annual': F1(_hur_l / 100, [_hur_l / 100, _hur_l / 100], f'levered IRR hurdle {_hur_l:.0f}%', _l_hur,
                                    unit='per year, annual', note=f'continuous ln(1 + r) = {r(math.log(1 + _hur_l / 100), 4)}; '
                                    'the engine converts. Whether the hurdles are minimum or projected IRRs is not in the extract '
                                    '(acquirer notes Section 8, item 11)'),
    'irr_window_years': F1(_irr_years, [_irr_years, _irr_years], 'IRR method: five years of free cash flow plus a terminal value',
                           _l_irr, unit='years'),
    'debt_ltv_cap_share_of_ev': F1(_ltv / 100, [_ltv / 100, _ltv / 100], 'assumed acquisition debt: the lower of 85% of '
                                   'enterprise value and the debt the projected FCF could repay within five years', _l_ltv,
                                   unit='share of enterprise value', note='debt rule: ND_0 = min{LTV P, ND^rep} (acquirer notes '
                                   'Section 3, item 4)'),
    'debt_repayment_years': F1(_rep_years, [_rep_years, _rep_years], 'debt the projected FCF could repay within five years',
                               _l_rep, unit='years', note='ND^rep = present value of FCF over T_rep at r_debt'),
    'covenant_max_leverage': F1(_cov, [_cov, _cov], 'leverage-ratio covenant of at most 4.00', _l_cov, unit='leverage ratio',
                                note='the ratio definition (net or gross, EBITDA basis) is not in the extract (acquirer notes '
                                     'Section 8, item 8)'),
    'covenant_leverage_actual': dict(P(_levq2, [min(_lev25, _levq1, _levq2), max(_lev25, _levq1, _levq2)], 'company_filing',
                                       f'{F1_CITE}, line {_l_cov}: ratio {_lev25} at end-2025 and {_levq1} at end-Q1 2026; '
                                       + SIXK_CITE.format(date='13 Aug 2026') + f', line {_l_levq2}: leverage ratio {_levq2} at '
                                       'end-Q2 2026 (unaudited)', unit='leverage ratio',
                                       note='value = latest (end-Q2 2026). The company computes the ratio on pro forma adjusted '
                                            'EBITDA that "reflects achieved cost savings from reorganizations as if ... achieved at '
                                            'the beginning" of the period, "as well as certain expected cost savings", so it is lower '
                                            'than a ratio on reported EBITDA'),
                                     grounding='a', by_period={'end-2025': _lev25, 'end-Q1 2026': _levq1, 'end-Q2 2026': _levq2}),
    'net_debt_usd_end_q2_2026': dict(P(_nd_b * 1e9, None, 'company_filing',
                                       SIXK_CITE.format(date='13 Aug 2026') + f', line {_l_nd}: net debt ${_nd_b}B (long-term debt '
                                       f'${_ltd_b}B, cash ${_cash_m:.0f}M), unaudited', unit='USD',
                                       note=f'check: {_ltd_b}B - {_cash_m / 1000:.3f}B = {_ltd_b - _cash_m / 1000:.3f}B'),
                                     grounding='a'),
    'terminal_value_rate_r_tv_annual': dict(P(params['ownership_regimes']['public']['r_own_wacc']['value'],
                                              params['ownership_regimes']['public']['r_own_wacc']['range'],
                                              'practitioner_dataset_disclosed',
                                              'same as ownership_regimes.public.r_own_wacc (Damodaran, January 2026): the '
                                              'F-1\'s own WACC for terminal values is not in the extract (acquirer notes '
                                              'Sections 5 and 8, item 11)', unit='per year, annual'),
                                            grounding='b', links='ownership_regimes.public.r_own_wacc'),
    'debt_rate_r_debt_annual': dict(P(_usd_cpn / 100, [min(_usd_cpn, _eur_cpn) / 100, max(_usd_cpn, _eur_cpn) / 100],
                                      'company_filing',
                                      SIXK_CITE.format(date='28 Oct 2026') + f', line {_l_notes}: senior secured notes priced 28 '
                                      f'Oct 2026, ${_usd_b}B at {_usd_cpn}% and EUR {_eur_m:.0f}M at {_eur_cpn}%, due {_due:.0f}',
                                      unit='per year, annual (coupon)',
                                      note='the company\'s marginal secured cost of new debt (coupons on its first notes), not its '
                                           'average cost of debt; value = the USD coupon. The EUR coupon is in euro terms, so the range '
                                           'mixes currencies. Replaces the earlier class d 8% (the engine\'s regime.debt_rate preset)'),
                                    grounding='a'),
}

params['acquirer'] = {'limits': {
    'treadmill': {
        'nrr_portfolio': F1({'2023': _n23 / 100, '2024': _n24 / 100, '2025': _n25 / 100, 'Q1 2026': _nq1 / 100},
                            [min(_nrr_full), max(_nrr_full)], 'net revenue retention, portfolio', _l_nrr,
                            unit='share of prior-year subscription revenue from the same customers',
                            note='range over the three full years; definition in the extract: subscription revenue in a quarter '
                                 'from customers acquired at least a year earlier over the same quarter a year earlier'),
        'nrr_by_business_avg_q1_2023_q1_2026': F1({'AOL': _aol / 100, 'Evernote': _ev / 100, 'Remini': _rem / 100,
                                                    'StreamYard': _sy / 100}, None, 'NRR averaged over Q1 2023 to Q1 2026',
                                                   _l_nrrb, note='the AOL average includes quarters before ownership (closed '
                                                   '2 Jan 2026; notes/ref_verification_acquirer.md)'),
        'decay_rate_minus_ln_nrr': dict(P(_decay['central'], [_decay['low'], _decay['high']], 'primary_data_fit',
                                          'our calculation (class c): -ln NRR, with NRR from nrr_portfolio; central = -ln of the median '
                                          f'full-year NRR ({_nrr_full[1]:.2f}); range from the highest ({_nrr_full[2]:.2f}) and lowest '
                                          f'({_nrr_full[0]:.2f}) full-year NRR', unit='per year, continuous',
                                          note='equals the acquired growth needed to stand still (-g^org without new customers), '
                                               'acquirer notes Section 3, item 6, and Section 4'),
                                        grounding='c'),
        'customer_life_T_life_years': dict(P(r(1 / _decay['central'], 1), [r(1 / _decay['high'], 1), r(1 / _decay['low'], 1)],
                                             'primary_data_fit', 'our calculation (class c): T^life = -1/ln NRR, from '
                                             'decay_rate_minus_ln_nrr', unit='years',
                                             note='used in the annuity bound of prop:acquired-score; the acquirer notes call it a '
                                                  'scenario when applied to another firm'),
                                           grounding='c'),
    },
    'debt_and_deal_capacity': {
        'net_debt_per_dollar_revenue_nd': SCN(0.0, 'symbolic only (check H1, g^max formula)', 'nd',
                                              'Net debt per dollar of revenue; take it from the firm\'s balance sheet when known.',
                                              'none numeric; code/verify_part2_acquirer.py check H1 verifies the g^max formula symbolically (it requires k^acq > nd)',
                                              unit='share of revenue'),
        'max_deals_per_year_n_dl': SCN(None, [1, 20], 'n^dl', 'Maximum deals a year; neutral = no cap.',
                                       'code/verify_part2_acquirer.py check H3 draws 1 to 20', unit='deals per year'),
        'hurdle_headroom_elasticity_eps_sz': SCN(0.0, [0.05, 1.5], 'eps_sz', 'Elasticity of hurdle headroom to target size; '
                                                 'the literature signs it (Fuller 2002; Renneboog and Vansteenkiste 2019; Billett '
                                                 'and Qian 2008; Aktas et al. 2009) but does not size it; neutral 0 = no size limit.',
                                                 'check H3 draws 0.05 to 1.5'),
        'hurdle_headroom_at_reference_size_h_0': SCN(None, [1.0, 3.0], 'h_0', 'Hurdle headroom at the reference target size; '
                                                     'irrelevant when eps_sz = 0.', 'check H3 draws 1 to 3', unit='ratio'),
    },
    'series_review': {
        'challenge_probability_form': {'value': 'p_ch(s) = min(1, a s^2), convex and nondecreasing in cumulative niche share s',
                                       'quality': 'assumed', 'assumed': True, 'grounding': 'd', 'scenario': True,
                                       'source': 'scenario (class d): functional form used by code/verify_part2_acquirer.py check '
                                                 'H4; prop:acq-limits(c) needs only convexity and monotonicity'},
        'challenge_curvature_a': SCN(0.0, [0.5, 5.0], 'p^ch (curvature a)', 'Neutral 0 = no challenge risk.',
                                     'check H4 draws 0.5 to 5'),
        'niche_share_per_deal_delta_s': SCN(None, [0.01, 0.10], 'Delta s', 'Cumulative niche share added per deal.',
                                            'check H4 draws 0.01 to 0.10', unit='share of the niche'),
        'loss_if_challenged_L_ch': SCN(None, [1.0, 10.0], 'L^ch', 'Loss if a deal is challenged, in the units of the deal\'s '
                                       'net value V_n - P_n.', 'check H4 draws 1 to 10 against net values of 0.05 to 1'),
        'fdi_review_probability_p_fdi': SCN(0.0, 'definitional [0, 1]; symbolic check H4', 'p^fdi', 'Probability of a foreign-investment review; neutral 0. '
                                            'No public record of an agency challenge to any of the case firm\'s deals was found '
                                            '(acquirer notes Section 6).', 'symbolic only (check H4)', unit='probability'),
        'fdi_review_delay_T_fdi_years': SCN(0.0, 'any positive (symbolic, check H4)', 'T^fdi', 'Review delay.',
                                            'symbolic only (check H4)', unit='years'),
    },
    'consumer_law': {
        'switching_cost_scale_h_cp': SCN(1.0, [0.2, 1.0], 'h^cp', 'Scale on switching costs from consumer and subscription '
                                         'law; neutral 1 = no effect.', 'check H5 draws 0.2 to 1', unit='ratio'),
        'repricing_cap_upsilon_cp': SCN(None, [0.0, 3.0], 'upsilon^cp', 'Cap on a repricing (price increase as a share of the '
                                        'old price); neutral = no cap.', 'check H5 draws 0 to 3', unit='share of the old price'),
    },
}}

set_grounding(params)

with open(f'{BASE}/data/tasks/params.yaml', 'w') as f:
    f.write('# Part II engine parameters. Built by code/data_part2/08_params.py; do not edit by hand.\n')
    f.write('# Every block: value, range, quality flag, source, assumed. Sources and URLs: notes/data_sources_part2.md\n')
    # same output as yaml.safe_dump(..., width=120), except that Hand strings keep their hand-set line breaks
    yaml.dump(params, f, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=120)
print('wrote params.yaml')


def walk(d, path=''):
    n = a = 0
    if isinstance(d, dict) and 'quality' in d:
        return 1, int(bool(d.get('assumed')))
    if isinstance(d, dict):
        for k, v in d.items():
            x, y = walk(v, path + '/' + k)
            n += x
            a += y
    return n, a


n, a = walk(params)
print(f'parameter blocks: {n}, assumed: {a}')


def classes(d, out=None):
    out = {} if out is None else out
    if isinstance(d, dict) and 'quality' in d:
        out[d.get('grounding')] = out.get(d.get('grounding'), 0) + 1
        for v in d.values():
            if isinstance(v, dict):
                classes(v, out)
        return out
    if isinstance(d, dict):
        for v in d.values():
            classes(v, out)
    return out


print('grounding classes (all blocks, nested included):', dict(sorted(classes(params).items())))
