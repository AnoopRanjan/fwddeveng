"""
Definitive FDE Masterclass & Project Exploration Guide:
Features official Microsoft C# & .NET crash courses exclusively:
Primary Course: Generative AI with .NET & C# for Beginners (Microsoft Official - vISLS8aY0RU)
Companion Course: AZ-104 Azure Administrator Complete IaaS Masterclass for .NET (Microsoft Learn / MSDN - 0Knf9nub4-k)
Alternative Masterclass: Let's Learn .NET Semantic Kernel in C# (Microsoft - lCQOCoH3Osk)
Briefing: Microsoft C# & .NET 101 Architecture (Microsoft Developer - 4vHBgwcz_I4)
"""

FDE_MASTER_COURSE = {
    "title": "Generative AI with .NET & C# for Beginners - Official Microsoft Full Crash Course",
    "instructor": "Microsoft .NET Official (@dotnet)",
    "duration": "Official Microsoft Full Crash Course Series (C#, Semantic Kernel & Azure AI)",
    "primary_video_id": "vISLS8aY0RU",
    "primary_video_embed": "https://www.youtube-nocookie.com/embed/vISLS8aY0RU",
    "primary_video_url": "https://www.youtube.com/watch?v=vISLS8aY0RU",
    
    # Companion FDE Foundations Video: The longest Microsoft / MSDN Azure IaaS Basics full course
    "companion_video_id": "0Knf9nub4-k",
    "companion_video_embed": "https://www.youtube-nocookie.com/embed/0Knf9nub4-k",
    "companion_video_url": "https://www.youtube.com/watch?v=0Knf9nub4-k",
    "companion_title": "AZ-104 Azure Administrator Complete Study Cram - Full Azure IaaS Masterclass for .NET (Microsoft Learn / MSDN)",
    "companion_label": "Azure IaaS for .NET (3.5+ Hrs)",
    "companion_duration": "3.5+ Hours Marathon Masterclass",
    "companion_instructor": "Microsoft Learn & MSDN Official Curriculum",
    "companion_description": "The definitive, longest full-length Microsoft Azure IaaS video masterclass openly available on YouTube. Teaches core cloud infrastructure foundations essential for Forward Deployed Engineers: Virtual Machines (VMs), VM Scale Sets (VMSS), Virtual Networks (VNets), Subnets, NSGs, Peering, Azure Bastion, Storage Accounts, Managed Disks, Entra ID RBAC, and Cloud Monitoring.",
    
    # Alternative MSDN Masterclass: Let's Learn .NET Semantic Kernel in C# (2 Hours)
    "companion_alt_video_id": "lCQOCoH3Osk",
    "companion_alt_video_embed": "https://www.youtube-nocookie.com/embed/lCQOCoH3Osk",
    "companion_alt_video_url": "https://www.youtube.com/watch?v=lCQOCoH3Osk",
    "companion_alt_title": "Let's Learn .NET: Semantic Kernel in C# - Building Intelligent Apps (Microsoft Official)",
    "companion_alt_label": "Semantic Kernel C# (2h)",

    "palantir_video_id": "4vHBgwcz_I4",
    "palantir_video_embed": "https://www.youtube-nocookie.com/embed/4vHBgwcz_I4",
    "palantir_video_url": "https://www.youtube.com/watch?v=4vHBgwcz_I4",
    "tim_video_id": "lCQOCoH3Osk",
    "tim_video_embed": "https://www.youtube-nocookie.com/embed/lCQOCoH3Osk",
    "tim_video_url": "https://www.youtube.com/watch?v=lCQOCoH3Osk",
    "description": "The definitive official Microsoft enterprise crash course for Forward Deployed Engineers (FDE) implementing AI with C# and .NET. Covers end-to-end cloud engineering: C# AI integration, prompt engineering, ML.NET model training, multi-agent AI orchestration with Semantic Kernel, Azure Functions serverless APIs, Docker containerization, and Azure DevOps CI/CD deployment.",
    "chapters": [
        {
            "part": "Module 1: Enterprise C# Architecture & .NET Environment Setup",
            "desc": "Modern C# syntax, dependency injection, solution structure, .NET CLI, and enterprise cloud development standards."
        },
        {
            "part": "Module 2: Machine Learning with ML.NET & Model Builder in C#",
            "desc": "Training custom classification models locally in C#, Model Builder tooling, data preprocessing, and evaluation."
        },
        {
            "part": "Module 3: Multi-Agent AI Orchestration in C# with Semantic Kernel",
            "desc": "Designing stateful multi-agent workflows, native C# function plugins, planners, memory stores, and guardrails."
        },
        {
            "part": "Module 4: Azure DevOps CI/CD, Containerization & Cloud Deployment for .NET",
            "desc": "Dockerizing ASP.NET Core microservices, automated Azure DevOps YAML pipelines, and client monitoring handover."
        }
    ],
    "iaas_chapters": [
        {
            "part": "IaaS Module 1: Compute & Virtual Machines",
            "desc": "Azure Virtual Machines (VMs), VM Scale Sets (VMSS), Availability Zones, Spot instances, auto-scaling, and Azure Bastion secure host management."
        },
        {
            "part": "IaaS Module 2: Virtual Networking & Security",
            "desc": "VNets, Subnets, Network Security Groups (NSGs), Application Security Groups (ASGs), VNet Peering, and User Defined Routes (UDRs)."
        },
        {
            "part": "IaaS Module 3: Storage & Managed Disks",
            "desc": "Azure Storage Accounts, Blob Storage, Azure Files, OS & Data Managed Disks, LRS/ZRS/GRS replication, and Private Endpoints."
        },
        {
            "part": "IaaS Module 4: Cloud Governance & Monitoring",
            "desc": "ARM/Bicep IaC, Azure Resource Groups, Entra ID RBAC, Azure Monitor, Log Analytics, and cost management baselines."
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

# Dedicated ~10 Minute Fast-Track Video for Microsoft C# Architecture
FDE_BRIEFING_10MIN = {
    "title": "C# & .NET 101 for Cloud, AI & Microservices - Microsoft Official",
    "instructor": "Microsoft Developer",
    "channel": "Microsoft Developer",
    "duration": "~10 Minutes Fast-Track",
    "badge": "Microsoft C# Cloud 101",
    "video_id": "4vHBgwcz_I4",
    "video_embed": "https://www.youtube-nocookie.com/embed/4vHBgwcz_I4",
    "video_url": "https://www.youtube.com/watch?v=4vHBgwcz_I4",
    "subtitle": "Microsoft's Official C# & .NET Architecture Primer for Enterprise Engineers",
    "summary": "The official Microsoft primer on modern C# syntax, solution architecture, and building enterprise cloud systems on Azure with .NET.",
    "takeaways": [
        "Enterprise C# Foundations: Clean object-oriented architecture, records, and dependency injection.",
        "Cloud-Native .NET: Building modular microservices and event-driven APIs.",
        "Microsoft Ecosystem: Seamless integration with Azure Services, Azure DevOps, and AI SDKs."
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
