from utils.log_collector import LogCollector
import json


logcollector = LogCollector("")

path = '/Users/alexander/VSC_local/Wayang/AI_Wayang_Single/logs/log_20251106_141140.json'
info, dataflow = logcollector.log_analysis(path)

print(json.dumps(info, indent=4, ensure_ascii=False))
print("----")
print(dataflow)