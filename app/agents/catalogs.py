"""
Shared detection catalogs for ERP, cloud, databases, languages, and keywords.

Centralizing these lists avoids duplication across independent agents.
"""

from __future__ import annotations

# Technology Detection Agent catalog: (canonical_name, category, aliases)
TECHNOLOGY_CATALOG: list[tuple[str, str, tuple[str, ...]]] = [
    ("IFS", "erp", ("ifs applications", "ifs apps", "ifs erp")),
    ("IFS Apps", "erp", ("ifs applications", "ifs apps 10", "ifs apps 9")),
    ("IFS Cloud", "erp", ("ifs cloud",)),
    ("SAP ECC", "erp", ("sap ecc", "sap r/3", "ecc 6")),
    ("SAP S/4HANA", "erp", ("sap s/4hana", "s/4hana", "s4hana", "sap s4")),
    ("Infor LN", "erp", ("infor ln", "baan")),
    ("Infor M3", "erp", ("infor m3", "movex")),
    ("Oracle ERP", "erp", ("oracle erp", "oracle e-business", "oracle ebs", "oracle fusion")),
    ("Microsoft Dynamics", "erp", ("microsoft dynamics", "dynamics 365", "dynamics ax", "dynamics nav")),
    ("Salesforce", "crm", ("salesforce", "sfdc")),
    ("Azure", "cloud", ("microsoft azure", "azure cloud", "azure devops")),
    ("AWS", "cloud", ("amazon web services", "aws cloud", "amazonaws")),
    ("GCP", "cloud", ("google cloud", "gcp", "google cloud platform")),
    ("SQL Server", "database", ("sql server", "mssql", "microsoft sql")),
    ("Oracle Database", "database", ("oracle database", "oracle db", "oracle rdbms")),
    ("PostgreSQL", "database", ("postgresql", "postgres")),
    ("Kubernetes", "devops", ("kubernetes", "k8s")),
    ("Docker", "devops", ("docker", "dockerfile", "containerized")),
]

# Opportunity keyword groups used by ERP Opportunity Detection Agent
OPPORTUNITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "upgrade": ("upgrade", "version upgrade", "reimplementation", "apps 10", "to cloud"),
    "migration": ("migration", "migrate", "s/4hana migration", "cloud migration", "data migration"),
    "modernization": ("modernization", "modernise", "modernize", "legacy transformation"),
    "digital_transformation": ("digital transformation", "digitization", "digitalisation", "industry 4.0"),
    "cloud_migration": ("cloud migration", "move to cloud", "saas migration", "lift and shift"),
    "manufacturing": ("manufacturing", "factory", "production plant", "shop floor", "discrete manufacturing"),
    "new_plant": ("new plant", "greenfield plant", "new factory", "new facility"),
    "expansion": ("expansion", "expanding", "new market", "capacity expansion", "growth initiative"),
    "acquisition": ("acquisition", "acquired", "merger", "m&a", "takeover"),
    "hiring": ("hiring", "we are hiring", "join our team", "open roles", "careers"),
}

# Hiring Intelligence Agent role keywords
HIRING_KEYWORDS: dict[str, tuple[str, ...]] = {
    "ERP": ("erp consultant", "erp analyst", "erp developer", "erp project"),
    "SAP": ("sap consultant", "sap basis", "s/4hana", "sap abap", "sap fico"),
    "IFS": ("ifs consultant", "ifs developer", "ifs cloud"),
    "Oracle": ("oracle erp", "oracle ebs", "oracle fusion", "oracle dba"),
    "Infor": ("infor ln", "infor m3", "infor consultant"),
    "Cloud": ("cloud engineer", "cloud architect", "azure", "aws", "gcp"),
    "DevOps": ("devops", "sre", "kubernetes", "ci/cd", "platform engineer"),
    "Database": ("database administrator", "dba", "sql server", "postgresql", "oracle dba"),
}

# Decision Maker Finder title patterns
DECISION_MAKER_PATTERNS: list[tuple[str, str]] = [
    ("ceo", "ceo|chief executive"),
    ("cio", "cio|chief information"),
    ("cto", "cto|chief technology"),
    ("vp_it", "vp it|vice president.*it|vp of it|vp information"),
    ("it_director", "it director|director of it|director of information"),
    ("erp_manager", "erp manager|erp program manager"),
    ("application_manager", "application manager|applications manager"),
    ("digital_transformation_lead", "digital transformation|head of digital"),
]

INDUSTRY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "Manufacturing": ("manufacturing", "industrial", "factory", "oem"),
    "Aerospace & Defense": ("aerospace", "defense", "defence", "aviation"),
    "Energy & Utilities": ("energy", "utilities", "oil", "gas", "power"),
    "Logistics": ("logistics", "supply chain", "warehouse", "freight"),
    "Healthcare": ("healthcare", "hospital", "pharma", "medical"),
    "Retail": ("retail", "e-commerce", "stores"),
    "Construction": ("construction", "engineering", "infrastructure"),
    "Technology": ("software", "saas", "technology", "it services"),
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
    "go ",
    "ruby",
    "php",
    "scala",
    "kotlin",
)

PRODUCT_HINTS: tuple[str, ...] = (
    "products",
    "solutions",
    "platforms",
    "services",
    "portfolio",
)
