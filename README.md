# 🛡️ Cloudera AI Sovereign Guard (Applied ML Prototype - AMP)

[![Cloudera AI Workbench](https://img.shields.io/badge/Cloudera_AI-AMP_Ready-ff5900?style=flat&logo=cloudera)](https://www.cloudera.com/)
[![License](https://img.shields.io/badge/Security-Air--Gapped%20%26%20Sovereign-16a34a)](https://www.cloudera.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask-000000)](https://flask.palletsproject.com/)

**Cloudera AI Sovereign Guard** is an enterprise AI governance gateway packaged as an **Applied ML Prototype (AMP)** for **Cloudera AI Workbench**.

This prototype inspects, redacts, and cleanses sensitive corporate data (PII, credentials, proprietary project keys) in real-time **before** prompts reach AI models—ensuring 100% data sovereignty and zero data exfiltration in air-gapped enterprise environments.

---

## 🚀 Quick Start & Deployment

Choose one of the following methods to deploy this AMP in Cloudera AI (CML).

### Method 1: Direct Deployment via Git (Recommended)

The fastest way to deploy and test this AMP without setting up a custom catalog.

1. Log in to **Cloudera AI / CML**.
2. Go to **Projects** and click **New Project**.
3. Select **Git** as the Initial Setup option.
4. Enter the Repository URL:
   ```text
   https://github.com/sanochihi/cloudera-sovereign-guard-amp.git

5. Set the project details and click Create Project.
6. Cloudera AI will automatically detect .project-metadata.yaml and trigger the startup tasks.


### What Happens Automatically:
Cloudera AI Workbench reads the `.project-metadata.yaml` file at the root of the repository and automatically executes the setup pipeline:
1. **Creates and Runs Dependency Job**: Executes `cml/install_deps.py` to install Python dependencies from `requirements.txt`.
2. **Deploys Application**: Starts the CAI Application (`app.py`), binding it to `CDSW_APP_PORT` on `127.0.0.1`.
3. **Provides One-Click UI URL**: Generates an authenticated web link to access the live Sovereign Guard UI in your browser.

---

## 📌 Key Features

* **🔒 100% Air-Gapped & Sovereign**: Operates entirely within Cloudera AI Workbench without making external internet or CDN calls.
* **🛡️ Real-Time PII & Secret Redaction**: Automatically redacts sensitive data including credit cards, email addresses, phone numbers, and confidential project keys (`[MASKED_CREDIT_CARD]`, `[MASKED_CONFIDENTIAL]`, etc.).
* **⚖️ Security Governance Scoring**: Evaluates prompt safety and computes a real-time **Security Score** (0–100%) with alert tags.
* **🤖 Local LLM Extensible Architecture**: Rule-based engine designed for instant live demos, with ready-to-use hooks to plug in air-gapped **Local LLMs** (e.g., Llama 3 via vLLM or CAI Model Deployments).
* **🖥️ Executive-Ready UI**: Clean, side-by-side comparative layout matching input prompts with cleansed prompts for high-impact demonstrations.

---

## 📂 Repository Structure

```text
├── .project-metadata.yaml   # [AMP Specification] Defines automated setup tasks & runtime
├── requirements.txt         # Python dependencies (Flask)
├── cml/
│   └── install_deps.py      # Automated task script to install requirements
├── app.py                   # Main Flask backend & governance logic controller
├── data/
│   └── sample_prompts.json  # Preset test scenario prompts (PII, secrets)
├── templates/
│   └── index.html           # Responsive single-page web UI (English interface)
└── README.md                # Documentation and AMP installation guide
```

---

## 🛠️ Tech Stack & Requirements

* **Platform**: Cloudera AI
* **AMP Specification**: Version 1.0
* **Backend**: Python 3.10+, Flask
* **Frontend**: HTML5, CSS3, JavaScript (Vanilla Fetch API)
* **Deployment Port**: `CDSW_APP_PORT` (bound to `127.0.0.1`)

---

## 🔌 Architecture & Local LLM Integration

For fast, deterministic live demo performance without heavy hardware dependencies, this repository uses lightweight regular expressions for PII/secret masking.

In an enterprise production setup on Cloudera AI Workbench, this rule-based engine can be seamlessly replaced or augmented by an air-gapped **Local LLM** (e.g., Llama 3 / Mistral / Qwen served via vLLM or CAI Model Deployment API) for zero-shot semantic governance.

### Sample Local LLM Extension (`app.py`):
```python
import requests

def sanitize_with_local_llm(prompt_text):
    """
    Optional extension: Replace regex rule engine with an air-gapped Local LLM
    hosted on Cloudera AI Workbench CAI Model Endpoint.
    """
    CAI_MODEL_ENDPOINT = "http://{ClouderaAI Site}:8080/v1/chat/completions"
    
    system_prompt = (
        "You are an air-gapped AI Sovereign Guard. "
        "Analyze the user input for sensitive PII, credit card details, or proprietary keys. "
        "Return sanitized text with confidential tokens masked."
    )
    
    payload = {
        "model": "local-sovereign-llm",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt_text}
        ],
        "temperature": 0.0
    }
    
    try:
        response = requests.post(CAI_MODEL_ENDPOINT, json=payload, timeout=5)
        return response.json()
    except Exception as e:
        # Fallback to rule-based engine if LLM endpoint is offline
        pass
```

---

## 🔄 Manual Running Option (Fallback)

If you prefer to clone and run the repository manually without using the AMP automated setup:

1. Clone the repository into your CAI Project session:
   ```bash
   git clone https://github.com/sanochihi/cloudera-sovereign-guard-amp.git
   cd cloudera-sovereign-guard
   ```
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a **New Application** in CAI Project settings:
   * **Name**: `Cloudera Sovereign Guard`
   * **Script**: `app.py`
   * **Resource Profile**: 1 vCPU / 2GB RAM
4. Click **Create Application**.

---

## 📜 License & Acknowledgments

Developed for the **Cloudera Anywhere Cloud Demo Contest**.  
Built on **Cloudera AI Workbench** for sovereign, sustainable, and secure enterprise AI workflows.
