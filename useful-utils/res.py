from typing import List, Dict, Any
# from ** import results
# from ** import Work
from rich.console import Console
from rich.panel import Panel
import json, pickle

console = Console()
r = results.Results()

def lock_events_from_file(pipeline: str, filename: str) -> None:
    """
    Locks events from a file.
    Reads from file in format: 'event_id<space>workflow_id'

    Args:
        pipeline (str): The pipeline to lock events for.
        filename (str): The path to the file containing the work IDs.

    Returns:
        None
    """
    try:
        with open(filename, "r") as file:
            for line in file:
                _, workflow_id = line.split()
                lock_event_from_workflow_id(pipeline, workflow_id)
    except Exception as e:
        console.print(f"Error: {e}")


def lock_events_from_file_with_event_id(pipeline, filename):
    """
    Locks events from a file that contains just the event IDs.

    Args:
        pipeline (Pipeline): The pipeline object.
        filename (str): The path to the file containing event IDs.

    Raises:
        Exception: If there is an error while processing the file.

    """
    try:
        with open(filename, "r") as file:
            for line in file:
                lock_event_from_event_id(pipeline, line)
    except Exception as e:
        console.print(f"Error: {e}")


def get_duplicate_event_counts_from_file(
    pipeline: str, filename: str
) -> List[Dict[str, int]]:
    """
    Reads event IDs from a file, checks each event in the database for successful
    duplicate runs, and writes the output to a file.

    Args:
        pipeline (str): The pipeline name.
        filename (str): The path to the file containing the event IDs.

    Returns:
        List[Dict[str, int]]: A list of dictionaries where each dictionary contains
        the event ID as the key and its count as the value.
    """
    duplicates = []
    try:
        with open(filename, "r") as file:
            for line in file:
                parts = line.split()
                if len(parts) == 1:
                    event_id = int(parts[0])
                else:
                    event_id, _ = parts
                    event_id = int(event_id)
                count = r.count(
                    pipeline=pipeline, query={"event": [event_id], "status": "success"}
                )
                duplicates.append({event_id: count})

        output_filename = f"{pipeline}_duplicate_event_counts.txt"
        with open(output_filename, "w") as output_file:
            for duplicate in duplicates:
                output_file.write(json.dumps(duplicate) + "\n")
    except Exception as e:
        console.print(f"Error: {e}")
    finally:
        return duplicates


def convert(works: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert a list of works from old workflow objects to new workflow objects
    that are supported by the new API.

    Args:
        works (List[Dict[str, Any]]): A list of old workflow work objects.

    Returns:
        List[Dict[str, Any]]: A list of payloads (converted), where each payload is represented as a dictionary.

    Note:
    Outliers (works with no results) are written to a file (outliers.txt).
    Converted objects are written to a text file (new_work_objs.txt) and
    pickled (new_work_objs.pkl).
    Convrted objects are locked in the database by default.

    """
    converted: List[Dict[str, Any]] = []
    outliers = Console(file=open("outliers.txt", "at"))

    for work in works:
        work.pop("config")
        if not work["results"]:
            outliers.print("The following events are missing results: \n")
            outliers.print(
                {
                    "workflow_id": work["id"],
                    "event_ID": work["event"],
                    "products": work["products"],
                    "plots": work["plots"],
                }
            )
        else:
            work["results"]["locked"] = True
            payload = Work(**work).payload
            converted.append(payload)

    return converted


def convert_from_file(filename: str) -> None:
    """
    Converts old work objects from a .pkl file to new work objects.

    Args:
        filename (str): The path to the pickle file containing the data.

    Returns:
        None
    """
    with open(filename, "rb") as f:
        data_loaded = pickle.load(f)
        converted = []
        new_work_objs_file = Console(file=open("new_work_objs.txt", "at"))

        for work in data_loaded:
            # Calls convert with each work object to convert it.
            # The output is written to a .txt and a .pkl file.
            converted.append(convert(work))

        console.print(converted)
        new_work_objs_file.print(converted)

        with open("new_work_objs.pkl", "wb") as f:
            pickle.dump(converted, f)

if __name__ == "__main__":
    # Run functions here
