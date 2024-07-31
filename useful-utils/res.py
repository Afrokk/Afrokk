from typing import List, Dict, Any
# from ** import results
# from ** import Work
from rich.console import Console
from rich.panel import Panel
import json, pickle

console = Console()
r = results.Results()

def get_by_count(pipeline: str, count: int) -> List[Dict[str, Any]]:
    try:
        work = r.view(pipeline=pipeline, query={}, projection={}, skip=0, limit=count)
        console.print(work)
        return work
    except Exception as e:
        console.print(f"Error: {e}")
        return {}

def get_single_work_from_workflow_id(
    pipeline: str, workflow_id: str
) -> List[Dict[str, Any]]:
    """
    Retrieve a single work from the given workflow ID.

    Args:
        pipeline (str): The pipeline to use for the query.
        workflow_id (str): The workflow ID, e.g. 65e4c2b9c5e8320d351c0d7c

    Returns:
        List[Dict[str, Any]]: A list of dictionaries representing the retrieved work.

    Raises:
        Exception: If an error occurs during the query.

    """
    try:
        work = r.view(
            pipeline=pipeline, query={"id": workflow_id}, projection={}, limit=-1
        )
        console.print(work)
        return work
    except Exception as e:
        console.print(f"Error: {e}")
        return {}


def get_single_work_from_event_id(pipeline: str, event_id: str) -> List[Dict[str, Any]]:
    try:
        work = r.view(
            pipeline=pipeline,
            query={"event": [int(event_id)]},
            projection={},
            limit=-1,
        )
        console.print(work)
        return work
    except Exception as e:
        console.print(f"Error: {e}")
        return {}


def get_overlapping_events_count(pipeline1: str, pipeline2: str) -> int:
    """
    Get the count of overlapping events between two pipelines.

    Args:
        pipeline1 (str): The name of the first pipeline.
        pipeline2 (str): The name of the second pipeline.

    Returns:
        int: The count of overlapping events.

    Raises:
        Exception: If there is an error during the execution.

    """
    try:
        projection = {"event": True}
        projection["results.derived_parameters.arrival_time_UTC"] = True

        try:
            slice = r.view(
                pipeline=pipeline1, query={}, projection=projection, skip=0, limit=-1
            )
        except Exception as e:
            console.print(f"Error: {e}")
            return {}

        pipeline1_events = {}
        errors = 0

        for event in slice:
            try:
                pipeline1_events[event["event"][0]] = event["results"][
                    "derived_parameters"
                ]["arrival_time_UTC"]
            except Exception as e:
                errors += 1
                continue

        output = f"Total number of classifications in {pipeline1}: {len(slice)}\n"
        output += f"Total number of events in {pipeline1}: {len(pipeline1_events)}\n"
        output += f"Total number of errors in {pipeline1}: {errors}"

        overlap_count = r.count(
            pipeline=pipeline2, query={"event": {"$in": list(pipeline1_events.keys())}}
        )
        console.print(
            f"Total number events in {pipeline1} pipeline: {len(pipeline1_events)}"
        )
        console.print(f"Total number of overlapping events: {overlap_count}")
    except Exception as e:
        console.print(f"Error: {e}")
        return 0


def get_locked_events(pipeline: str) -> List[Dict[str, Any]]:
    """
    Retrieves locked events from a given pipeline.

    Args:
        pipeline (str): The pipeline to query.

    Returns:
        List[Dict[str, Any]]: A list of locked events as dictionaries (objects).

    Raises:
        Exception: If an error occurs during the query.

    """
    try:
        event = r.view(
            pipeline=pipeline,
            query={"results.locked": True},
            projection={
                "event": True,
                "plots": True,
                "products": True,
                "results": True,
            },
            skip=0,
            limit=1,
        )
        if not event:
            console.print(f"No locked events found in {pipeline}.")
            return event
        else:
            console.print(event)
            return event
    except Exception as e:
        console.print(f"Error: {e}")
        return {}


def get_locked_event_count(pipeline: str) -> List[Dict[str, Any]]:
    try:
        count = r.count(
            pipeline=pipeline,
            query={"results.locked": True},
        )
        if not count:
            console.print(f"No locked events found in {pipeline}.")
            return count
        else:
            console.print(f"There are {count} locked events in {pipeline}.")
            return count
    except Exception as e:
        console.print(f"Error: {e}")
        return {}


def lock_event_from_workflow_id(pipeline: str, workflow_id: str) -> None:
    try:
        work_object = get_single_work_from_workflow_id(pipeline, workflow_id)
        work_object[0]["results"]["locked"] = True
        console.print(work_object)
        response = r.update(work_object)
        output = f"Locking event {workflow_id}\n"
        output += f"Lock Successful." if response else f"Lock Failed."
        console.print(Panel(output))
    except Exception as e:
        console.print(f"Error: {e}")


def lock_event_from_event_id(pipeline: str, event_id: str) -> None:
    """
    Locks a single work/event in the database.

    Args:
        pipeline (str): The pipeline name.
        event_id (str): The event ID of the event to be locked,
        e.g. 270582780

    Returns:
        None
    """
    try:
        work_object = get_single_work_from_event_id(pipeline, event_id)
        work_object[0]["results"]["locked"] = True
        response = r.update(work_object)
        output = f"Locking event {event_id}\n"
        output += f"Lock Successful." if response else f"Lock Failed."
        console.print(Panel(output))
    except Exception as e:
        console.print(f"Error: {e}")


def unlock_single_event(pipeline: str, workflow_id: str) -> None:
    """
    Unlocks a single work/event in the database.

    Args:
        pipeline (str): The pipeline name.
        eworkflow_id (str): The workflow ID of the event to be locked,
        e.g. 65e4c2b9c5e8320d351c0d7c

    Returns:
        None
    """
    try:
        work_object = get_single_work_from_workflow_id(pipeline, workflow_id)
        work_object[0]["results"]["locked"] = False
        response = r.update(work_object)
        output = f"Unlocking event {workflow_id}\n"
        output += f"Unlock Successful." if response else f"Unlock Failed."
        console.print(Panel(output))
    except Exception as e:
        console.print(f"Error: {e}")


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


def get_all_old_works(pipeline, filename):
    """
    Gets all old works based on the given pipeline and filename.

    Args:
        pipeline (str): The pipeline to get old work from.
        filename (str): The name of the file containing the workflow IDs.

    Returns:
        None
    """
    old_work_objs: List[Dict][str, Any] = []

    def get_single_old_work(workflow_id: str) -> List[Dict[str, Any]]:
        """
        Helper Function:
        Retrieves a single old work item based on the provided workflow ID.

        Args:
            workflow_id (str): The ID of the workflow to retrieve.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the retrieved work item.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        try:
            work = r.view(
                pipeline=pipeline,
                query={"id": workflow_id, "config": None},
                projection={},
                limit=-1,
            )
            return work
        except Exception as e:
            print(f"Error: {e}")
            return {}

    def get_single_old_work_from_event_id(event_id: str) -> List[Dict[str, Any]]:
        """
        Helper Function:
        Retrieves a single old work from the given event ID.

        Args:
            event_id (str): The ID of the event.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the retrieved work.

        Raises:
            Exception: If an error occurs during the retrieval process.
        """
        try:
            work = r.view(
                pipeline=pipeline,
                query={"event": [int(event_id)], "config": None},
                projection={},
                limit=-1,
            )
            return work
        except Exception as e:
            print(f"Error: {e}")
            return {}

    try:
        with open(filename, "r") as file:
            for line in file:
                _, workflow_id = line.split()
                old_work = get_single_old_work(workflow_id)
                if old_work:
                    old_work_objs.append(get_single_old_work(workflow_id))

        # Temporary, to read from a 2nd file containing the event IDs:
        # with open("results_to_lock_with_event_id.txt", "r") as file:
        #     for line in file:
        #         event_id = line.strip()
        #         old_work = get_single_old_work_from_event_id(event_id)
        #         if old_work:
        #             old_work_objs.append(get_single_old_work_from_event_id(event_id))

        with open("old_work_objs.pkl", "wb") as f:
            pickle.dump(old_work_objs, f)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run functions here
