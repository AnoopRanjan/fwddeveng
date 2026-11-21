# 🚀 Forward Deployed Engineer (FDE) + AI + Cybersecurity Advisor Portal

A full-stack, local Python web application built to transform a **Cloud Technical Lead** (Azure, .NET, cloud migrations, integrations, automation) into a high-impact **Forward Deployed Engineer (FDE)** and **Part-Time Technical Advisor / Cloud, AI & Security Consultant**.

---

## ⚡ How to Run (No Batch File Needed!)

### Option A: Run Locally
Run directly with standard Python from this directory:

```bash
python app.py
```

Then open your browser at:
👉 **[http://localhost:5000](http://localhost:5000)**

*(No batch file, no Docker, and no Node.js/npm required! Everything runs on standard Python 3 with Flask and SQLite).*

---

### Option B: Deploy Instantly to Vercel (Zero-Config Serverless)

This repository is pre-configured for instant deployment on **Vercel** with `@vercel/python`:

#### Method 1: Using the Vercel Dashboard (GitHub / GitLab / Bitbucket)
1. Push this project folder to your GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of FDE learning portal"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```
2. Log into [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Import your GitHub repository.
4. Leave all build settings as default (Framework Preset: **Other**, Root Directory: `./`).
5. Click **"Deploy"**. Vercel will install dependencies from `requirements.txt` and launch your live URL in under 60 seconds!

#### Method 2: Using the Vercel CLI
From this directory, simply run:
```bash
vercel
```
(Follow the prompts: accept defaults, and Vercel will build and deploy instantly).

> **Note on Vercel Architecture**: Serverless environments have a read-only root filesystem. The application automatically detects Vercel (`VERCEL=1`), directs SQLite database operations to the writable `/tmp` directory, and syncs user progress via browser `localStorage` so checkmarks and notes persist seamlessly across serverless container recycles.

---

## 🎯 The 10 Core Focus Areas (Fully Covered)

Each topic includes official **Microsoft Learn / MSDN documentation paths**, **embedded YouTube course playlists**, **key architectural concepts**, **FDE client advisory angles**, **hands-on lab exercises**, and **interview practice Q&A**:

1. **Azure Cloud Security**: Secure enterprise cloud architecture, Landing Zones, Cloud Adoption Framework (CAF), Azure Policy, RBAC, Key Vault with Purge Protection. *(AZ-500, AZ-305, SC-100)*
2. **Microsoft Sentinel**: Cloud-native SIEM/SOAR, Log Analytics Workspace design, KQL detection rules, alert grouping, and automated Logic Apps playbooks. *(SC-200, AZ-500)*
3. **Microsoft Defender for Cloud**: Cloud Security Posture Management (CSPM), Secure Score engine, CIS / NIST SP 800-53 compliance, CWPP for Servers/Storage, and JIT VM Access. *(SC-200, AZ-500)*
4. **Entra ID Security**: Modern Auth (OAuth 2.0 / OIDC), Conditional Access policy engine, Zero Trust Identity, Privileged Identity Management (PIM), and Workload Identities. *(SC-300, AZ-500)*
5. **Network Security & Zero Trust**: Hub-and-Spoke topology, NSGs, Application Security Groups, Azure Firewall Premium (IDPS/TLS inspection), WAF (OWASP CRS), and Private Endpoints. *(AZ-500, AZ-700)*
6. **Incident Response & Forensics**: NIST SP 800-61 / SANS 4-stage IR lifecycle, cloud identity lockdown (`Revoke-AzureADUserAllRefreshToken`), VM network quarantine, disk snapshots, and Root Cause Analysis (RCA). *(SC-200, SC-100)*
7. **Vulnerability Management**: CVE / CVSS v3.1 & v4.0 metrics, Exploit Prediction Scoring System (EPSS), Microsoft Defender Vulnerability Management (MDVM), and automated patching with Azure Update Manager. *(SC-200, AZ-500)*
8. **AI Security & OWASP LLM Top 10**: Direct & Indirect Prompt Injection, System Prompt extraction, Azure AI Content Safety Prompt Shields, private AI endpoints, and Permission-Aware RAG. *(AI-102, SC-100)*
9. **AI Engineering & Enterprise RAG**: Azure AI Search (Hybrid Search + Semantic Reranking), text-embedding-3 models, chunking strategies, Semantic Kernel / LangChain, and Agentic Tool Calling. *(AI-102, AZ-305)*
10. **Forward Deployed Engineering (FDE) Methodology**: Root-cause customer discovery, rapid prototyping, enterprise legacy integrations, Architecture Review Boards (ARB), and executive advisory communication. *(AZ-305, SC-100)*

---

## 📅 The 35-Day Structured Transformation Roadmap

Organized into 5 distinct 7-day phases:

| Phase | Days | Focus Area | Major Milestone |
|---|---|---|---|
| **Phase 1** | Days 1–7 | **Enterprise Cloud Architecture & Identity Foundations** | Deploy Hardened Enterprise Landing Zone Review |
| **Phase 2** | Days 8–14 | **Posture Management, Workload Protection & Vulnerability Mgmt** | Cloud Posture & Vulnerability Audit Report |
| **Phase 3** | Days 15–21 | **SIEM, SOAR, KQL & Threat Detection Engineering** | **Portfolio Project 1**: Microsoft Sentinel Detection & SOAR Playbook |
| **Phase 4** | Days 22–28 | **Incident Response & Enterprise AI Engineering** | **Portfolio Project 2**: Secure Enterprise Application Architecture |
| **Phase 5** | Days 29–35 | **AI Security, FDE Advisory & Executive Pitch Mastery** | **Portfolio Project 3**: AI Cybersecurity Triage Assistant & Full Mock Interview |

Each day is split into:
- 🌅 **Morning (~60m)**: Theory, official MSDN reading, and embedded YouTube video playlist study.
- 💻 **Afternoon (~60m)**: Hands-on implementation lab (Azure CLI, PowerShell, Bicep, or Portal configuration).
- 🗣️ **Evening (~30m)**: Client advisory scenario & interview rehearsal.

---

## 🛠️ Built-in Features

- **Dynamic Progress Tracker**: One-click checkbox for each day and status dropdown for each topic, persisted in a local SQLite database (`learning_portal.db`).
- **Interactive KQL Workbench**: Browse production-tested KQL queries, read detection mechanics, copy queries, and run live simulated executions against mock Log Analytics datasets.
- **3 Portfolio Project Blueprints**: Comprehensive architecture diagrams (ASCII), tech stacks, step-by-step checklists, audit KQL queries, and interview elevator pitches for:
  1. *Enterprise Cloud Security Monitoring & Automated SOAR (Sentinel + Logic Apps)*
  2. *Secure Azure Enterprise Application Architecture (Zero Trust Private Link + Key Vault + OIDC)*
  3. *Enterprise AI Cybersecurity Assistant (Permission-Aware RAG + Content Safety Prompt Shields)*
- **Interview Studio & Pitch Pack**:
  - Verbatim 60-second executive pitch script tailored to your Cloud Lead background.
  - Strategic positioning cheat-sheet (what to own vs. what to avoid).
  - Humorous & professional tip for handling the JD's **"1222 years of experience"** typo.
  - 20 deep interview questions with model answers and key takeaways.
- **Personal Learning Journal**: Add and persist study reflections, lab notes, and key commands.

---

## 📂 Project Architecture

```
c:\Games\Interview\FDE\
├── app.py                  # Main Flask application & SQLite database layer
├── learning_portal.db      # SQLite database for progress and notes persistence
├── data/
│   ├── topics.py           # 10 Topics: MSDN, YouTube embeds, labs, concepts, Q&A
│   ├── roadmap.py          # 35-Day curriculum with phases, daily tasks & milestones
│   ├── projects.py         # 3 Portfolio project blueprints & architecture diagrams
│   ├── kql_queries.py      # Production KQL queries, explanations, and mock log data
│   └── interview_prep.py   # Pitch script, positioning strategy & 20 interview Q&A
├── templates/
│   ├── base.html           # Dark cyber-aesthetic layout, navigation & live progress bar
│   ├── index.html          # Executive dashboard, mission of the day, curriculum phases
│   ├── roadmap.html        # Interactive 35-day roadmap with filters and notes
│   ├── day_detail.html     # Dedicated daily study guide (Morning/Afternoon/Evening)
│   ├── topics_list.html    # 10 Core Focus Areas with status selector & exam tags
│   ├── topic_detail.html   # Subject deep-dive with video player, MSDN links, & labs
│   ├── kql_lab.html        # Interactive KQL Workbench & log execution simulator
│   ├── projects.html       # Portfolio blueprints with ASCII architecture diagrams
│   ├── interview.html      # 20 Interview questions & executive pitch studio
│   └── notes.html          # Learning journal & reflection notebook
├── static/
│   ├── css/custom.css      # Dark theme styling, glow accents & animations
│   └── js/main.js          # AJAX progress toggles, KQL simulator, toast alerts
└── README.md               # User guide & operational documentation
```
