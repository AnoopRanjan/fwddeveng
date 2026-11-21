"""
Projects module: Contains detailed blueprints, architecture diagrams,
and step-by-step implementation guides for the 3 portfolio projects that
prove hands-on competence to hiring managers.
"""

PROJECTS = [
    {
        "id": "project-1",
        "title": "Project 1: Enterprise Cloud Security Monitoring & Automated SOAR",
        "subtitle": "Microsoft Sentinel + Log Analytics + Custom KQL Detections + Azure Logic Apps Playbook",
        "category": "Cloud Security Operations (SIEM/SOAR)",
        "badge": "Core Portfolio 1",
        "summary": "Deploy a cloud-native security monitoring architecture in Azure. Ingest diagnostic and security telemetry into Microsoft Sentinel, author high-fidelity KQL detection analytics rules (brute-force credential attacks, privilege escalations), and build an automated SOAR playbook with Azure Logic Apps for rapid incident enrichment and containment.",
        "architecture_diagram": """
+-----------------------------------------------------------------------------------------+
|                                    AZURE ENVIRONMENT                                    |
|                                                                                         |
|  +-------------------+       +--------------------+       +--------------------------+  |
|  |  Microsoft Entra  |       |  Virtual Machines  |       | Azure PaaS (SQL/Storage) |  |
|  |  (Sign-in/Audit)  |       |   (Syslog/SecEvent)|       |   (Resource Logs)        |  |
|  +---------+---------+       +---------+----------+       +------------+-------------+  |
|            |                           |                               |                |
|            +---------------------------+-------------------------------+                |
|                                        |                                                |
|                                        v (Data Connectors)                              |
|                    +----------------------------------------+                           |
|                    |     Log Analytics Workspace (LAW)      |                           |
|                    +-------------------+--------------------+                           |
|                                        |                                                |
|                                        v (Streaming Telemetry)                          |
|                    +----------------------------------------+                           |
|                    |           Microsoft Sentinel           |                           |
|                    |  - Custom KQL Analytics Rules          |                           |
|                    |  - MITRE ATT&CK Mapping (T1110, T1078) |                           |
|                    |  - Entity Mapping (Account, IP, Host)  |                           |
|                    +-------------------+--------------------+                           |
|                                        |                                                |
|                                        v (Trigger on Incident Creation)                 |
|                    +----------------------------------------+                           |
|                    |       Sentinel Automation Rules        |                           |
|                    +-------------------+--------------------+                           |
|                                        |                                                |
|                                        v                                                |
|                    +----------------------------------------+                           |
|                    |      Azure Logic Apps SOAR Playbook    |                           |
|                    |  1. Geolocation lookup for Attacker IP |                           |
|                    |  2. Calculate User Risk Score via Entra|                           |
|                    |  3. Post Adaptive Card to Teams / Slack|                           |
|                    |  4. Optional: Revoke User Sessions     |                           |
|                    +----------------------------------------+                           |
+-----------------------------------------------------------------------------------------+
""",
        "tech_stack": [
            "Microsoft Sentinel",
            "Azure Log Analytics Workspace",
            "Kusto Query Language (KQL)",
            "Azure Logic Apps (SOAR)",
            "Microsoft Entra ID (AuditLogs & SigninLogs)",
            "ARM / Bicep Infrastructure-as-Code"
        ],
        "step_by_step": [
            {
                "step": "1. Infrastructure Provisioning",
                "details": "Create a Log Analytics Workspace with 90 days retention. Enable Microsoft Sentinel on the workspace using Bicep or Azure CLI."
            },
            {
                "step": "2. Data Connector Onboarding",
                "details": "Connect Microsoft Entra ID (SignInLogs, NonInteractiveUserSignInLogs, and AuditLogs) and Azure Activity logs to stream real-time events."
            },
            {
                "step": "3. KQL Detection Rule Development",
                "details": "Author a scheduled query rule that detects multiple authentication failures followed by a successful sign-in from the same IP within a 15-minute sliding window."
            },
            {
                "step": "4. Alert Enrichment & Incident Grouping",
                "details": "Map alert entities to Account (UserPrincipalName) and IP (IPAddress). Group multiple matching alerts within 5 hours into a single incident to avoid alert fatigue."
            },
            {
                "step": "5. Logic App Playbook Orchestration",
                "details": "Create an Azure Logic App triggered by a Microsoft Sentinel incident creation. The playbook enriches the incident with IP Whois data and posts an interactive Teams adaptive card."
            }
        ],
        "kql_snippet": """// Detection: Multiple Failed Sign-ins followed by a Success within 15 mins
let timeframe = 1d;
let threshold = 5;
SigninLogs
| where TimeGenerated >= ago(timeframe)
| where ResultType != "0" // Failed login
| summarize FailureCount = count(), 
            FirstFailure = min(TimeGenerated), 
            LastFailure = max(TimeGenerated) 
            by IPAddress, UserPrincipalName
| where FailureCount >= threshold
| join kind=inner (
    SigninLogs
    | where TimeGenerated >= ago(timeframe)
    | where ResultType == "0" // Successful login
    | project SuccessTime = TimeGenerated, IPAddress, UserPrincipalName, AppDisplayName, Location
) on IPAddress, UserPrincipalName
| where SuccessTime > LastFailure and SuccessTime <= LastFailure + 15m
| project SuccessTime, UserPrincipalName, IPAddress, FailureCount, AppDisplayName, Location""",
        "interviewer_pitch": "In this project, I demonstrated cloud security monitoring by standing up Microsoft Sentinel, ingesting Entra ID telemetry, and writing custom KQL detection rules mapped to MITRE ATT&CK T1110 (Brute Force). Instead of stopping at alerts, I connected Sentinel to Azure Logic Apps to automate incident triage—enriching the alert with IP intelligence and alerting SOC responders in real-time."
    },
    {
        "id": "project-2",
        "title": "Project 2: Secure Azure Enterprise Application Architecture",
        "subtitle": "Web API + Managed Identity + Azure Key Vault + Private Endpoints + Secure CI/CD",
        "category": "Cloud Security Architecture & DevSecOps",
        "badge": "Core Portfolio 2",
        "summary": "Architect and deploy an enterprise-grade, Zero Trust web application in Azure. All PaaS services (Azure SQL, Azure Storage, Key Vault) are isolated from the public internet using Azure Private Link. Authentication is strictly passwordless via Entra ID User-Assigned Managed Identity, and deployment pipelines incorporate automated security scanning.",
        "architecture_diagram": """
+-----------------------------------------------------------------------------------------+
|                                    AZURE SECURE VNET                                    |
|                                                                                         |
|  [ Internet ] ---> [ Azure Front Door / Application Gateway WAF (CRS 3.2) ]             |
|                                        | (Encrypted TLS 1.3)                            |
|                                        v                                                |
|                      +-----------------------------------+                              |
|                      |        App Service Subnet         |                              |
|                      |  Azure App Service / Azure Func   |                              |
|                      |  - Managed Identity Assigned      |                              |
|                      |  - Regional VNet Integration      |                              |
|                      +-----------------+-----------------+                              |
|                                        |                                                |
|                                        | (VNet Internal Routing via Private DNS)        |
|                                        v                                                |
|                      +-----------------------------------+                              |
|                      |      Private Endpoints Subnet     |                              |
|                      |                                   |                              |
|                      |  [Private Endpoint: Key Vault]    | <--- Managed Identity RBAC   |
|                      |  [Private Endpoint: Azure SQL]    | <--- Microsoft Entra Auth    |
|                      |  [Private Endpoint: Blob Storage] | <--- Storage Blob Contributor|
|                      +-----------------------------------+                              |
|                                                                                         |
|  [ Azure DevOps / GitHub Actions ]                                                      |
|       |                                                                                 |
|       v (OIDC Workload Identity Federation - No Static Secrets)                         |
|  [ Trivy / Microsoft Security DevOps Linter ] ---> [ Deploy Bicep & Artifacts ]         |
+-----------------------------------------------------------------------------------------+
""",
        "tech_stack": [
            "Azure App Service / Azure Functions",
            "Azure Key Vault (RBAC model)",
            "Azure SQL Database with Entra-only authentication",
            "Azure Private Endpoints & Private DNS Zones",
            "Azure Application Gateway with WAF",
            "GitHub Actions / Azure DevOps with OIDC Federation"
        ],
        "step_by_step": [
            {
                "step": "1. Zero Trust Network Partitioning",
                "details": "Create an Azure Virtual Network with dedicated subnets: AppSubnet (delegated to Microsoft.Web/serverFarms) and PrivateEndpointSubnet."
            },
            {
                "step": "2. Deploying PaaS with Public Access Disabled",
                "details": "Deploy Azure Key Vault, Azure SQL, and Azure Storage with publicNetworkAccess set to 'Disabled'."
            },
            {
                "step": "3. Private Link & Private DNS Integration",
                "details": "Provision Private Endpoints for each resource and link to respective Private DNS Zones (privatelink.vaultcore.azure.net, privatelink.database.windows.net)."
            },
            {
                "step": "4. Identity-Based Zero Secrets Access",
                "details": "Configure a User-Assigned Managed Identity on the App Service. Grant 'Key Vault Secrets User' and configure Azure SQL Contained Database User linked to the Managed Identity."
            },
            {
                "step": "5. Secure CI/CD with OIDC",
                "details": "Configure GitHub Actions / Azure DevOps using Entra ID Workload Identity Federation (OIDC) to deploy code without storing credentials in repository secrets."
            }
        ],
        "kql_snippet": """// Audit: Identify any Storage Account or Key Vault that has Public Network Access Enabled
AzureResources
| where type in ("microsoft.storage/storageaccounts", "microsoft.keyvault/vaults")
| extend PublicAccess = properties.publicNetworkAccess
| where PublicAccess != "Disabled"
| project ResourceName = name, ResourceType = type, ResourceGroup = resourceGroup, PublicAccess, Location = location""",
        "interviewer_pitch": "My background in cloud engineering and .NET migrations allowed me to design this reference architecture. I completely eradicated hardcoded secrets by leveraging Managed Identities and Entra ID authentication end-to-end. PaaS resources are zero-trust isolated behind Private Endpoints, and CI/CD pipelines authenticate seamlessly via OIDC federation."
    },
    {
        "id": "project-3",
        "title": "Project 3: Enterprise AI Cybersecurity Assistant (Permission-Aware RAG)",
        "subtitle": "Azure OpenAI + Azure AI Search (Hybrid + Reranking) + Prompt Shields + Security Trimming",
        "category": "AI Engineering & AI Security",
        "badge": "Core Portfolio 3",
        "summary": "Develop a production-grade, secure AI assistant that triages cybersecurity alerts and queries enterprise security knowledge bases. Integrates Azure AI Content Safety Prompt Shields to prevent direct and indirect prompt injection, and enforces Permission-Aware RAG to ensure users only access security data they are authorized to view.",
        "architecture_diagram": """
+-----------------------------------------------------------------------------------------+
|                        SECURE AI CYBERSECURITY ASSISTANT PIPELINE                       |
|                                                                                         |
|  [ User / SOC Analyst ]                                                                 |
|         |                                                                               |
|         v (Query + Entra ID JWT Token)                                                  |
|  +-----------------------------------------------------------------------------------+  |
|  | Fast API / Python Orchestrator Service                                            |  |
|  |                                                                                   |  |
|  |  Step 1: Input Guardrail Layer                                                    |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |  | Azure AI Content Safety API: Prompt Shield (Detects Jailbreak & Injection)    |  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |                                                                                   |  |
|  |  Step 2: Permission-Aware Retrieval                                               |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |  | Azure AI Search:                                                            |  |  |
|  |  | - Hybrid Search: text-embedding-3-small + BM25 keyword                      |  |  |
|  |  | - Semantic Reranking                                                        |  |  |
|  |  | - OData Security Filter: security_principals/any(p: p in user_token_groups)   |  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |                                                                                   |  |
|  |  Step 3: Grounded LLM Generation                                                  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |  | Azure OpenAI (GPT-4o) via Private Endpoint                                  |  |  |
|  |  | System Prompt: Strict citation required; reject out-of-context instructions    |  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |                                                                                   |  |
|  |  Step 4: Output Guardrail Layer                                                   |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  |  | PII Masking & Groundedness Verification                                      |  |  |
|  |  +-----------------------------------------------------------------------------+  |  |
|  +-----------------------------------------------------------------------------------+  |
|         |                                                                               |
|         v (Safe, Verified, Grounded Response with Citations)                            |
|  [ Analyst Response & Remediation Plan ]                                                |
+-----------------------------------------------------------------------------------------+
""",
        "tech_stack": [
            "Azure OpenAI Service (GPT-4o)",
            "Azure AI Search (Hybrid + Semantic Ranker)",
            "Azure AI Content Safety (Prompt Shields)",
            "Python 3.12 (LangChain / Semantic Kernel)",
            "Entra ID Security Token Group Trimming",
            "Azure Private Link"
        ],
        "step_by_step": [
            {
                "step": "1. Vector Ingestion Pipeline with Security Metadata",
                "details": "Chunk enterprise security runbooks and CVE advisories. Store chunks in Azure AI Search with metadata fields: id, content, vector, and allowed_security_groups."
            },
            {
                "step": "2. Prompt Shield Pre-Flight Inspection",
                "details": "Before submitting any query to the LLM, pass the user input to Azure AI Content Safety Prompt Shield API to detect adversarial attacks and jailbreak attempts."
            },
            {
                "step": "3. Permission-Aware Hybrid Retrieval",
                "details": "Extract the caller's Entra ID group claims from their bearer token. Pass an OData filter to Azure AI Search ensuring only chunks matching their group access are retrieved."
            },
            {
                "step": "4. Grounded Prompt Formulation",
                "details": "Format the retrieved chunks with strict XML delimiters (<context></context>) and mandate that GPT-4o only answer using the provided context, citing chunk IDs."
            },
            {
                "step": "5. Output Sanitization & Logging",
                "details": "Verify output against PII regex patterns and Azure AI Content Safety Groundedness detector. Log all interactions and prompt evaluations to Log Analytics for security auditing."
            }
        ],
        "kql_snippet": """// Audit AI Service Invocations and Content Safety Blocks
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where OperationName contains "PromptShield" or OperationName contains "ContentSafety"
| extend BlockReason = tostring(parse_json(properties_s).action)
| summarize BlockCount = count() by BlockReason, bin(TimeGenerated, 1h)
| render timechart""",
        "interviewer_pitch": "AI in enterprise security is only viable if it is defended against prompt injection and respects data boundaries. In this project, I built a Permission-Aware RAG assistant. Even if a user asks for executive incident logs, the OData security filter enforces document-level permissions before embeddings are retrieved. Furthermore, Azure AI Prompt Shields neutralize prompt injection attacks at the perimeter."
    }
]

def get_project_by_id(project_id: str):
    for p in PROJECTS:
        if p["id"] == project_id:
            return p
    return None
