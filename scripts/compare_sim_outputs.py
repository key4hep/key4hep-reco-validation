import argparse
from podio.root_io import Reader
import numpy as np
import os
from tqdm import tqdm

# Dictionary defining which members to compare for each collection type
members_dict = {
    "MCParticle": {
        "continuous": ["Charge", "Mass", "Time"],
        "discrete": ["PDG", "GeneratorStatus", "SimulatorStatus"],
        "vector": ["Momentum", "Vertex", "Endpoint", "MomentumAtEndpoint", "Spin"],
    },
    "CaloHitContribution": {
        "continuous": ["Energy", "Time"],
        "discrete": ["PDG"],
        "vector": ["StepPosition"],
    },
    "SimCalorimeterHit": {
        "continuous": ["Energy"],
        "discrete": ["CellID"],
        "vector": ["Position"],
    },
    "SimTrackerHit": {
        "continuous": ["EDep", "Time", "PathLength"],
        "discrete": ["CellID", "Quality"],
        "vector": ["Position", "Momentum"],
    },
}

relations_dict = {
    "MCParticle": ["Parents", "Daughters"],
    "CaloHitContribution": ["Particle"],
    "SimCalorimeterHit": ["Contributions"],
    "SimTrackerHit": ["Particle"],
}

def parse_args():
    """
    Parse command-line arguments for new and reference files.
    """
    parser = argparse.ArgumentParser(description="Compare hits from new and reference files")
    parser.add_argument("--new-file", default="output_calo_digi.root", help="New output file")
    parser.add_argument("--reference-file", default="output_REC.edm4hep.root", help="Reference output file")
    return parser.parse_args()

def add_bad_hit(err_dict, frame, collection, member, bad_hit):
    """
    Record the index of a hit that differs between new and reference files.
    """
    if member not in err_dict[f'Frame[{frame}]'][f'Collection: {collection}']["members"]:
        err_dict[f'Frame[{frame}]'][f'Collection: {collection}']["members"][member] = {"bad_hits": []}
    err_dict[f'Frame[{frame}]'][f'Collection: {collection}']["members"][member]["bad_hits"].append(bad_hit)

def get_collection_members(collection, members_dict):
    """
    Determine which members to compare for a given collection based on its type.
    """
    for collection_from_dict, members in members_dict.items():
        if collection_from_dict in str(type(collection)):
            return members
    return {"continuous": [], "discrete": [], "vector": []}

def compare_hits(hits_new, hits_reference, members, i, collection, err_dict):
    """
    Compare hits between new and reference collections for all specified members.
    Returns statistics for each member.
    """
    lists_for_stats = {"continuous": {}, "discrete": {}, "vector": {}}
    # Initialize lists for statistics
    for member in members["continuous"]:
        lists_for_stats["continuous"][member] = []
    for member in members["discrete"]:
        lists_for_stats["discrete"][member] = []
    for member in members["vector"]:
        lists_for_stats["vector"][member] = []

    # Compare each hit in the collections
    for j, (hit_new, hit_reference) in enumerate(zip(hits_new, hits_reference)):
        # Compare continuous members (e.g., energies)
        new_getters = {member: getattr(hit_new, f'get{member}') for member in lists_for_stats["continuous"].keys()}
        ref_getters = {member: getattr(hit_reference, f'get{member}') for member in lists_for_stats["continuous"].keys()}
        for member in lists_for_stats["continuous"].keys():
            new_val = new_getters[member]()
            ref_val = ref_getters[member]()
            if new_val != ref_val:
                add_bad_hit(err_dict, i, collection, member, j)
            lists_for_stats["continuous"][member].append(
                (new_val - ref_val) / ref_val if ref_val != 0 else 0
            )
        # Compare discrete members (e.g., IDs)
        for member in lists_for_stats["discrete"].keys():
            if getattr(hit_new, f'get{member}')() != getattr(hit_reference, f'get{member}')():
                lists_for_stats["discrete"][member].append(1)
                add_bad_hit(err_dict, i, collection, member, j)
            else:
                lists_for_stats["discrete"][member].append(0)
        # Compare 3-vector members (e.g., positions, momenta)
        for member in lists_for_stats["vector"].keys():
            vec_new = getattr(hit_new, f'get{member}')()
            vec_ref = getattr(hit_reference, f'get{member}')()
            disp_x = vec_new.x - vec_ref.x
            disp_y = vec_new.y - vec_ref.y
            disp_z = vec_new.z - vec_ref.z
            disp_norm = np.linalg.norm([disp_x, disp_y, disp_z])
            ref_norm = np.linalg.norm([vec_ref.x, vec_ref.y, vec_ref.z])
            rel_disp_err = disp_norm / ref_norm if ref_norm != 0 else 0
            if rel_disp_err > 0:
                add_bad_hit(err_dict, i, collection, member, j)
            lists_for_stats["vector"][member].append(rel_disp_err)
    return lists_for_stats

def process_event(frame_new, frame_reference, members_dict, i, err_dict, comparison_dict):
    """
    Compare all collections in a single event (frame) between new and reference files.
    Records errors and statistics.
    """
    reference_collections = frame_reference.getAvailableCollections()
    new_collections = frame_new.getAvailableCollections()
    # Check for missing collections
    if len(reference_collections) != len(new_collections):
        missing_in_new = set(reference_collections) - set(new_collections)
        missing_in_reference = set(new_collections) - set(reference_collections)
        if missing_in_new:
            err_dict[f"Frame[{i}]"]["Errors"].append(
                {"Collections missing in new": missing_in_new}
            )
        elif missing_in_reference:
            err_dict[f"Frame[{i}]"]["Errors"].append(
                {"Collections missing in reference": missing_in_reference}
            )
        else:
            err_dict[f"Frame[{i}]"]["Errors"].append(
                {"Collections are different in length": f"{len(reference_collections)} vs {len(new_collections)}"}
            )
    # Only compare collections present in both files
    common_collections = [c for c in reference_collections if c in new_collections]
    for collection in common_collections:
        err_dict[f"Frame[{i}]"][f"Collection: {collection}"] = {"Errors": [], 'members': {}}
        comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"] = {}
        hits_new = frame_new.get(collection)
        hits_reference = frame_reference.get(collection)
        # Check for different number of hits
        if len(hits_new) != len(hits_reference):
            err_dict[f"Frame[{i}]"][f"Collection: {collection}"]["Errors"].append(
                {"Number of hits differ": f"{len(hits_new)} vs {len(hits_reference)}"}
            )
        # Get members to compare for this collection
        members = get_collection_members(hits_new, members_dict)
        # Compare hits and collect statistics
        lists_for_stats = compare_hits(hits_new, hits_reference, members, i, collection, err_dict)
        # Store mean statistics for each member
        for member, values in lists_for_stats["continuous"].items():
            comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Continuous: {member}"] = np.mean(values) if values else None
        for member, values in lists_for_stats["discrete"].items():
            comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Discrete: {member}"] = np.mean(values) if values else None
        for member, values in lists_for_stats["vector"].items():
            comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Vector: {member}"] = np.mean(values) if values else None

def gen_error_string(err_dict):
    """
    Generate a human-readable string summarizing all errors found during comparison.
    """
    error_string = []
    error_string.append("\nErrors found during comparison:\n")
    for frame, frame_errors in err_dict.items():
        frame_has_errors = False
        if "Errors" in frame_errors and frame_errors["Errors"]:
            frame_has_errors = True
        collections_with_errors = []
        for collection_key, collection_errors in frame_errors.items():
            if collection_key == "Errors":
                continue
            has_collection_error = (
                ("Errors" in collection_errors and collection_errors["Errors"])
                or any(
                    "bad_hits" in member_info and member_info["bad_hits"]
                    for member_info in collection_errors.get("members", {}).values()
                )
            )
            if has_collection_error:
                collections_with_errors.append(collection_key)
                frame_has_errors = True
        if frame_has_errors:
            error_string.append(f"{frame}:")
            if "Errors" in frame_errors and frame_errors["Errors"]:
                for err in frame_errors["Errors"]:
                    error_string.append(f"  General error: {err}")
            for collection_key in collections_with_errors:
                collection_errors = frame_errors[collection_key]
                error_string.append(f"  {collection_key}:")
                if "Errors" in collection_errors and collection_errors["Errors"]:
                    for err in collection_errors["Errors"]:
                        error_string.append(f"    Error: {err}")
                if "members" in collection_errors:
                    for member, member_info in collection_errors["members"].items():
                        if "bad_hits" in member_info and member_info["bad_hits"]:
                            error_string.append(f"    Member '{member}' bad hit indices: {member_info['bad_hits']}")
    return "\n".join(error_string)

def summarize_offsets(comparison_dict, err_dict):
    """
    Summarize the offsets (differences) between new and reference files.
    Includes per-collection and per-event statistics, as well as errors.
    """
    summary = []
    summary.append("Summary of Offsets\n")
    collection_stats = {}
    # Aggregate statistics across all events for each collection/member
    for frame_key, collections in comparison_dict.items():
        for collection_key, members in collections.items():
            collection_name = collection_key.split(": ", 1)[-1]
            if collection_name not in collection_stats:
                collection_stats[collection_name] = {}
            for key, value in members.items():
                if key not in collection_stats[collection_name]:
                    collection_stats[collection_name][key] = []
                if value is not None:
                    collection_stats[collection_name][key].append(value)
    # Add error summary
    summary.append(gen_error_string(err_dict))
    summary.append("Averages across all events:\n")
    # Add average statistics for each collection/member
    for collection_name, stats in collection_stats.items():
        summary.append(f"{collection_name}:\n")
        for key, values in stats.items():
            avg = np.mean(values) if values else None
            summary.append(f"  {key}: {avg}\n")
    # Add per-event statistics
    for frame_key, collections in comparison_dict.items():
        summary.append(f"\n{frame_key}:\n")
        for collection_key, members in collections.items():
            summary.append(f"  {collection_key}:\n")
            for key, value in members.items():
                summary.append(f"    {key}: {value}\n")
    return "".join(summary)

def main():
    """
    Main function: parses arguments, loads files, compares events, and writes summary.
    """
    args = parse_args()
    reader_new = Reader(args.new_file)
    reader_reference = Reader(args.reference_file)
    events_new = reader_new.get("events")
    events_reference = reader_reference.get("events")
    print(f"Number of events in new file: {len(events_new)}")
    print(f"Number of events in reference file: {len(events_reference)}")
    comparison_dict = {}
    err_dict = {}
    # Loop over all events and compare
    for i, frame_new in tqdm(enumerate(events_new), total=len(events_new)):
        err_dict[f"Frame[{i}]"] = {"Errors": []}
        comparison_dict[f"Frame[{i}]"] = {}
        frame_reference = events_reference[i]
        process_event(frame_new, frame_reference, members_dict, i, err_dict, comparison_dict)
    # Write summary to file
    new_file_base = os.path.basename(args.new_file)
    ref_file_base = os.path.basename(args.reference_file)
    summary_filename = f"summary_offsets_{new_file_base}_vs_{ref_file_base}.txt"
    print(gen_error_string(err_dict))
    with open(summary_filename, "w") as f:
        f.write(summarize_offsets(comparison_dict, err_dict))
    print(f"Summary written to {summary_filename}")

if __name__ == "__main__":
    main()
