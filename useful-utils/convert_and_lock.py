from typing import List, Dict, Any
from * import HTTPContext # redacted
from rich.console import Console

ResultsContext = HTTPContext(backends=["results"])

r = ResultsContext.results
console = Console()
 
PIPELINE = "" # redacted
FILENAME = "" # redacted

def convert_and_update(old_work_obj: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    converted_obj = [{}]
    sample_new_obj = r.get_by_id(PIPELINE, ["ID"]) # redacted
    converted_obj[0] = old_work_obj[0]
    converted_obj[0]["config"] = sample_new_obj[0]["config"]
    console.print(r.update(converted_obj))
    console.print("Conversion successful.")
    return converted_obj

console.print("Locked Count Before in Pipeline: ", r.get_locked_count(PIPELINE))

with open(FILENAME, "r") as f:
    curr_locked_count = 0
    old_objs_converted = 0

    for line in f:
        _, workflow_id = line.strip().split()
        response = r.get_by_id(PIPELINE, [workflow_id])
        if not response[0]["config"]:
            console.print(f"Converting and Updating {workflow_id}")
            convert_and_update(response)
            console.print(r.lock(PIPELINE, [workflow_id]))
            old_objs_converted += 1
            curr_locked_count += 1
        else:
            console.print(r.lock(PIPELINE, [workflow_id]))
            curr_locked_count += 1

    f.seek(0)
    console.print("Total Work Count in file (to be locked): ", len(f.readlines()))
    console.print(f"Successfully Locked {curr_locked_count} works.")
    console.print(f"Successfully Converted {old_objs_converted} old work objects.")

console.print("Locked Count After in Pipeline: ", r.get_locked_count(PIPELINE))
