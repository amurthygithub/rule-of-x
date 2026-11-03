"""processes.csv and process_activities.csv: a constructed cross-industry process library (contract Section 12).

Construction rules
1. Processes follow APQC PCF 7.4 process groups (column apqc_ref) and common end-to-end names (order-to-cash etc.).
2. Each process is an ordered chain of steps; each step is one O*NET work activity. Steps are written against an
   O*NET Intermediate Work Activity (IWA, IDs from the O*NET 29.0 list redistributed in microsoft/working-with-ai,
   iwa_metrics.csv), plus a keyword pattern for the DWA title. O*NET 31.0 renumbered IWAs and DWAs; legacy IWA IDs
   are mapped to 31.0 IDs by exact title (common.iwa_legacy_map) and both are written.
3. DWA resolution (when O*NET 31.0 gwas_to_iwas_to_dwas and occ_activity are present): candidates are the DWAs in
   the step's IWA whose title matches the pattern (all DWAs in the IWA if none match); the pick is the candidate with
   the largest time mass in the owning function's occupations, sum over soc of function_occ weight x time_share
   (if none of the function's occupations performs any candidate, the candidate with the largest economy-wide
   time mass). Patterns anchored with ^ pin a specific DWA title chosen by reading the IWA's DWA list.
   If the IWA ID is absent from 31.0, the pattern is searched over all DWA titles. The rule used is recorded.
4. critical_path = 1 for steps every unit of output must pass through in sequence; 0 for conditional (exception,
   escalation), periodic (monitoring, reporting) or parallel steps.
5. Volumes are ASSUMED unless a source is named: a central value and a low-high range, with the derivation in
   volume_note. volume_basis says whether the volume scales with revenue (per $M), headcount (per employee) or is a
   fixed count per year.
6. ICFR scope (author request, 29 Oct 2026). Process scope (full, partial, none) and the in-scope steps of partial
   processes come from the engine builder's icfr_scope.csv and icfr_steps.csv, copied verbatim into this script as
   read at 10:34 on 29 Oct 2026 (sha256 asserted); their basis text is copied with "class b, PCAOB AS 2201; common
   SOX scoping" appended. The data contract is the single source: since 10:45 the engine's files mirror this output. typical_systems is a constructed PRIOR (class d): the system classes a step usually reads or
   writes. financial_system_written names the financial-reporting system a step writes (billing, ERP/GL and its
   subledgers, inventory and costing in the ERP, payroll or the HRIS pay data that feeds it). A step that writes such
   a system is in scope even where the engine lists did not flag it (icfr_source = typical_systems); its process then
   becomes partial if it was none, and the engine's value is kept in icfr_scope_engine. The author's principle: SOX
   scope covers the processes, systems, integrations and policies that affect the timeliness, accuracy and
   completeness of financial reporting. Every step of a full process is in scope. icfr_channel says why a step is in
   scope: process (a financial-reporting process or significant account), system (it writes or changes an in-scope
   system), integration (its data reaches an in-scope system through an interface), policy (an accounting policy or
   estimate, for example ASC 450 or ASC 606 judgments); several channels are separated by '; '.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import warnings
warnings.filterwarnings("ignore", message="This pattern")
import re
import numpy as np
import pandas as pd
from common import OUT, MSAI, read_onet, pick, write_csv, save_meta, onet_hierarchy, iwa_legacy_map

S = lambda name, iwa, rx, cp=1: (name, iwa, rx, cp)
# process_id: (name, function_id, output_unit, apqc_ref, volume_basis, central, low, high, note, steps)
P = {
    'P01': ('Order to cash', 'F11', 'customer invoice', '9.2 Perform revenue accounting', 'per_musd_revenue', 160, 20, 2000,
            'B2B: about 40 customers per $M at a $25k average contract, about 4 invoices a year each; transactional and B2C firms are far higher',
            [S('Verify customer and order data', '4.A.2.a.3.I01', r'^Examine documents to verify'),
             S('Prepare invoice', '4.A.3.b.6.I01', r'invoice|bill|financial'),
             S('Record receivable', '4.A.3.b.6.I10', r'record|maintain|financial|sales'),
             S('Collect payment', '4.A.4.c.3.I04', r'collect|payment|fee'),
             S('Apply cash and reconcile', '4.A.2.a.2.I04', r'reconcil'),
             S('Resolve billing disputes', '4.A.4.a.8.I03', r'customer|complain|inquir|billing', 0)]),
    'P02': ('Procure to pay', 'F10', 'supplier invoice', '4.2 Procure materials and services', 'per_musd_revenue', 100, 30, 500,
            'assumed supplier invoices per $M of revenue for a services or software firm',
            [S('Identify need and gather supplier information', '4.A.1.a.1.I07', r'supplier|vendor|goods|product|price'),
             S('Negotiate terms', '4.A.4.a.7.I02', r'negotiat|contract'),
             S('Issue purchase order', '4.A.4.c.3.I05', r'purchas|order'),
             S('Receive and inspect goods or services', '4.A.1.b.2.I06', r'^Inspect items for damage', 0),
             S('Match invoice to order and receipt', '4.A.2.a.2.I04', r'reconcil|match|verif'),
             S('Execute payment', '4.A.4.c.1.I03', r'payment|disburs|transaction'),
             S('Record payable', '4.A.3.b.6.I10', r'record|maintain|financial')]),
    'P03': ('Record to report', 'F11', 'reporting period (month)', '9.3 Perform general accounting and reporting', 'fixed_per_year', 12, 12, 12,
            'one cycle per month', [
             S('Compile ledger and subledger data', '4.A.2.a.2.I03', r'compile|financial|record|data'),
             S('Post journal entries', '4.A.3.b.6.I10', r'record|financial|account'),
             S('Reconcile accounts', '4.A.2.a.2.I04', r'reconcil'),
             S('Analyze variances', '4.A.2.a.4.I11', r'financial|analy|budget'),
             S('Prepare financial statements', '4.A.3.b.6.I01', r'financial (statement|report)|report'),
             S('Review for accuracy and compliance', '4.A.2.a.3.I03', r'examin|audit|review|financial'),
             S('Explain results to management', '4.A.4.a.1.I04', r'^Interpret financial information')]),
    'P04': ('Month-end close', 'F11', 'close cycle', '9.3 Perform general accounting and reporting', 'fixed_per_year', 12, 12, 12,
            'one close per month; overlaps P03 by design (the engine should not count both for the same firm)', [
             S('Calculate accruals and adjustments', '4.A.1.b.3.I03', r'calculat|financial|cost'),
             S('Reconcile balance sheet accounts', '4.A.2.a.2.I04', r'reconcil'),
             S('Consolidate entities', '4.A.2.a.2.I03', r'compile|consolidat|financial'),
             S('Review close checklist and controls', '4.A.2.a.3.I01', r'examin|accura|complian|document'),
             S('Prepare close package', '4.A.3.b.6.I01', r'financial|report')]),
    'P05': ('Hire to retire', 'F12', 'hire', '7.2 Recruit, source, and select employees; 7.3; 7.6', 'per_employee', 0.2, 0.1, 0.5,
            'hires per employee per year; replace with BLS JOLTS hires rate for the firm industry when available',
            [S('Plan staffing needs', '4.A.2.b.1.I08', r'^Determine resource needs'),
             S('Recruit candidates', '4.A.4.c.2.I01', r'recruit|applicant|candidate|hire'),
             S('Interview candidates', '4.A.1.a.1.I23', r'interview'),
             S('Evaluate and select candidates', '4.A.2.a.1.I04', r'evaluat|applicant|personnel|candidate'),
             S('Onboard and train', '4.A.4.b.3.I04', r'train|orient'),
             S('Administer HR records and benefits', '4.A.4.c.2.I02', r'benefit|human resource|personnel|record'),
             S('Review performance', '4.A.2.a.1.I04', r'perform|evaluat', 0),
             S('Process separation', '4.A.4.c.2.I02', r'terminat|separat|exit|human resource', 0)]),
    'P06': ('Payroll', 'F11', 'pay statement', '9.5 Process payroll', 'per_employee', 26, 12, 52,
            'pay statements per employee per year (biweekly central)',
            [S('Compile time and attendance', '4.A.2.a.2.I03', r'time|attendance|payroll|record'),
             S('Calculate pay and deductions', '4.A.1.b.3.I03', r'payroll|wage|calculat'),
             S('Execute payment', '4.A.4.c.1.I03', r'^Issue money, credit, or vouchers'),
             S('Record payroll', '4.A.3.b.6.I10', r'payroll|record|financial'),
             S('File payroll taxes', '4.A.3.b.6.I14', r'^Complete documentation required by programs or regulations')]),
    'P07': ('Ticket to resolution', 'F05', 'support ticket', '6.2 Plan and manage customer service contacts', 'per_musd_revenue', 500, 50, 5000,
            'assumed tickets per $M of revenue for B2B software; consumer services are far higher',
            [S('Receive and triage inquiry', '4.A.4.a.8.I03', r'customer|inquir|complain|respond'),
             S('Gather customer information', '4.A.1.a.1.I04', r'^Gather information in order to provide services to clients'),
             S('Diagnose problem', '4.A.2.b.1.I02', r'diagnos|troubleshoot|problem'),
             S('Explain solution', '4.A.4.a.1.I01', r'explain|product|technical|service'),
             S('Escalate and coordinate fix', '4.A.4.a.2.I04', r'coordinat|resolve|problem', 0),
             S('Record resolution', '4.A.3.b.6.I08', r'record|maintain|document')]),
    'P08': ('Lead to close', 'F04', 'qualified opportunity', '3.5 Develop and manage sales plans', 'per_musd_revenue', 50, 10, 500,
            'assumed qualified opportunities per $M of revenue (about 10 wins per $M at a 20% win rate)',
            [S('Prospect and build relationships', '4.A.4.a.4.I01', r'relationship|contact|network|prospect'),
             S('Qualify needs', '4.A.4.a.2.I13', r'needs|client|customer|requirement'),
             S('Present and demonstrate', '4.A.4.a.1.I01', r'explain|demonstrat|product|feature'),
             S('Price the offer', '4.A.2.b.1.I01', r'price|pric|cost|value'),
             S('Negotiate', '4.A.4.a.7.I02', r'negotiat'),
             S('Close sale', '4.A.4.a.6.I02', r'sell|sale'),
             S('Record in CRM', '4.A.3.b.6.I10', r'sales|record|maintain')]),
    'P09': ('Quote to contract', 'F04', 'executed contract', '3.5 Develop and manage sales plans; 12.0', 'per_musd_revenue', 15, 5, 200,
            'assumed contracts executed per $M of revenue',
            [S('Capture requirements', '4.A.4.a.2.I13', r'needs|client|specification|order'),
             S('Prepare quote', '4.A.2.b.1.I01', r'price|pric|cost|estimat'),
             S('Draft contract', '4.A.3.b.6.I13', r'contract|agreement|document'),
             S('Review terms for compliance', '4.A.2.a.3.I01', r'^Review documents or materials for compliance'),
             S('Negotiate terms', '4.A.4.a.7.I02', r'negotiat|contract'),
             S('Approve and sign', '4.A.2.b.1.I03', r'authoriz|approv')]),
    'P10': ('Idea to release', 'F02', 'feature release', '2.2 Generate and define new product/service ideas; 2.3', 'per_musd_revenue', 2, 0.5, 20,
            'assumed feature releases per $M of revenue; better scaled by engineering headcount when Tier 2 data exist',
            [S('Gather requirements', '4.A.4.a.2.I09', r'specification|requirement|project|detail'),
             S('Design solution', '4.A.2.b.2.I02', r'design|software|system|application'),
             S('Write code', '4.A.3.b.1.I01', r'program|code|software|computer'),
             S('Test', '4.A.1.b.2.I08', r'test|software|system'),
             S('Document', '4.A.3.b.6.I09', r'document|technical|specification'),
             S('Deploy', '4.A.3.b.1.I03', r'install|deploy|set up|configur|computer'),
             S('Monitor in production', '4.A.1.a.2.I10', r'monitor|computer|system|performance', 0)]),
    'P11': ('Incident to resolution', 'F16', 'production incident', '8.7 Create and manage support services/solutions', 'per_musd_revenue', 5, 1, 50,
            'assumed production incidents per $M of revenue',
            [S('Detect through monitoring', '4.A.1.a.2.I10', r'monitor|computer|network|system'),
             S('Notify responders', '4.A.4.a.2.I08', r'^Notify others of emergencies, problems, or hazards'),
             S('Diagnose', '4.A.2.b.1.I02', r'diagnos|troubleshoot|problem|malfunction'),
             S('Restore service', '4.A.3.b.1.I04', r'resolve|repair|computer|problem'),
             S('Write post-incident report', '4.A.3.b.6.I15', r'report|incident|operation', 0)]),
    'P12': ('Campaign to lead', 'F03', 'marketing campaign', '3.3 Develop and manage marketing plans', 'per_musd_revenue', 1, 0.2, 5,
            'assumed campaigns per $M of revenue',
            [S('Analyze market', '4.A.2.a.4.I02', r'market|industry|competit|trend'),
             S('Plan campaign', '4.A.2.b.2.I03', r'marketing|plan|strateg|campaign'),
             S('Create content', '4.A.2.b.2.I12', r'marketing|promotion|advertis|material'),
             S('Run promotion', '4.A.4.a.6.I03', r'promot|advertis|market'),
             S('Measure response', '4.A.1.a.1.I14', r'consumer|customer|survey|market|data', 0)]),
    'P13': ('Onboard to renew', 'F06', 'customer renewal', '6.1; 3.5', 'per_musd_revenue', 40, 5, 1000,
            'one renewal per customer per year; about 40 customers per $M at a $25k contract',
            [S('Train customer users', '4.A.4.b.3.I05', r'train|use|equipment|product'),
             S('Advise on adoption', '4.A.4.b.6.I02', r'advise|product|service|customer'),
             S('Resolve account issues', '4.A.4.a.8.I03', r'customer|complain|inquir|resolve', 0),
             S('Renew and expand', '4.A.4.a.6.I02', r'^Sell products or services')]),
    'P14': ('Implementation project', 'F07', 'customer implementation', '5.3 Deliver service to customer', 'per_musd_revenue', 4, 0.5, 40,
            'assumed implementations per $M of revenue',
            [S('Confer with client on scope', '4.A.4.a.2.I13', r'client|needs|customer|requirement'),
             S('Plan project', '4.A.2.b.6.I02', r'plan|schedul|project|work'),
             S('Configure systems', '4.A.3.b.1.I03', r'install|configur|set up|computer|system'),
             S('Train client staff', '4.A.4.b.3.I05', r'train|instruct'),
             S('Document solution', '4.A.3.b.6.I09', r'document|technical|procedure'),
             S('Coordinate with client and partners', '4.A.4.a.2.I11', r'^Coordinate operational activities with external stakeholders', 0)]),
    'P15': ('Contract review and legal advice', 'F13', 'legal matter', '12.0 Manage External Relationships (level 1)', 'per_musd_revenue', 20, 5, 200,
            'assumed legal matters (mostly commercial contracts) per $M of revenue',
            [S('Research law and precedent', '4.A.2.a.4.I08', r'law|legal|precedent|regulat'),
             S('Review documents', '4.A.2.a.3.I01', r'examin|legal|document|complian'),
             S('Prepare legal documents', '4.A.3.b.6.I14', r'legal|contract|document'),
             S('Advise client', '4.A.4.b.6.I08', r'advise|legal|regulat'),
             S('Negotiate', '4.A.4.a.7.I02', r'negotiat|settle|agreement', 0)]),
    'P16': ('Control test to remediation', 'F14', 'control test', '11.0 Manage Enterprise Risk, Compliance, Remediation, and Resiliency (level 1)', 'fixed_per_year', 200, 50, 1000,
            'assumed key controls tested per year by an SEC filer',
            [S('Plan test', '4.A.2.b.6.I02', r'^Plan work procedures'),
             S('Examine evidence', '4.A.2.a.3.I03', r'examin|audit|financial|record'),
             S('Evaluate compliance', '4.A.1.a.2.I11', r'^Monitor organizational compliance with regulations'),
             S('Document findings', '4.A.3.b.6.I15', r'report|document|finding|audit'),
             S('Coordinate remediation', '4.A.4.b.4.I14', r'complian|regulat|coordinat', 0)]),
    'P17': ('IT service request', 'F15', 'service request', '8.7 Create and manage support services/solutions', 'per_employee', 6, 2, 20,
            'assumed IT requests per employee per year',
            [S('Receive request', '4.A.3.b.1.I04', r'resolve|computer|problem|user|request'),
             S('Provision access or system', '4.A.3.b.1.I03', r'install|set up|configur|account|computer|network'),
             S('Apply security controls', '4.A.3.b.1.I02', r'security|access|protect'),
             S('Record ticket', '4.A.3.b.6.I08', r'record|maintain|log|document'),
             S('Instruct user', '4.A.4.b.3.I05', r'train|instruct|use', 0)]),
    'P18': ('Plan to budget', 'F11', 'budget or forecast cycle', '9.1 Perform planning and management accounting', 'fixed_per_year', 5, 4, 13,
            'one annual budget plus quarterly forecasts (monthly in some firms)',
            [S('Gather operating data', '4.A.1.a.1.I06', r'data|operat|information|gather'),
             S('Analyze financial data', '4.A.2.a.4.I11', r'financial|analy|business'),
             S('Develop financial plan', '4.A.2.b.2.I09', r'financial|business|plan|budget'),
             S('Prepare budget', '4.A.3.b.6.I01', r'budget|financial'),
             S('Manage budget', '4.A.4.b.4.I09', r'budget|financ|manage'),
             S('Explain to management', '4.A.4.a.1.I04', r'^Interpret financial information', 0)]),
    'P19': ('Expense to reimburse', 'F11', 'expense report', '9.0 (level 1)', 'per_employee', 6, 0, 24,
            'assumed expense reports per employee per year',
            [S('Check receipts and policy', '4.A.2.a.3.I01', r'examin|verif|complian|document|accura'),
             S('Reconcile to card feed', '4.A.2.a.2.I04', r'reconcil'),
             S('Reimburse', '4.A.4.c.1.I03', r'^Issue money, credit, or vouchers'),
             S('Record expense', '4.A.3.b.6.I10', r'record|financial')]),
    'P20': ('Order fulfilment', 'F09', 'customer order shipped', '4.4 Manage logistics and warehousing', 'per_musd_revenue', 1000, 50, 20000,
            'assumed orders per $M of revenue for a distributor of physical goods',
            [S('Schedule order', '4.A.2.b.5.I02', r'schedul|order|shipment'),
             S('Check inventory', '4.A.4.c.3.I07', r'inventor|stock|monitor'),
             S('Pick and move goods', '4.A.3.a.1.I10', r'move|transport|material|load'),
             S('Pack', '4.A.3.a.2.I42', r'pack|wrap'),
             S('Ship and document', '4.A.4.c.1.I05', r'^Prepare outgoing shipments'),
             S('Replenish stock', '4.A.4.c.3.I01', r'replenish|order|inventor|stock', 0)]),
    'P21': ('Plan to produce', 'F09', 'production order', '4.3 Produce/Assemble/Test product', 'per_musd_revenue', 100, 10, 1000,
            'assumed production orders per $M of revenue for a discrete manufacturer',
            [S('Schedule production', '4.A.2.b.5.I02', r'schedul|production|operation'),
             S('Set up equipment', '4.A.3.a.2.I46', r'set up|setup|adjust|equipment'),
             S('Operate production equipment', '4.A.3.a.3.I06', r'^Operate industrial equipment'),
             S('Inspect output', '4.A.1.b.2.I06', r'inspect|quality|product'),
             S('Maintain equipment', '4.A.3.b.4.I01', r'^Perform basic equipment maintenance', 0),
             S('Record production', '4.A.3.b.6.I08', r'record|production|operation')]),
    'P22': ('Facilities work order', 'F17', 'work order', '10.0 (level 1)', 'per_employee', 1, 0.2, 5,
            'assumed facilities work orders per employee per year',
            [S('Receive request', '4.A.4.a.8.I03', r'customer|request|inquir|respond'),
             S('Inspect site', '4.A.1.b.2.I05', r'inspect|facilit|equipment|building'),
             S('Schedule work', '4.A.2.b.5.I01', r'^Arrange facility schedules'),
             S('Repair or maintain', '4.A.3.b.4.I01', r'maintain|repair|facilit|building'),
             S('Record completion', '4.A.3.b.6.I08', r'record|maintain|log')]),
    'P23': ('Strategy to plan', 'F01', 'strategic plan', '1.2 Develop business strategy', 'fixed_per_year', 1, 1, 2,
            'one strategic planning cycle per year',
            [S('Analyze market and competitors', '4.A.2.a.4.I02', r'market|industry|competit|trend'),
             S('Set goals', '4.A.2.b.2.I27', r'goal|objective|organization'),
             S('Develop business plan', '4.A.2.b.2.I09', r'^Develop financial or business plans'),
             S('Communicate strategy', '4.A.4.a.2.I06', r'strateg|business|communicat'),
             S('Direct execution', '4.A.4.b.4.I12', r'direct|organization|operation')]),
    'P24': ('Tax compliance', 'F11', 'tax filing', '9.0 (level 1)', 'fixed_per_year', 20, 5, 200,
            'assumed filings per year (federal, state and indirect)',
            [S('Compile tax data', '4.A.2.a.2.I03', r'compile|tax|financial|record'),
             S('Calculate liability', '4.A.1.b.3.I03', r'tax|calculat'),
             S('Prepare return', '4.A.3.b.6.I14', r'^Complete documentation required by programs or regulations'),
             S('Review', '4.A.2.a.3.I03', r'examin|tax|financial|review'),
             S('Pay and file', '4.A.4.c.1.I03', r'payment|transaction|tax')]),
}


# ---------------------------------------------------------------- systems touched by each step (PRIOR, class d)
# per process, one tuple per step: (typical_systems, financial_system_written, condition). Constructed by the data
# agent from the step and its owning function; no dataset. financial_system_written is '' when the step writes no
# financial-reporting system.
SYSTEMS = {
    'P01': [('CRM; billing (customer master); ERP/GL (customer master)', '', ''),
            ('billing; ERP/GL (AR)', 'billing (invoice)', ''),
            ('ERP/GL (AR subledger)', 'ERP/GL (AR subledger)', ''),
            ('billing; payment gateway; bank portal', 'billing (payment status)', ''),
            ('ERP/GL (AR, cash); bank feed', 'ERP/GL (cash application)', ''),
            ('ticketing; CRM; billing (credits and adjustments)', 'billing (credit memos, adjustments)', '')],
    'P02': [('procurement (P2P); ERP (vendor master)', 'ERP (vendor master)', ''),
            ('contract management (CLM); procurement (P2P)', '', ''),
            ('procurement (P2P); ERP (purchase order)', 'ERP (purchase order)', ''),
            ('procurement (P2P); ERP (goods receipt)', 'ERP (goods receipt)', ''),
            ('ERP/GL (AP subledger); procurement (P2P)', 'ERP/GL (AP subledger)', ''),
            ('ERP/GL (AP); bank or payment platform', 'ERP/GL (AP, cash)', ''),
            ('ERP/GL (AP subledger)', 'ERP/GL (AP subledger)', '')],
    'P03': [('ERP/GL; subledgers (AR, AP, payroll, fixed assets)', '', ''),
            ('ERP/GL', 'ERP/GL (journal entries)', ''),
            ('ERP/GL; reconciliation tool; bank feed', 'reconciliation tool (sign-off)', ''),
            ('ERP/GL; BI/reporting', '', ''),
            ('ERP/GL; consolidation and reporting', 'consolidation and reporting', ''),
            ('ERP/GL; close management', '', ''),
            ('BI/reporting', '', '')],
    'P04': [('ERP/GL', 'ERP/GL (accrual entries)', ''),
            ('ERP/GL; reconciliation tool', 'reconciliation tool (sign-off)', ''),
            ('consolidation; ERP/GL', 'consolidation (eliminations)', ''),
            ('close management; ERP/GL', '', ''),
            ('consolidation and reporting', 'consolidation and reporting', '')],
    'P05': [('HRIS; planning (FP&A)', '', ''),
            ('ATS', '', ''),
            ('ATS', '', ''),
            ('ATS', '', ''),
            ('HRIS (new-hire record, pay rate); LMS; IAM (accounts)', 'HRIS (new-hire pay data feeding payroll)',
             'new-hire record and pay rate set up in the HRIS feed payroll'),
            ('HRIS; payroll (compensation and job changes); benefits administration', 'HRIS and payroll (compensation changes)', ''),
            ('HRIS (performance module)', '', ''),
            ('HRIS; payroll (final pay); IAM (access removal)', 'HRIS and payroll (termination)', '')],
    'P06': [('time and attendance; HRIS', 'time and attendance (hours feeding pay)', ''),
            ('payroll', 'payroll', ''),
            ('payroll; bank', 'payroll (disbursement)', ''),
            ('payroll; ERP/GL', 'ERP/GL (payroll journal)', ''),
            ('payroll (tax filing); tax agency portals', 'payroll (tax liabilities)', '')],
    'P07': [('ticketing', '', ''),
            ('ticketing; CRM; billing (read: account and invoice history)', '', ''),
            ('ticketing; knowledge base; product telemetry', '', ''),
            ('ticketing; knowledge base', '', ''),
            ('ticketing; billing (refunds/credits)', 'billing (refunds/credits)',
             'ticket resolved with a refund, credit or billing adjustment'),
            ('ticketing; CRM', '', '')],
    'P08': [('CRM', '', ''),
            ('CRM', '', ''),
            ('CRM; demo environment', '', ''),
            ('CPQ; CRM (price book)', '', ''),
            ('CRM; CPQ', '', ''),
            ('CRM; CPQ; e-signature; billing (order or subscription created through the CRM-to-billing integration)',
             'billing (order booking via integration)', 'closed-won orders create billing records through a CRM-to-billing integration'),
            ('CRM', '', '')],
    'P09': [('CRM', '', ''),
            ('CPQ; CRM (price book)', '', ''),
            ('contract management (CLM); document management', '', ''),
            ('contract management (CLM)', '', ''),
            ('contract management (CLM); e-signature', '', ''),
            ('contract management (CLM); e-signature; CPQ; billing (order booking)', 'billing (order booking)', '')],
    'P10': [('issue tracker', '', ''),
            ('issue tracker; documentation', '', ''),
            ('source control', '', ''),
            ('CI/CD; test management', '', ''),
            ('documentation', '', ''),
            ('CI/CD; production systems (including in-scope financial systems)', '', ''),
            ('monitoring and observability', '', '')],
    'P11': [('monitoring and observability', '', ''),
            ('incident management; paging', '', ''),
            ('monitoring and observability; logs', '', ''),
            ('production systems (including in-scope financial systems); change management', 'in-scope financial systems (data or configuration fixes)',
             'when the fix changes data or configuration in an in-scope system'),
            ('incident management; documentation', '', '')],
    'P12': [('BI/web analytics', '', ''),
            ('marketing automation', '', ''),
            ('content management; digital asset management', '', ''),
            ('marketing automation; ad platforms', '', ''),
            ('marketing automation; BI/web analytics', '', '')],
    'P13': [('LMS; product', '', ''),
            ('CRM; customer success platform', '', ''),
            ('CRM; customer success platform; billing (service credits/adjustments)', 'billing (service credits/adjustments)',
             'account issue resolved with a service credit or billing adjustment'),
            ('CRM; CPQ; billing (renewal or subscription change)', 'billing (renewal or subscription change)',
             'renewal or expansion amends the billing subscription')],
    'P14': [('CRM; PSA (project system)', '', ''),
            ('PSA (project budget and estimate at completion)', 'PSA (estimate at completion feeding revenue)', ''),
            ('customer environment; PSA (time and progress entry)', 'PSA (time and progress feeding revenue and billing)',
             'when time or progress entries feed percent-complete revenue or billing'),
            ('LMS', '', ''),
            ('documentation', '', ''),
            ('PSA; email and collaboration', '', '')],
    'P15': [('legal research database', '', ''),
            ('document management', '', ''),
            ('document management; contract management (CLM)', '', ''),
            ('matter management', '', ''),
            ('contract management (CLM); matter management; ERP/GL (contingency accrual, through finance)',
             'ERP/GL (loss-contingency accrual) and disclosures',
             'when a settlement or claim feeds a loss-contingency accrual or disclosure (ASC 450)')],
    'P16': [('GRC', '', ''),
            ('GRC; ERP/GL and other in-scope systems (read: evidence)', '', ''),
            ('GRC', 'GRC (control conclusions)', ''),
            ('GRC', 'GRC (deficiencies)', ''),
            ('GRC', '', '')],
    'P17': [('ITSM', '', ''),
            ('ITSM; IAM; target systems (including ERP/GL, billing, payroll)', 'IAM (access to financial systems)', ''),
            ('IAM; security tooling', 'IAM (access to financial systems)', ''),
            ('ITSM', '', ''),
            ('ITSM; knowledge base', '', '')],
    'P18': [('ERP/GL (read); BI/reporting', '', ''),
            ('planning (FP&A); BI/reporting', '', ''),
            ('planning (FP&A)', '', ''),
            ('planning (FP&A); ERP/GL (budget load)', '', ''),
            ('planning (FP&A); procurement (P2P) budget checks', '', ''),
            ('BI/reporting', '', '')],
    'P19': [('T&E (expense)', '', ''),
            ('T&E (expense); corporate card feed', '', ''),
            ('T&E (expense); payroll or bank', 'payroll or bank (reimbursement)', ''),
            ('ERP/GL', 'ERP/GL (expense entries)', '')],
    'P20': [('ERP (sales order); WMS', '', ''),
            ('WMS; ERP (inventory)', 'ERP (inventory)', ''),
            ('WMS', '', ''),
            ('WMS', '', ''),
            ('WMS; ERP (goods issue); billing (invoice trigger)', 'ERP (inventory relief) and billing (invoice trigger)', ''),
            ('ERP (purchase order, inventory receipt); WMS', 'ERP (inventory)', '')],
    'P21': [('MRP/ERP (production order)', '', ''),
            ('MES', '', ''),
            ('MES', '', ''),
            ('QMS; MES; ERP (scrap and yield)', 'ERP (inventory: scrap and yield)', 'scrap and yield recorded in the ERP'),
            ('EAM/CMMS', '', ''),
            ('MES; ERP (inventory, costing)', 'ERP (inventory and costing)', '')],
    'P22': [('CMMS (work orders)', '', ''),
            ('CMMS', '', ''),
            ('CMMS', '', ''),
            ('CMMS; procurement (P2P) for parts and contractors', '', ''),
            ('CMMS', '', '')],
    'P23': [('BI/reporting', '', ''),
            ('planning (FP&A)', '', ''),
            ('planning (FP&A)', '', ''),
            ('collaboration', '', ''),
            ('planning (FP&A); BI/reporting', '', '')],
    'P24': [('ERP/GL; tax provision software', '', ''),
            ('tax provision software; tax engine', 'tax provision software', ''),
            ('tax compliance software', '', ''),
            ('tax provision software', '', ''),
            ('ERP/GL (tax payments); bank', 'ERP/GL (tax entries)', '')],
}

# channel through which an in-scope step affects financial reporting (author's principle: processes, systems,
# integrations and policies); full-scope processes are 'process'. Per-step basis text where the generic wording
# does not fit.
CHANNEL = {
    ('P05', 5): 'system; integration', ('P05', 6): 'system; integration', ('P05', 8): 'system; integration',
    ('P07', 5): 'system', ('P08', 6): 'integration', ('P09', 4): 'policy', ('P09', 6): 'process',
    ('P10', 4): 'system', ('P10', 6): 'system', ('P11', 4): 'system', ('P13', 3): 'system', ('P13', 4): 'system',
    ('P14', 2): 'policy', ('P14', 3): 'system; integration', ('P15', 5): 'policy', ('P17', 2): 'system',
    ('P17', 3): 'system', ('P20', 2): 'process', ('P20', 5): 'process', ('P20', 6): 'process', ('P21', 4): 'system',
    ('P21', 6): 'process'}
BASIS = {
    ('P05', 5): 'new-hire pay data in the HRIS feeds payroll expense through the HRIS-to-payroll integration',
    ('P08', 6): 'closed-won orders create billing records through the CRM-to-billing integration',
    ('P11', 4): 'a fix that changes data or configuration in an in-scope financial system falls under data and change management (ITGC)',
    ('P14', 3): 'time and progress entries are the progress input of percent-complete revenue (ASC 606 input method) and of time-based billing; closes the progress-input gap in the engine list for P14',
    ('P15', 5): 'a settlement or claim feeds a loss-contingency accrual or disclosure (ASC 450): policy and estimate channel'}
for pid, v in P.items():
    assert len(SYSTEMS[pid]) == len(v[9]), f'{pid}: {len(SYSTEMS[pid])} system tuples for {len(v[9])} steps'

iw = pd.read_csv(f'{MSAI}/iwa_metrics.csv').set_index('IWA').title
bad = [(p, s[0], s[1]) for p, v in P.items() for s in v[9] if s[1] not in iw.index]
assert not bad, bad

proc = pd.DataFrame([(pid, v[0], v[1], v[2], v[3], v[4],
                      v[5] if v[4] == 'per_musd_revenue' else np.nan, v[6] if v[4] == 'per_musd_revenue' else np.nan,
                      v[7] if v[4] == 'per_musd_revenue' else np.nan,
                      v[5] if v[4] != 'per_musd_revenue' else np.nan, v[6] if v[4] != 'per_musd_revenue' else np.nan,
                      v[7] if v[4] != 'per_musd_revenue' else np.nan, 'assumed', True, v[8]) for pid, v in P.items()],
                    columns=['process_id', 'process_name', 'function_id', 'output_unit', 'apqc_ref', 'volume_basis',
                             'typical_volume_per_musd_revenue', 'volume_low', 'volume_high', 'volume_other',
                             'volume_other_low', 'volume_other_high', 'volume_source', 'volume_assumed', 'volume_note'])

# ---------------------------------------------------------------- DWA resolution
h = onet_hierarchy()
oa_path = f'{OUT}/occ_activity.csv'
fo = pd.read_csv(f'{OUT}/function_occ.csv', dtype={'soc': str})
if h is not None:
    oa = pd.read_csv(oa_path, dtype={'soc': str}) if os.path.exists(oa_path) else None
    act_path = f'{OUT}/activities.csv'
    USMASS = pd.read_csv(act_path).set_index('dwa_id').emp_time_share_us.fillna(0) if os.path.exists(act_path) else None
    IWMAP = iwa_legacy_map()          # step IWAs are written with legacy (O*NET 29.0) IDs; 31.0 renumbered them
rows = []
for pid, v in P.items():
    f = v[1]
    for k, (name, iwa, rx, cp) in enumerate(v[9], start=1):
        dwa, title, rule, iwa31 = '', '', 'pending O*NET 31.0 download', ''
        if h is not None:
            iwa31 = IWMAP.get(iwa, '')
            cand = h[h.iwa_id == iwa31]
            rule = 'iwa'
            if cand.empty:
                cand, rule = h, 'all_dwas_by_pattern'
            m = cand[cand.dwa_title.str.contains(rx, case=False, regex=True)]
            if not m.empty:
                cand, rule = m, rule + '+pattern'
            if oa is not None and len(cand) > 1:
                w = fo[fo.function_id == f].set_index('soc').weight
                sub = oa[oa.dwa_id.isin(cand.dwa_id) & oa.soc.isin(w.index)]
                mass = (sub.time_share * sub.soc.map(w)).groupby(sub.dwa_id).sum()
                if len(mass):
                    best = mass.idxmax()
                    cand = cand[cand.dwa_id == best]
                    rule += '+function_mass'
                elif USMASS is not None:                     # no function occupation performs any candidate
                    best = USMASS.reindex(cand.dwa_id).idxmax()
                    cand = cand[cand.dwa_id == best]
                    rule += '+us_time_mass'
            dwa, title = cand.iloc[0].dwa_id, cand.iloc[0].dwa_title
        rows.append(dict(process_id=pid, step=k, dwa_id=dwa, critical_path=cp, step_name=name, iwa_id=iwa31, iwa_id_legacy=iwa,
                         iwa_title_onet29=iw[iwa], dwa_title=title, dwa_pattern=rx, resolution=rule))
pa = pd.DataFrame(rows)

# ---------------------------------------------------------------- ICFR scope (rule 6)
import hashlib
import io
# The engine builder's lists, copied verbatim from engine/src/autofrontier/priors/icfr_scope.csv and icfr_steps.csv as
# read on 29 Oct 2026 at 10:34 (sha256 asserted below). Since 10:45 the engine files mirror this script's output, so the
# data contract is the single source and the engine files are not read here.
ICFR_SCOPE_ENGINE_ORIG = '''process_id,process_name,icfr_scope,basis
P01,Order to cash,full,"revenue and receivables are significant accounts (PCAOB AS 2201 para. 28-33: significant accounts and relevant assertions); common SOX process scoping"
P02,Procure to pay,full,"purchases, payables and cash disbursements are significant accounts; PO approval and vendor master changes are key controls (AS 2201; common SOX scoping)"
P03,Record to report,full,"journal entries, reconciliations and the financial reporting process (AS 2201 para. 34-38, period-end financial reporting)"
P04,Month-end close,full,"period-end financial reporting process (AS 2201 para. 34)"
P05,Hire to retire,partial,"only compensation, job and termination changes that feed payroll and HR master data; not recruiting, sourcing or selection"
P06,Payroll,full,"payroll expense and accruals are significant accounts (AS 2201)"
P07,Ticket to resolution,none,"customer support: no significant account or relevant assertion"
P08,Lead to close,none,"sales pipeline before contract: no significant account"
P09,Quote to contract,partial,"only contract approval and non-standard terms that affect revenue recognition (ASC 606)"
P10,Idea to release,partial,"only change management for in-scope financial systems (ITGC, AS 2201 para. B29-B34)"
P11,Incident to resolution,none,"IT operations incidents: no significant account"
P12,Campaign to lead,none,"marketing: no significant account"
P13,Onboard to renew,none,"customer success: no significant account"
P14,Implementation project,partial,"only revenue recognized over time: percent-of-completion inputs (ASC 606-10-55-16 to 55-21)"
P15,Contract review and legal advice,none,"legal advice: no significant account"
P16,Control test to remediation,full,"the ICFR monitoring component (COSO 2013 monitoring activities; AS 2201)"
P17,IT service request,partial,"only access provisioning and removal for financial systems (ITGC, AS 2201 para. B29-B34)"
P18,Plan to budget,none,"budgeting and forecasting: no recorded transactions"
P19,Expense to reimburse,full,"employee expenses and their accruals (significant accounts at most firms)"
P20,Order fulfilment,partial,"only inventory, costing and cut-off steps, where the firm holds inventory"
P21,Plan to produce,partial,"only inventory and costing steps, where the firm holds inventory"
P22,Facilities work order,none,"facilities maintenance: no significant account"
P23,Strategy to plan,none,"strategy: no recorded transactions"
P24,Tax compliance,full,"the income tax provision is a significant account (ASC 740; AS 2201)"
'''
ICFR_STEPS_ENGINE_ORIG = '''process_id,step,dwa_id,step_name,icfr_step,condition,basis
P05,6,4.A.4.c.2.b.2,Administer HR records and benefits,true,,"compensation and job changes feed payroll and HR master data"
P05,8,4.A.4.c.2.b.1,Process separation,true,,"termination changes feed payroll (final pay, access removal)"
P09,4,4.A.2.a.3.a.4,Review terms for compliance,true,,"review of non-standard terms that affect revenue recognition (ASC 606 contract terms)"
P09,6,4.A.2.b.1.c.4,Approve and sign,true,,"contract approval"
P10,4,4.A.1.b.2.h.3,Test,true,,"change-management testing for in-scope financial systems (ITGC)"
P10,6,4.A.3.b.1.c.1,Deploy,true,,"authorized promotion of changes to production for in-scope financial systems (ITGC)"
P14,2,4.A.2.b.6.b.8,Plan project,true,,"total estimated cost, the denominator of percent-of-completion (ASC 606 input method); no step of the library records progress"
P17,2,4.A.3.b.1.c.2,Provision access or system,true,,"access provisioning and removal for financial systems (ITGC user access)"
P17,3,4.A.3.b.1.b.1,Apply security controls,true,,"logical access and security configuration of financial systems (ITGC)"
P20,2,4.A.4.c.3.g.4,Check inventory,true,inventory,"inventory existence and counts"
P20,5,4.A.4.c.1.e.5,Ship and document,true,inventory,"shipping cut-off for revenue and inventory relief"
P20,6,4.A.4.c.3.a.3,Replenish stock,true,inventory,"inventory receipts and valuation"
P21,6,4.A.3.b.6.h.3,Record production,true,inventory,"production reporting feeds inventory costing"
'''
icfr_files = {'icfr_scope.csv (engine, 10:34)': hashlib.sha256(ICFR_SCOPE_ENGINE_ORIG.encode()).hexdigest(),
              'icfr_steps.csv (engine, 10:34)': hashlib.sha256(ICFR_STEPS_ENGINE_ORIG.encode()).hexdigest()}
assert list(icfr_files.values()) == ['c447a55bad242a196c4066fab39131f55ba47e27e2b7cbf43f03111cd76f83ad',
                                     'fc4a76ede3855bc64d31b1681a6160fcf25dae22146694087efcb650f5500e30'], icfr_files
TAG = 'class b, PCAOB AS 2201; common SOX scoping'
sc = pd.read_csv(io.StringIO(ICFR_SCOPE_ENGINE_ORIG), dtype=str, keep_default_na=False)
stp = pd.read_csv(io.StringIO(ICFR_STEPS_ENGINE_ORIG), dtype={'step': int, 'icfr_step': str}, keep_default_na=False)
assert set(sc.process_id) == set(proc.process_id) and sc.icfr_scope.isin(['full', 'partial', 'none']).all()
assert (sc.set_index('process_id').process_name == proc.set_index('process_id').process_name).all(), 'process names differ'
key = pa.set_index(['process_id', 'step'])
for r in stp.itertuples():                             # the engine's steps must be the library's steps
    assert (r.process_id, r.step) in key.index, (r.process_id, r.step)
    assert key.loc[(r.process_id, r.step), 'step_name'] == r.step_name, (r.process_id, r.step, r.step_name)
    assert key.loc[(r.process_id, r.step), 'dwa_id'] == r.dwa_id, (r.process_id, r.step, r.dwa_id)
    assert r.icfr_step.lower() == 'true'
scope = dict(zip(sc.process_id, sc.icfr_scope))
pbasis = dict(zip(sc.process_id, sc.basis))
eng = {(r.process_id, r.step): r for r in stp.itertuples()}
sysrows = [(pid, k + 1) + t for pid, v in SYSTEMS.items() for k, t in enumerate(v)]
sy = pd.DataFrame(sysrows, columns=['process_id', 'step', 'typical_systems', 'financial_system_written', 'sys_condition'])
pa = pa.merge(sy, on=['process_id', 'step'], how='left')
flag, cond, basis, src = [], [], [], []
for r in pa.itertuples():
    e = eng.get((r.process_id, r.step))
    if scope[r.process_id] == 'full':
        flag.append(True); cond.append(''); src.append('icfr_scope.csv (full process)')
        basis.append(f'{pbasis[r.process_id]}; {TAG}')
    elif e is not None:
        flag.append(True); cond.append(e.condition); src.append('icfr_steps.csv')
        basis.append(f'{e.basis}; {TAG}')
    elif r.financial_system_written:
        flag.append(True); cond.append(r.sys_condition); src.append('typical_systems')
        basis.append(BASIS.get((r.process_id, r.step), f'writes {r.financial_system_written}, which feeds financial reporting '
                     f'(accuracy and completeness of revenue, receivables, payroll or inventory)') + f'; {TAG}')
    else:
        flag.append(False); cond.append(''); src.append(''); basis.append('')
pa['icfr_step'], pa['icfr_condition'], pa['icfr_basis'], pa['icfr_source'] = flag, cond, basis, src
pa['icfr_channel'] = [('process' if scope[r.process_id] == 'full' else CHANNEL[(r.process_id, r.step)]) if r.icfr_step else ''
                      for r in pa.itertuples()]
assert set(CHANNEL) == {(r.process_id, r.step) for r in pa.itertuples() if r.icfr_step and scope[r.process_id] != 'full'}, \
    'CHANNEL must cover exactly the in-scope steps of non-full processes'
pa['typical_systems_basis'] = 'prior: constructed by the data agent from the step and owning function (class d; no dataset)'
pa = pa.drop(columns=['sys_condition'])
newly = pa[pa.icfr_source == 'typical_systems']
proc['icfr_scope_engine'] = proc.process_id.map(scope)
proc['icfr_scope'] = proc.icfr_scope_engine
raised = sorted(set(newly.process_id) & set(proc.loc[proc.icfr_scope == 'none', 'process_id']))
proc.loc[proc.process_id.isin(raised), 'icfr_scope'] = 'partial'
proc['icfr_basis'] = [f'{pbasis[p_]}; {TAG}' + (
    '; raised from none to partial because step(s) ' + ', '.join(str(x) for x in newly[newly.process_id == p_].step)
    + ' write ' + '; '.join(newly[newly.process_id == p_].financial_system_written) if p_ in raised else '')
    for p_ in proc.process_id]
write_csv(proc, 'processes.csv')
write_csv(pa, 'process_activities.csv')
save_meta('processes', dict(n_processes=len(proc), n_steps=len(pa), resolved=int((pa.dwa_id != '').sum()),
                            resolution_counts=pa.resolution.value_counts().to_dict(), icfr_files_sha256=icfr_files,
                            icfr_scope_counts=proc.icfr_scope.value_counts().to_dict(), icfr_steps_in_scope=int(pa.icfr_step.sum()),
                            icfr_flagged_by_typical_systems=newly[['process_id', 'step', 'step_name', 'financial_system_written']].values.tolist(),
                            icfr_scope_raised=raised,
                            icfr_channel_counts=pa.loc[pa.icfr_step, 'icfr_channel'].value_counts().to_dict()))
