import time
from connection import DatabaseSessionManager
import requests
import json
from typing import Any, Dict, List

def register_anomaly_triggers(
    threshold: float = 5.0,
    batch_size: int = 1,
    delay_minutes: int = 1
) -> List[Dict[str, Any]]:
    """Register triggers for anomalous metrics.
    
    Args:
        threshold: Minimum anomaly score to trigger
        batch_size: Number of requests to process in each batch
        delay_minutes: Minutes to wait between batches
    """
    results = []
    
    try:
        query = f"""
            SELECT 
                agent_id,
                anomaly_flags
            FROM deltamesh_fact.agent_kpi_fact 
            WHERE anomaly_score > {threshold}
        """
        
        db_manager = DatabaseSessionManager()
        with db_manager.session(using="deltamesh_fact") as session:
            result = session.query(query)
            rows = [dict(row) for row in result.named_results()]
        import pdb
        pdb.set_trace()
        print(ngrok)
        url = f"{ngrok}/api/triggers/register/"
        
        for i, row in enumerate(rows):
            try:
                anomaly_flags = json.loads(row.get('anomaly_flags', '{}'))

                formatted_metrics = {
                    metric: {
                        'z_score': str(details.get('z_score', '')),
                        'direction': details.get('direction', ''),
                        'severity': details.get('severity', '')
                    }
                    for metric, details in anomaly_flags.items()
                }
                
                payload = {
                    "role": "agent",
                    "entity_id": row.get('agent_id'),
                    "metrics": formatted_metrics,
                    "description": f"Anomaly detected with score above {threshold}"
                }
                
                print("Sending payload:", json.dumps(payload, indent=2))
                
                response = requests.post(
                    url, 
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=10
                )
                
                results.append({
                    "status": response.status_code,
                    "response": response.json(),
                    "payload": payload
                })
            
            except json.JSONDecodeError as je:
                print(f"Error parsing JSON for agent {row.get('agent_id')}: {je}")
                results.append({
                    "status": "error",
                    "error": f"Invalid JSON in anomaly_flags: {je}",
                    "payload": {"agent_id": row.get('agent_id')}
                })
            except Exception as e:
                print(f"Error processing agent {row.get('agent_id')}: {e}")
                results.append({
                    "status": "error",
                    "error": str(e),
                    "payload": {"agent_id": row.get('agent_id')}
                })

            # Batching logic
            if (i + 1) % batch_size == 0 and (i + 1) < len(rows):
                print(f"Batch complete. Sleeping for {delay_minutes} minute(s)...")
                time.sleep(delay_minutes * 60)
                
    except Exception as e:
        print(f"Error in register_anomaly_triggers: {e}")
        if 'rows' in locals():
            print(f"Query result: {rows}")
        raise
    
    return results
