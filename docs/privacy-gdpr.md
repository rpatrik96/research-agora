# Privacy & GDPR Compliance Guide

This guide converts GDPR rules into decisions you can act on today. It covers what cloud AI tools transmit, how paid plans differ for institutional compliance, and how to protect sensitive data in agent workflows.

*This is informational guidance, not legal advice. For binding guidance on specific situations, consult your institution's Datenschutzbeauftragte(r).*

---

## Before You Start: Decision Flowchart

Work through this before opening any AI tool with research data.

```
Does your data contain personal information about identifiable individuals?
│
├── YES → Is it health, biometric, or clinical data?
│         │
│         ├── YES → See "Medical & Clinical Data" section below.
│         │         Use local models (Ollama) only, on approved infrastructure.
│         │         Contact your Datenschutzbeauftragte(r) before proceeding.
│         │
│         └── NO  → Is it pseudonymized or fully anonymized?
│                   │
│                   ├── ANONYMIZED → Cloud AI permitted.
│                   │               Use Team plan (DPA required for GDPR).
│                   │
│                   └── PSEUDONYMIZED / IDENTIFIABLE →
│                       Does your institution have a DPA with the provider?
│                       │
│                       ├── YES (Team/Enterprise) → Cloud AI permitted with care.
│                       │                           Scope working directory tightly.
│                       │
│                       └── NO (Pro plan / no DPA) → Local models only,
│                                                     or upgrade to Team.
│
└── NO  → Is it unpublished research, embargoed data, or confidential grant content?
          │
          ├── YES → Do not paste into cloud AI. Draft locally, then paste
          │         anonymized/synthetic excerpts for editing help only.
          │
          └── NO  → Cloud AI permitted. Standard precautions apply.
```

---

## What Gets Sent to the Cloud

Everything you type or paste into a cloud AI tool (Claude.ai, ChatGPT, Copilot) is transmitted to external servers. This includes:

| What you do | What gets transmitted |
|-------------|----------------------|
| Type a prompt | The full prompt text |
| Paste text, code, or data into the chat | The full pasted content |
| Upload or attach a file | The full file contents |
| Run `claude` in a project directory | Prompts and model responses (encrypted via TLS); **not** your file system |

**Claude Code specifically:** Claude Code runs locally on your machine. It reads files into its context window and sends that context to the API with each request. This is not excerpts or summaries — it is full file contents. A large session with many files read can transmit substantial portions of a codebase.

What also gets loaded automatically at session start, without a permission prompt:
- `CLAUDE.md` files in the current directory and parent directories
- `MEMORY.md` (first 200 lines from previous sessions)
- Git state (branch, uncommitted changes, recent commits)
- Skill descriptions and MCP server tool definitions

During the agentic loop, Claude proactively reads additional files — `package.json`, source files, lock files, tests — to gather context. Each file's content is appended to the context window and transmitted on the next API call.

---

## What Stays Local

| What stays local | How to enforce it |
|-----------------|-------------------|
| Files you do not paste or upload | Don't paste them |
| Files excluded by `.claudeignore` | Add patterns to `.claudeignore` in your project root |
| Your file system (not scanned or indexed) | No action needed |
| Telemetry and error logs | Set `DISABLE_TELEMETRY=1` (see Privacy Kill Switches) |

**Important caveat:** `.claudeignore` rules are not fully reliable in agentic mode. See "The .env Problem" below.

---

## Paid Plan Comparison

| Feature | Claude Pro ($20/mo) | Claude Team ($30/user/mo) | Claude Enterprise |
|---------|-------------------|--------------------------|-------------------|
| Trains on your data | No (opt-in only) | No | No |
| Data retention | 30 days | 30 days | 30 days (custom configurable) |
| Zero Data Retention | Not available | Not available | Available |
| Data Processing Agreement (DPA) | **Not available** | Yes — automatic, includes EU SCCs | Yes — automatic, includes EU SCCs |
| Anthropic's legal role | Data **controller** | Data **processor** | Data **processor** |
| GDPR Art. 28 compliance | No | Yes | Yes |
| Recommended for institutional use | No | Yes | Yes |

**Key implications:**

- **Pro plan:** Anthropic does not train on your conversations by default. However, no DPA is available. Anthropic acts as a data controller — not a processor — which means the controller-processor relationship required for GDPR Art. 28 compliance does not exist. This matters for institutional use.
- **Team/Enterprise:** Anthropic acts as a data processor. DPA with EU Standard Contractual Clauses (SCCs) is automatically included. Conversations are never used for training. This is what institutional GDPR compliance requires.
- **All tiers:** Data is stored in the US. Cross-border transfer safeguards rely on SCCs post-Schrems II.

For institutional use with any personal data, Team or Enterprise is the minimum. Pro is not GDPR-compliant for research involving personal data.

Sources: [privacy.claude.com](https://privacy.claude.com), [Anthropic DPA](https://www.anthropic.com/legal/data-processing-addendum), [Claude Code data usage](https://code.claude.com/docs/en/data-usage)

---

## Medical & Clinical Data

Health data is a **special category** under GDPR Art. 9. Stricter rules apply beyond standard personal data protections.

### Legal Basis

Processing health data requires explicit consent *or* falls under the research exemption (Art. 9(2)(j)). Legitimate interest — the fallback for standard personal data — does not apply.

### Ethics Board Requirements

Using AI tools on study data may require amendment to your existing ethics approval. German Ethikkommissionen increasingly require AI tool disclosure in study protocols. Check with your ethics board before integrating any cloud AI into a study pipeline.

### DICOM De-identification

Medical images contain embedded patient metadata — name, date of birth, hospital ID — that survives standard export. This metadata must be stripped before any AI processing.

| Tool | What it does | Limitation |
|------|-------------|------------|
| `pydicom` with de-identification recipe | Strips DICOM tags systematically | Requires configuration; verify output |
| CTP / Clinical Trial Processor | Full de-identification pipeline | Requires Java setup |
| `dcm2niix` | Format converter | **Not designed for anonymization** — strips some headers but not all PII |

Do not rely on format converters for de-identification.

### Practical Decision Tree

```
Is the data identifiable clinical data (patient records, DICOM, study data)?
│
├── YES → Local models (Ollama) only, on approved institutional infrastructure.
│         Contact Datenschutzbeauftragte(r) first.
│
└── NO  → Is it anonymized research data derived from patient contact?
          │
          ├── YES → Cloud AI permitted with Team plan (DPA included).
          │         Verify anonymization is complete before uploading.
          │
          └── NO  → Standard GDPR decision flowchart applies.
```

### Institutional DPA

Contact your Datenschutzbeauftragte(r) before using cloud AI on any data derived from patient contact. The university's framework agreement may or may not cover research use — do not assume it does.

---

## Privacy Kill Switches

Add these to your shell profile (`~/.zshrc` or `~/.bashrc`) to disable telemetry and non-essential data transmission:

```bash
export DISABLE_TELEMETRY=1                              # No usage metrics sent to Anthropic
export DISABLE_ERROR_REPORTING=1                         # No error logs to Sentry
export DISABLE_FEEDBACK_COMMAND=1                        # Prevents transcript upload via /feedback
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1        # Disables all non-essential network calls
```

Add these patterns to `.claudeignore` in your project root to prevent Claude from reading sensitive files:

```
.env
.env.*
.env.local
credentials*
**/secrets/**
*.pem
*.key
id_rsa*
**/patient-data/**
**/dicom/**
```

**Critical caveat:** `.claudeignore` is not a security boundary. See "The .env Problem" below. Use `.claudeignore` as one layer of defense, not the only one.

---

## The .env Problem

Claude Code does not reliably prevent reading `.env` files.

Security researcher Dor Munis ([Knostic, 2025](https://www.knostic.ai/blog/claude-loads-secrets-without-permission)) documented that Claude Code loads `.env`, `.env.local`, and similar files — including API keys and passwords — into the context window automatically, without explicit permission.

In January 2026, [*The Register*](https://www.theregister.com/2026/01/28/claude_code_ai_secrets_files/) verified that `.claudeignore` rules intended to block `.env` access were inconsistently enforced. Claude read blocked files when operating in agentic mode.

**What this means in practice:**

Any file in or under your project directory is potentially readable by Claude Code. "Potentially readable" means "potentially transmitted to Anthropic's API."

**Mitigation:**

| What not to do | What to do instead |
|---------------|-------------------|
| Store secrets in `.env` inside the project directory | Move `.env` files to the parent directory (outside the project root) |
| Rely on `.claudeignore` alone to protect secrets | Use a secrets manager (Doppler, 1Password CLI, `direnv`) that injects credentials at runtime |
| Put API keys in any file Claude might read | Use environment variables injected by your shell, not stored in files |

The pattern to internalize: if a file is in the project directory tree, treat it as readable by the agent. Structure your project so secrets never live there.

Sources: [Claude Code Data Usage](https://code.claude.com/docs/en/data-usage), [Knostic .env research](https://www.knostic.ai/blog/claude-loads-secrets-without-permission), [The Register investigation](https://www.theregister.com/2026/01/28/claude_code_ai_secrets_files/)

---

## Local & Self-Hosted Alternatives

When cloud AI is not an option — identifiable clinical data, institutional policy, or sovereignty concerns — local models provide full data control at the cost of capability.

| Tool | What it does | Trade-off | Best for |
|------|-------------|-----------|----------|
| [Ollama](https://ollama.com) | Run open-weight LLMs locally (Llama 3, Mistral, Phi-3) | Less capable than frontier models; requires GPU for good performance | Privacy-sensitive tasks, offline environments |
| [vLLM](https://github.com/vllm-project/vllm) | High-throughput LLM serving on your infrastructure | Requires infrastructure setup | Group-level deployment, shared research infrastructure |
| [Mistral (Le Chat / API)](https://mistral.ai) | EU-hosted frontier model, GDPR-native | Smaller ecosystem, fewer agentic tools | EU sovereignty requirements |
| [Aleph Alpha (Luminous)](https://aleph-alpha.com) | German-hosted, on-premise available | Smaller models, less capable at coding | Maximum data sovereignty, German institutional preference |

**EU sovereignty note:** Using Mistral or Aleph Alpha addresses concerns about US jurisdiction and data residency. Both offer DPAs and are subject to EU law. Capabilities lag US frontier models, particularly for coding and complex reasoning, as of early 2026.

**Practical decision:** For routine tasks (editing, brainstorming, literature search) where data is not sensitive, use the best available tool. For anything involving personal data or institutional constraints, default to local models until you've confirmed your DPA coverage.

---

## Non-EU Researchers

The workflow patterns in this guide apply regardless of your legal jurisdiction. Equivalent frameworks:

| Jurisdiction | Framework | Key similarities to GDPR |
|-------------|-----------|--------------------------|
| South Africa | POPIA (Protection of Personal Information Act) | Lawful basis required; cross-border transfer restrictions |
| United Kingdom | UK GDPR | Near-identical to EU GDPR; SCCs replaced by International Data Transfer Agreements |
| United States | Sector-specific (HIPAA for health data, FERPA for education) | HIPAA in particular: cloud AI requires a Business Associate Agreement (BAA) for PHI |
| Canada | PIPEDA / provincial laws | Consent-based; cross-border adequacy requirements |

**US health data specifically:** HIPAA-covered entities need a BAA with any cloud AI provider processing Protected Health Information (PHI). Anthropic offers BAAs only at the Enterprise tier. For health research, check with your IRB and compliance office before using any cloud AI on patient data.

The core principle — local models for identifiable data, institutional DPA for anonymized data, cloud AI freely for public/non-personal data — holds across all jurisdictions.
