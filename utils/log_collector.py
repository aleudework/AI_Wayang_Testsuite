from pathlib import Path
from pandas import DataFrame
from typing import Tuple, Dict, List
import pandas as pd
import re
import json
from urllib.parse import urlparse


class LogCollector:
    """
    Collects data from logs for inspection and testing.
    """

    def __init__(self, log_folder):
        self.log_folder = Path(log_folder)

    def get_log_info(
        self, log_path: str, architecture_name: str = "Standard", debugger: bool = True
    ) -> Tuple[str, str, str, str, dict, List]:
        """
        Analysis a log and return information - Important for multiple log runs to compare results.

        """

        try:
            # Url path
            info, dataflow = self.log_analysis(log_path, architecture_name, debugger)

            # Url path
            url = info["filepath"]
            parsed_url = urlparse(url)
            filepath = parsed_url.path

            debugger = info["debugger"]
            status = info["status"]
            query = info["query"]

            return query, status, debugger, filepath, info, dataflow

        except Exception as e:
            print(f"[Error] {e}")

    def log_analysis(
        self, log_path: str, architecture_name: str = "Standard", debugger: bool = True
    ) -> Tuple[dict, List]:
        """
        Analysis a session from json log.

        """

        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log = json.load(f)

            info = {}
            info["agents"] = {}
            info["classes"] = {}
            dataflow = []

            debugger_counter = 0
            total_errors = 0
            val_errors = 0
            wayang_errors = 0
            total_input_tokens = 0
            total_netto_input_tokens = 0
            total_output_tokens = 0
            total_reasoning_tokens = 0
            total_total_tokens = 0
            output_filepath = ""
            null_value_filepath = ""

            agents = set()
            models = set()
            classes = set()

            latest_plan = None

            # Reverse loop, get last plan (the finished one)
            for item in reversed(log):
                if isinstance(item.get("log"), dict):
                    plan = item["log"].get("plan", {})
                    if isinstance(plan, dict) and "operators" in plan:
                        latest_plan = plan
            # Get textfile path for output
            if latest_plan:
                operations = latest_plan["operators"]
                # Find textfile and output
                for op in reversed(operations):
                    if op.get("operatorName") == "textFileOutput":
                        output_filepath = op.get("data", {}).get("filename")
                        break

            for item in log:

                # User query
                if item["title"].startswith("User query:"):
                    info["query"] = item["log"]
                    dataflow.append("Query")
                
                # Architecture
                if item["title"].startswith("Architecture"):
                    data = item["log"]
                    info["model"] = data["model"]
                    info["architecture"] = data["architecture"]
                    info["debugger"] = data["debugger"]
                    

                # Class / Wayang
                if item["title"].startswith("Class:") or item["title"].startswith(
                    "Wayang:"
                ):

                    instance = item["title"].split(":", 1)[1].strip().split()[0]
                    classes.add(instance)
                    dataflow.append(instance)

                    if instance not in info["classes"]:
                        info["classes"][instance] = {"count": 1, "errors": 0}
                    else:
                        info["classes"][instance]["count"] += 1

                # Errors
                if item["title"].startswith("Err:"):
                    instance = item["title"].split(":", 1)[1].strip().split()[0]
                    if instance in info["classes"]:
                        info["classes"][instance]["errors"] += 1
                        total_errors += 1

                    if instance == "PlanValidator":
                        val_errors += 1

                    if instance == "Wayang":
                        wayang_errors += 1

                # Final status
                if item["title"].startswith("Final:"):
                    status = item["title"].split(":", 1)[1].strip().split()[0]
                    info["status"] = status
                    dataflow.append(status)
                else:
                    info["status"] = "Unsucessful"

                # Text file error
                if item["title"].startswith("Err: Wayang error"):
                    output_text = item["log"]["output"]

                    if "JavaTextFileSink" in output_text:
                        match = re.search(r"file:///[^]\s)]+", output_text)
                        if match:
                            filepath = match.group(0)
                            null_value_filepath = filepath


                # Agent usage
                if item["title"].startswith("Agent Usage:"):

                    agent = item["title"].split(":", 1)[1].strip().split()[0]
                    agents.add(agent)
                    dataflow.append(agent)

                    if agent == "DebuggerAgent" or agent == "DebuggerAgent.":
                        debugger_counter += 1

                    if agent not in info["agents"]:
                        info["agents"][agent] = {
                            "count": 0,
                            "model": 0,
                            "input_tokens": 0,
                            "netto_input_tokens": 0,
                            "reasoning_tokens": 0,
                            "output_tokens": 0,
                            "total_tokens": 0,
                            "usages": [],
                        }

                    model = item["log"]["model"]
                    usage = item["log"]["usage"]

                    info["agents"][agent]["usages"].append(usage)
                    info["agents"][agent]["count"] += 1
                    info["agents"][agent]["model"] = model

                    input_tokens = usage["input_tokens"]
                    output_tokens = usage["output_tokens"]
                    cached_tokens = usage["input_tokens_details"]["cached_tokens"]
                    reasoning_tokens = usage["output_tokens_details"][
                        "reasoning_tokens"
                    ]
                    total_tokens = usage["total_tokens"]

                    netto_input_tokens = input_tokens - cached_tokens

                    info["agents"][agent]["input_tokens"] += input_tokens
                    info["agents"][agent]["netto_input_tokens"] += netto_input_tokens
                    info["agents"][agent]["reasoning_tokens"] += reasoning_tokens
                    info["agents"][agent]["output_tokens"] += output_tokens
                    info["agents"][agent]["total_tokens"] += total_tokens

                    models.add(model)

                    total_input_tokens += input_tokens
                    total_netto_input_tokens += netto_input_tokens
                    total_output_tokens += output_tokens
                    total_reasoning_tokens += reasoning_tokens
                    total_total_tokens += total_tokens

            info["models"] = list(models)
            info["used_agents"] = list(agents)
            info["used_classes"] = list(classes)
            info["total_input_tokens"] = total_input_tokens
            info["total_netto_input_tokens"] = total_netto_input_tokens
            info["total_output_tokens"] = total_output_tokens
            info["total_reasoning_tokens"] = total_reasoning_tokens
            info["total_tokens"] = total_total_tokens
            info["debug_itr"] = debugger_counter
            info["errors_validation"] = val_errors
            info["errors_wayang"] = wayang_errors
            info["errors_total"] = total_errors
            info["dataflow"] = dataflow
            info["architecture2"] = architecture_name
            info["debugger2"] = debugger
            info["filepath"] = output_filepath
            info["null_value_filepath"] = null_value_filepath

            return info, dataflow

        except Exception as e:
            print(f"[Error] {e}")
            return {}, []
