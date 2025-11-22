from typing import Tuple, List
import pandas as pd
from pandas import DataFrame
from utils.log_collector import LogCollector
import os

class Tester:

    def __init__(self):
        pass

    
    def get_testdata(self, architecture_list: List, val_folder_path: str) -> DataFrame:
        """
        Get a full dataset for testing
        """
        df_queries = self.get_validation_data(val_folder_path)

        df_arc = pd.DataFrame(architecture_list)

        # For cross join
        df_queries["id"] = 1
        df_arc["id"] = 1

        df_test = df_queries.merge(df_arc, on="id").drop(columns="id")

        return df_test


    def get_evaluation_data(self, log_folder: str, val_folder_path: str) -> DataFrame:
        """
        Get results from tests

        Works for both closed and open data sources because of inner join
        """

        # Get testqueries and results
        df_val = self.get_validation_data(val_folder_path)

        eval_data = []

        log_paths = []
        for file in os.listdir(log_folder):
            if file.endswith(".json"):
                full_path = os.path.join(log_folder, file)
                log_paths.append(full_path)
        

            # Get data from each log
        for log_path in log_paths:
            eval_dict = self.evaluate_run(log_path)
            eval_data.append(eval_dict)
            
        df_eval = pd.DataFrame(eval_data)

        df_joined = df_eval.merge(df_val, left_on="query", right_on="user_request", how="inner")

        # Make outputs last
        cols = df_joined.columns.tolist()
        last = ["output_test", "output_act"]

        new_cols = [c for c in cols if c not in last] + last

        df = df_joined[new_cols]

        return df

    
    def get_validation_data(self, folder_path: str) -> DataFrame:
        """
        Get validation data
        """
        data = []
        test_files = []

        for file in os.listdir(folder_path):
            if file.endswith(".txt"):
                test_files.append(file)
        
        for file in test_files:
            filepath = os.path.join(folder_path, file)
            filename = os.path.splitext(os.path.basename(file))[0]

            user_request = ""
            sql_query = ""
            output_lines = []

            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # USER_REQUEST
            for line in lines:
                if line.startswith("USER_REQUEST:"):
                    user_request = line.split("USER_REQUEST:")[1].strip()
                    break
            
            # SQL_QUERY
            sql_start = None
            sql_end = None
            for i, line in enumerate(lines):
                if line.startswith("SQL_QUERY:"):
                    sql_start = i + 1
                if line.startswith("OUTPUT:"):
                    sql_end = i
                    break
            
            if sql_start is not None and sql_end is not None:
                sql_query = "".join(lines[sql_start:sql_end]).strip()

            # OUTPUT
            output_start = None
            for i, line in enumerate(lines):
                if line.startswith("OUTPUT:"):
                    output_start = i + 1
                    break

            if output_start is not None:
                for i in range(output_start, min(output_start + 5, len(lines))):
                    output_lines.append({
                        "line": i - output_start + 1,
                        "data": lines[i].strip()
                    })

            data.append({
                "test_name": filename,
                "user_request": user_request,
                "sql_query": sql_query,
                "output_act": output_lines
            })

        return pd.DataFrame(data)


    def evaluate_run(
        self,
        log_path: str
    ) -> dict:
        """
        Return af dict with relevant information to a log - including output

        """
        # Initialize log collector
        lc = LogCollector(log_path)

        query, status, actual_debugger, filepath, info, dataflow = lc.get_log_info(
            log_path, "", ""
        )

        # Get top 5 lines from output file

        lines = []

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for i in range(5):
                    line = f.readline()
                    if not line:
                        break
                    lines.append({"line": i + 1, "data": line.strip()})

        except Exception:
            # Hvis filen ikke kan åbnes
            lines = [{"line": 1, "data": "Couldn't open file"}]

        dictionary = {
            "architecture": info["architecture"],
            "model": info["model"],
            "reasoning": "medium",
            "query": query,
            "status": status,
            "debugger": actual_debugger,
            "output_test": lines,
            "dataflow": dataflow,
            "debug_itr": info["debug_itr"],
            "errors_total": info["errors_total"],
            "errors_validation": info["errors_validation"],
            "errors_wayang": info["errors_wayang"],
            "total_tokens": info["total_tokens"],
            "total_input_tokens": info["total_input_tokens"],
            "total_output_tokens": info["total_output_tokens"],
            "total_reasoning_tokens": info["total_reasoning_tokens"],
            "total_netto_input_tokens": info["total_netto_input_tokens"],
            "log_path": log_path,
            "filepath": filepath,
            "null_value_file_path": info["null_value_filepath"]
        }

        return dictionary
