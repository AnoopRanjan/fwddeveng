"""
Definitive FDE Masterclass & Project Exploration Guide:
Features the longest-duration, comprehensive free full course for Forward Deployed Engineering,
paired with enterprise project implementation and Palantir methodology.
"""

FDE_MASTER_COURSE = {
    "title": "Forward Deployed Engineer Full Course (Zero to Production Field Deployment)",
    "instructor": "Saurav Verma (GenAI / FDE Course) with Krish Naik & Palantir",
    "duration": "Comprehensive Full Course (Multi-Hour Marathon)",
    "primary_video_id": "NFiDNzQTzXY",
    "primary_video_embed": "https://www.youtube-nocookie.com/embed/NFiDNzQTzXY",
    "primary_video_url": "https://www.youtube.com/watch?v=NFiDNzQTzXY",
    "project_video_id": "FSZhPDzESPU",
    "project_video_embed": "https://www.youtube-nocookie.com/embed/FSZhPDzESPU",
    "project_video_url": "https://www.youtube.com/watch?v=FSZhPDzESPU",
    "palantir_video_id": "5OYy_UtINo4",
    "palantir_video_embed": "https://www.youtube-nocookie.com/embed/5OYy_UtINo4",
    "palantir_video_url": "https://www.youtube.com/watch?v=5OYy_UtINo4",
    "tim_video_id": "vLlIBT0HSSc",
    "tim_video_embed": "https://www.youtube-nocookie.com/embed/vLlIBT0HSSc",
    "tim_video_url": "https://www.youtube.com/watch?v=vLlIBT0HSSc",
    "description": "The definitive, longest-duration free full course on Forward Deployed Engineering (FDE) available on YouTube. Designed specifically to convert any developer at any level into an elite Forward Deployed Engineer. Covers the complete spectrum: role definitions, tech foundations from zero (APIs, SQL, Python, Git, Terminal, Models, RAG, MCP, Docker), end-to-end client project implementation, and interview preparation for $300k+ enterprise roles.",
    "chapters": [
        {
            "part": "Part 1: The FDE Job Profile & Mindset",
            "time": "Module 1",
            "desc": "How FDE fundamentally differs from standard SWE, Solutions Engineering, and IT consulting. Understanding customer empathy, discovering unstated operational bottlenecks, and the high-agency delivery loop."
        },
        {
            "part": "Part 2: The Core Tech Stack from Zero",
            "time": "Module 2",
            "desc": "Non-negotiable technical skills: APIs, HTTP protocols, SQL/database plumbing, Python backend systems, Git workflows, Docker containerization, and modern AI orchestration (RAG, vector search, MCP)."
        },
        {
            "part": "Part 3: End-to-End Enterprise Client Project",
            "time": "Module 3",
            "desc": "Building a full client solution from scratch: discovery interview, scoping requirements, designing the cloud & AI architecture, writing production glue code, live testing, and system handover."
        },
        {
            "part": "Part 4: Getting Hired as an FDE",
            "time": "Module 4",
            "desc": "The 90-day transition roadmap, tailoring your resume from software engineering to FDE advisory, building convincing proof-of-work portfolio artifacts, and acing mock system design rounds."
        }
    ],
    "core_stages": [
        {
            "stage": 1,
            "name": "The Mindset Shift: From Ticket Taker to Field Problem Solver",
            "summary": "Traditional developers wait for product managers to write Jira user stories. Forward Deployed Engineers operate directly on the frontline with client C-levels, operations leads, and end-users to uncover the messy, unstated operational bottlenecks.",
            "takeaways": [
                "Diagnose root problems instead of executing symptom requests",
                "Empathize with non-technical business users",
                "Deliver business ROI, not just code coverage"
            ]
        },
        {
            "stage": 2,
            "name": "The Technical T-Shape: Cloud + Integrations + AI + Security",
            "summary": "FDEs are not generalists who can't code, nor are they siloed backend coders. They possess deep engineering foundations (.NET, Python, APIs) with broad capabilities across cloud infrastructure (Azure Landing Zones), AI orchestration (RAG, Agents), and security governance.",
            "takeaways": [
                "Full-stack and cloud plumbing proficiency (Azure Functions, Logic Apps, Service Bus)",
                "Generative AI integration (Azure OpenAI, Semantic Kernel, vector search)",
                "Zero Trust security posture (Managed Identities, Private Link, Entra PIM)"
            ]
        },
        {
            "stage": 3,
            "name": "The 48-Hour Field Prototyping Playbook",
            "summary": "How to enter an unfamiliar enterprise customer environment, inspect their legacy data silos, and ship a functioning, secure Proof of Concept (PoC) in 48 hours without getting bogged down in endless corporate bureaucracy.",
            "takeaways": [
                "Rapid API mocking and event-driven data ingestion",
                "Deploying isolated sandbox infrastructure using Bicep/Terraform",
                "Building quick visual feedback loops that amaze executive stakeholders"
            ]
        },
        {
            "stage": 4,
            "name": "Enterprise Legacy Systems & Integration Mastery",
            "summary": "Real enterprises don't run pristine greenfield code; they run 15-year-old on-prem SQL databases, SOAP services, and legacy ERPs. An FDE acts as the connective tissue, bridging legacy systems to modern cloud AI and Sentinel security pipelines.",
            "takeaways": [
                "Handling dirty, unstandardized enterprise data feeds",
                "Hybrid networking (ExpressRoute, VPN, Private Endpoints)",
                "Resilient distributed messaging patterns (Claim Check, Saga, Pub-Sub)"
            ]
        },
        {
            "stage": 5,
            "name": "Executive Advisory, Architecture Review Boards (ARB) & Enablement",
            "summary": "The consulting capstone: presenting architecture trade-offs to CISOs and CTOs, defending security choices, and running interactive enablement workshops to train the client's internal engineering team to own the solution.",
            "takeaways": [
                "Translating technical risks into financial and operational metrics",
                "Running high-impact corporate training and brown-bag workshops",
                "Securing long-term advisory contracts and client trust"
            ]
        }
    ]
}

PROJECT_EXPLORATION_PILLARS = [
    {
        "id": "pillar-1",
        "title": "Enterprise Cloud Architecture & Zero Trust Landing Zones",
        "badge": "Core Foundation",
        "icon": "cloud",
        "color": "emerald",
        "description": "Establish multi-subscription governance, Cloud Adoption Framework (CAF) baselines, and Azure Landing Zones. Enforce policy initiatives, implement Customer-Managed Keys (CMK) in Azure Key Vault with Purge Protection, and eliminate public attack surfaces.",
        "skills": ["Management Groups", "Azure Policy Initiatives", "Key Vault RBAC", "CAF Security Baseline"]
    },
    {
        "id": "pillar-2",
        "title": "SIEM, SOAR & Cloud Detection Engineering",
        "badge": "Security Operations",
        "icon": "terminal",
        "color": "indigo",
        "description": "Architect scalable Log Analytics Workspaces and Microsoft Sentinel instances. Ingest streaming telemetry, author high-precision Kusto Query Language (KQL) detection rules, and trigger automated Logic Apps SOAR playbooks for instant alert triage.",
        "skills": ["Microsoft Sentinel", "KQL Detection Engineering", "Alert Grouping", "Logic Apps SOAR"]
    },
    {
        "id": "pillar-3",
        "title": "Posture Management & Workload Protection (CSPM/CWPP)",
        "badge": "Compliance & Hygiene",
        "icon": "shield-check",
        "color": "sky",
        "description": "Maximize Microsoft Defender for Cloud's Secure Score. Map enterprise controls to CIS Azure Foundations Benchmark, NIST SP 800-53, and ISO 27001. Deploy Defender for Servers Plan 2, agentless scanning, and Just-in-Time (JIT) VM access.",
        "skills": ["Secure Score Engine", "CIS Benchmarks", "Defender for Servers", "JIT Access"]
    },
    {
        "id": "pillar-4",
        "title": "Identity Perimeter & Zero Trust Access",
        "badge": "Identity Architecture",
        "icon": "key",
        "color": "amber",
        "description": "Treat Identity as the primary security perimeter. Master OAuth 2.0 / OIDC modern authentication, deploy phishing-resistant Conditional Access, eradicate standing administrative privileges via Entra PIM, and transition to Managed Identities.",
        "skills": ["Entra ID", "Conditional Access Engine", "Entra PIM (JIT)", "Workload Identities"]
    },
    {
        "id": "pillar-5",
        "title": "Network Micro-segmentation & Perimeter Defense",
        "badge": "Perimeter Defense",
        "icon": "network",
        "color": "teal",
        "description": "Architect resilient Hub-and-Spoke virtual networks with User Defined Routes (0.0.0.0/0) forcing egress through Azure Firewall Premium. Protect web APIs with Application Gateway WAF (OWASP CRS) and project PaaS onto VNets with Private Endpoints.",
        "skills": ["Hub-Spoke Topology", "Azure Firewall Premium", "WAF CRS 3.2", "Azure Private Link"]
    },
    {
        "id": "pillar-6",
        "title": "Cloud Incident Response & Evidence Forensics",
        "badge": "SOC & Forensics",
        "icon": "flame",
        "color": "rose",
        "description": "Execute the 4-phase NIST SP 800-61 / SANS incident response lifecycle. Perform live cloud containment (token revocation, network isolation NSGs), snapshot managed VM disks for forensics, and write executive Post-Incident Reviews (PIR).",
        "skills": ["NIST 800-61 Lifecycle", "Session Revocation", "Disk Forensics", "Root Cause Analysis"]
    },
    {
        "id": "pillar-7",
        "title": "Vulnerability Management & DevSecOps Pipelines",
        "badge": "Vulnerability & SLA",
        "icon": "bug",
        "color": "orange",
        "description": "Move beyond theoretical CVSS base scores using EPSS and CISA KEV risk-based prioritization. Automate OS patch management with Azure Update Manager maintenance windows, and shift security left into CI/CD container scanning.",
        "skills": ["MDVM", "CVSS v3/v4 & EPSS", "Azure Update Manager", "Container CI/CD Linter"]
    },
    {
        "id": "pillar-8",
        "title": "Enterprise AI Engineering & Permission-Aware RAG",
        "badge": "AI Implementation",
        "icon": "cpu",
        "color": "violet",
        "description": "Build production-grade Retrieval-Augmented Generation (RAG) with Azure AI Search (Hybrid Search + Semantic Reranker) and Azure OpenAI. Orchestrate multi-tool AI Agents with Semantic Kernel and enforce document-level Entra ID security trimming.",
        "skills": ["Hybrid Vector Search", "Semantic Kernel", "Azure OpenAI GPT-4o", "Security Trimming"]
    },
    {
        "id": "pillar-9",
        "title": "AI Security, OWASP LLM Top 10 & Content Safety",
        "badge": "AI Security",
        "icon": "shield-x",
        "color": "purple",
        "description": "Defend enterprise AI against direct and indirect prompt injection, sensitive data leakage, and jailbreaks. Intercept adversarial payloads using Azure AI Content Safety Prompt Shields and sandbox all tool execution environments.",
        "skills": ["Prompt Injection Defense", "Azure AI Content Safety", "OWASP LLM Top 10", "Groundedness Guards"]
    },
    {
        "id": "pillar-10",
        "title": "Forward Deployed Engineering (FDE) Methodology",
        "badge": "Advisory & GTM",
        "icon": "briefcase",
        "color": "cyan",
        "description": "Lead customer discovery sessions, navigate legacy enterprise friction, build scalable integration glue code, present before Architecture Review Boards (ARBs), and deliver corporate enablement training that commands executive trust.",
        "skills": ["Customer Discovery", "Architecture Review Boards", "Executive Pitching", "Corporate Training"]
    }
]
