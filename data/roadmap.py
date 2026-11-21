"""
Roadmap module: Comprehensive 35-day structured plan transforming a Cloud Technical Lead
into a Forward Deployed Engineer (FDE) + AI + Cybersecurity Advisor.
"""

ROADMAP_DAYS = [
    # Phase 1: Days 1-7
    {
        "day": 1,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 1,
        "title": "Cloud Adoption Framework (CAF) & Azure Landing Zone Security",
        "objective": "Master Azure enterprise governance, management group hierarchies, and CAF security baselines.",
        "morning_task": "Study Microsoft CAF Security Methodology and Enterprise Landing Zone architecture on Microsoft Learn.",
        "afternoon_task": "Review and deploy an Azure Policy initiative denying public IP creation on virtual machines via Azure CLI / Portal.",
        "evening_task": "Practice FDE scenario: Explaining to a client CTO why their subscription hierarchy is failing security audits.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 2,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 4,
        "title": "Entra ID Architecture & Modern Authentication Protocols",
        "objective": "Deep-dive into OAuth 2.0, OpenID Connect (OIDC), SAML, and tenant security configurations.",
        "morning_task": "Watch John Savill's SC-300 Entra ID Core Architecture video; review OIDC token exchange and scopes.",
        "afternoon_task": "Audit your Azure tenant for legacy authentication protocols; analyze sign-in diagnostic logs.",
        "evening_task": "Answer interview question: 'How do you transition a client from legacy basic auth to modern OAuth 2.0 without service downtime?'",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 3,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 4,
        "title": "Conditional Access Policies & Zero Trust Identity Perimeter",
        "objective": "Design and simulate granular Conditional Access policies enforcing MFA and device compliance.",
        "morning_task": "Read MSDN guide on Conditional Access policy design, signal aggregation, and emergency break-glass account setup.",
        "afternoon_task": "Configure a Conditional Access policy in 'Report-Only' mode requiring Phishing-Resistant MFA and blocking legacy protocols.",
        "evening_task": "Draft a rollback and emergency access plan for a client deploying Conditional Access across 5,000 users.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 4,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 4,
        "title": "Privileged Identity Management (PIM) & Workload Identities",
        "objective": "Eliminate standing administrative privileges and secure service principals with Managed Identities.",
        "morning_task": "Study Microsoft Entra PIM workflows: Eligible assignments, approval gates, and time-bound activations.",
        "afternoon_task": "Convert an App Service / Function app from using static client secrets to User-Assigned Managed Identity.",
        "evening_task": "Prepare pitch: Why Managed Identities eliminate credential leakage in git repositories.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 5,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 5,
        "title": "Hub-and-Spoke Network Topology & Micro-segmentation",
        "objective": "Architect secure Azure VNets using Peering, Network Security Groups (NSGs), and Application Security Groups (ASGs).",
        "morning_task": "Read Azure Architecture Center reference pattern on Hub-and-Spoke networks and User Defined Routes (UDRs).",
        "afternoon_task": "Deploy a Hub VNet and Spoke VNet with peering; configure ASGs to isolate web and database tiers.",
        "evening_task": "Evaluate trade-offs between Azure Virtual WAN and custom Hub-and-Spoke for mid-sized enterprise clients.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 6,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 5,
        "title": "Perimeter Defense: Azure Firewall Premium, WAF & Private Link",
        "objective": "Implement Layer 7 deep packet inspection, OWASP Core Rules on WAF, and isolate PaaS with Private Endpoints.",
        "morning_task": "Study Azure Firewall Premium IDPS & TLS inspection; study Application Gateway WAF CRS rules.",
        "afternoon_task": "Create a Private Endpoint for Azure Key Vault / Azure SQL and verify DNS resolution against private IP.",
        "evening_task": "Interview practice: 'How do you defend against data exfiltration if an internal compute resource is compromised?'",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 7,
        "phase": 1,
        "phase_title": "Enterprise Cloud Architecture & Identity Foundations",
        "topic_id": 1,
        "title": "Phase 1 Capstone Lab: Enterprise Secure Landing Zone Review",
        "objective": "Synthesize Identity, Networking, and Governance into a hardened Landing Zone architecture.",
        "morning_task": "Review all Phase 1 concepts (CAF, PIM, CA, Hub-Spoke, Private Link, Key Vault).",
        "afternoon_task": "Perform an architectural security review on a simulated legacy cloud deployment; identify 10 key vulnerabilities.",
        "evening_task": "Phase 1 Checkpoint: Record a 5-minute Loom-style architectural briefing as an FDE advising a client CTO.",
        "milestone": True,
        "estimated_hours": 3
    },

    # Phase 2: Days 8-14
    {
        "day": 8,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 3,
        "title": "Microsoft Defender for Cloud Architecture & Secure Score",
        "objective": "Understand CSPM fundamentals, recommendation engines, and Secure Score calculations.",
        "morning_task": "Watch Microsoft Security Community webinar on Defender for Cloud architecture and Secure Score mechanics.",
        "afternoon_task": "Explore Defender for Cloud dashboard; identify the top 3 recommendations with the highest Secure Score impact.",
        "evening_task": "Explain how to present Secure Score improvements to executive leadership as a business KPI.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 9,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 3,
        "title": "Regulatory Compliance Baselines (CIS, NIST SP 800-53, ISO 27001)",
        "objective": "Map cloud configurations against international cybersecurity compliance frameworks.",
        "morning_task": "Study the Microsoft Cloud Security Benchmark (MCSB) and how it maps to CIS Azure Foundations and NIST.",
        "afternoon_task": "Assign the CIS Microsoft Azure Foundations Benchmark initiative to a subscription in Defender for Cloud.",
        "evening_task": "Consulting scenario: Helping a client prepare for a SOC 2 Type II audit using automated Azure compliance dashboards.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 10,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 3,
        "title": "Cloud Workload Protection (CWPP): Defender for Servers & Storage",
        "objective": "Configure runtime protection, Defender for Endpoint (MDE) integration, and malware scanning for Blob Storage.",
        "morning_task": "Read MSDN on Defender for Servers Plan 1 vs Plan 2 and Defender for Storage malware scanning.",
        "afternoon_task": "Enable JIT (Just-in-Time) VM access on an NSG; test initiating a time-bound access request.",
        "evening_task": "Interview practice: 'What are the operational and cost differences between Defender for Servers Plan 1 and Plan 2?'",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 11,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 7,
        "title": "Vulnerability Management Lifecycle & CVSS / EPSS Scoring",
        "objective": "Master CVE analysis, CVSS v3.1/v4.0 vector strings, and Exploit Prediction Scoring System (EPSS).",
        "morning_task": "Deep-dive into CVSS v3.1 specification (AV, AC, PR, UI, S, C, I, A) and CISA KEV catalog.",
        "afternoon_task": "Analyze 3 real-world CVEs (e.g., Log4Shell, Azure OMIGOD, Spring4Shell) and calculate their true operational risk.",
        "evening_task": "Develop an SLA remediation matrix (Critical, High, Medium, Low) for an enterprise software client.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 12,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 7,
        "title": "Microsoft Defender Vulnerability Management (MDVM) & Patching",
        "objective": "Deploy continuous vulnerability scanning and automate OS patch management via Azure Update Manager.",
        "morning_task": "Study MDVM exposed devices inventory, software weaknesses, and event timelines.",
        "afternoon_task": "Configure Azure Update Manager with a scheduled maintenance window for automatic security updates.",
        "evening_task": "Address client dilemma: 'How do you patch zero-day OS vulnerabilities across production clusters without taking services offline?'",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 13,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 7,
        "title": "DevSecOps: Container Vulnerability Scanning & CI/CD Security",
        "objective": "Integrate automated security testing (SAST, DAST, SCA) into Azure DevOps and GitHub pipelines.",
        "morning_task": "Read MSDN on Defender for Containers and image vulnerability scanning in Azure Container Registry (ACR).",
        "afternoon_task": "Build an Azure DevOps YAML pipeline step that runs Trivy or Microsoft Security DevOps to scan Docker images.",
        "evening_task": "Prepare FDE talk track: 'Shifting security left from runtime firefighting into the developer commit loop.'",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 14,
        "phase": 2,
        "phase_title": "Posture Management, Workload Protection & Vulnerability Mgmt",
        "topic_id": 3,
        "title": "Phase 2 Capstone Lab: Cloud Posture & Vulnerability Audit Report",
        "objective": "Deliver a comprehensive Cloud Posture & Vulnerability Assessment for an enterprise workload.",
        "morning_task": "Consolidate Defender for Cloud findings, Secure Score gaps, and vulnerability scan results.",
        "afternoon_task": "Draft an executive remediation roadmap prioritizing quick-wins, high-risk CVEs, and compliance controls.",
        "evening_task": "Phase 2 Milestone Review: Verify mastery of CSPM, CWPP, MDVM, and CVSS prioritization.",
        "milestone": True,
        "estimated_hours": 3
    },

    # Phase 3: Days 15-21
    {
        "day": 15,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Microsoft Sentinel Architecture & Data Ingestion Design",
        "objective": "Design scalable Sentinel workspaces, data ingestion tiers, and retention strategies.",
        "morning_task": "Watch Microsoft Security Community video on Sentinel Workspace Architecture and Data Connectors.",
        "afternoon_task": "Enable Microsoft Entra ID and Azure Activity data connectors in a test Sentinel workspace.",
        "evening_task": "Calculate ingestion costs: evaluate Basic Logs vs Analytics Logs for high-volume telemetry.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 16,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Kusto Query Language (KQL) Fundamentals for Security",
        "objective": "Master core KQL syntax: operators, time windows, aggregations, and string manipulation.",
        "morning_task": "Study KQL documentation: where, summarize, count(), bin(), extend, project, parse_json().",
        "afternoon_task": "Write 5 KQL queries against SigninLogs analyzing failed logins, IP distributions, and application IDs.",
        "evening_task": "Complete KQL flash exercises: extracting nested JSON properties from Azure Activity logs.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 17,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Advanced KQL: Multi-Table Joins, Time Series & Anomalies",
        "objective": "Write advanced threat hunting queries joining Identity, Network, and Resource telemetry.",
        "morning_task": "Learn KQL join kinds (inner, leftouter), make_series, series_decompose_anomalies(), and prev()/next().",
        "afternoon_task": "Write a KQL query correlating failed sign-ins from an IP followed by a successful sign-in within 15 minutes.",
        "evening_task": "Interview practice: Explain how KQL enables rapid threat hunting compared to traditional SQL queries.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 18,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Sentinel Analytics Rules & Alert Tuning",
        "objective": "Create scheduled and NRT detection rules, map MITRE ATT&CK tactics, and configure alert grouping.",
        "morning_task": "Read MSDN on Sentinel Analytics Rules, entity mapping (Account, Host, IP), and incident creation.",
        "afternoon_task": "Create a custom Sentinel Analytics Rule to detect 'Suspicious Azure Role Assignment to External Guest Account'.",
        "evening_task": "Analyze strategies for alert tuning to suppress false positives without blinding SOC analysts.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 19,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Sentinel SOAR: Automation Rules & Logic Apps Playbooks",
        "objective": "Build automated incident response playbooks using Azure Logic Apps and Sentinel triggers.",
        "morning_task": "Study Sentinel Automation Rules and Logic Apps connector for incident enrichment and containment.",
        "afternoon_task": "Build a Logic App playbook that triggers on incident creation: geo-locates the attacker IP and posts an adaptive card to Slack/Teams.",
        "evening_task": "Pitch to client: How automated SOAR reduces Mean Time to Respond (MTTR) from hours to seconds.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 20,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Threat Intelligence & Watchlists in Microsoft Sentinel",
        "objective": "Incorporate STIX/TAXII threat feeds, dynamic watchlists, and MITRE ATT&CK matrices into detection pipelines.",
        "morning_task": "Study Threat Intelligence Platforms (TIP) integration with Sentinel and creating custom Watchlists.",
        "afternoon_task": "Create a Watchlist of VIP Executive Accounts and modify analytics rules to trigger high-severity alerts when targeted.",
        "evening_task": "Explain how threat intelligence feeds prevent targeted spear-phishing and credential harvesting.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 21,
        "phase": 3,
        "phase_title": "SIEM, SOAR, KQL & Threat Detection Engineering",
        "topic_id": 2,
        "title": "Capstone Project 1: Cloud Security Monitoring & SOAR Pipeline",
        "objective": "Build & deploy Capstone Project 1: End-to-end Sentinel detection & automated incident containment.",
        "morning_task": "Synthesize data connectors, custom KQL rules, alert grouping, and Logic App playbooks.",
        "afternoon_task": "Simulate an attack (brute force + role elevation), trigger the Sentinel incident, and verify automated enrichment.",
        "evening_task": "Phase 3 Milestone: Document the project architecture diagram and GitHub repository readme.",
        "milestone": True,
        "estimated_hours": 4
    },

    # Phase 4: Days 22-28
    {
        "day": 22,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 6,
        "title": "Cloud Incident Response Framework (NIST 800-61 / SANS)",
        "objective": "Master the 4 phases of cloud IR: Preparation, Detection & Analysis, Containment & Eradication, Post-Incident.",
        "morning_task": "Read NIST SP 800-61 Rev 2 and Microsoft Cloud Incident Response guidelines.",
        "afternoon_task": "Map out a step-by-step triage checklist for an Azure subscription compromise scenario.",
        "evening_task": "Interview practice: Walk through the first 60 minutes of discovering an active data exfiltration incident.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 23,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 6,
        "title": "Containment Tactics: Identity Lockdown & Network Quarantine",
        "objective": "Execute cloud-native containment actions without destroying forensic evidence.",
        "morning_task": "Learn Azure CLI / PowerShell containment commands: Revoke-AzureADUserAllRefreshToken, VM isolation NSGs.",
        "afternoon_task": "Execute a hands-on simulation: isolate a VM's NIC and revoke active OAuth tokens for a compromised test account.",
        "evening_task": "Discuss the trade-off between immediate business continuity vs preserving forensic artifacts.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 24,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 6,
        "title": "Cloud Forensics: Disk Snapshots, Immutable Storage & RCA",
        "objective": "Preserve disk images, export audit logs to immutable storage, and draft an executive Root Cause Analysis (RCA).",
        "morning_task": "Study Azure Managed Disk snapshots, SAS URL exports, and WORM storage policies.",
        "afternoon_task": "Snapshot a VM disk, mount it read-only on an analysis VM, and verify file hashes.",
        "evening_task": "Write an executive Post-Incident Report (PIR) detailing attack vector, timeline, blast radius, and lessons learned.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 25,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 9,
        "title": "Enterprise AI Foundations: Azure OpenAI & Architecture Patterns",
        "objective": "Understand Azure OpenAI models, token dynamics, rate limiting, and enterprise hosting topologies.",
        "morning_task": "Study Azure OpenAI documentation, model capabilities (GPT-4o, embedding models), and provisioned throughput (PTU).",
        "afternoon_task": "Deploy an Azure OpenAI instance with Managed Identity authentication and disable public network access.",
        "evening_task": "Answer client inquiry: 'How does Microsoft ensure enterprise data entered into Azure OpenAI is not used to train base models?'",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 26,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 9,
        "title": "RAG Architecture: Chunking, Vector Embeddings & Azure AI Search",
        "objective": "Build a robust Retrieval-Augmented Generation ingestion and hybrid search pipeline.",
        "morning_task": "Read MSDN on Azure AI Search vector indexes, HNSW algorithm, BM25 keyword matching, and Semantic Reranker.",
        "afternoon_task": "Build a Python ingestion script that chunks markdown/PDF files, generates vector embeddings, and uploads to Azure AI Search.",
        "evening_task": "Analyze chunking strategies: fixed character size vs semantic sentence splitting vs hierarchical chunking.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 27,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 9,
        "title": "Agentic AI Systems: Semantic Kernel, Function Calling & MCP",
        "objective": "Design AI agents capable of calling tools, querying APIs, and executing structured workflows.",
        "morning_task": "Study Microsoft Semantic Kernel documentation and Azure OpenAI function calling specification.",
        "afternoon_task": "Implement an AI agent with tool plugins that can query Azure Resource Graph and check VM security status.",
        "evening_task": "Explore Model Context Protocol (MCP) and how standardized tool calling connects enterprise backends to LLMs.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 28,
        "phase": 4,
        "phase_title": "Incident Response & Enterprise AI Engineering",
        "topic_id": 9,
        "title": "Capstone Project 2: Secure Azure Enterprise Application Architecture",
        "objective": "Deliver Capstone Project 2: High-security cloud application architecture integrating Azure AI, Private Endpoints & Key Vault.",
        "morning_task": "Assemble Bicep/Terraform template for Web App + Private Endpoint + Key Vault + Azure OpenAI.",
        "afternoon_task": "Deploy and test end-to-end zero-trust connectivity with Entra Workload Identity.",
        "evening_task": "Phase 4 Milestone: Architecture review and documentation complete.",
        "milestone": True,
        "estimated_hours": 4
    },

    # Phase 5: Days 29-35
    {
        "day": 29,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 8,
        "title": "OWASP LLM Top 10 Deep Dive: Prompt Injection & Extraction",
        "objective": "Analyze vulnerabilities unique to LLM applications: direct/indirect prompt injection, training data poisoning, insecure output.",
        "morning_task": "Study OWASP Top 10 for LLM Applications (LLM01 to LLM10) and real-world exploit writeups.",
        "afternoon_task": "Test adversarial prompt injection techniques against a test RAG pipeline and observe extraction behaviors.",
        "evening_task": "Formulate defense-in-depth strategies: input sanitization, delimiter engineering, and separate trust boundaries.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 30,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 8,
        "title": "Azure AI Content Safety, Prompt Shields & Permission-Aware RAG",
        "objective": "Implement automated guardrails using Azure AI Content Safety Prompt Shields and document-level security trimming.",
        "morning_task": "Read MSDN on Azure AI Content Safety Prompt Shields (Jailbreak & Indirect attacks) and Groundedness Detection.",
        "afternoon_task": "Integrate Azure AI Content Safety API into your RAG pipeline to intercept malicious queries before LLM inference.",
        "evening_task": "Architecture challenge: Implement Entra ID group security filtering on Azure AI Search index queries.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 31,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 10,
        "title": "FDE Methodology: Customer Problem Discovery & Scoping",
        "objective": "Master the art of uncovering the real operational problem behind client feature requests.",
        "morning_task": "Study Palantir Forward Deployed Engineering case studies and client engagement methodologies.",
        "afternoon_task": "Draft a Client Discovery Interview Template: questions to uncover security bottlenecks, integration hurdles, and legacy debt.",
        "evening_task": "Roleplay: Turning vague client requirements ('We want AI and better security') into a 3-phase technical delivery roadmap.",
        "milestone": False,
        "estimated_hours": 2
    },
    {
        "day": 32,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 10,
        "title": "Enterprise Integration Patterns & Cloud Migration Acceleration",
        "objective": "Bridge legacy enterprise systems (SQL, mainframes, ERP) with modern cloud event streams and APIs.",
        "morning_task": "Review Azure integration architecture patterns (Claim Check, Event-Driven Architecture, Service Bus vs Event Hub).",
        "afternoon_task": "Architect an event-driven ingestion pipeline handling 100k security events/minute with Azure Functions and Service Bus.",
        "evening_task": "Highlight how your existing .NET and Azure migration background gives you unfair advantage in FDE delivery.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 33,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 10,
        "title": "Executive Advisory, Architecture Review Boards & Training",
        "objective": "Communicate complex technical trade-offs to CISOs and train internal client engineering teams.",
        "morning_task": "Learn the structure of an Architecture Review Board (ARB) presentation: Context, Options, Trade-offs, Recommendation.",
        "afternoon_task": "Create a 10-slide executive pitch deck for an enterprise cloud security & AI modernization initiative.",
        "evening_task": "Develop an internal corporate training syllabus to upskill client developers on secure cloud coding.",
        "milestone": False,
        "estimated_hours": 3
    },
    {
        "day": 34,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 8,
        "title": "Capstone Project 3: AI-Powered Cybersecurity Triage Assistant",
        "objective": "Build & deploy Capstone Project 3: Production RAG assistant analyzing security alerts with guardrails and citations.",
        "morning_task": "Assemble Azure AI Search index with security playbooks/CVE documentation, configure Prompt Shields.",
        "afternoon_task": "Deploy the complete AI assistant web API; test query parsing, retrieval, and guardrail enforcement.",
        "evening_task": "Record a demo video walkthrough showcasing architecture, security guardrails, and real-time triage.",
        "milestone": True,
        "estimated_hours": 4
    },
    {
        "day": 35,
        "phase": 5,
        "phase_title": "AI Security, FDE Advisory & Executive Pitch Mastery",
        "topic_id": 10,
        "title": "Final Milestone: Comprehensive FDE Interview Simulation & GTM",
        "objective": "Execute full mock interview, finalize portfolio, and deploy client-ready FDE positioning.",
        "morning_task": "Rehearse the professional pitch for hiring managers: Cloud & AI Lead transitioning to FDE Advisor.",
        "afternoon_task": "Conduct a 20-question rapid-fire technical interview simulation across all 10 roadmap domains.",
        "evening_task": "Final Polish: Celebrate 35-day completion, review completed portfolio, and prepare for real-world client engagements!",
        "milestone": True,
        "estimated_hours": 3
    }
]

def get_day_by_number(day_num: int):
    for d in ROADMAP_DAYS:
        if d["day"] == day_num:
            return d
    return None

def get_days_by_phase(phase_num: int):
    return [d for d in ROADMAP_DAYS if d["phase"] == phase_num]
