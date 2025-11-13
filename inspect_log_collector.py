from utils.log_collector import LogCollector
from utils.plan_visualisor import PlanVisualisor
import json


logcollector = LogCollector("")
pv = PlanVisualisor()

path_err = '/Users/alexander/VSC_local/Wayang/AI_Wayang_Single/logs/log_20251106_141704.json'
path = '/Users/alexander/VSC_local/Wayang/AI_Wayang_Single/logs/log_20251106_151033.json'
path = '/Users/alexander/VSC_local/Wayang/AI_Wayang_Multi/logs/log_20251110_213352.json'
info, dataflow = logcollector.log_analysis(path, "Multi", True)

print(json.dumps(info, indent=4, ensure_ascii=False))
print("----")
print(dataflow)

pv.visualise_plan_from_log(path)

"""


"""