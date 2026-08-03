import json
import re
import subprocess
import shutil
import os

# ─── Find cortex executable path dynamically ──────────────────────────────────
def find_cortex():
    path = shutil.which("cortex")
    if path:
        return path
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    cortex_dir = os.path.join(local_app_data, "cortex")
    if os.path.exists(cortex_dir):
        for root, dirs, files in os.walk(cortex_dir):
            for f in files:
                if f == "cortex.exe":
                    return os.path.join(root, f)
    return None

CORTEX_PATH = find_cortex()

# ─── Mock data (Snowflake DB simulation for demo/fallback) ────────────────────
MOCK_SHIPMENTS = [
    {"shipment_id": "SHP-4092", "origin": "Port of Los Angeles",
     "destination": "New York Distribution Center",
     "product_id": "PROD-A1", "quantity": 1000, "status": "In Transit"},
    {"shipment_id": "SHP-8812", "origin": "Shenzhen",
     "destination": "Seattle Warehouse",
     "product_id": "PROD-B2", "quantity": 500, "status": "Delayed"},
]
MOCK_INVENTORY = [
    {"warehouse": "New York Distribution Center", "product_id": "PROD-A1",
     "current_stock": 200, "minimum_required": 500},
    {"warehouse": "Texas Regional Warehouse",    "product_id": "PROD-A1",
     "current_stock": 2500, "minimum_required": 1000},
    {"warehouse": "Seattle Warehouse",           "product_id": "PROD-B2",
     "current_stock": 50,   "minimum_required": 100},
]

# ─── Cortex CLI call (real AI) ────────────────────────────────────────────────
def run_cortex_query(prompt):
    if not CORTEX_PATH:
        return None
    try:
        result = subprocess.run(
            f'"{CORTEX_PATH}" -p "{prompt}" --output-format stream-json',
            capture_output=True, text=True, shell=True, timeout=30
        )
        responses = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    if data.get('role') == 'assistant' and 'content' in data:
                        responses.append(data['content'])
                except json.JSONDecodeError:
                    continue
        output = "".join(responses)
        return output if output.strip() else None
    except Exception:
        return None

# ─── SKILL 1 ─ Ingestion & Anomaly Detection ─────────────────────────────────
def skill_1_ingest_and_detect(alert_text):
    print("\n--- [SKILL 1] INGESTION & ANOMALY DETECTION ---")
    print(f"Received unstructured alert:\n  '{alert_text}'")

    # Try real Cortex AI first
    if CORTEX_PATH:
        print("[Cortex CLI] Extracting entities with real AI...")
        prompt = (f'Extract the shipment ID and delay in days from this alert. '
                  f'Return ONLY a JSON object with keys shipment_id (string) '
                  f'and delay_days (integer). Alert: "{alert_text}"')
        response = run_cortex_query(prompt)
        if response:
            try:
                clean = re.search(r'\{.*\}', response.replace('\n', ''), re.DOTALL).group()
                data = json.loads(clean)
                print(f"[Cortex AI] Extracted: {json.dumps(data, indent=2)}")
                return data
            except Exception:
                pass

    # Fallback: rule-based extraction
    print("[Fallback] Using rule-based extraction...")
    shipment_match = re.search(r'Shipment\s+#?([A-Z0-9-]+)', alert_text)
    delay_match    = re.search(r'delayed by\s+(\d+)', alert_text)
    if not shipment_match:
        print("ERROR: Could not extract shipment ID.")
        return None
    data = {
        "shipment_id": shipment_match.group(1),
        "delay_days":  int(delay_match.group(1)) if delay_match else 0,
        "anomaly_type": "Delay"
    }
    print(f"Extracted: {json.dumps(data, indent=2)}")
    return data

# ─── SKILL 2 ─ Data Retrieval & Reasoning ────────────────────────────────────
def skill_2_retrieve_and_reason(extracted_data):
    print("\n--- [SKILL 2] DATA RETRIEVAL & REASONING ---")
    shipment_id = extracted_data["shipment_id"]

    # Try real Cortex AI first
    if CORTEX_PATH:
        print(f"[Cortex CLI] Querying Snowflake for shipment {shipment_id}...")
        prompt = (
            f"Query SUPPLY_CHAIN_DB.LOGISTICS.SHIPMENTS for SHIPMENT_ID='{shipment_id}'. "
            f"Then query SUPPLY_CHAIN_DB.LOGISTICS.INVENTORY for the product. "
            f"Find a warehouse (not the destination) with surplus >= needed quantity. "
            f"Return JSON with keys: affected_product, affected_destination, "
            f"quantity_needed, source_warehouse, available_surplus."
        )
        response = run_cortex_query(prompt)
        if response:
            try:
                clean = re.search(r'\{.*\}', response.replace('\n', ''), re.DOTALL).group()
                result = json.loads(clean)
                print(f"[Cortex AI] Reasoning: {json.dumps(result, indent=2)}")
                return result
            except Exception:
                pass

    # Fallback: query mock data
    print("[Fallback] Using mock Snowflake data...")
    shipment = next((s for s in MOCK_SHIPMENTS if s["shipment_id"] == shipment_id), None)
    if not shipment:
        print(f"Shipment {shipment_id} not found.")
        return None

    product_id   = shipment["product_id"]
    quantity     = shipment["quantity"]
    destination  = shipment["destination"]

    print(f"Shipment: {quantity} units of {product_id} to {destination} delayed.")
    print(f"Checking inventory for surplus of {product_id}...")

    source_warehouse = None
    available_surplus = 0
    for inv in MOCK_INVENTORY:
        if inv["product_id"] == product_id and inv["warehouse"] != destination:
            surplus = inv["current_stock"] - inv["minimum_required"]
            if surplus >= quantity:
                source_warehouse  = inv["warehouse"]
                available_surplus = surplus
                break

    result = {
        "affected_product":     product_id,
        "affected_destination": destination,
        "quantity_needed":      quantity,
        "resolution_possible":  bool(source_warehouse),
        "source_warehouse":     source_warehouse,
        "available_surplus":    available_surplus,
    }
    print(f"Reasoning result:\n{json.dumps(result, indent=2)}")
    return result

# ─── SKILL 3 ─ Action Execution ──────────────────────────────────────────────
def skill_3_execute_action(reasoning_result):
    print("\n--- [SKILL 3] ACTION EXECUTION ---")
    if not reasoning_result.get("resolution_possible"):
        print("No surplus found. Escalating to human manager.")
        return

    source      = reasoning_result["source_warehouse"]
    destination = reasoning_result["affected_destination"]
    quantity    = reasoning_result["quantity_needed"]
    product     = reasoning_result["affected_product"]

    print("Generating Snowflake SQL resolution commands...\n")

    sql_1 = (f"UPDATE SUPPLY_CHAIN_DB.LOGISTICS.INVENTORY "
             f"SET CURRENT_STOCK = CURRENT_STOCK - {quantity} "
             f"WHERE WAREHOUSE = '{source}' AND PRODUCT_ID = '{product}';")
    sql_2 = (f"UPDATE SUPPLY_CHAIN_DB.LOGISTICS.INVENTORY "
             f"SET CURRENT_STOCK = CURRENT_STOCK + {quantity} "
             f"WHERE WAREHOUSE = '{destination}' AND PRODUCT_ID = '{product}';")

    print("=" * 60)
    print("   *** SUPPLY CHAIN DISRUPTION RESOLUTION PLAN ***")
    print("=" * 60)
    print(f"  ISSUE    : Shortage of {quantity} units of {product}")
    print(f"             at {destination}")
    print(f"  SOLUTION : Reroute {quantity} units from {source}")
    print(f"             (Available surplus: {reasoning_result['available_surplus']} units)")
    print()
    print("  [SNOWFLAKE CoCo CLI COMMANDS TO EXECUTE]")
    print(f"  > {sql_1}")
    print(f"  > {sql_2}")
    print("=" * 60)
    print("\n  Agent successfully resolved the workflow autonomously! [DONE]")

# ─── Main Orchestrator ────────────────────────────────────────────────────────
def run_workflow():
    mode = "LIVE (Snowflake Cortex AI)" if CORTEX_PATH else "DEMO (Mock Data)"
    print(f"\n{'='*60}")
    print(f"   Logistics Auto-Resolve Agent  [{mode}]")
    print(f"{'='*60}\n")

    incoming_alert = (
        "URGENT: Shipment SHP-4092 from LA Port is delayed by 4 days "
        "due to severe weather conditions."
    )

    extracted_data    = skill_1_ingest_and_detect(incoming_alert)
    if not extracted_data: return
    reasoning_result  = skill_2_retrieve_and_reason(extracted_data)
    if not reasoning_result: return
    skill_3_execute_action(reasoning_result)

if __name__ == "__main__":
    run_workflow()
