# Copyright (c) 2026 Akshaya Bangalore Sreenivasa Murthy. Licensed under the PolyForm Noncommercial License 1.0.0 or, at your option, the PolyForm Internal Use License 1.0.0 (see LICENSE.md and LICENSE-INTERNAL-USE.md).
# Commercial use requires prior written permission from the copyright holder.
"""Input tiers (spec Section 9, plus the Tier 3 organizational inputs of Section 14) as pydantic
models, and the templates a user fills in (CSV and XLSX, with a README per file)."""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator


# --------------------------------------------------------------------------------------------
# Tier 0: public financials (10-K or XBRL). One record.
# --------------------------------------------------------------------------------------------
class Financials(BaseModel):
    company_name: str = "Unnamed company"
    fiscal_year: int = 2025
    currency: str = "USD"
    revenue: float = Field(gt=0, description="Annual revenue")
    cogs: float = Field(ge=0, description="Cost of revenue")
    rnd: float = Field(ge=0, description="Research and development expense")
    sm: float = Field(ge=0, description="Sales and marketing expense")
    ga: float = Field(ge=0, description="General and administrative expense")
    sbc: Optional[float] = Field(default=None, ge=0, description="Stock-based compensation (included in the lines above)")
    da: Optional[float] = Field(default=None, ge=0, description="Depreciation and amortization")
    capex: Optional[float] = Field(default=None, ge=0, description="Capital expenditure, including capitalized software")
    headcount: Optional[float] = Field(default=None, gt=0, description="Employees at year end")
    naics: Optional[str] = None
    sic: Optional[str] = None
    revenue_growth: Optional[float] = Field(default=None, ge=-0.9, le=5.0)
    market_growth: Optional[float] = Field(default=None, ge=-0.5, le=2.0)
    capital_intensity_k: Optional[float] = Field(default=None, ge=-1.0, le=5.0)
    inventory: Optional[float] = Field(default=None, ge=0, description="Inventory on the balance sheet (inventory steps enter ICFR scope when positive)")
    ev_revenue_multiple: Optional[float] = Field(default=None, gt=0)
    growth_weight_low: Optional[float] = Field(default=None, gt=0, le=60, description="Low end of the owner's decision weight on growth X, if the firm has a view")
    growth_weight_high: Optional[float] = Field(default=None, gt=0, le=60, description="High end of the owner's decision weight on growth X")
    multiple_is_net_of_pressure: Optional[float] = Field(default=None, ge=0, le=1, description="1 if the EV/revenue multiple is a public filer's revealed weight, net of earnings pressure (prop:reg-weight(b))")
    fcf_margin: Optional[float] = Field(default=None, ge=-2, le=1, description="Free cash flow after stock-based compensation over revenue; when given, m0 = fcf_margin + sigma + k g")
    tax_rate: Optional[float] = Field(default=None, ge=0, le=0.6)
    owned_compute_share: Optional[float] = Field(default=None, ge=0, le=1)
    bonus_election: Optional[Literal["none", "elect_out", "transitional_40", "transitional_60"]] = Field(
        default=None, description="Bonus depreciation on owned servers: none (100% allowance, current law), elect_out "
        "(168(k)(7): MACRS), transitional_40 or transitional_60 (168(k)(10))")
    foreign_server_share: Optional[float] = Field(default=None, ge=0, le=1, description="Share of owned servers used "
        "predominantly outside the United States (ADS, no bonus)")
    context_engine: Optional[float] = Field(default=None, ge=0, le=1)
    ownership_regime: Optional[str] = Field(default=None, description="public, private_family, pe, vc, hybrid or permanent_capital (spec Section 16)")
    net_debt: Optional[float] = None
    ebitda: Optional[float] = None
    shares_outstanding: Optional[float] = Field(default=None, gt=0)
    market_hhi: Optional[float] = Field(default=None, gt=0, le=1, description="Herfindahl index of the firm's product markets")
    industry_pass_through: Optional[float] = Field(default=None, ge=0, le=3, description="Industry pass-through of a common cost change")

    @model_validator(mode="after")
    def _costs_below_revenue_scale(self):
        if self.cogs + self.rnd + self.sm + self.ga > 5 * self.revenue:
            raise ValueError("operating costs exceed five times revenue; check units (revenue may be in thousands or millions while costs are in currency units; enter every amount in currency units)")
        return self


class OpexRow(BaseModel):
    cost_center: str
    cost_center_name: Optional[str] = None
    gl_account: Optional[str] = None
    gl_name: Optional[str] = None
    amount: float
    function_id: Optional[str] = None
    headcount: Optional[float] = None


class RosterRow(BaseModel):
    role_id: Optional[str] = None
    title: str
    cost_center: Optional[str] = None
    function_id: Optional[str] = None
    soc: Optional[str] = None
    fte: float = Field(gt=0)
    annual_base_comp: float = Field(gt=0, description="Per FTE, gross wage before benefits")
    annual_total_comp: Optional[float] = Field(default=None, gt=0)
    location: Optional[str] = None
    wage_index: Optional[float] = Field(default=None, gt=0)
    worker_type: Literal["employee", "contractor"] = "employee"
    level: Optional[str] = None

    @field_validator("worker_type", mode="before")
    @classmethod
    def _wt(cls, v):
        v = (str(v).strip().lower() if v is not None and str(v) != "nan" else "employee")
        return "contractor" if v.startswith("contract") or v in {"cwk", "temp", "vendor"} else "employee"


class VendorRow(BaseModel):
    vendor: str
    description: Optional[str] = None
    category: Optional[str] = None
    function_id: Optional[str] = None
    annual_spend: float = Field(ge=0)


class SystemRow(BaseModel):
    system: str
    function_id: Optional[str] = None
    process_id: Optional[str] = None
    system_of_record: float = Field(default=0.5, ge=0, le=1)
    api_available: float = Field(default=0.5, ge=0, le=1)
    data_quality: float = Field(default=0.5, ge=0, le=1)
    identity_resolution: float = Field(default=0.5, ge=0, le=1)
    unstructured_share: float = Field(default=0.5, ge=0, le=1)
    annual_license_cost: Optional[float] = Field(default=None, ge=0)
    data_classification: Optional[Literal["public", "internal", "confidential", "restricted"]] = None
    write_access: Optional[float] = Field(default=None, ge=0, le=1, description="1 if automation on this system can write or transact")
    external_inputs: Optional[float] = Field(default=None, ge=0, le=1, description="Share of inputs from outside the firm (email, documents, web)")
    in_scope_system: Optional[float] = Field(default=None, ge=0, le=1, description="1 if the system is in ICFR scope (ERP/GL, subledgers, billing, payroll, HRIS feeding payroll, revenue, tax, consolidation)")
    system_type: Optional[str] = Field(default=None, description="ERP/GL, billing, payroll, HRIS, CRM, ticketing, ...")

    @field_validator("data_classification", mode="before")
    @classmethod
    def _cls(cls, v):
        if v is None or str(v).strip() == "" or str(v) == "nan":
            return None
        v = str(v).strip().lower()
        alias = {"pii": "confidential", "sensitive": "confidential", "secret": "restricted", "highly confidential": "restricted",
                 "regulated": "restricted", "private": "confidential", "open": "public"}
        return alias.get(v, v)


class IntegrationRow(BaseModel):
    """Tier 3 (systems): one row per integration (interface) between systems (spec 24.4 channel c)."""
    integration: str
    source_system: Optional[str] = None
    target_system: Optional[str] = None
    process_id: Optional[str] = None
    feeds_in_scope: float = Field(default=0.0, ge=0, le=1, description="1 if the integration feeds an in-scope (ICFR) system")


class VolumeRow(BaseModel):
    process_id: Optional[str] = None
    process_name: Optional[str] = None
    annual_volume: float = Field(gt=0)
    unit: Optional[str] = None
    regulated: Optional[bool] = Field(default=None, description="Override the engine's regulated status for this process (regulated class, ICFR scope, EU AI Act high-risk, licensed sign-off)")
    icfr_scope: Optional[Literal["full", "partial", "none"]] = Field(default=None, description="Override the process's ICFR scope")

    @model_validator(mode="after")
    def _one_id(self):
        if not (self.process_id or self.process_name):
            raise ValueError("process_id or process_name is required")
        return self


class OrgInputs(BaseModel):
    """Tier 3 organizational inputs (spec Section 14.2). All optional; wide priors fill gaps."""
    governance_layers: Optional[float] = Field(default=None, ge=1, le=10)
    approval_steps_small: Optional[float] = Field(default=None, ge=0, le=20)
    approval_steps_medium: Optional[float] = Field(default=None, ge=0, le=20)
    approval_steps_large: Optional[float] = Field(default=None, ge=0, le=20)
    concurrent_initiatives: Optional[float] = Field(default=None, ge=0, le=100)
    past_transformations_attempted: Optional[float] = Field(default=None, ge=0)
    past_transformations_succeeded: Optional[float] = Field(default=None, ge=0)
    transformation_office_fte: Optional[float] = Field(default=None, ge=0)
    team_capability: Optional[float] = Field(default=None, ge=0, le=1)
    experienced_share: Optional[float] = Field(default=None, ge=0, le=1)
    delegation: Optional[float] = Field(default=None, ge=0, le=1)
    sponsor_tenure_years: Optional[float] = Field(default=None, ge=0, le=40)
    leadership_tenure_years: Optional[float] = Field(default=None, ge=0, le=40)
    planned_reorg_years: Optional[str] = Field(default=None, description="Calendar years of planned reorganizations, e.g. '2028; 2030'")
    key_persons: Optional[float] = Field(default=None, ge=0, description="People who hold critical process knowledge")
    documentation_coverage: Optional[float] = Field(default=None, ge=0, le=1)
    context_engine_coverage: Optional[float] = Field(default=None, ge=0, le=1)
    # Class d organizational parameters: the firm's own values replace the scenario ranges (spec 21.1)
    decisions_per_year: Optional[float] = Field(default=None, gt=0, le=500, description="Major go/no-go decisions on initiatives leadership can take a year (decision bandwidth)")
    change_capacity_fte: Optional[float] = Field(default=None, gt=0, description="Employees whose work can be changed in one year without disruption")
    ai_engineers_per_process: Optional[float] = Field(default=None, ge=0, le=10)
    process_owners_per_process: Optional[float] = Field(default=None, ge=0, le=5)
    sme_fte_per_process: Optional[float] = Field(default=None, ge=0, le=5)
    affected_fte_per_change_manager: Optional[float] = Field(default=None, gt=0, le=2000)
    benefit_realization_past: Optional[float] = Field(default=None, gt=0, le=1.5, description="Share of business-case benefits past programs realized")
    pilots_to_production_past: Optional[float] = Field(default=None, ge=0, le=1, description="Share of past AI pilots that reached production")
    redeployment_share: Optional[float] = Field(default=None, ge=0, le=1, description="Share of displaced staff the firm expects to redeploy")
    sells_to_us_government: Optional[float] = Field(default=None, ge=0, le=1, description="1 if the firm sells to the U.S. federal government (PQC deadline 2030)")
    it_spend: Optional[float] = Field(default=None, ge=0, description="Annual IT spend (scales the post-quantum migration cost)")
    severance_standard: Optional[Literal["asc420", "asc712"]] = Field(default=None, description="asc712 if a written severance plan exists, else asc420")
    domestic_dev_share: Optional[float] = Field(default=None, ge=0, le=1, description="Share of development work done in the U.S. (tax: sec. 174A vs 174)")
    asu_2025_06_adoption_year: Optional[float] = Field(default=None, ge=2025, le=2030)
    # labor, talent and residency (theory_labor; labor notes Section 4)
    ai_engineers_in_house: Optional[float] = Field(default=None, ge=0, description="AI and agent engineers today (Gamma_0)")
    ai_engineer_hires_per_year: Optional[float] = Field(default=None, ge=0, description="AI engineers the firm can hire a year")
    contractor_access: Optional[float] = Field(default=None, ge=0, le=1, description="1 if contract AI engineers can be engaged")
    knowledge_holders_per_process: Optional[float] = Field(default=None, ge=0, le=20, description="Critical knowledge holders per automated process (n_K)")
    knowledge_holders_displaced: Optional[float] = Field(default=None, ge=0, le=1, description="1 if those holders are among the displaced")
    contemplation_date_years: Optional[float] = Field(default=None, ge=0, le=5, description="Years from the decision until redundancies are contemplated (EU, UK default 0)")
    release_early: Optional[float] = Field(default=None, ge=0, le=1, description="1 to pay notice in lieu and release staff early")
    sub_threshold_pacing: Optional[float] = Field(default=None, ge=0, le=1, description="1 to pace dismissals below collective-procedure thresholds")
    vendor_regions: Optional[str] = Field(default=None, description="AI vendor deployment regions, e.g. 'US; EU'")
    vendor_region_premium: Optional[float] = Field(default=None, ge=0, le=1, description="Price premium of in-region deployment (p_reg)")
    vendor_dpf_certified: Optional[float] = Field(default=None, ge=0, le=1, description="1 if the AI vendor is certified under the EU-U.S. Data Privacy Framework")
    transfer_cost: Optional[float] = Field(default=None, ge=0, description="Legal and transfer-impact-assessment cost of a transfer mechanism (F_tr)")
    eu_market: Optional[float] = Field(default=None, ge=0, le=1, description="1 if AI output is used in the EU or AI systems are placed on the EU market (EU AI Act Art. 2)")
    # conditions of conditional ICFR steps (spec 24.4); unknown means "assumed in scope"
    holds_inventory: Optional[float] = Field(default=None, ge=0, le=1)
    issues_refunds_credits: Optional[float] = Field(default=None, ge=0, le=1, description="1 if support or account teams issue refunds, credits or billing adjustments")
    crm_billing_integration: Optional[float] = Field(default=None, ge=0, le=1, description="1 if booked orders flow from CRM to billing through an integration")
    subscription_billing: Optional[float] = Field(default=None, ge=0, le=1, description="1 if renewals amend billing subscriptions")
    hris_feeds_payroll: Optional[float] = Field(default=None, ge=0, le=1)
    incident_fixes_in_scope_systems: Optional[float] = Field(default=None, ge=0, le=1)
    percent_complete_revenue: Optional[float] = Field(default=None, ge=0, le=1, description="1 if revenue is recognized over time from time or progress entries")
    legal_settlements_accrued: Optional[float] = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def _past(self):
        a, s = self.past_transformations_attempted, self.past_transformations_succeeded
        if a is not None and s is not None and s > a:
            raise ValueError("past_transformations_succeeded exceeds attempted")
        return self


class SponsorRow(BaseModel):
    function_id: str
    sponsor_title: Optional[str] = None
    engaged: float = Field(default=1.0, ge=0, le=1)


class TimeStudyRow(BaseModel):
    process_id: str
    step: Optional[float] = None
    dwa_id: Optional[str] = None
    activity: Optional[str] = None
    hours_per_unit: float = Field(gt=0)
    sample_size: Optional[float] = Field(default=None, ge=0)
    cycle_time_days: Optional[float] = Field(default=None, ge=0, description="Measured elapsed time per unit, days (playbook KPI)")


class FirmTaskRow(BaseModel):
    """Tier 3 (tasks): the firm's own task list for a process step. Mapped tasks replace that step's DWA mix and
    hours (spec 29: a firm's own task list overrides the defaults)."""
    firm_task: str
    process_id: str
    step: float
    dwa_id: Optional[str] = None
    hours: float = Field(gt=0, description="Hours per output unit of the process spent on this task")
    volume: Optional[float] = Field(default=None, gt=0, description="Annual units of the task when they differ from the process's")


class PolicyInputs(BaseModel):
    """Tier 3 (policy): the firm's acceptance values for the playbook's go/no-go gates. All optional; the model
    thresholds apply where none is given."""
    residual_error_tolerance: Optional[float] = Field(default=None, gt=0, lt=1, description="Largest residual error rate accepted after review")
    min_pilot_success: Optional[float] = Field(default=None, gt=0, lt=1, description="Pilot success probability needed to scale")
    payback_limit_years: Optional[float] = Field(default=None, gt=0, le=20, description="Longest cash payback accepted")


class ProductRow(BaseModel):
    """Tier 3 (product, spec 17.4): one row per product line."""
    product_line: str
    revenue: float = Field(ge=0, description="Annual revenue of the line")
    pricing_model: Literal["seat", "usage", "outcome", "two_part", "hybrid"] = "seat"
    seats: Optional[float] = Field(default=None, ge=0)
    price_per_seat: Optional[float] = Field(default=None, ge=0)
    usage_units: Optional[float] = Field(default=None, ge=0)
    price_per_unit: Optional[float] = Field(default=None, ge=0)
    nrr: Optional[float] = Field(default=None, ge=0, le=3, description="Net revenue retention, e.g. 1.10")
    grr: Optional[float] = Field(default=None, ge=0, le=1, description="Gross revenue retention, e.g. 0.90")
    gross_margin: Optional[float] = Field(default=None, ge=-1, le=1)
    labor_substituting: Optional[float] = Field(default=None, ge=0, le=1, description="1 if the product does work the customer's staff would do")
    proprietary_data: Optional[float] = Field(default=None, ge=0, le=1, description="Proprietary data and workflow lock-in score, 0 to 1")
    competitor_price: Optional[float] = Field(default=None, ge=0, description="A rival's price per seat or per outcome, if known")
    customer_hours_per_outcome: Optional[float] = Field(default=None, gt=0, description="Customer staff hours one outcome (e.g. one resolution) replaces")
    seat_share_of_bill: Optional[float] = Field(default=None, ge=0, le=1, description="Share of the bill priced per seat (1 for pure seat pricing)")
    billing_in_advance: Optional[float] = Field(default=None, ge=0, le=1, description="1 if billed annually in advance")
    agent_unit_cost: Optional[float] = Field(default=None, ge=0, description="Your AI agent's cost per outcome (inference, escalation, hosting)")
    entrant_unit_cost: Optional[float] = Field(default=None, ge=0, description="An AI-native entrant's estimated cost per outcome")
    entry_hazard: Optional[float] = Field(default=None, ge=0, le=5, description="Expected AI-native entries a year in this line")

    @field_validator("pricing_model", mode="before")
    @classmethod
    def _pm(cls, v):
        if v is None or str(v).strip() == "" or str(v) == "nan":
            return "seat"
        v = str(v).strip().lower().replace("-", "_").replace(" ", "_")
        return {"per_seat": "seat", "subscription": "seat", "consumption": "usage", "per_outcome": "outcome",
                "fixed_plus_usage": "two_part", "two_part_tariff": "two_part"}.get(v, v)


class ProductOccupationRow(BaseModel):
    """Tier 3 (product): the customer occupations behind each line's seats (spec 17.1)."""
    product_line: str
    soc: str
    seat_share: float = Field(gt=0, le=1)


class AIFeatureRow(BaseModel):
    """Tier 3 (product): candidate AI features or AI-native products with cost estimates (spec 17.4)."""
    feature: str
    product_line: Optional[str] = None
    kind: Literal["copilot", "agent", "new_product"] = "copilot"
    dev_cost: Optional[float] = Field(default=None, ge=0)
    run_cost_per_year: Optional[float] = Field(default=None, ge=0)
    price_uplift_share: Optional[float] = Field(default=None, ge=0, le=2)
    new_revenue_at_full_adoption: Optional[float] = Field(default=None, ge=0)
    inference_units_per_year: Optional[float] = Field(default=None, ge=0, description="Customer work hours the feature performs a year at full adoption")
    model_choice: Literal["api", "open_weights", "own", "any"] = "any"
    bass_p: Optional[float] = Field(default=None, gt=0, le=1)
    bass_q: Optional[float] = Field(default=None, ge=0, le=3)
    retention_gain: Optional[float] = Field(default=None, ge=-0.2, le=0.2)


class SecurityInputs(BaseModel):
    """Tier 3 (security, spec 18.5). All optional."""
    security_team_fte: Optional[float] = Field(default=None, ge=0)
    reviews_per_year: Optional[float] = Field(default=None, ge=0, description="Security and compliance reviews the team can complete a year")
    certifications: Optional[str] = Field(default=None, description="Current certifications, separated by semicolons: soc2; iso27001; iso42001")
    risk_appetite_max_class: Optional[Literal["public", "internal", "confidential", "restricted"]] = None
    vendor_preference: Optional[Literal["build", "buy", "either"]] = None
    incidents_last_3_years: Optional[float] = Field(default=None, ge=0)
    max_tolerable_loss: Optional[float] = Field(default=None, gt=0)
    change_controls_share: Optional[float] = Field(default=None, ge=0, le=1, description="Share of model, prompt and tool "
        "regressions the firm's change controls stop (pinned versions, testing before promotion, rollback)")


class RegimeInputs(BaseModel):
    """Tier 3 (ownership, spec 16.3). All optional; presets fill the rest."""
    ownership_regime: Optional[Literal["public", "private_family", "pe", "vc", "hybrid", "permanent_capital"]] = None
    hold_years_elapsed: Optional[float] = Field(default=None, ge=0, le=20)
    hold_years_total: Optional[float] = Field(default=None, gt=0, le=20)
    entry_ev: Optional[float] = Field(default=None, gt=0)
    exit_multiple: Optional[float] = Field(default=None, gt=0, le=60)
    covenant_max_leverage: Optional[float] = Field(default=None, gt=0, le=20)
    target_irr: Optional[float] = Field(default=None, gt=0, le=1)
    guidance_r40: Optional[float] = Field(default=None, ge=-1, le=2)
    guidance_eps_growth: Optional[float] = Field(default=None, ge=-1, le=5)
    dividend_payout: Optional[float] = Field(default=None, ge=0, le=1)
    controlling_holder: Optional[float] = Field(default=None, ge=0, le=1, description="1 if a controlling holder or dual-class shares exist")
    # buying growth (theory_acquirer.tex prop:acq-limits); all optional
    nrr: Optional[float] = Field(default=None, gt=0, le=3, description="Net revenue retention, share of prior-year revenue from the same customers")
    acquisition_price_to_revenue: Optional[float] = Field(default=None, gt=0, le=50, description="Price paid per dollar of acquired revenue (k_acq)")
    target_growth: Optional[float] = Field(default=None, ge=-1, le=5, description="Revenue growth the owner wants to hold")
    reference_target_revenue: Optional[float] = Field(default=None, gt=0, description="Target revenue at which the hurdle headroom is h_0")
    switching_cost_ratio_mean: Optional[float] = Field(default=None, gt=0, le=20, description="Mean ratio of customers' switching cost to a contract term's bill")
    # buying growth after round 2 (notes/acquirer_fixes_v2.md Section 5); all optional
    subscription_share: Optional[float] = Field(default=None, ge=0, le=1, description="Subscription share of revenue at the start of the year (the part that retains at NRR)")
    nonsub_zero_spend_growth: Optional[float] = Field(default=None, ge=-1, le=1, description="Annual change of non-subscription revenue without spend")
    organic_growth_reported: Optional[float] = Field(default=None, ge=-1, le=5, description="Organic growth as the company reports it (annual; company-defined, usually unaudited)")
    operating_cash_flow: Optional[float] = Field(default=None, description="Operating cash flow as reported (after interest paid under U.S. GAAP)")
    interest_paid: Optional[float] = Field(default=None, ge=0, description="Cash paid for interest in the year (interest expense if not reported)")
    interest_tax_rate: Optional[float] = Field(default=None, ge=0, le=0.6, description="Tax rate the interest deduction saves (statutory; e.g. 0.24 for Italy's IRES)")
    acquisition_outlays: Optional[str] = Field(default=None, description="Acquisition outlays net of cash acquired: 'year:amount' or "
                                               "'year:amount@date' entries separated by semicolons; date is the share of the year elapsed (default 0.5)")


class JurisdictionRow(BaseModel):
    """Tier 3 (people and law, spec 24.5 and 24.6): headcount by country and site, with the labor-law and
    data-residency attributes that set timing and cost."""
    site: str
    country: Optional[str] = None
    headcount: float = Field(ge=0)
    works_council: float = Field(default=0.0, ge=0, le=1, description="1 if a works council must be consulted")
    union_coverage: float = Field(default=0.0, ge=0, le=1, description="Share of the site's staff covered by a collective agreement")
    data_residency: Literal["none", "region", "country"] = "none"
    function_id: Optional[str] = None
    # labor-law inputs (theory_labor ass:labor-proc; labor notes Section 4). All optional.
    subnational: Optional[str] = Field(default=None, description="U.S. state (CA, NY, NJ ...) or Indian state")
    headcount_max_12m: Optional[float] = Field(default=None, ge=0, description="Maximum headcount in the preceding 12 months (Cal-WARN)")
    employer_country_headcount: Optional[float] = Field(default=None, ge=0, description="Employer headcount in the country (WARN 100, NY 50, FR PSE 50)")
    part_time_share: Optional[float] = Field(default=None, ge=0, le=1)
    tenure_mean: Optional[float] = Field(default=None, ge=0, le=50, description="Mean tenure of staff at the site, years")
    age_mean: Optional[float] = Field(default=None, ge=16, le=80)
    monthly_pay: Optional[float] = Field(default=None, ge=0, description="Typical monthly pay at the site, local currency converted to USD")
    india_site_type: Optional[Literal["factory", "mine", "plantation", "other"]] = None
    severance_plan_months: Optional[float] = Field(default=None, ge=0, le=36, description="Negotiated severance plan, months of pay per displaced employee")
    transfer_mechanism: Optional[Literal["none", "adequacy", "dpf", "scc", "bcr", "cn_contract", "cn_assessment"]] = Field(
        default=None, description="Legal basis for transferring the site's personal data to the AI vendor's region")
    cn_subjects_per_year: Optional[float] = Field(default=None, ge=0, description="Chinese data subjects whose data leave China a year")
    ciio: Optional[float] = Field(default=None, ge=0, le=1, description="1 if a Chinese critical information infrastructure operator")
    wage_index: Optional[float] = Field(default=None, gt=0, le=3, description="Site wage relative to the U.S. median for the same roles")

    @field_validator("data_residency", mode="before")
    @classmethod
    def _dr(cls, v):
        if v is None or str(v).strip() == "" or str(v) == "nan":
            return "none"
        v = str(v).strip().lower()
        return {"eu": "region", "regional": "region", "national": "country", "no": "none", "0": "none"}.get(v, v)


class MappingRow(BaseModel):
    source_type: Literal["cost_center", "gl_account", "title", "vendor"]
    source_value: str
    target: str
    confidence: float = Field(default=1.0, ge=0, le=1)
    user_confirmed: float = Field(default=1.0, ge=0, le=1)


# --------------------------------------------------------------------------------------------
# Template specifications
# --------------------------------------------------------------------------------------------
TemplateKind = Literal["table", "keyvalue"]


class TemplateSpec(BaseModel):
    name: str
    tier: str
    kind: TemplateKind
    model: str
    purpose: str
    columns: list[tuple[str, str, bool]]  # (column, description, required)
    example: list[dict]


TEMPLATES: dict[str, TemplateSpec] = {}


def _t(**kw):
    TEMPLATES[kw["name"]] = TemplateSpec(**kw)


_t(name="tier0_financials", tier="Tier 0", kind="keyvalue", model="Financials",
   purpose="Public financials for one fiscal year, as in a 10-K or XBRL filing. This file is required.",
   columns=[("revenue", "Annual revenue", True), ("cogs", "Cost of revenue", True),
            ("rnd", "Research and development expense", True), ("sm", "Sales and marketing expense", True),
            ("ga", "General and administrative expense", True),
            ("company_name", "Company name", False), ("fiscal_year", "Fiscal year, for example 2025", False),
            ("currency", "Currency code; the engine assumes amounts are in this currency", False),
            ("sbc", "Stock-based compensation, already included in the expense lines", False),
            ("da", "Depreciation and amortization", False), ("capex", "Capital expenditure including capitalized software", False),
            ("headcount", "Employees at year end", False), ("naics", "NAICS code (2 to 6 digits)", False),
            ("sic", "SIC code", False), ("revenue_growth", "Revenue growth over the year, as a fraction (0.15 = 15 percent)", False),
            ("market_growth", "Growth of the addressable market, as a fraction", False),
            ("capital_intensity_k", "Capital per dollar of revenue (Part I k)", False),
            ("ev_revenue_multiple", "Enterprise value to revenue, if public", False),
            ("growth_weight_low", "Low end of your decision weight on growth X, if you have a view (else 2.5, 5, 9 are shown)", False),
            ("growth_weight_high", "High end of your decision weight on growth X", False),
            ("multiple_is_net_of_pressure", "1 if that multiple is already net of public earnings pressure (default 0)", False),
            ("fcf_margin", "Free cash flow after stock-based compensation over revenue, if known", False),
            ("tax_rate", "Cash tax rate, as a fraction", False),
            ("owned_compute_share", "Share of AI inference run on owned computing capacity, 0 to 1", False),
            ("bonus_election", "Owned servers: none (100% bonus, current law), elect_out, transitional_40 or transitional_60", False),
            ("foreign_server_share", "Owned servers: share used predominantly outside the United States (no bonus)", False),
            ("context_engine", "1 if an organizational context engine or long-term memory platform is in place, else 0", False),
            ("ownership_regime", "public, private_family, pe, vc, hybrid or permanent_capital", False),
            ("net_debt", "Net debt (debt minus cash)", False), ("ebitda", "EBITDA, if reported", False),
            ("shares_outstanding", "Diluted shares, for the EPS path of public firms", False),
            ("market_hhi", "Your own value: Herfindahl index of your product markets (1/number of equal rivals). Without it results are shown over HHI 0.1 to 0.5", False),
            ("industry_pass_through", "Your own value: share of a common cost change passed to prices in your industry", False)],
   example=[{"field": "revenue", "value": 650000000}, {"field": "cogs", "value": 156000000},
            {"field": "rnd", "value": 150000000}, {"field": "sm", "value": 215000000},
            {"field": "ga", "value": 78000000}, {"field": "naics", "value": "513210"}])
_t(name="tier1_opex", tier="Tier 1", kind="table", model="OpexRow",
   purpose="Operating expense by cost center and GL account (a trial balance). The engine maps each cost center to a function and each GL account to a cost type.",
   columns=[("cost_center", "Cost center code", True), ("amount", "Annual amount", True),
            ("cost_center_name", "Cost center name; used for mapping to functions", False),
            ("gl_account", "GL account code", False), ("gl_name", "GL account name; used to separate labor from other costs", False),
            ("function_id", "Optional function id from the engine taxonomy; overrides the mapping", False),
            ("headcount", "Optional headcount in the cost center", False)],
   example=[{"cost_center": "CC-4100", "cost_center_name": "Customer Support Americas", "gl_account": "6000",
             "gl_name": "Salaries and wages", "amount": 9800000}])
_t(name="tier2_roster", tier="Tier 2", kind="table", model="RosterRow",
   purpose="Headcount and pay by role. One row per role and location (or per person). Titles are mapped to SOC codes.",
   columns=[("title", "Job title", True), ("fte", "Full-time equivalents in this row", True),
            ("annual_base_comp", "Gross annual pay per FTE before benefits", True),
            ("role_id", "Optional identifier", False), ("cost_center", "Cost center code", False),
            ("function_id", "Optional function id; overrides the cost-center mapping", False),
            ("soc", "Optional SOC 2018 code (for example 15-1252); overrides title matching", False),
            ("annual_total_comp", "Optional total pay including bonus and equity", False),
            ("location", "City or country; sets the wage index", False),
            ("wage_index", "Optional wage index relative to the US national median", False),
            ("worker_type", "employee or contractor", False), ("level", "Optional level or grade", False)],
   example=[{"title": "Software Developer", "cost_center": "CC-2000", "fte": 12, "annual_base_comp": 135980,
             "location": "Austin, TX", "worker_type": "employee"}])
_t(name="tier3_vendors", tier="Tier 3", kind="table", model="VendorRow",
   purpose="Vendor and outsourcing spend. Outsourced labor becomes work in the outsourced mode; other spend is classified by category.",
   columns=[("vendor", "Vendor name", True), ("annual_spend", "Annual spend", True),
            ("description", "What the vendor provides; used for mapping", False),
            ("category", "Optional category id (see README)", False), ("function_id", "Optional function id", False)],
   example=[{"vendor": "Northwind Support Partners", "description": "Tier 1 contact center BPO", "annual_spend": 6200000}])
_t(name="tier3_systems", tier="Tier 3", kind="table", model="SystemRow",
   purpose="Systems inventory with readiness proxies. Used to compute data readiness per function and process.",
   columns=[("system", "System name", True), ("function_id", "Function the system serves", False),
            ("process_id", "Optional process id", False),
            ("system_of_record", "1 if it is the system of record for its data, else 0 (or a share)", False),
            ("api_available", "Share of the data reachable by API, 0 to 1", False),
            ("data_quality", "Master-data quality, 0 to 1", False), ("identity_resolution", "Identity resolution across systems, 0 to 1", False),
            ("unstructured_share", "Share of inputs that are unstructured (documents, email), 0 to 1", False),
            ("annual_license_cost", "Annual license and infrastructure cost", False),
            ("data_classification", "public, internal, confidential or restricted: the most sensitive data the system holds", False),
            ("write_access", "1 if automation on this system could write or transact, 0 if read-only", False),
            ("external_inputs", "Share of inputs that come from outside the firm (email, documents, web): prompt-injection surface", False),
            ("in_scope_system", "1 if the system is in ICFR scope (ERP/GL, subledgers, billing, payroll, HRIS feeding payroll, revenue, tax, consolidation)", False),
            ("system_type", "ERP/GL, billing, payroll, HRIS, CRM, ticketing, ...", False)],
   example=[{"system": "ERP", "function_id": "F11", "system_of_record": 1, "api_available": 0.7,
             "data_quality": 0.7, "identity_resolution": 0.6, "unstructured_share": 0.2, "data_classification": "confidential",
             "write_access": 1, "external_inputs": 0.1}])
_t(name="tier3_integrations", tier="Tier 3", kind="table", model="IntegrationRow",
   purpose="Integrations between systems, with a flag for those that feed an ICFR in-scope system (spec 24.4: interface completeness and accuracy). Wave 0 inventories them.",
   columns=[("integration", "Name of the interface", True), ("source_system", "Sending system", False),
            ("target_system", "Receiving system", False), ("process_id", "Process it serves (P01 ...)", False),
            ("feeds_in_scope", "1 if it feeds ERP/GL, a subledger, billing, payroll, revenue, tax or consolidation", False)],
   example=[{"integration": "CRM to billing orders", "source_system": "CRM", "target_system": "Billing", "process_id": "P08", "feeds_in_scope": 1}])
_t(name="tier3_volumes", tier="Tier 3", kind="table", model="VolumeRow",
   purpose="Annual process volumes (tickets, invoices, orders). Replaces the per-revenue priors.",
   columns=[("process_id", "Process id from the engine library (or give process_name)", False),
            ("process_name", "Process name", False), ("annual_volume", "Units per year", True), ("unit", "Output unit", False)],
   example=[{"process_id": "ticket_to_resolution", "annual_volume": 780000, "unit": "ticket"}])
_t(name="tier3_org", tier="Tier 3 (organizational)", kind="keyvalue", model="OrgInputs",
   purpose="Decision-making capacity and transformation record (spec Section 14). Every field is optional; wide priors fill gaps.",
   columns=[("governance_layers", "Layers of governance an initiative passes through", False),
            ("approval_steps_small", "Approval steps for a small initiative", False),
            ("approval_steps_medium", "Approval steps for a medium initiative", False),
            ("approval_steps_large", "Approval steps for a large initiative", False),
            ("concurrent_initiatives", "Major initiatives running today", False),
            ("past_transformations_attempted", "Transformation programs attempted in the last five years", False),
            ("past_transformations_succeeded", "Of those, how many met their goals", False),
            ("transformation_office_fte", "Full-time staff in a transformation office", False),
            ("team_capability", "Self-assessed delivery capability, 0 to 1", False),
            ("experienced_share", "Share of delivery staff with prior automation experience, 0 to 1", False),
            ("delegation", "Share of approval decisions delegated below the executive team, 0 to 1", False),
            ("sponsor_tenure_years", "Years the program's executive sponsor has been in role", False),
            ("leadership_tenure_years", "Years the CEO has been in role", False),
            ("planned_reorg_years", "Calendar years of planned or likely reorganizations, separated by semicolons", False),
            ("key_persons", "Number of people who hold critical process knowledge", False),
            ("documentation_coverage", "Share of critical processes with current documentation, 0 to 1", False),
            ("context_engine_coverage", "Share of process context held in an organizational context engine, 0 to 1", False),
            ("decisions_per_year", "Your own value: major go/no-go decisions on initiatives leadership can take a year. Without it the engine reports results over a scenario range", False),
            ("change_capacity_fte", "Your own value: employees whose work can change in one year without disruption. Without it the engine uses a scenario range", False),
            ("ai_engineers_per_process", "Your own team ratio: AI engineers per automated process in run mode", False),
            ("process_owners_per_process", "Your own team ratio: process owners per process in transition", False),
            ("sme_fte_per_process", "Your own team ratio: subject-matter experts per process in transition", False),
            ("affected_fte_per_change_manager", "Your own team ratio: affected employees one change manager supports a year", False),
            ("benefit_realization_past", "Your success history: share of business-case benefits past programs realized, e.g. 0.7", False),
            ("pilots_to_production_past", "Your success history: share of past AI pilots that reached production", False),
            ("redeployment_share", "Share of displaced staff you expect to redeploy", False),
            ("sells_to_us_government", "1 if you sell to the U.S. federal government (post-quantum deadline 2030)", False),
            ("it_spend", "Annual IT spend; scales the post-quantum cryptography migration cost", False),
            ("severance_standard", "asc712 if a written severance plan exists, else asc420", False),
            ("domestic_dev_share", "Share of AI development done in the U.S.; the rest is amortized over 15 years for tax", False),
            ("asu_2025_06_adoption_year", "Fiscal year you adopt ASU 2025-06 (2028 if not early)", False),
            ("ai_engineers_in_house", "AI and agent engineers employed today", False),
            ("ai_engineer_hires_per_year", "AI engineers you can hire in a year", False),
            ("knowledge_holders_per_process", "People per process whose knowledge is critical and undocumented", False),
            ("knowledge_holders_displaced", "1 if those people are among the displaced", False),
            ("vendor_regions", "Regions where your AI vendor can run models, e.g. 'US; EU'", False),
            ("vendor_dpf_certified", "1 if the AI vendor is certified under the EU-U.S. Data Privacy Framework", False),
            ("transfer_cost", "Legal and impact-assessment cost of a data-transfer mechanism", False),
            ("eu_market", "1 if AI output is used in the EU or AI systems are placed on the EU market (EU AI Act)", False),
            ("holds_inventory", "1 if the firm holds inventory (inventory steps enter ICFR scope)", False),
            ("issues_refunds_credits", "1 if support or account teams issue refunds, credits or billing adjustments", False),
            ("crm_billing_integration", "1 if booked orders flow from CRM to billing through an integration", False),
            ("subscription_billing", "1 if renewals and expansions amend billing subscriptions", False),
            ("percent_complete_revenue", "1 if revenue is recognized over time from time or progress entries", False)],
   example=[{"field": "governance_layers", "value": 3}, {"field": "concurrent_initiatives", "value": 5},
            {"field": "decisions_per_year", "value": 12}, {"field": "benefit_realization_past", "value": 0.7}])
_t(name="tier3_jurisdictions", tier="Tier 3 (people and law)", kind="table", model="JurisdictionRow",
   purpose="Headcount by country and site, works councils, union coverage and data-residency rules (spec 24.5, 24.6). Sets notice and consultation timing, severance and in-region deployment costs.",
   columns=[("site", "Site or legal entity", True), ("headcount", "Employees at the site", True),
            ("country", "Country name or ISO code", False),
            ("works_council", "1 if a works council must be consulted before changes in work organization", False),
            ("union_coverage", "Share of staff covered by a collective agreement, 0 to 1", False),
            ("data_residency", "none, region (e.g. EU) or country: where personal and confidential data must stay", False),
            ("function_id", "Optional function id if the site serves one function", False),
            ("subnational", "U.S. state (CA, NY, NJ) or Indian state; state rules apply", False),
            ("employer_country_headcount", "Employees of the employer in this country (WARN coverage, PSE)", False),
            ("tenure_mean", "Mean tenure at the site, years (statutory floors and notice)", False),
            ("age_mean", "Mean age at the site (UK redundancy pay)", False),
            ("severance_plan_months", "Negotiated severance, months of pay; the engine takes the larger of this and the statutory floor", False),
            ("transfer_mechanism", "none, adequacy, dpf, scc, bcr, cn_contract or cn_assessment: basis for moving personal data to the AI vendor", False),
            ("india_site_type", "factory, mine, plantation or other (Indian Chapter X prior permission)", False),
            ("wage_index", "Site wage relative to the U.S. median for the same roles (otherwise OECD averages)", False)],
   example=[{"site": "Austin", "country": "US", "headcount": 900}, {"site": "Dublin", "country": "IE", "headcount": 300,
             "works_council": 0, "data_residency": "region"}, {"site": "Munich", "country": "DE", "headcount": 120, "works_council": 1, "data_residency": "region"}])
_t(name="tier3_sponsors", tier="Tier 3 (organizational)", kind="table", model="SponsorRow",
   purpose="Executive sponsor assignment by function.",
   columns=[("function_id", "Function id", True), ("sponsor_title", "Sponsor's role", False),
            ("engaged", "1 if the sponsor is committed, 0 if not, or a probability", False)],
   example=[{"function_id": "finance_accounting", "sponsor_title": "CFO", "engaged": 1}])
_t(name="tier4_time_study", tier="Tier 4", kind="table", model="TimeStudyRow",
   purpose="Optional time studies or event-log measures of hours per unit by process step.",
   columns=[("process_id", "Process id", True), ("hours_per_unit", "Measured hours per output unit", True),
            ("step", "Step number in the process library", False), ("dwa_id", "O*NET DWA or GWA id of the step", False),
            ("activity", "Free-text activity name", False), ("sample_size", "Number of observations", False),
            ("cycle_time_days", "Measured elapsed time per unit, days", False)],
   example=[{"process_id": "procure_to_pay", "step": 2, "hours_per_unit": 0.12, "sample_size": 400}])
_t(name="tier3_tasks", tier="Tier 3 (tasks)", kind="table", model="FirmTaskRow",
   purpose="Your own task list for a process step. Each task is mapped to an O*NET detailed work activity (the dwa_id you give, else the closest O*NET task statement); mapped tasks replace the step's activity mix and hours, unmapped ones are listed in firm_tasks_mapping.csv.",
   columns=[("firm_task", "Task as your team describes it", True), ("process_id", "Process id (P01 ...)", True),
            ("step", "Step number in the process library", True), ("dwa_id", "O*NET DWA id, if known", False),
            ("hours", "Hours per output unit spent on the task", True), ("volume", "Annual units, if not the process's volume", False)],
   example=[{"firm_task": "Match supplier invoices to purchase orders and receipts", "process_id": "P02", "step": 5, "hours": 0.08}])
_t(name="tier3_policy", tier="Tier 3 (policy)", kind="keyvalue", model="PolicyInputs",
   purpose="Your acceptance values for the playbook's go/no-go gates. The model thresholds apply where you give none.",
   columns=[("residual_error_tolerance", "Largest residual error rate accepted after review, e.g. 0.02", False),
            ("min_pilot_success", "Pilot success probability needed to scale, e.g. 0.7", False),
            ("payback_limit_years", "Longest cash payback accepted, years", False)],
   example=[{"field": "residual_error_tolerance", "value": 0.02}, {"field": "payback_limit_years", "value": 3}])
_t(name="tier3_products", tier="Tier 3 (product)", kind="table", model="ProductRow",
   purpose="Revenue by product line and pricing model (spec 17). Used for seat compression, pricing migration and the AI product roadmap.",
   columns=[("product_line", "Name of the product line", True), ("revenue", "Annual revenue of the line", True),
            ("pricing_model", "seat, usage, outcome, two_part (fixed fee plus usage) or hybrid", False),
            ("seats", "Seats sold", False), ("price_per_seat", "Annual price per seat", False),
            ("usage_units", "Usage units billed a year", False), ("price_per_unit", "Price per usage unit or outcome", False),
            ("nrr", "Net revenue retention, e.g. 1.10", False), ("grr", "Gross revenue retention, e.g. 0.90", False),
            ("gross_margin", "Gross margin of the line, e.g. 0.75", False),
            ("labor_substituting", "1 if the product does work the customer's staff would otherwise do", False),
            ("proprietary_data", "Proprietary data and workflow lock-in, 0 to 1", False),
            ("competitor_price", "A rival's price per seat or per outcome, if known", False),
            ("customer_hours_per_outcome", "Customer staff hours that one outcome replaces (e.g. 0.3 for a support resolution)", False)],
   example=[{"product_line": "Help desk", "revenue": 420000000, "pricing_model": "seat", "seats": 350000, "price_per_seat": 1200,
             "nrr": 1.08, "grr": 0.9, "gross_margin": 0.78, "labor_substituting": 1, "proprietary_data": 0.6}])
_t(name="tier3_product_occupations", tier="Tier 3 (product)", kind="table", model="ProductOccupationRow",
   purpose="The customer occupations behind each product line's seats. Seat compression is projected from these occupations' exposure to AI.",
   columns=[("product_line", "Product line name as in tier3_products", True), ("soc", "SOC 2018 code of the seat holders, e.g. 43-4051", True),
            ("seat_share", "Share of the line's seats held by this occupation, 0 to 1", True)],
   example=[{"product_line": "Help desk", "soc": "43-4051", "seat_share": 0.7}, {"product_line": "Help desk", "soc": "15-1232", "seat_share": 0.3}])
_t(name="tier3_ai_features", tier="Tier 3 (product)", kind="table", model="AIFeatureRow",
   purpose="Candidate AI features or AI-native products with cost estimates. Blank cells use documented defaults.",
   columns=[("feature", "Feature name", True), ("product_line", "Product line it belongs to", False),
            ("kind", "copilot (assists the customer's staff), agent (does the work) or new_product", False),
            ("dev_cost", "One-time development cost", False), ("run_cost_per_year", "Annual run cost beyond inference", False),
            ("price_uplift_share", "Price uplift at full adoption, share of the line's price", False),
            ("new_revenue_at_full_adoption", "New annual revenue at full adoption", False),
            ("inference_units_per_year", "Customer work hours the feature performs a year at full adoption", False),
            ("model_choice", "api, open_weights, own or any (the engine chooses)", False),
            ("bass_p", "Innovation coefficient, if you have your own adoption data", False),
            ("bass_q", "Imitation coefficient, if you have your own adoption data", False),
            ("retention_gain", "Net revenue retention gain at full adoption, e.g. 0.01", False)],
   example=[{"feature": "Resolution agent", "product_line": "Help desk", "kind": "agent", "dev_cost": 6000000}])
_t(name="tier3_security", tier="Tier 3 (security)", kind="keyvalue", model="SecurityInputs",
   purpose="Security team capacity, certifications and risk appetite (spec 18). Every field is optional.",
   columns=[("security_team_fte", "Security and compliance staff who review deployments", False),
            ("reviews_per_year", "Deployment reviews the team can complete a year", False),
            ("certifications", "Current certifications separated by semicolons, e.g. soc2; iso27001", False),
            ("risk_appetite_max_class", "Most sensitive data class AI may touch: public, internal, confidential or restricted", False),
            ("vendor_preference", "build, buy or either", False),
            ("incidents_last_3_years", "Security incidents in the last three years", False),
            ("max_tolerable_loss", "Largest single loss the firm will bear", False),
            ("change_controls_share", "Share of model, prompt and tool regressions your change controls stop, 0 to 1", False)],
   example=[{"field": "security_team_fte", "value": 12}, {"field": "certifications", "value": "soc2; iso27001"}])
_t(name="tier3_regime", tier="Tier 3 (ownership)", kind="keyvalue", model="RegimeInputs",
   purpose="Ownership regime and its terms (spec 16). Every field is optional; presets fill the rest.",
   columns=[("ownership_regime", "public, private_family, pe, vc, hybrid or permanent_capital", False),
            ("hold_years_elapsed", "PE or VC: years since entry", False), ("hold_years_total", "PE or VC: planned hold", False),
            ("entry_ev", "Enterprise value at entry", False), ("exit_multiple", "Expected EV/EBITDA at exit", False),
            ("covenant_max_leverage", "Covenant cap on net debt / EBITDA", False), ("target_irr", "Target IRR", False),
            ("guidance_r40", "Public: guided Rule-of-40 score, e.g. 0.30", False),
            ("guidance_eps_growth", "Public: guided EPS growth, e.g. 0.10", False),
            ("dividend_payout", "Dividends and buybacks, share of free cash flow", False),
            ("controlling_holder", "1 if a controlling holder or dual-class shares exist", False),
            ("nrr", "Buying growth: net revenue retention, e.g. 0.93", False),
            ("acquisition_price_to_revenue", "Buying growth: price paid per dollar of acquired revenue", False),
            ("target_growth", "Buying growth: revenue growth to hold, e.g. 0.30", False),
            ("reference_target_revenue", "Buying growth: target revenue at which the hurdle headroom is h_0", False),
            ("switching_cost_ratio_mean", "Repricing: mean switching cost over a contract term's bill", False),
            ("subscription_share", "Buying growth: subscription share of revenue, e.g. 0.8", False),
            ("nonsub_zero_spend_growth", "Buying growth: annual change of non-subscription revenue without spend, e.g. 0", False),
            ("organic_growth_reported", "Buying growth: organic growth as the company reports it, e.g. 0.03", False),
            ("operating_cash_flow", "Buying growth: operating cash flow as reported", False),
            ("interest_paid", "Buying growth: cash paid for interest", False),
            ("interest_tax_rate", "Buying growth: tax rate the interest deduction saves, e.g. 0.24", False),
            ("acquisition_outlays", "Buying growth: outlays by year, e.g. 2023:520e6; 2024:900e6; 2025:1850e6@0.8", False)],
   example=[{"field": "ownership_regime", "value": "public"}, {"field": "guidance_r40", "value": 0.3}])
_t(name="mappings", tier="Feedback", kind="table", model="MappingRow",
   purpose="Corrections to the engine's mappings. Copy rows from mapping_review.csv in an output folder, fix the target, set user_confirmed to 1 and put the file in the input folder.",
   columns=[("source_type", "cost_center, gl_account, title or vendor", True), ("source_value", "The value as it appears in your files", True),
            ("target", "Function id, cost type, SOC code or vendor category", True),
            ("confidence", "Ignored on input; kept for reference", False), ("user_confirmed", "1 to apply the row", False)],
   example=[{"source_type": "title", "source_value": "Revenue Operations Lead", "target": "13-1199", "user_confirmed": 1}])


TIER_GUIDE = """# autofrontier input folder

Fill in the files you have. Only tier0_financials is required; every other file is optional and the engine
fills what is missing from documented priors, with wider confidence intervals.

| tier | files | what it adds |
|---|---|---|
| Tier 0 | tier0_financials | public financials: revenue, cost lines, headcount, industry |
| Tier 1 | tier1_opex | opex by cost center and GL account |
| Tier 2 | tier2_roster | headcount and pay by title, mapped to SOC occupations |
| Tier 3 | tier3_vendors, tier3_systems, tier3_volumes | outsourcing spend, systems and readiness, process volumes |
| Tier 3 (organizational) | tier3_org, tier3_sponsors | governance, decision capacity, leadership tenure, key persons |
| Tier 3 (product) | tier3_products, tier3_product_occupations, tier3_ai_features | product lines, seats and the customer occupations behind them, AI feature candidates |
| Tier 3 (security) | tier3_security | security review capacity, certifications, risk appetite |
| Tier 3 (ownership) | tier3_regime | ownership regime and its terms |
| Tier 3 (people and law) | tier3_jurisdictions | headcount by site, works councils, unions, data residency |
| Tier 4 | tier4_time_study | measured hours per unit by process step |
| Feedback | mappings | your corrections to the engine's mappings |

Fields marked "your own value" replace scenario ranges: without them the engine reports the results that depend
on them as ranges over documented scenario values, not as points.

Each file has its own README_<file>.md. Put either the CSV or the XLSX version (from the xlsx folder) in this
folder, not both. Then run:

    autofrontier run <this folder> --out <output folder>

The engine runs on your computer, makes no network calls and writes only to the output folder.
"""


def _readme_text(spec: TemplateSpec, function_ids: list[str] | None = None, vendor_categories: list[str] | None = None) -> str:
    lines = [f"# {spec.name}", "", f"{spec.tier}. {spec.purpose}", "",
             "Fill in this file and leave it in your input folder. The CSV and XLSX versions are equivalent; use one.",
             "Amounts are annual and in the currency of tier0_financials. Leave a cell blank if you do not know the value.", "",
             "## Columns", "", "| column | required | meaning |", "|---|---|---|"]
    for c, d, req in spec.columns:
        lines.append(f"| {c} | {'yes' if req else 'no'} | {d} |")
    lines += ["", "## Example", ""]
    if spec.kind == "keyvalue":
        lines.append("This file has two columns, field and value, one row per field.")
        lines.append("")
    ex = pd.DataFrame(spec.example)
    lines.append("| " + " | ".join(ex.columns) + " |")
    lines.append("|" + "---|" * len(ex.columns))
    for _, row in ex.iterrows():
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in row.values) + " |")
    if spec.name == "tier3_vendors" and vendor_categories:
        lines += ["", "## Vendor categories", "", ", ".join(vendor_categories)]
    if function_ids and spec.name in ("tier1_opex", "tier2_roster", "tier3_systems", "tier3_sponsors", "tier3_vendors"):
        lines += ["", "## Function ids", "", ", ".join(function_ids)]
    lines += ["", "## If something is wrong", "",
              "The engine checks every row. A row with a wrong type or a value out of range is reported in "
              "validation_report.md in the output folder, with the row number and how to fix it, and the row is left out. "
              "A missing optional file is filled from priors and listed under data gaps in the report.", "",
              "Privacy: the engine runs on your computer, makes no network calls and writes only to the output folder you choose."]
    return "\n".join(lines) + "\n"


def template_frame(spec: TemplateSpec) -> pd.DataFrame:
    if spec.kind == "keyvalue":
        return pd.DataFrame({"field": [c for c, _, _ in spec.columns], "value": [""] * len(spec.columns)})
    return pd.DataFrame(columns=[c for c, _, _ in spec.columns])


def write_templates(folder: str | Path, function_ids: list[str] | None = None,
                    vendor_categories: list[str] | None = None) -> list[Path]:
    """`autofrontier init`: every template as CSV and XLSX, a README per file and a tier guide."""
    from .safeio import OutputDir
    out = OutputDir(folder)
    written = []
    for spec in TEMPLATES.values():
        df = template_frame(spec)
        written.append(out.write_csv(f"{spec.name}.csv", df))
        readme = _readme_text(spec, function_ids, vendor_categories)
        written.append(out.write_xlsx(f"xlsx/{spec.name}.xlsx", {"data": df,
                                                                 "readme": pd.DataFrame({"readme": readme.splitlines()})}))
        written.append(out.write_text(f"README_{spec.name}.md", readme))
    written.append(out.write_text("README.md", TIER_GUIDE))
    return written
