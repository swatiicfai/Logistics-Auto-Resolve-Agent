# Supply Chain Disruption Resolution Agent

This is a prototype submitted for the **Intelligent Workflow Automation Agent** category.

## Overview
This agent simulates an autonomous AI workflow that integrates with Snowflake CoCo CLI to resolve supply chain disruptions. 
When a shipment is delayed, the agent automatically:
1. **Ingests** the unstructured alert (e.g., an email from a port).
2. **Retrieves** the affected products from the shipment database.
3. **Reasons** over the inventory database to find surplus stock in alternative warehouses.
4. **Executes** a resolution plan by drafting the exact Snowflake CoCo CLI commands required to reroute the inventory.

## Project Structure
- `mock_data.py`: Simulates the Snowflake database with mock shipments and inventory data.
- `agent.py`: Contains the 3 Agent Skills and the main orchestration loop.

## How to Run the Prototype
1. Ensure you have Python installed.
2. Clone this repository or download the files.
3. Open a terminal in the project directory.
4. Run the agent script:
   ```bash
   python agent.py
   ```

## Example Output
The agent will ingest a simulated alert: `"URGENT: Shipment SHP-4092 from LA Port is delayed by 4 days due to severe weather conditions."`

It will then output its thought process, the mocked Snowflake queries, and finally output a generated resolution plan like this:
```
*** SUPPLY CHAIN DISRUPTION RESOLUTION ***
ISSUE: Shortage of 1000 units of PROD-A1 at New York Distribution Center.
RESOLUTION: Rerouting 1000 units from Texas Regional Warehouse.

[GENERATED COCO CLI COMMAND FOR EXECUTION]
coco query "UPDATE inventory SET current_stock = current_stock - 1000 WHERE warehouse = 'Texas Regional Warehouse' AND product_id = 'PROD-A1'"
coco query "UPDATE inventory SET current_stock = current_stock + 1000 WHERE warehouse = 'New York Distribution Center' AND product_id = 'PROD-A1'"
```
