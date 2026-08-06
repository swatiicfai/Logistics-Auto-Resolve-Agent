# 📦 Logistics Auto-Resolve Agent

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://logistics-auto-resolve-agent-bu2wdxre6jewsaujrtvknb.streamlit.app)
[![YouTube Demo](https://img.shields.io/badge/YouTube-Watch_Demo-red?logo=youtube)](https://youtu.be/KK2Dl9Mo3zY)

> **Cortex Code CLI Hackathon 2026 Submission**  
> **Category:** Intelligent Workflow Automation Agent  
> **Team:** SnowQuery Ninjas  

---

## 🚀 Overview

The **Logistics Auto-Resolve Agent** is an autonomous AI workflow designed to proactively resolve supply chain disruptions. By bridging unstructured data (emails, alerts) with structured database operations, the agent eliminates the need for manual, time-consuming interventions.

When a shipment is delayed, the agent automatically:
1. **Ingests** the unstructured alert using Snowflake Cortex LLM.
2. **Retrieves** the affected products from the shipment database.
3. **Reasons** over the inventory database to find surplus stock in alternative warehouses.
4. **Executes** a resolution plan by drafting and executing the exact Snowflake CoCo CLI commands required to reroute the inventory.

---

## 🛠️ Architecture & Skills

This agent operates using three modular skills:

### 1. Ingestion & Anomaly Detection
Parses unstructured alert data (e.g., emails about delayed shipments) using Cortex LLM to extract structured entities like `shipment_id` and `delay_days`.

### 2. Data Retrieval & Reasoning
Queries a Snowflake database (Shipments and Inventory tables) to assess the impact of the delay and logically identifies alternative warehouses with surplus stock to fulfill shortages.

### 3. Action Execution
Generates precise SQL `UPDATE` statements via the Cortex CLI to reroute inventory and execute the resolution plan autonomously.

---

## 💻 Try the Prototype

We have built a fully functional web interface for our agent. You can test the autonomous resolution workflow live:

👉 **[Live Streamlit Dashboard](https://logistics-auto-resolve-agent-bu2wdxre6jewsaujrtvknb.streamlit.app)**

---

## 📂 Project Structure

- `app.py`: The Streamlit web application providing the user interface for the agent workflow.
- `agent.py`: Contains the core logic for the 3 Agent Skills and the main orchestration loop.
- `mock_data.py`: Simulates the Snowflake database with mock shipments and inventory data.
- `requirements.txt`: Dependencies required to run the prototype.

---

## 🏃‍♂️ How to Run Locally

1. Clone this repository:
   ```bash
   git clone https://github.com/swatiicfai/Logistics-Auto-Resolve-Agent.git
   cd Logistics-Auto-Resolve-Agent
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
   Or run the CLI version:
   ```bash
   python agent.py
   ```

---

## 📈 Business Impact

- **Speed:** Reduces disruption response times from hours to seconds.
- **Accuracy:** Eliminates manual data entry errors.
- **Scalability:** The modular design easily scales to handle thousands of simultaneous alerts across global warehouse networks.
- **Future Integration:** Can be hooked directly into enterprise ERP systems (SAP, Oracle) to automatically trigger new supplier purchase orders.
