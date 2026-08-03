import json
import re
import subprocess
import time

def run_cortex_query(prompt):
    """
    Helper function to run a prompt against the Snowflake Cortex Code CLI
    and return the output.
    """
    print(f"\n[Cortex CLI] Sending prompt...")
    try:
        # Run the cortex CLI via subprocess
        result = subprocess.run(
            ["cortex", "-p", prompt, "--output-format", "stream-json"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # The CLI outputs stream-json, we capture the final assistant response
        responses = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    data = json.loads(line)
                    if data.get('role') == 'assistant' and 'content' in data:
                        responses.append(data['content'])
                except json.JSONDecodeError:
                    continue
                    
        return "".join(responses) if responses else result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error calling Cortex CLI: {e.stderr}")
        return None

def skill_1_ingest_and_detect(alert_text):
    print("\n--- [SKILL 1] INGESTION & ANOMALY DETECTION ---")
    print(f"Received unstructured alert: '{alert_text}'")
    
    # We now use Cortex LLM to extract this!
    prompt = f"""
    Extract the shipment ID and delay in days from the following alert text.
    Return ONLY a valid JSON object with keys 'shipment_id' (string) and 'delay_days' (integer).
    Alert: "{alert_text}"
    """
    response = run_cortex_query(prompt)
    
    try:
        # Clean up Markdown formatting if Cortex adds it
        clean_json = re.search(r'\{.*\}', response.replace('\n', ''), re.DOTALL).group()
        extracted_data = json.loads(clean_json)
        print(f"Agent extracted: {json.dumps(extracted_data, indent=2)}")
        return extracted_data
    except Exception as e:
        print(f"Failed to parse JSON from Cortex: {response}")
        return None

def skill_2_retrieve_and_reason(extracted_data):
    print("\n--- [SKILL 2] DATA RETRIEVAL & REASONING ---")
    shipment_id = extracted_data.get("shipment_id")
    
    print(f"Agent asking Cortex to query Snowflake for shipment {shipment_id} details and inventory alternatives...")
    
    prompt = f"""
    1. Query the SUPPLY_CHAIN_DB.LOGISTICS.SHIPMENTS table for SHIPMENT_ID = '{shipment_id}'.
    2. Note the PRODUCT_ID, QUANTITY, and DESTINATION.
    3. Query the SUPPLY_CHAIN_DB.LOGISTICS.INVENTORY table for that PRODUCT_ID.
    4. Find a WAREHOUSE (other than the DESTINATION) where (CURRENT_STOCK - MINIMUM_REQUIRED) >= the delayed QUANTITY.
    5. Return a JSON object with keys: 'affected_product', 'affected_destination', 'quantity_needed', 'source_warehouse', 'available_surplus'.
    """
    response = run_cortex_query(prompt)
    
    try:
        clean_json = re.search(r'\{.*\}', response.replace('\n', ''), re.DOTALL).group()
        reasoning_result = json.loads(clean_json)
        print(f"Agent reasoning output:\n{json.dumps(reasoning_result, indent=2)}")
        return reasoning_result
    except Exception as e:
        print(f"Failed to parse JSON from Cortex: {response}")
        return None

def skill_3_execute_action(reasoning_result):
    print("\n--- [SKILL 3] ACTION EXECUTION ---")
    
    source = reasoning_result.get("source_warehouse")
    destination = reasoning_result.get("affected_destination")
    quantity = reasoning_result.get("quantity_needed")
    product = reasoning_result.get("affected_product")
    
    print("Agent generating final resolution plan and executing SQL via Cortex...")
    
    prompt = f"""
    The supply chain disruption requires rerouting {quantity} units of {product} from '{source}' to '{destination}'.
    Generate the two SQL UPDATE statements required to adjust the CURRENT_STOCK in the SUPPLY_CHAIN_DB.LOGISTICS.INVENTORY table.
    Execute these SQL statements against the database. 
    Confirm when complete.
    """
    
    response = run_cortex_query(prompt)
    print("\n*** SUPPLY CHAIN DISRUPTION RESOLUTION ***")
    print(response)
    print("\nAgent successfully resolved the workflow autonomously.")

def run_workflow():
    print("Initializing LIVE Snowflake Cortex Supply Chain Disruption Agent...\n")
    incoming_alert = "URGENT: Shipment SHP-4092 from LA Port is delayed by 4 days due to severe weather conditions."
    
    extracted_data = skill_1_ingest_and_detect(incoming_alert)
    if not extracted_data: return
    reasoning_result = skill_2_retrieve_and_reason(extracted_data)
    if not reasoning_result: return
    skill_3_execute_action(reasoning_result)

if __name__ == "__main__":
    run_workflow()
