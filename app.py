from flask import Flask, render_template, request, jsonify
import os
import json
import re
import math

# --- CAI Workbench Application Path Configuration ---
# Dynamically locate project directory when deployed as AMP or run locally
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
if os.path.exists(os.path.join(BASE_DIR, "templates")):
    APP_DIR = BASE_DIR
else:
    # CHANGE THIS DIRECTORY TO YOUR OWN PROJECT FILE'S PATH
    # /home/cdsw/ is the fixed home directory path
    APP_DIR = "/home/cdsw/wild-chihiro/demo2"

TEMPLATE_DIR = os.path.join(APP_DIR, "templates")
JSON_PATH = os.path.join(APP_DIR, "data", "sample_prompts.json")

app = Flask(__name__, template_folder=TEMPLATE_DIR)

# Load preset data (for demo purpose)
def load_presets():
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# --- Local analysis ---
def analyze_and_compute(text):
    masked_text = text
    risk_found = []

    # =========================================================================
    # [DEMO ARCHITECTURE NOTE & LOCAL LLM EXTENSIBILITY]
    # For fast, deterministic live demo performance without heavy hardware
    # dependencies, this demo currently uses lightweight regex pattern matching
    # for PII and confidential secret masking.
    # 
    # In a production enterprise setup on Cloudera AI Workbench (CML / CDSW),
    # this rule-based engine can be seamlessly replaced or augmented by an
    # air-gapped Local LLM (e.g., Llama 3 / Mistral / Qwen served via vLLM, 
    # Ollama, or CML Model Deployment API) for zero-shot semantic governance.
    #
    # Sample Code for Air-Gapped Local LLM Integration:
    # -------------------------------------------------------------------------
    # import requests
    # 
    # def sanitize_with_local_llm(prompt_text):
    #     # Example: Calling a local air-gapped LLM endpoint deployed on CML
    #     LOCAL_LLM_ENDPOINT = "http://localhost:8080/v1/chat/completions"
    #     system_prompt = (
    #         "You are an air-gapped AI Sovereign Guard. "
    #         "Identify sensitive PII, credit cards, or secret keys in the input text. "
    #         "Return a JSON object with 'masked_text', 'detected_risks', and 'risk_score'."
    #     )
    #     payload = {
    #         "model": "local-sovereign-llm",
    #         "messages": [
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": prompt_text}
    #         ],
    #         "temperature": 0.0
    #     }
    #     try:
    #         res = requests.post(LOCAL_LLM_ENDPOINT, json=payload, timeout=5)
    #         res_json = res.json()
    #         return res_json.get("masked_text"), res_json.get("detected_risks"), res_json.get("risk_score")
    #     except Exception as e:
    #         # Fallback to rule-based sanitization if local LLM endpoint is unreachable
    #         pass
    # =========================================================================
    
    patterns = {
        "Credit Card Number": (r'\b(?:\d[ -]*?){13,16}\b', 'XXXX-XXXX-XXXX-1234'),
        "Email Address": (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', 'xxxx@masked-domain.com'),
        "Phone Number": (r'\b0\d{1,4}[-(]?\d{1,4}[-)]?\d{3,4}\b', '090-XXXX-XXXX'),
        "Project Code": (r'\b[Pp]roject-[a-zA-Z0-9.-]+\b', 'Project-[confidential]'),
        "Secret Key": (r'\bSK-\d{4}-[A-Za-z0-9]{3}\b', 'SK-1234-ABC')
    }

    for risk_type, (pattern, replacement) in patterns.items():
        if re.search(pattern, masked_text):
            risk_found.append(risk_type)
            masked_text = re.sub(pattern, replacement, masked_text)

    risk_score = max(0, 100 - (len(risk_found) * 35))

    char_count = len(text)
    estimated_tokens = max(10, math.ceil(char_count / 1.5))

    cloud_kwh_per_token = 0.00012
    local_kwh_per_token = 0.000018
    
    cloud_co2_g_per_kwh = 400
    local_co2_g_per_kwh = 250
    
    cloud_cost_per_token = 0.0045
    local_cost_per_token = 0.0004

    cloud_kwh = estimated_tokens * cloud_kwh_per_token
    local_kwh = estimated_tokens * local_kwh_per_token
    
    cloud_co2 = cloud_kwh * cloud_co2_g_per_kwh
    local_co2 = local_kwh * local_co2_g_per_kwh
    
    cloud_cost = estimated_tokens * cloud_cost_per_token
    local_cost = estimated_tokens * local_cost_per_token

    co2_reduction = round(((cloud_co2 - local_co2) / cloud_co2) * 100, 1) if cloud_co2 > 0 else 0
    cost_reduction = round(((cloud_cost - local_cost) / cloud_cost) * 100, 1) if cloud_cost > 0 else 0

    return {
        "original_text": text,
        "masked_text": masked_text,
        "risks": risk_found,
        "risk_score": risk_score,
        "metrics": {
            "tokens": estimated_tokens,
            "cloud_co2_g": round(cloud_co2, 3),
            "local_co2_g": round(local_co2, 3),
            "cloud_cost_yen": round(cloud_cost, 2),
            "local_cost_yen": round(local_cost, 2),
            "co2_reduction_pct": co2_reduction,
            "cost_reduction_pct": cost_reduction
        }
    }

# --- Flask Routing ---
@app.route('/', methods=['GET'])
def index():
    presets = load_presets()
    return render_template('index.html', presets=presets)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.get_json() or {}
    text = data.get('text', '')
    if not text.strip():
        return jsonify({"error": "Empty text"}), 400
    
    result = analyze_and_compute(text)
    return jsonify(result)

# --- Cloudera AI Workbench Application Main ---
if __name__ == '__main__':
    try:
        port = int(os.environ.get("CDSW_APP_PORT", "5000"))
        app.run(host="127.0.0.1", port=port)
    except Exception as e:
        print(f"ERROR: unable to run application:\n {str(e)}")
