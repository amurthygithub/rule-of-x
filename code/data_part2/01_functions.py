"""functions.csv: the standard enterprise function taxonomy (spec Section 2, contract Section 12).

Constructed table. APQC mapping uses the APQC Process Classification Framework (PCF) Cross-Industry v7.4 (August
2024): level-1 categories 1.0 to 13.0 and the level-2 groups of categories 1.0 to 9.0 with their element IDs were read
from the v7.4 PDF (copy hosted at solutions.ifrc.org, see notes/data_sources_part2.md). Level-2 groups for categories
10.0 to 13.0 were not in the readable copy, so those mappings are given at level 1 only (apqc_level = 1).

cost_bucket is the income-statement line where the function's cost usually sits for a U.S. GAAP filer
(cogs = cost of revenue, rnd = research and development, sm = sales and marketing, ga = general and administrative).
Where practice varies (customer success, professional services) the alternative is given in cost_bucket_alt.
"""
import sys
sys.path.insert(0, '/home/claude/paper/code/data_part2')
import pandas as pd
from common import write_csv

APQC_L1 = {
    '1.0': 'Develop Vision and Strategy', '2.0': 'Develop and Manage Products and Services',
    '3.0': 'Market and Sell Products and Services', '4.0': 'Manage Supply Chain for Physical Products',
    '5.0': 'Deliver Service', '6.0': 'Manage Customer Service', '7.0': 'Develop and Manage Human Capital',
    '8.0': 'Manage Information Technology (IT)', '9.0': 'Manage Financial Resources',
    '10.0': 'Acquire, Construct, and Manage Assets',
    '11.0': 'Manage Enterprise Risk, Compliance, Remediation, and Resiliency',
    '12.0': 'Manage External Relationships', '13.0': 'Develop and Manage Business Capabilities',
}

# function_id, name, description, apqc L1 list, apqc L2 (number and element id) where verified, bucket, alt bucket, customer_facing
ROWS = [
    ('F01', 'Executive and strategy', 'Executive leadership, corporate strategy, corporate development and planning of the business model.',
     ['1.0'], '1.1 (17040); 1.2 (10015); 1.3 (10016); 1.4 (20944)', 'ga', '', 0),
    ('F02', 'Product and engineering', 'Product management, design, software and hardware engineering, quality assurance and technical documentation of the product.',
     ['2.0'], '2.1 (19696); 2.2 (19698); 2.3 (10062)', 'rnd', '', 0),
    ('F03', 'Marketing', 'Market research, brand, demand generation, content, product marketing and campaign management.',
     ['3.0'], '3.1 (10101); 3.2 (10102); 3.3 (20008)', 'sm', '', 1),
    ('F04', 'Sales', 'Prospecting, account executives, sales engineering, sales operations, pricing and deal desk.',
     ['3.0'], '3.4 (10103); 3.5 (10105)', 'sm', '', 1),
    ('F05', 'Customer support', 'Inbound customer service and technical support: contacts, tickets, troubleshooting and escalation.',
     ['6.0'], '6.2 (10379); 6.3 (12658); 6.5 (20595)', 'cogs', 'sm', 1),
    ('F06', 'Customer success and account management', 'Onboarding, adoption, renewals, expansion and relationship management for existing customers.',
     ['6.0', '3.0'], '6.1 (10378); 3.5 (10105)', 'sm', 'cogs', 1),
    ('F07', 'Professional services', 'Implementation, consulting, training and other billable services delivered to customers.',
     ['5.0'], '5.1 (20026); 5.2 (20040); 5.3 (20058)', 'cogs', '', 1),
    ('F08', 'Service delivery and operations', 'Production of the core service for customers where it is labor-intensive (claims, transactions, content moderation, fulfilment of digital orders).',
     ['5.0'], '5.2 (20040); 5.3 (20058)', 'cogs', '', 0),
    ('F09', 'Supply chain, manufacturing and logistics', 'Planning, production, assembly, testing, warehousing and transport of physical products.',
     ['4.0'], '4.1 (10215); 4.3 (10217); 4.4 (10219)', 'cogs', '', 0),
    ('F10', 'Procurement', 'Sourcing, purchasing, supplier management and requisition-to-order for materials and services.',
     ['4.0'], '4.2 (10216)', 'ga', 'cogs', 0),
    ('F11', 'Finance and accounting', 'Planning and management accounting, revenue accounting, general accounting and reporting, payroll, payables, treasury and tax.',
     ['9.0'], '9.1 (10728); 9.2 (10729); 9.3 (10730); 9.4 (10731); 9.5 (10732)', 'ga', '', 0),
    ('F12', 'Human resources', 'Workforce planning, recruiting, onboarding, learning, employee relations, rewards, HR information and employee communication.',
     ['7.0'], '7.1 (17043); 7.2 (10410); 7.3 (20599); 7.4 (17052); 7.5 (10412); 7.6 (10413); 7.7 (17056); 7.8 (21451)', 'ga', '', 0),
    ('F13', 'Legal', 'Commercial contracts, corporate and securities law, intellectual property, litigation and privacy counsel.',
     ['12.0', '11.0'], '', 'ga', '', 0),
    ('F14', 'Risk, compliance, audit and governance', 'Enterprise risk management, regulatory compliance, internal audit, internal control over financial reporting, AI and data governance.',
     ['11.0'], '', 'ga', '', 0),
    ('F15', 'Information technology and security', 'Internal IT: end-user support, enterprise applications, infrastructure, identity and information security.',
     ['8.0'], '8.1 (20608); 8.2 (20652); 8.3 (20706); 8.4 (20765); 8.5 (20784); 8.6 (20824); 8.7 (20866)', 'ga', '', 0),
    ('F16', 'Technical operations and hosting', 'Operation of the customer-facing production platform: site reliability, cloud infrastructure, monitoring and incident response.',
     ['8.0'], '8.6 (20824); 8.7 (20866)', 'cogs', '', 0),
    ('F17', 'Facilities and real estate', 'Workplace, real estate, physical security and maintenance of owned or leased assets.',
     ['10.0'], '', 'ga', '', 0),
    ('F18', 'Business operations and transformation', 'Process management, project and portfolio management, quality, change management and knowledge management.',
     ['13.0'], '', 'ga', '', 0),
    ('F19', 'Corporate affairs and investor relations', 'Investor relations, public relations, government affairs and external communications.',
     ['12.0'], '', 'ga', '', 0),
]

df = pd.DataFrame(ROWS, columns=['function_id', 'function_name', 'description', 'apqc_l1', 'apqc_l2_verified',
                                 'cost_bucket', 'cost_bucket_alt', 'customer_facing'])
df['apqc_category'] = df.apqc_l1.apply(lambda ls: '; '.join(f'{c} {APQC_L1[c]}' for c in ls))
df['apqc_level'] = df.apqc_l2_verified.apply(lambda s: 2 if s else 1)
df['apqc_l1'] = df.apqc_l1.apply(lambda ls: ';'.join(ls))
df['apqc_version'] = 'PCF Cross-Industry 7.4 (Aug 2024)'
df = df[['function_id', 'function_name', 'description', 'apqc_category', 'cost_bucket', 'customer_facing',
         'apqc_l1', 'apqc_l2_verified', 'apqc_level', 'apqc_version', 'cost_bucket_alt']]
assert df.cost_bucket.isin(['cogs', 'rnd', 'sm', 'ga']).all()
write_csv(df, 'functions.csv')
