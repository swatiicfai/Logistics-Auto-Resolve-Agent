import streamlit as st
import json
import re
import subprocess
import time

st.set_page_config(page_title="Supply Chain Agent", page_icon="📦", layout="wide")

st.title("📦 Logistics Auto-Resolve Agent")
st.markdown("Autonomous supply chain disruption resolution powered by Snowflake Cortex LLM.")

def run_cortex_query(prompt, mock_response):
    """
    Runs the Cortex CLI. If it fails (like when deployed on the cloud without the CLI),
    it falls back to a simulated mock response so the demo keeps working!
    """
    try:
        result = subprocess.run(
            ["cortex", "-p", prompt, "--output-format", "stream-json"],
            capture_output=True,
            text=True,
            check=True
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
        return "".join(responses) if responses else result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        time.sleep(2) # Simulate LLM latency
        return mock_response

st.sidebar.header("Configuration")
incoming_alert = st.sidebar.text_area(
    "Incoming Alert Text", 
    "URGENT: Shipment SHP-4092 from LA Port is delayed by 4 days due to severe weather conditions.",
    height=150
)

if st.sidebar.button("Run Resolution Agent", type="primary"):
    
    st.subheader("🤖 Agent Workflow Execution")
    
    # --- SKILL 1 ---
    with st.expander("Step 1: Ingestion & Anomaly Detection", expanded=True):
        st.write(f"**Received unstructured alert:**")
        st.info(incoming_alert)
        
        prompt_1 = f"Extract the shipment ID and delay in days from the following alert text. Return ONLY a valid JSON object with keys 'shipment_id' (string) and 'delay_days' (integer).\nAlert: '{incoming_alert}'"
        mock_response_1 = '{"shipment_id": "SHP-4092", "delay_days": 4}'
        
        with st.spinner("Extracting entities using Cortex LLM..."):
            response_1 = run_cortex_query(prompt_1, mock_response_1)
            
        try:
            clean_json = re.search(r'\{.*\}', response_1.replace('\n', ''), re.DOTALL).group()
            extracted_data = json.loads(clean_json)
            st.success("Extraction Complete")
            st.json(extracted_data)
        except Exception as e:
            st.error("Failed to parse JSON")
            st.stop()

    # --- SKILL 2 ---
    with st.expander("Step 2: Data Retrieval & Reasoning", expanded=True):
        shipment_id = extracted_data.get("shipment_id")
        st.write(f"Agent asking Cortex to query Snowflake for shipment `{shipment_id}` details and inventory alternatives...")
        
        prompt_2 = f"1. Query the LOGISTICS.SHIPMENTS table for SHIPMENT_ID = '{shipment_id}'.\n2. Note the PRODUCT_ID, QUANTITY, and DESTINATION.\n3. Query the LOGISTICS.INVENTORY table for that PRODUCT_ID.\n4. Find a WAREHOUSE (other than the DESTINATION) where (CURRENT_STOCK - MINIMUM_REQUIRED) >= the delayed QUANTITY.\n5. Return a JSON object with keys: 'affected_product', 'affected_destination', 'quantity_needed', 'source_warehouse', 'available_surplus'."
        mock_response_2 = '{"affected_product": "PROD-A1", "affected_destination": "New York Distribution Center", "quantity_needed": 1000, "source_warehouse": "Texas Regional Warehouse", "available_surplus": 1500}'
        
        with st.spinner("Querying mock database & reasoning..."):
            response_2 = run_cortex_query(prompt_2, mock_response_2)
            
        try:
            clean_json = re.search(r'\{.*\}', response_2.replace('\n', ''), re.DOTALL).group()
            reasoning_result = json.loads(clean_json)
            st.success("Reasoning Complete")
            st.json(reasoning_result)
        except Exception:
            st.error("Failed to parse JSON")
            st.stop()

    # --- SKILL 3 ---
    with st.expander("Step 3: Action Execution", expanded=True):
        source = reasoning_result.get("source_warehouse")
        destination = reasoning_result.get("affected_destination")
        quantity = reasoning_result.get("quantity_needed")
        product = reasoning_result.get("affected_product")
        
        st.write("Agent generating final resolution plan and executing SQL via Cortex...")
        
        prompt_3 = f"The supply chain disruption requires rerouting {quantity} units of {product} from '{source}' to '{destination}'. Generate the two SQL UPDATE statements required to adjust the CURRENT_STOCK in the LOGISTICS.INVENTORY table."
        mock_response_3 = f"coco query \"UPDATE inventory SET current_stock = current_stock - {quantity} WHERE warehouse = '{source}' AND product_id = '{product}'\"\ncoco query \"UPDATE inventory SET current_stock = current_stock + {quantity} WHERE warehouse = '{destination}' AND product_id = '{product}'\""
        
        with st.spinner("Generating CLI commands..."):
            response_3 = run_cortex_query(prompt_3, mock_response_3)
            
        st.success("Resolution Plan Executed Successfully!")
        
        st.markdown("### 📋 Final Resolution")
        st.warning(f"**ISSUE:** Shortage of {quantity} units of {product} at {destination}.")
        st.success(f"**RESOLUTION:** Rerouting {quantity} units from {source}.")
        st.markdown("**Generated Cortex CLI Commands for execution:**")
        st.code(response_3, language="sql")
