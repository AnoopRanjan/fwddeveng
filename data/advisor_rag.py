"""
RAG + Gemini LLM Virtual Advisor Engine for Forward Deployed Engineer + AI + Cybersecurity Advisor.

Indexes all portal domain modules (Topics, Roadmap, Projects, Interview Prep, KQL, FDE Masterclass)
plus curated FDE/AI/Cybersecurity concise knowledge entries. Uses TF-IDF cosine retrieval (RAG)
paired with Google Gemini LLM (via REST API when GEMINI_API_KEY / GOOGLE_API_KEY is configured)
and an automatic concise RAG extractive fallback when offline or unconfigured.
"""

import json
import math
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter


def _load_local_env():
    """Lightweight .env loader (no extra dependency) for local GEMINI_API_KEY / GOOGLE_CSE_* config."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8") as fh:
            for raw_line in fh:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass


_load_local_env()

from data.fde_masterclass import FDE_BRIEFING_10MIN, FDE_MASTER_COURSE, PROJECT_EXPLORATION_PILLARS
from data.interview_prep import ELEVATOR_PITCH, INTERVIEW_QUESTIONS, POSITIONING_STRATEGY
from data.kql_queries import KQL_QUERIES
from data.projects import PROJECTS
from data.roadmap import ROADMAP_DAYS
from data.topics import TOPICS

OUT_OF_SCOPE_MESSAGE = (
    "Out of scope: I only answer questions related to Forward Deployed Engineering (FDE), "
    "AI engineering/security, and Cybersecurity Advisory. How can I help you on those topics?"
)

GREETING_MESSAGE = (
    "Hello! I'm your virtual FDE + AI + Cybersecurity Advisor sitting at the company helpdesk. "
    "How can I help you?"
)

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "can", "could", "do", "does",
    "for", "from", "had", "has", "have", "how", "i", "in", "is", "it", "its", "may", "me",
    "my", "of", "on", "or", "our", "should", "so", "that", "the", "their", "them", "there",
    "these", "they", "this", "to", "us", "was", "we", "were", "what", "when", "where",
    "which", "who", "why", "will", "with", "would", "you", "your", "about", "into", "tell",
    "explain", "define", "describe", "please", "give", "short", "brief", "small", "smallest"
}

SYNONYMS = {
    "fde": ["forward", "deployed", "engineer", "engineering", "field"],
    "rag": ["retrieval", "augmented", "generation", "vector", "grounding"],
    "llm": ["large", "language", "model", "gemini", "gpt", "openai"],
    "genai": ["generative", "ai", "llm"],
    "ai": ["artificial", "intelligence", "genai", "llm", "ml"],
    "ml": ["machine", "learning", "mlnet"],
    "kql": ["kusto", "query", "language", "sentinel", "logs"],
    "siem": ["sentinel", "logging", "detection", "soc"],
    "soar": ["automation", "playbook", "logic", "apps", "response"],
    "soc": ["security", "operations", "analyst", "siem"],
    "iam": ["identity", "access", "entra", "rbac", "pim", "mfa"],
    "entra": ["identity", "aad", "oauth", "oidc", "conditional"],
    "pim": ["privileged", "identity", "jit", "eligible"],
    "rbac": ["role", "based", "access", "control", "policy"],
    "zero": ["trust", "verify", "explicitly", "least", "privilege"],
    "ciso": ["executive", "advisor", "governance", "risk"],
    "poc": ["prototype", "prototyping", "48-hour", "mvp"],
    "owasp": ["prompt", "injection", "llm", "top10", "vulnerability"],
    "cve": ["vulnerability", "epss", "kev", "patch", "defender"],
    "devsecops": ["cicd", "pipeline", "shift", "left", "oidc", "sast"],
    "vnet": ["network", "hub", "spoke", "nsg", "private", "endpoint"],
    "kv": ["key", "vault", "secrets", "cmk", "encryption"],
}

# Domain and closely-related technical/advisory terms for strict scope gating
DOMAIN_TERMS = {
    "fde", "forward", "deployed", "engineer", "engineering", "advisor", "advisory",
    "consulting", "consultant", "client", "stakeholder", "ciso", "cto", "arb",
    "prototype", "prototyping", "poc", "mvp", "enablement", "workshop", "legacy",
    "enterprise", "architecture", "architect", "transformation", "roadmap", "portal",
    "interview", "pitch", "outreach", "course", "topic", "project", "learning",
    "ai", "genai", "generative", "llm", "llms", "rag", "gemini", "openai", "gpt",
    "copilot", "claude", "agent", "agents", "agentic", "semantic", "kernel", "ml",
    "mlnet", "machine", "embedding", "embeddings", "vector", "vectors", "rerank",
    "reranking", "hybrid", "hallucination", "hallucinations", "grounding", "groundedness",
    "prompt", "prompts", "injection", "jailbreak", "guardrail", "guardrails", "token",
    "tokens", "fine-tuning", "finetuning", "finetune", "model", "models", "neural",
    "cyber", "cybersecurity", "security", "secure", "secops", "soc", "siem", "soar",
    "kql", "kusto", "sentinel", "defender", "posture", "score", "threat", "threats",
    "hunting", "hunt", "alert", "alerts", "incident", "containment", "forensics",
    "ransomware", "malware", "phishing", "bruteforce", "brute", "credential", "password",
    "zero", "trust", "ztna", "iam", "identity", "entra", "aad", "oauth", "oidc", "saml",
    "mfa", "sso", "conditional", "pim", "jit", "rbac", "abac", "privilege", "privileged",
    "least", "encryption", "encrypt", "decrypt", "kms", "cmk", "keyvault", "vault",
    "secret", "secrets", "certificate", "tls", "ssl", "hmac", "pbkdf2", "hash",
    "network", "networking", "vnet", "subnet", "nsg", "asg", "firewall", "bastion",
    "peering", "udr", "private", "endpoint", "link", "dns", "hub", "spoke", "vpn",
    "expressroute", "waf", "ddos", "exfiltration", "quarantine", "isolation",
    "vulnerability", "vulnerabilities", "cve", "cvss", "epss", "kev", "cisa", "patch",
    "patching", "owasp", "nist", "cis", "compliance", "governance", "audit", "policy",
    "caf", "landing", "zone", "zones", "bicep", "terraform", "iac", "arm",
    "devsecops", "devops", "cicd", "pipeline", "sast", "dast", "sca", "trivy",
    "container", "docker", "kubernetes", "aks", "serverless", "function", "functions",
    "logic", "servicebus", "microservices", "api", "apis", "rest", "webhook", "cloud",
    "azure", "aws", "gcp", "iaas", "paas", "saas", "vm", "vms", "storage", "sql",
    "log", "logs", "analytics", "monitor", "monitoring", "telemetry", "mitre", "attck",
    "dotnet", "csharp", "python", "flask", "managed", "workload", "federation",
    "playbook", "playbooks", "impossible", "travel", "signinlogs", "auditlogs",
}

GREETING_PATTERNS = {
    "hi", "hello", "hey", "hii", "helo", "greetings", "good morning",
    "good afternoon", "good evening", "howdy", "yo", "sup", "who are you",
    "what are you", "what can you do", "how can you help", "help", "start"
}

CURATED_ADVISOR_KNOWLEDGE = [
    {
        "title": "Forward Deployed Engineer (FDE) Role",
        "category": "FDE",
        "text": (
            "A Forward Deployed Engineer (FDE) embeds directly with enterprise clients to diagnose "
            "root operational bottlenecks, build rapid proofs of concept (often within 48 hours), "
            "and ship secure, production-grade cloud, AI, and integration solutions."
        ),
    },
    {
        "title": "FDE + AI + Cybersecurity Advisor Value",
        "category": "Advisory",
        "text": (
            "An FDE + AI + Cybersecurity Advisor bridges software engineering, generative AI, and "
            "security architecture—helping clients design Zero Trust cloud landing zones, permission-aware "
            "RAG pipelines, automated Sentinel detections, and practical risk-reduction roadmaps."
        ),
    },
    {
        "title": "Retrieval-Augmented Generation (RAG) & Gemini",
        "category": "AI Engineering",
        "text": (
            "RAG combines vector/keyword retrieval from trusted enterprise documents with an LLM like "
            "Gemini so answers stay grounded in verified company knowledge, include source context, "
            "and dramatically reduce hallucinations without expensive model retraining."
        ),
    },
    {
        "title": "Fine-Tuning vs RAG in Enterprise AI",
        "category": "AI Engineering",
        "text": (
            "RAG retrieves live, permission-trimmed corporate context at query time with instant updates "
            "and citations, whereas fine-tuning modifies model weights for tone or format. Enterprises "
            "prefer RAG for factual knowledge retrieval and access control."
        ),
    },
    {
        "title": "AI Security & OWASP LLM Top 10",
        "category": "AI Security",
        "text": (
            "Key enterprise LLM risks include direct/indirect prompt injection, sensitive data disclosure, "
            "and excessive agency. Mitigate them using Prompt Shields, strict system delimiters, "
            "permission-aware RAG filtering by Entra ID, and Private Endpoints."
        ),
    },
    {
        "title": "Zero Trust Architecture",
        "category": "Cybersecurity",
        "text": (
            "Zero Trust follows three core principles: Verify Explicitly, Use Least Privilege Access, "
            "and Assume Breach. In Azure, this means Entra ID Conditional Access, PIM just-in-time admin "
            "access, Managed Identities, and Private Endpoints eliminating public IPs."
        ),
    },
    {
        "title": "Microsoft Sentinel & KQL",
        "category": "SIEM & SOC",
        "text": (
            "Microsoft Sentinel is a cloud-native SIEM/SOAR platform built on Log Analytics. Engineers "
            "use Kusto Query Language (KQL) with pipe operators to correlate SigninLogs and AuditLogs, "
            "and trigger Azure Logic Apps playbooks for automated threat containment."
        ),
    },
    {
        "title": "Managed Identities vs Hardcoded Secrets",
        "category": "Cloud Security",
        "text": (
            "Managed Identities eliminate hardcoded passwords and connection strings in code by issuing "
            "automatic Entra ID tokens to Azure compute services, paired with Azure Key Vault RBAC "
            "and Private Endpoints."
        ),
    },
    {
        "title": "Incident Response Containment in Cloud",
        "category": "Incident Response",
        "text": (
            "During an active cloud compromise, revoke Entra refresh tokens immediately, reverse unauthorized "
            "role assignments in AuditLogs, and isolate compromised VMs via quarantine NSGs plus disk "
            "snapshots instead of rebooting—preserving volatile RAM forensics."
        ),
    },
    {
        "title": "DevSecOps Shift-Left Guardrails",
        "category": "DevSecOps",
        "text": (
            "DevSecOps embeds automated secret scanning, SAST, dependency checks (SCA), container CVE "
            "scanning, and passwordless OIDC workload identity federation directly into CI/CD pipelines "
            "to catch risks before production."
        ),
    },
    {
        "title": "Docker, Containers & Microservice Security",
        "category": "Cloud & DevSecOps",
        "text": (
            "In FDE cloud delivery, Docker packages .NET or Python AI microservices consistently across "
            "environments. Security advisors harden containers using minimal base images, Trivy/Defender "
            "CVE scanning, non-root users, and Azure Key Vault / Managed Identities."
        ),
    },
    {
        "title": "FDE 48-Hour Field Prototyping & Legacy Integration",
        "category": "FDE",
        "text": (
            "In the field, FDEs connect legacy on-prem SQL, ERP, or SOAP systems to modern cloud AI "
            "and security pipelines using isolated IaC sandboxes (Bicep/Terraform), event-driven Azure "
            "Functions/Service Bus, and hybrid Private Link networking."
        ),
    },
    {
        "title": "Portal Curriculum & 35-Day Roadmap",
        "category": "Portal",
        "text": (
            "This portal provides a 35-day transformation roadmap across 5 phases, 10 core Microsoft "
            "cloud/AI/security topics (AZ-500, SC-200, SC-300, AI-102, AZ-305, SC-100), a live KQL lab, "
            "3 portfolio projects, and 20 FDE interview scenarios."
        ),
    },
]


def _tokenize(text: str, expand_synonyms: bool = False) -> list[str]:
    if not text:
        return []
    raw_tokens = re.findall(r"[a-z0-9][a-z0-9\-\./+#]*", text.lower())
    tokens: list[str] = []
    for tok in raw_tokens:
        clean = tok.strip(".-/")
        if not clean or len(clean) < 2 and clean not in {"c", "r"}:
            continue
        if clean in STOPWORDS:
            continue
        tokens.append(clean)
        # Split compound tokens like c#/ci-cd/az-500
        if any(sep in clean for sep in ("-", "/", ".")):
            for part in re.split(r"[-/.]", clean):
                if len(part) >= 2 and part not in STOPWORDS:
                    tokens.append(part)
        if expand_synonyms and clean in SYNONYMS:
            tokens.extend(SYNONYMS[clean])
    return tokens


def _truncate_concise(text: str, max_sentences: int = 3, max_chars: int = 320) -> str:
    """Extracts the smallest clear description (2-3 crisp sentences)."""
    cleaned = re.sub(r"\s+", " ", (text or "").strip())
    if not cleaned:
        return ""
    # Split on sentence boundaries while avoiding breaking abbreviations like e.g.
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", cleaned)
    selected = []
    total_len = 0
    for sent in sentences[:max_sentences]:
        sent = sent.strip()
        if not sent:
            continue
        if total_len + len(sent) > max_chars and selected:
            break
        selected.append(sent)
        total_len += len(sent) + 1
    result = " ".join(selected).strip()
    if not result:
        result = cleaned[:max_chars].rsplit(" ", 1)[0] + "..."
    elif len(result) > max_chars:
        result = result[: max_chars - 3].rsplit(" ", 1)[0] + "..."
    return result


class AdvisorRAGEngine:
    """In-memory TF-IDF RAG retriever + Gemini LLM / fallback concise synthesizer."""

    def __init__(self):
        self.documents: list[dict] = []
        self.idf: dict[str, float] = {}
        self.doc_vectors: list[dict[str, float]] = []
        self._build_index()

    def _add_doc(self, title: str, category: str, text: str):
        clean_text = re.sub(r"\s+", " ", (text or "").strip())
        if not clean_text:
            return
        self.documents.append({
            "id": len(self.documents),
            "title": title.strip(),
            "category": category.strip(),
            "text": clean_text,
        })

    def _build_index(self):
        for entry in CURATED_ADVISOR_KNOWLEDGE:
            self._add_doc(entry["title"], entry["category"], entry["text"])

        # Index 10 Core Topics
        for topic in TOPICS:
            concepts = "; ".join(topic.get("core_concepts", [])[:4])
            self._add_doc(
                f"{topic.get('title', '')} ({', '.join(topic.get('exams', []))})",
                topic.get("category", "Topic"),
                f"{topic.get('subtitle', '')}. {topic.get('fde_perspective', '')} Core concepts: {concepts}.",
            )
            for qa in topic.get("interview_qa", []):
                self._add_doc(
                    f"{topic.get('title', '')}: {qa.get('q', '')}",
                    "Topic Q&A",
                    qa.get("a", ""),
                )

        # Index 35-Day Roadmap
        for day in ROADMAP_DAYS:
            self._add_doc(
                f"Day {day.get('day')}: {day.get('title', '')}",
                day.get("phase_title", "Roadmap"),
                f"{day.get('objective', '')} Tasks: {day.get('morning_task', '')} {day.get('evening_task', '')}",
            )

        # Index 3 Portfolio Projects
        for proj in PROJECTS:
            stack = ", ".join(proj.get("tech_stack", []))
            self._add_doc(
                proj.get("title", "Portfolio Project"),
                proj.get("category", "Project"),
                f"{proj.get('summary', '')} Stack: {stack}.",
            )

        # Index Interview Prep
        self._add_doc(
            "FDE Advisory Positioning & Elevator Pitch",
            "Interview Strategy",
            f"{POSITIONING_STRATEGY.get('value_proposition', '')} {POSITIONING_STRATEGY.get('what_to_own', '')}",
        )
        for q in INTERVIEW_QUESTIONS:
            self._add_doc(
                f"Interview ({q.get('category', '')}): {q.get('question', '')}",
                q.get("category", "Interview"),
                q.get("model_answer", ""),
            )

        # Index KQL Queries
        for kql in KQL_QUERIES:
            self._add_doc(
                f"KQL: {kql.get('title', '')}",
                "KQL & Sentinel",
                f"{kql.get('description', '')} {kql.get('explanation', '')}",
            )

        # Index FDE Masterclass & Pillars
        for stage in FDE_MASTER_COURSE.get("core_stages", []):
            self._add_doc(
                f"FDE Stage {stage.get('stage')}: {stage.get('name', '')}",
                "FDE Masterclass",
                stage.get("summary", ""),
            )
        for pillar in PROJECT_EXPLORATION_PILLARS:
            self._add_doc(
                pillar.get("title", "FDE Pillar"),
                "FDE Exploration",
                f"{pillar.get('desc', '')} {pillar.get('outcome', '')}",
            )
        self._add_doc(
            FDE_BRIEFING_10MIN.get("title", "C# & .NET 101"),
            "FDE Briefing",
            FDE_BRIEFING_10MIN.get("summary", ""),
        )

        # Build TF-IDF vectors
        n_docs = len(self.documents)
        df: Counter[str] = Counter()
        tokenized_docs: list[list[str]] = []

        for doc in self.documents:
            # Weight title tokens higher by repeating title tokens twice
            tokens = _tokenize(doc["title"], expand_synonyms=True) * 2 + _tokenize(doc["text"])
            tokenized_docs.append(tokens)
            for term in set(tokens):
                df[term] += 1

        self.idf = {
            term: math.log((n_docs + 1) / (freq + 1)) + 1.0
            for term, freq in df.items()
        }

        self.doc_vectors = []
        for tokens in tokenized_docs:
            tf = Counter(tokens)
            vec: dict[str, float] = {}
            norm_sq = 0.0
            for term, count in tf.items():
                w = (1.0 + math.log(count)) * self.idf.get(term, 1.0)
                vec[term] = w
                norm_sq += w * w
            norm = math.sqrt(norm_sq) or 1.0
            for term in vec:
                vec[term] /= norm
            self.doc_vectors.append(vec)

    def retrieve(self, query: str, top_k: int = 4) -> list[dict]:
        q_tokens = _tokenize(query, expand_synonyms=True)
        if not q_tokens:
            return []

        q_tf = Counter(q_tokens)
        q_vec: dict[str, float] = {}
        q_norm_sq = 0.0
        for term, count in q_tf.items():
            w = (1.0 + math.log(count)) * self.idf.get(term, 1.0)
            q_vec[term] = w
            q_norm_sq += w * w
        q_norm = math.sqrt(q_norm_sq) or 1.0
        for term in q_vec:
            q_vec[term] /= q_norm

        raw_q_terms = set(_tokenize(query, expand_synonyms=False))
        scored: list[tuple[float, dict]] = []

        for idx, doc_vec in enumerate(self.doc_vectors):
            dot = sum(w * doc_vec.get(term, 0.0) for term, w in q_vec.items())
            if dot <= 0.0:
                continue
            doc = self.documents[idx]
            title_terms = set(_tokenize(doc["title"]))
            title_overlap = len(raw_q_terms & title_terms)
            # Slight bonus for exact title term overlap
            score = dot + (0.08 * min(title_overlap, 3))
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "title": doc["title"],
                "category": doc["category"],
                "text": doc["text"],
                "score": round(score, 4),
            }
            for score, doc in scored[:top_k]
        ]

    def is_greeting(self, query: str) -> bool:
        normalized = re.sub(r"[^\w\s]", "", (query or "").lower()).strip()
        if not normalized:
            return True
        if normalized in GREETING_PATTERNS:
            return True
        words = normalized.split()
        if len(words) <= 3 and words[0] in {"hi", "hello", "hey", "greetings"}:
            return True
        return False

    def is_in_scope(self, query: str, retrieved: list[dict]) -> bool:
        raw_tokens = set(_tokenize(query, expand_synonyms=False))
        normalized = (query or "").lower()

        # Direct domain term match
        if raw_tokens & DOMAIN_TERMS:
            return True

        # Multi-word phrase checks for common close concepts
        close_phrases = (
            "forward deployed", "cyber security", "cloud security", "cloud architecture",
            "artificial intelligence", "machine learning", "large language", "prompt engineering",
            "prompt injection", "zero trust", "threat hunting", "incident response",
            "vulnerability management", "access control", "key vault", "private endpoint",
            "virtual network", "landing zone", "semantic kernel", "vector database",
            "how does rag", "what is fde", "what is ai", "what is cyber", "security advisor",
            "blue team", "red team", "penetration test", "pentest", "soc analyst",
        )
        if any(phrase in normalized for phrase in close_phrases):
            return True

        # Fallback: strong RAG cosine similarity to indexed FDE/AI/Security corpus
        if retrieved and retrieved[0]["score"] >= 0.34:
            return True

        return False

    def _fetch_google_cse(self, query: str, num_results: int = 4) -> list[dict]:
        """Fetches live Google Search snippets & links via Google Custom Search JSON API when configured."""
        cse_key = (os.environ.get("GOOGLE_CSE_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
        cse_cx = (os.environ.get("GOOGLE_CSE_CX") or os.environ.get("GOOGLE_SEARCH_ENGINE_ID") or "").strip()
        if not cse_key or not cse_cx:
            return []

        params = urllib.parse.urlencode({
            "key": cse_key,
            "cx": cse_cx,
            "q": query,
            "num": max(1, min(num_results, 5)),
        })
        url = f"https://www.googleapis.com/customsearch/v1?{params}"
        req = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = []
                for item in data.get("items") or []:
                    title = (item.get("title") or "").strip()
                    snippet = re.sub(r"\s+", " ", (item.get("snippet") or "").strip())
                    link = (item.get("link") or "").strip()
                    if snippet or title:
                        results.append({"title": title, "snippet": snippet, "url": link})
                return results
        except Exception:
            return []

    def _extract_grounding_sources(self, candidate: dict) -> tuple[list[dict], list[str]]:
        """Extracts Google Search grounding URLs and search queries from Gemini groundingMetadata."""
        grounding = candidate.get("groundingMetadata") or {}
        web_queries = [q for q in (grounding.get("webSearchQueries") or []) if isinstance(q, str) and q.strip()]
        sources = []
        seen_urls = set()
        for chunk in grounding.get("groundingChunks") or []:
            web = chunk.get("web") or {}
            uri = (web.get("uri") or "").strip()
            title = (web.get("title") or uri or "Google Search Result").strip()
            if uri and uri not in seen_urls:
                seen_urls.add(uri)
                sources.append({"title": title, "url": uri})
        return sources, web_queries

    def _call_gemini(
        self,
        query: str,
        retrieved: list[dict],
        google_cse_results: list[dict],
        history: list[dict],
    ) -> dict | None:
        api_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
        if not api_key:
            return None

        rag_block = "\n".join(
            f"- [{chunk['category']}] {chunk['title']}: {chunk['text']}"
            for chunk in retrieved
        ) or "No specific portal snippet matched."

        google_block = ""
        if google_cse_results:
            google_block = "\n\nGoogle Search Fetched Context:\n" + "\n".join(
                f"- {g['title']} ({g['url']}): {g['snippet']}"
                for g in google_cse_results
            )

        system_instruction = (
            "You are a friendly virtual advisor sitting at a company helpdesk specializing ONLY in "
            "Forward Deployed Engineer (FDE), Artificial Intelligence (AI/LLM/RAG), and Cybersecurity Advisory "
            "(including closely related cloud architecture, DevSecOps, IAM, SIEM/KQL, and enterprise engineering).\n"
            "STRICT RULES:\n"
            "1. Use Google Search grounding to fetch the live answer from Google for the user's question and combine it with the RAG Context.\n"
            "2. Give the SMALLEST clear description possible: 2 to 3 crisp sentences maximum (under 70 words). No filler.\n"
            "3. Speak naturally like a knowledgeable company advisor helping a colleague or client.\n"
            "4. If the user's question is NOT about Forward Deployed Engineering, AI, or Cybersecurity Advisory "
            "(or closely related technical/cloud/security concepts), reply ONLY with:\n"
            f"\"{OUT_OF_SCOPE_MESSAGE}\""
        )

        contents = []
        for turn in (history or [])[-4:]:
            role = "user" if turn.get("role") == "user" else "model"
            msg = (turn.get("content") or "").strip()
            if msg:
                contents.append({"role": role, "parts": [{"text": msg[:400]}]})

        user_prompt = (
            f"RAG Context:\n{rag_block}"
            f"{google_block}\n\n"
            f"Question: {query}\n\n"
            "Fetch/ground the answer from Google and the context above, then put the answer into a concise 2-3 sentence response (or state it is out of scope)."
        )
        contents.append({"role": "user", "parts": [{"text": user_prompt}]})

        preferred_model = (os.environ.get("GEMINI_MODEL") or "gemini-2.5-flash").strip()
        candidate_models = [preferred_model]
        for fallback_model in ("gemini-2.5-flash", "gemini-2.0-flash"):
            if fallback_model not in candidate_models:
                candidate_models.append(fallback_model)

        base_payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 200,
            },
        }

        for model_name in candidate_models:
            url = (
                f"https://generativelanguage.googleapis.com/v1beta/models/"
                f"{model_name}:generateContent?key={api_key}"
            )
            # First attempt with Google Search Grounding enabled; if endpoint rejects tool schema (400), retry without tools
            for use_google_tool in (True, False):
                payload = dict(base_payload)
                if use_google_tool:
                    payload["tools"] = [{"google_search": {}}]
                body_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url,
                    data=body_bytes,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                try:
                    with urllib.request.urlopen(req, timeout=14) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        candidates = data.get("candidates") or []
                        if candidates:
                            cand = candidates[0]
                            parts = (cand.get("content") or {}).get("parts") or []
                            text = "".join(p.get("text", "") for p in parts).strip()
                            if text:
                                grounding_sources, web_queries = self._extract_grounding_sources(cand)
                                return {
                                    "text": text,
                                    "model": model_name,
                                    "grounding_sources": grounding_sources,
                                    "web_queries": web_queries,
                                    "grounding_requested": use_google_tool,
                                }
                except urllib.error.HTTPError as e:
                    if e.code == 400 and use_google_tool:
                        continue
                    if e.code == 404:
                        break
                    return None
                except Exception:
                    return None

        return None

    def answer(self, query: str, history: list[dict] | None = None) -> dict:
        clean_query = (query or "").strip()
        if not clean_query:
            return {
                "answer": GREETING_MESSAGE,
                "in_scope": True,
                "mode": "greeting",
                "google_used": False,
                "google_queries": [],
                "sources": [],
            }

        if self.is_greeting(clean_query):
            return {
                "answer": GREETING_MESSAGE,
                "in_scope": True,
                "mode": "greeting",
                "google_used": False,
                "google_queries": [],
                "sources": [],
            }

        retrieved = self.retrieve(clean_query, top_k=4)

        if not self.is_in_scope(clean_query, retrieved):
            return {
                "answer": OUT_OF_SCOPE_MESSAGE,
                "in_scope": False,
                "mode": "out_of_scope",
                "google_used": False,
                "google_queries": [],
                "sources": [],
            }

        # 1. Fetch live Google Search snippets (if Google CSE is configured)
        google_cse_results = self._fetch_google_cse(clean_query, num_results=3)

        # 2. Try Gemini LLM + Google Search Grounding + RAG altogether
        gemini_res = self._call_gemini(clean_query, retrieved, google_cse_results, history or [])
        if gemini_res:
            gemini_text = gemini_res["text"]
            is_oos = "out of scope" in gemini_text.lower()
            google_sources = list(gemini_res.get("grounding_sources") or [])
            for cse in google_cse_results:
                if cse.get("url") and all(s.get("url") != cse["url"] for s in google_sources):
                    google_sources.append({"title": cse["title"], "url": cse["url"]})

            google_used = bool(
                google_sources
                or gemini_res.get("web_queries")
                or gemini_res.get("grounding_requested")
            )
            rag_sources = [{"title": c["title"], "url": None} for c in retrieved[:2]]
            combined_sources = ([] if is_oos else (google_sources[:3] if google_sources else rag_sources))

            return {
                "answer": gemini_text,
                "in_scope": not is_oos,
                "mode": "google_gemini_rag" if google_used else "gemini_rag",
                "model": gemini_res["model"],
                "google_used": google_used and not is_oos,
                "google_queries": [] if is_oos else (gemini_res.get("web_queries") or ([clean_query] if google_cse_results else [])),
                "sources": combined_sources,
            }

        # 3. Direct Google CSE fetched answer (when Google CSE is configured without Gemini)
        if google_cse_results:
            top_google = google_cse_results[0]
            concise_google = _truncate_concise(top_google.get("snippet") or top_google.get("title", ""), max_sentences=3, max_chars=300)
            return {
                "answer": concise_google,
                "in_scope": True,
                "mode": "google_search_rag",
                "google_used": True,
                "google_queries": [clean_query],
                "sources": [
                    {"title": g["title"], "url": g["url"]}
                    for g in google_cse_results[:3]
                    if g.get("title")
                ],
            }

        # 4. RAG Concise Extractive Synthesizer (works offline / without external key)
        if retrieved:
            best = retrieved[0]
            concise = _truncate_concise(best["text"], max_sentences=3, max_chars=300)
            return {
                "answer": concise,
                "in_scope": True,
                "mode": "rag",
                "google_used": False,
                "google_queries": [],
                "sources": [{"title": c["title"], "url": None} for c in retrieved[:2]],
            }

        # 5. Domain term was present, provide brief baseline FDE+AI+Security advisor guidance
        return {
            "answer": (
                "In FDE + AI + Cybersecurity Advisory, we align cloud architecture, Zero Trust controls, "
                "and grounded AI workflows directly to measurable business risk reduction. "
                "Ask about Azure security, Sentinel/KQL, RAG, or FDE delivery for specifics."
            ),
            "in_scope": True,
            "mode": "rag",
            "google_used": False,
            "google_queries": [],
            "sources": [{"title": "FDE + AI + Cybersecurity Advisor Value", "url": None}],
        }


# Singleton engine loaded once per worker
_ADVISOR_ENGINE: AdvisorRAGEngine | None = None


def get_advisor_engine() -> AdvisorRAGEngine:
    global _ADVISOR_ENGINE
    if _ADVISOR_ENGINE is None:
        _ADVISOR_ENGINE = AdvisorRAGEngine()
    return _ADVISOR_ENGINE


def answer_advisor_question(query: str, history: list[dict] | None = None) -> dict:
    return get_advisor_engine().answer(query, history=history)


def is_gemini_configured() -> bool:
    return bool((os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip())


def is_google_search_configured() -> bool:
    cse_ready = bool(
        (os.environ.get("GOOGLE_CSE_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
        and (os.environ.get("GOOGLE_CSE_CX") or os.environ.get("GOOGLE_SEARCH_ENGINE_ID") or "").strip()
    )
    return is_gemini_configured() or cse_ready
