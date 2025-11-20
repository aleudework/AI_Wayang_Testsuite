# Run the test

import sys
import pandas as pd
sys.path.append("/Users/alexander/VSC_local/Wayang/Client")

from mcpclient import MCPClient
from utils.log_collector import LogCollector


if __name__ == "__main__":
    # Initialize client
    client = MCPClient()

    # Get testdata
    path_to_testdata = '/Users/alexander/VSC_local/Wayang/AI_Wayang_Testsuite/closed_dataset_multi.parquet'
    df_testdata = pd.read_parquet(path_to_testdata)

    # Test by loading schemas
    sc = client.call_tool("load_schemas")
    print(sc)

    for index, row in df_testdata.iterrows():
        id = row["id"]
        user_request = row["user_request"]
        model = row["model"]
        architecture = row["name"]
        debugger = row["debugger"]

        arguments = {
            "describe_wayang_plan": user_request,
            "model": model,
            "reasoning": "low",
            "use_debugger": debugger
        }

        print(f"== Test user_request: {id} | {model} | {architecture} | {debugger} ==")

        result = client.call_tool("query_wayang", arguments)
    
    print("Done")

