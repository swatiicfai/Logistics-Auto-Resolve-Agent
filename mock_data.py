import json

# Simulated Snowflake Database Tables

def get_shipments():
    """Returns a list of active shipments"""
    return [
        {
            "shipment_id": "SHP-4092",
            "origin": "Port of Los Angeles",
            "destination": "New York Distribution Center",
            "contents": {"product_id": "PROD-A1", "quantity": 1000},
            "status": "In Transit",
            "expected_arrival": "2026-08-10"
        },
        {
            "shipment_id": "SHP-8812",
            "origin": "Shenzhen",
            "destination": "Seattle Warehouse",
            "contents": {"product_id": "PROD-B2", "quantity": 500},
            "status": "Delayed",
            "expected_arrival": "2026-08-15"
        }
    ]

def get_inventory():
    """Returns current inventory across all warehouses"""
    return [
        {
            "warehouse": "New York Distribution Center",
            "product_id": "PROD-A1",
            "current_stock": 200,
            "minimum_required": 500
        },
        {
            "warehouse": "Texas Regional Warehouse",
            "product_id": "PROD-A1",
            "current_stock": 2500,  # Surplus!
            "minimum_required": 1000
        },
        {
            "warehouse": "Seattle Warehouse",
            "product_id": "PROD-B2",
            "current_stock": 50,
            "minimum_required": 100
        }
    ]

def query_snowflake(query_type, params=None):
    """
    Mock function to simulate querying data via Snowflake CoCo CLI.
    In reality, this would execute a command like:
    `coco query "SELECT * FROM inventory WHERE product_id = 'PROD-A1'"`
    """
    print(f"[Snowflake] Executing query: {query_type}...")
    
    if query_type == "get_shipment":
        shipments = get_shipments()
        for s in shipments:
            if s["shipment_id"] == params.get("shipment_id"):
                return s
        return None
        
    elif query_type == "check_inventory":
        inventory = get_inventory()
        results = []
        for i in inventory:
            if i["product_id"] == params.get("product_id"):
                results.append(i)
        return results

if __name__ == "__main__":
    print("Mock data loaded.")
    print(json.dumps(query_snowflake("get_shipment", {"shipment_id": "SHP-4092"}), indent=2))
