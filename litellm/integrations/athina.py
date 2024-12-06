import datetime



TOKEN_ACTION_MAPPING = {
    "openai": {
        "o1-mini": {
            "input_ratio":  3.0,
            "output_ratio":  12.0, 
        },
        "o1-preview": {
            "input_ratio": 15.0, 
            "output_ratio": 60.0,  
        },
        "gpt-4o-mini": {
            "input_ratio":  0.15,   
            "output_ratio":  0.6,  
        },
        "gpt-4o": {
            "input_ratio": 2.5,   
            "output_ratio": 10.0,  
        },
        "text-embedding-ada-002":{
            "input_ratio" :  0.1,
            "output_ratio": 0
        },
        "text-embedding-3-small":{
            "input_ratio" :  0.2,
            "output_ratio": 0
        },
        "text-embedding-3-large":{
            "input_ratio" :   0.13,
            "output_ratio": 0
        },
    }
}


def calculate_actions(llm_provider: str, language_model: str, num_input_tokens: int, num_output_tokens: int) -> float:
    provider_mapping = TOKEN_ACTION_MAPPING.get(llm_provider.lower(), TOKEN_ACTION_MAPPING["openai"])
    model_config = provider_mapping.get(language_model)
    
    if not model_config:
        return 0.0
        
    input_ratio = model_config.get("input_ratio", 0)
    output_ratio = model_config.get("output_ratio", 0)
    
    input_actions = math.ceil((input_ratio / 2000) * num_input_tokens * 100) / 100
    output_actions = math.ceil((output_ratio / 2000) * num_output_tokens * 100) / 100
    
    total_actions = input_actions + output_actions
    return total_actions

 
class AthinaLogger:
    def __init__(self):
        import os
        self.env = os.getenv("ENV")
        if self.env == "DEV":
            self.factory_collection = "factory_dev"

        elif self.env == "PROD":
            self.factory_collection = "factory"

        elif self.env == "PROD":
            self.factory_collection = "factory"
            
        self.pagos_admin_token = os.getenv("PAGOS_ADMIN_TOKEN")
        self.pagos_api_url = os.getenv("PAGOS_API_URL")

        self.db_client = os.getenv("MONGO_URL")
        

        self.headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {self.pagos_admin_token}'
        }   

    def log_event(self, kwargs, response_obj, start_time, end_time, print_verbose):
        import json
        import traceback

        import requests 

        try:
            data = {
                "language_model_id": kwargs.get("model"),
                "prompt_tokens": response_obj.get("usage", {}).get("prompt_tokens"),
                "completion_tokens": response_json.get("usage", {}).get(
                    "completion_tokens"
                ),
                "total_tokens": response_json.get("usage", {}).get("total_tokens"),
            }

            if (
                type(end_time) is datetime.datetime
                and type(start_time) is datetime.datetime
            ):
                data["_latency_ms"] = int(
                    (end_time - start_time).total_seconds() * 1000
                )

          
            data["created_at"] = datetime.utcnow()


            metadata = kwargs.get("litellm_params", {}).get("metadata", {})
            if metadata:
                for key in self.additional_keys:
                    if key in metadata:
                        data[key] = metadata[key]
            url = f"{self.pagos_api_url}/api/v1/usages/{org_id}/deduct/actions"

            response = requests.post(
                url,
                headers=self.headers,
                params={'count': data["_latency_ms"]}
            )
            import pdb
            
            pdb.set_trace()
            if response.status_code != 200:
                print_verbose(
                    f"Lyzr Logger Error - {response.text}, {response.status_code}"
                )
            else:
                print_verbose(f"Lyzr Logger Succeeded - {response.text}")
        except Exception as e:
            print_verbose(
                f"Lyzr Logger Error - {e}, Stack trace: {traceback.format_exc()}"
            )
            pass
