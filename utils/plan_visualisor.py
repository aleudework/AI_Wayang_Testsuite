from typing import List
from graphviz import Digraph
import json

class PlanVisualisor():
    """
    Takes an Wayang Plan and visualizes it
    """

    def __init__(self):
        pass

    def visualize_from_log(self, log_path: str):
        """
        Gets log path og visualize "newest" valid Wayang JSON plan in a log

        Args:
            log_path (str): Path to log

        """
        
        # Open log file
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)

        # Initialize list for operations
        operations = []

        # Find the first plan (reversed) in the log / the final plan
        for data in reversed(log):
            if isinstance(data.get("log"), dict):
                plan = data["log"].get("plan", {})
                if isinstance(plan, dict) and "operators" in plan:
                    operations = plan["operators"].copy() # Copy the operatins in the plan to the operation list

        # Visualize plan
        self._visualize_wayang_plan(operations)
        print("[INFO] Wayang plan visualized")


    def visualize_from_plan(self, wayang_plan: json):
        """
        Visualize a JSON Wayang plan

        Args:
            wayang_plan (json): Visualize a JSON Wayang Plan.

        """

        # Get operations
        operations = wayang_plan.get(operations, [])

        # Visualize plan
        self._visualize_wayang_plan(operations)


    def _visualize_wayang_plan(self, operations: List, filename: str = "wayang_plan"):
        """
        Visualizes Wayang Plan (picture) from a list of operations

        Args:
            operations (List): List of operations / plan
            filename (str): Name of visualized plan picture / file

        Returns:
            visualization of plan
        """

        # Initialize graph
        graph = Digraph()

        # Add nodes to graph
        for op in operations:
            label = f"{op['id']}\n{op['operatorName']}"
            graph.node(str(op["id"]), label)

        # Add edges
        for op in operations:
            for edge in op.get("input", []):
                graph.edge(str(edge), str(op["id"]))
        
        # Render graph (in PDF)
        graph.render(filename, view=True)

