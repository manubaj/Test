"""
Detection catalogs for ERP sales intelligence agents.

Aligned with target opportunities:
IFS Implementation / Upgrade / Cloud Migration / Managed Support,
SAP S/4HANA Migration / Support, Infor Upgrade, Oracle ERP Migration,
ERP Digital Transformation, ERP Performance Optimization.
"""

from __future__ import annotations

# (canonical_name, category, aliases)
TECHNOLOGY_CATALOG: list[tuple[str, str, tuple[str, ...]]] = [
    ("IFS", "erp", ("ifs applications", "ifs apps", "ifs erp", "industrial and financial systems")),
    ("IFS Apps", "erp", ("ifs applications", "ifs apps 10", "ifs apps 9", "ifs apps 8")),
    ("IFS Cloud", "erp", ("ifs cloud", "ifs cloud erp")),
    ("SAP ECC", "erp", ("sap ecc", "sap r/3", "ecc 6", "sap erp ecc")),
    ("SAP S/4HANA", "erp", ("sap s/4hana", "s/4hana", "s4hana", "sap s4", "sap s/4")),
    ("Infor LN", "erp", ("infor ln", "baan", "infor baan")),
    ("Infor M3", "erp", ("infor m3", "movex", "infor movex")),
    ("Oracle ERP", "erp", ("oracle erp", "oracle e-business", "oracle ebs", "oracle fusion", "oracle cloud erp")),
    ("Microsoft Dynamics", "erp", ("microsoft dynamics", "dynamics 365", "dynamics ax", "dynamics nav", "d365")),
    ("Salesforce", "crm", ("salesforce", "sfdc", "salesforce crm")),
    ("Azure", "cloud", ("microsoft azure", "azure cloud", "azure devops", "azure sql")),
    ("AWS", "cloud", ("amazon web services", "aws cloud", "amazonaws", "amazon aws")),
    ("GCP", "cloud", ("google cloud", "gcp", "google cloud platform")),
    ("SQL Server", "database", ("sql server", "mssql", "microsoft sql", "microsoft sql server")),
    ("Oracle Database", "database", ("oracle database", "oracle db", "oracle rdbms", "oracle 19c")),
    ("PostgreSQL", "database", ("postgresql", "postgres")),
    ("Kubernetes", "devops", ("kubernetes", "k8s", "eks", "aks", "gke")),
    ("Docker", "devops", ("docker", "dockerfile", "containerized", "containers")),
]

# Opportunity signal groups (Agent 2)
OPPORTUNITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "upgrade": (
        "upgrade",
        "version upgrade",
        "reimplementation",
        "apps 10",
        "to cloud",
        "release upgrade",
        "system upgrade",
    ),
    "migration": (
        "migration",
        "migrate",
        "s/4hana migration",
        "cloud migration",
        "data migration",
        "erp migration",
        "brownfield",
        "greenfield",
    ),
    "modernization": (
        "modernization",
        "modernise",
        "modernize",
        "legacy transformation",
        "legacy system",
        "technical debt",
    ),
    "digital_transformation": (
        "digital transformation",
        "digitization",
        "digitalisation",
        "industry 4.0",
        "smart factory",
        "digital roadmap",
    ),
    "cloud_migration": (
        "cloud migration",
        "move to cloud",
        "saas migration",
        "lift and shift",
        "cloud first",
        "hosted in cloud",
    ),
    "manufacturing": (
        "manufacturing",
        "factory",
        "production plant",
        "shop floor",
        "discrete manufacturing",
        "process manufacturing",
        "oem",
    ),
    "new_plant": (
        "new plant",
        "greenfield plant",
        "new factory",
        "new facility",
        "plant opening",
    ),
    "expansion": (
        "expansion",
        "expanding",
        "new market",
        "capacity expansion",
        "growth initiative",
        "global expansion",
    ),
    "acquisition": (
        "acquisition",
        "acquired",
        "merger",
        "m&a",
        "takeover",
        "bought",
    ),
    "hiring": (
        "hiring",
        "we are hiring",
        "join our team",
        "open roles",
        "careers",
        "job openings",
    ),
    "support": (
        "managed services",
        "application support",
        "ams",
        "managed support",
        "outsourcing it",
        "support partner",
    ),
    "performance": (
        "performance optimization",
        "system performance",
        "slow erp",
        "optimize erp",
        "process improvement",
    ),
}

# Map signals + ERP stack → recommended services (original prompt goals)
OPPORTUNITY_SERVICE_RULES: list[tuple[str, tuple[str, ...], tuple[str, ...]]] = [
    # (service_label, required_erp_substrings, signal_keys)
    ("IFS Cloud Migration", ("IFS",), ("cloud_migration", "migration")),
    ("IFS Upgrade", ("IFS",), ("upgrade", "modernization")),
    ("IFS Managed Support", ("IFS",), ("support", "hiring")),
    ("IFS Implementation", ("IFS",), ("expansion", "new_plant", "acquisition")),
    ("SAP S/4HANA Migration", ("SAP",), ("migration", "cloud_migration", "upgrade")),
    ("SAP Support", ("SAP",), ("support", "hiring", "performance")),
    ("Infor Upgrade", ("Infor",), ("upgrade", "modernization", "migration")),
    ("Oracle ERP Migration", ("Oracle",), ("migration", "cloud_migration", "upgrade")),
    ("ERP Digital Transformation", (), ("digital_transformation", "modernization")),
    ("ERP Performance Optimization", (), ("performance", "modernization")),
]

HIRING_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ERP": ("erp consultant", "erp analyst", "erp developer", "erp project", "erp architect", "erp manager"),
    "SAP": ("sap consultant", "sap basis", "s/4hana", "sap abap", "sap fico", "sap mm", "sap pp", "sap hana"),
    "IFS": ("ifs consultant", "ifs developer", "ifs cloud", "ifs apps", "ifs technical"),
    "Oracle": ("oracle erp", "oracle ebs", "oracle fusion", "oracle dba", "oracle cloud"),
    "Infor": ("infor ln", "infor m3", "infor consultant", "infor developer"),
    "Cloud": ("cloud engineer", "cloud architect", "azure architect", "aws architect", "gcp engineer"),
    "DevOps": ("devops", "sre", "kubernetes", "ci/cd", "platform engineer", "site reliability"),
    "Database": ("database administrator", "dba", "sql server dba", "postgresql", "oracle dba"),
}

DECISION_MAKER_PATTERNS: list[tuple[str, str, str]] = [
    # role_key, regex, display title hint
    ("ceo", r"\b(ceo|chief executive officer)\b", "CEO"),
    ("cio", r"\b(cio|chief information officer)\b", "CIO"),
    ("cto", r"\b(cto|chief technology officer)\b", "CTO"),
    ("vp_it", r"\b(vp(?:\s+of)?\s+it|vice president(?:\s+of)?\s+(?:it|information technology))\b", "VP IT"),
    ("it_director", r"\b(it director|director of it|director of information technology)\b", "IT Director"),
    ("erp_manager", r"\b(erp manager|erp program manager|erp project manager)\b", "ERP Manager"),
    ("application_manager", r"\b(application(?:s)? manager|apps manager)\b", "Application Manager"),
    ("digital_transformation_lead", r"\b(digital transformation(?:\s+lead|\s+head|\s+director)?|head of digital)\b", "Digital Transformation Lead"),
]

INDUSTRY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Manufacturing": ("manufacturing", "industrial", "factory", "oem", "production"),
    "Aerospace & Defense": ("aerospace", "defense", "defence", "aviation", "avionics"),
    "Energy & Utilities": ("energy", "utilities", "oil", "gas", "power generation"),
    "Logistics": ("logistics", "supply chain", "warehouse", "freight", "distribution"),
    "Healthcare": ("healthcare", "hospital", "pharma", "medical device", "life sciences"),
    "Retail": ("retail", "e-commerce", "stores", "consumer goods"),
    "Construction": ("construction", "engineering", "infrastructure", "epc"),
    "Technology": ("software", "saas", "technology", "it services", "systems integrator"),
    "Automotive": ("automotive", "vehicle", "tier 1", "tier-1 supplier"),
    "Food & Beverage": ("food", "beverage", "f&b", "dairy", "agri"),
}

PROGRAMMING_LANGUAGES: tuple[str, ...] = (
    "python",
    "java",
    "javascript",
    "typescript",
    "c#",
    "csharp",
    ".net",
    "golang",
    "ruby",
    "php",
    "scala",
    "kotlin",
    "abap",
    "pl/sql",
)

PRODUCT_HINTS: tuple[str, ...] = (
    "products",
    "solutions",
    "platforms",
    "services",
    "portfolio",
    "offerings",
    "capabilities",
)

# Lead scoring weights (Agent 6) — from original prompt examples
LEAD_SCORE_WEIGHTS: dict[str, int] = {
    "ERP Detected": 30,
    "Manufacturing": 10,
    "Hiring ERP": 20,
    "Cloud Migration": 20,
    "Expansion": 20,
}
