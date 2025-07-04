import argparse
from podio.root_io import Reader
import numpy as np
import os
from tqdm import tqdm
import sys

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
    "MCParticle": {
        "OneToOne": [],
        "OneToMany": ["Parents", "Daughters"],
    },
    "CaloHitContribution": {
        "OneToOne": ["Particle"],
        "OneToMany": [],
    },
    "SimCalorimeterHit": {
        "OneToOne": [],
        "OneToMany": ["Contributions"],
    },
    "SimTrackerHit": {
        "OneToOne": ["Particle"],
        "OneToMany": [],
    },
}

def parse_args():
    """
    Parse command-line arguments for new and reference files.
    """
    parser = argparse.ArgumentParser(description="Compare hits from new and reference files")
    parser.add_argument("--new-file", default="output_new.edm4hep.root", help="New output file")
    parser.add_argument("--reference-file", default="output_ref.edm4hep.root", help="Reference output file")
    parser.add_argument("--output-file", default=None, help="Output file")

    parser.add_argument("-m", "--modified-output", action="store_true", help="Use modified output (default: False)")

    verbosity_group = parser.add_mutually_exclusive_group()
    verbosity_group.add_argument("-b", "--brief", action="store_const", dest="verbosity", const="brief", help="Brief output")
    verbosity_group.add_argument("-d", "--detailed", action="store_const", dest="verbosity", const="detailed", help="Detailed output")
    verbosity_group.add_argument("-s", "--standard", action="store_const", dest="verbosity", const="standard", help="Standard output")

    parser.set_defaults(verbosity="standard")

    return parser.parse_args()

def add_bad_hit(err_dict, frame, collection, member, hit_it, is_relation=False):
    """
    Record the index of a hit that differs between new and reference files.
    """
    key = "relations" if is_relation else "members"
    err_dict[f'Frame[{frame}]'][f'Collection: {collection}'][key].setdefault(member, {"bad_hits": []})["bad_hits"].append(hit_it)

def get_collection_members(collection, members_dict):
    """
    Determine which members to compare for a given collection based on its type.
    """
    for collection_from_dict, members in members_dict.items():
        if collection_from_dict in str(type(collection)):
            return members
    return {"continuous": [], "discrete": [], "vector": []}

def get_relation_members(hit, relations_dict):
    """
    Determine which relations to compare for a given hit based on its type.
    """
    for relation_type, relations in relations_dict.items():
        if relation_type in str(type(hit)):
            return relations
    return {'OneToMany': [], 'OneToOne': []}

def compare_members(hit_new, hit_reference, frame_it, hit_it, collection, err_dict, lists_for_stats, hit_counter):
    # Compare continuous members (e.g., energies)
    members = get_collection_members(hit_new, members_dict)
    new_getters = {member: getattr(hit_new, f'get{member}') for member in members["continuous"]}
    ref_getters = {member: getattr(hit_reference, f'get{member}') for member in members["continuous"]}
    for member in members["continuous"]:
        hit_counter[0] += 1
        new_val = new_getters[member]()
        ref_val = ref_getters[member]()
        if new_val != ref_val:
            add_bad_hit(err_dict, frame_it, collection, member, hit_it)
        lists_for_stats["continuous"][member].append(
            (new_val - ref_val) / ref_val if ref_val != 0 else 0
        )
    # Compare discrete members (e.g., IDs)
    for member in members["discrete"]:
        hit_counter[0] += 1
        if getattr(hit_new, f'get{member}')() != getattr(hit_reference, f'get{member}')():
            lists_for_stats["discrete"][member].append(1)
            add_bad_hit(err_dict, frame_it, collection, member, hit_it)
        else:
            lists_for_stats["discrete"][member].append(0)
    # Compare 3-vector members (e.g., positions, momenta)
    for member in members["vector"]:
        hit_counter[0] += 1
        vec_new = getattr(hit_new, f'get{member}')()
        vec_ref = getattr(hit_reference, f'get{member}')()
        disp_x = vec_new.x - vec_ref.x
        disp_y = vec_new.y - vec_ref.y
        disp_z = vec_new.z - vec_ref.z
        disp_norm = np.linalg.norm([disp_x, disp_y, disp_z])
        ref_norm = np.linalg.norm([vec_ref.x, vec_ref.y, vec_ref.z])
        rel_disp_err = disp_norm / ref_norm if ref_norm != 0 else 0
        if rel_disp_err > 0:
            add_bad_hit(err_dict, frame_it, collection, member, hit_it)
        lists_for_stats["vector"][member].append(rel_disp_err)
    return lists_for_stats

def compare_relations(hit_new, hit_reference, relations_dict, frame_it, hit_it, collection, err_dict, hit_counter):
    """
    Compare relations between hits in new and reference collections.
    Records errors if relations differ.
    """
    relations = get_relation_members(hit_new, relations_dict)
    for relation in relations['OneToMany']:
        hit_counter[0] += 1
        new_relation = [elem.id().index for elem in getattr(hit_new, f"get{relation}")()]
        ref_relation = [elem.id().index for elem in getattr(hit_reference, f"get{relation}")()]
        if new_relation != ref_relation:
            add_bad_hit(err_dict, frame_it, collection, relation, hit_it, is_relation=True)
            print(f"Relation '{relation}' differs for hit {hit_it} in collection {collection} of frame {frame_it}")
            print(f"New: {new_relation}, Reference: {ref_relation}")
    for relation in relations['OneToOne']:
        hit_counter[0] += 1
        new_relation = getattr(hit_new, f"get{relation}")().id().index
        ref_relation = getattr(hit_reference, f"get{relation}")().id().index
        if new_relation != ref_relation:
            add_bad_hit(err_dict, frame_it, collection, relation, hit_it, is_relation=True)
            print(f"Relation '{relation}' differs for hit {hit_it} in collection {collection} of frame {frame_it}")
            print(f"New: {new_relation}, Reference: {ref_relation}")

def compare_hits(hits_new, hits_reference, members, frame_it, collection, err_dict, hit_counter):
    """
    Compare hits between new and reference collections for all specified members.
    Returns statistics for each member.
    """
    args = parse_args()
    lists_for_stats = {"continuous": {}, "discrete": {}, "vector": {}}
    # Initialize lists for statistics
    for member in members["continuous"]:
        lists_for_stats["continuous"][member] = []
    for member in members["discrete"]:
        lists_for_stats["discrete"][member] = []
    for member in members["vector"]:
        lists_for_stats["vector"][member] = []

    # Compare each hit in the collections
    for hit_it, (hit_new, hit_reference) in enumerate(zip(hits_new, hits_reference)):
        # Compare members of the hits
        lists_for_stats = compare_members(hit_new, hit_reference, frame_it, hit_it, collection, err_dict, lists_for_stats, hit_counter)
        if not args.modified_output:
            compare_relations(hit_new, hit_reference, relations_dict, frame_it, hit_it, collection, err_dict, hit_counter)
    return lists_for_stats



def process_event(frame_new, frame_reference, members_dict, frame_it, err_dict, comparison_dict, hit_counter):
    """
    Compare all collections in a single event (frame) between new and reference files.
    Records errors and statistics.
    """
    reference_collections = frame_reference.getAvailableCollections()
    new_collections = frame_new.getAvailableCollections()
    args = parse_args()
    modified_colls = []
    if args.modified_output:
        # If modified output is used, find which collections have been modified
        modified_colls = [c[:-9] for c in new_collections if c.endswith("_modified")]
        new_collections = [c for c in new_collections if not c.endswith("_modified")]
    # Check for missing collections
    if len(reference_collections) != len(new_collections):
        missing_in_new = set(reference_collections) - set(new_collections)
        missing_in_reference = set(new_collections) - set(reference_collections)
        if missing_in_new:
            err_dict[f"Frame[{frame_it}]"]["Errors"].append(
                {"Collections missing in new": missing_in_new}
            )
        elif missing_in_reference:
            err_dict[f"Frame[{frame_it}]"]["Errors"].append(
                {"Collections missing in reference": missing_in_reference}
            )
        else:
            err_dict[f"Frame[{frame_it}]"]["Errors"].append(
                {"Collections are different in length": f"{len(reference_collections)} vs {len(new_collections)}"}
            )
    # Only compare collections present in both files
    common_collections = [c for c in reference_collections if c in new_collections]
    for collection in common_collections:
        err_dict[f"Frame[{frame_it}]"][f"Collection: {collection}"] = {"Errors": [], 'members': {}, 'relations': {}}
        comparison_dict[f"Frame[{frame_it}]"][f"Collection: {collection}"] = {}
        new_collection = collection + "_modified" if collection in modified_colls else collection
        hits_new = frame_new.get(new_collection)
        hits_reference = frame_reference.get(collection)
        # Check for different number of hits
        if len(hits_new) != len(hits_reference):
            err_dict[f"Frame[{frame_it}]"][f"Collection: {collection}"]["Errors"].append(
                {"Number of hits differ": f"{len(hits_new)} vs {len(hits_reference)}"}
            )
        # Get members to compare for this collection
        members = get_collection_members(hits_new, members_dict)
        # Compare hits and collect statistics
        lists_for_stats = compare_hits(hits_new, hits_reference, members, frame_it, collection, err_dict, hit_counter)
        # Store mean statistics for each member
        for member, values in lists_for_stats["continuous"].items():
            comparison_dict[f"Frame[{frame_it}]"][f"Collection: {collection}"][f"Continuous: {member}"] = np.mean(values) if values else None
        for member, values in lists_for_stats["discrete"].items():
            comparison_dict[f"Frame[{frame_it}]"][f"Collection: {collection}"][f"Discrete: {member}"] = np.mean(values) if values else None
        for member, values in lists_for_stats["vector"].items():
            comparison_dict[f"Frame[{frame_it}]"][f"Collection: {collection}"][f"Vector: {member}"] = np.mean(values) if values else None

def gen_error_string(err_dict, verbosity="standard"):
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
                or any(
                    "bad_hits" in relation_info and relation_info["bad_hits"]
                    for relation_info in collection_errors.get("relations", {}).values()
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
                if verbosity != "brief":
                    if "members" in collection_errors:
                        for member, member_info in collection_errors["members"].items():
                            if "bad_hits" in member_info and member_info["bad_hits"]:
                                error_string.append(f"    Member '{member}' bad hit indices: {member_info['bad_hits']}")
                    if "relations" in collection_errors:
                        for relation, relation_info in collection_errors["relations"].items():
                            if "bad_hits" in relation_info and relation_info["bad_hits"]:
                                error_string.append(f"    Relation '{relation}' bad hit indices: {relation_info['bad_hits']}")
    return "\n".join(error_string)

def summarize_offsets(comparison_dict, err_dict, verbosity, hit_counter, modified):
    """
    Summarize the offsets (differences) between new and reference files.
    Includes per-collection and per-event statistics, as well as errors.
    """
    summary = []
    summary.append("Summary of Offsets\n")
    summary.append("=" * 30 + "\n")
    summary.append(f"Verbosity level: {verbosity}\n")
    summary.append(f"Artificially modified output: {'Yes' if modified else 'No'}\n")
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

    # Count total bad_hits and total hits
    total_bad_hits = 0
    for frame in err_dict.values():
        for collection in frame.values():
            if isinstance(collection, dict):
                # Count bad_hits in members
                for member_info in collection.get("members", {}).values():
                    total_bad_hits += len(member_info.get("bad_hits", []))
                # Count bad_hits in relations
                for relation_info in collection.get("relations", {}).values():
                    total_bad_hits += len(relation_info.get("bad_hits", []))
    summary.append(f"\nTotal hits compared: {hit_counter[0]}\n")
    summary.append(f"Total bad_hits: {total_bad_hits}\n")
    summary.append(f"Ratio (bad_hits / total_hits): {total_bad_hits / hit_counter[0] if hit_counter[0] else 0}\n\n")

    # Add error summary
    summary.append(gen_error_string(err_dict, verbosity) + "\n")

    # Add average statistics for each collection/member
    if verbosity != "brief":
        summary.append("\nAverages across all events:\n")
        for collection_name, stats in collection_stats.items():
            summary.append(f"{collection_name}:\n")
            for key, values in stats.items():
                avg = np.mean(values) if values else None
                summary.append(f"  {key}: {avg}\n")
        
    # Add per-event statistics
    if verbosity == "detailed":
        summary.append("\nPer-event statistics:\n")
        for frame_key, collections in comparison_dict.items():
            summary.append(f"\n{frame_key}:\n")
            for collection_key, members in collections.items():
                summary.append(f"  {collection_key}:\n")
                for key, value in members.items():
                    summary.append(f"    {key}: {value}\n")
    return "".join(summary)

def has_errors(err_dict):
    for frame in err_dict.values():
        if "Errors" in frame and frame["Errors"]:
            return True
        for collection in frame.values():
            if isinstance(collection, dict):
                if collection.get("Errors"):
                    return True
                for member_info in collection.get("members", {}).values():
                    if member_info.get("bad_hits"):
                        return True
                for relation_info in collection.get("relations", {}).values():
                    if relation_info.get("bad_hits"):
                        return True
    return False

def main():
    """
    Main function: parses arguments, loads files, compares events, and writes summary.
    """
    args = parse_args()
    hit_counter = [0] # Initialize hit counter as a list to allow modification in nested functions
    reader_new = Reader(args.new_file)
    reader_reference = Reader(args.reference_file)
    events_new = reader_new.get("events")
    events_reference = reader_reference.get("events")
    print(f"Number of events in new file: {len(events_new)}")
    print(f"Number of events in reference file: {len(events_reference)}")
    comparison_dict = {}
    err_dict = {}
    # Loop over all events and compare
    for frame_it, frame_new in tqdm(enumerate(events_new), total=len(events_new)):
        err_dict[f"Frame[{frame_it}]"] = {"Errors": []}
        comparison_dict[f"Frame[{frame_it}]"] = {}
        frame_reference = events_reference[frame_it]
        process_event(frame_new, frame_reference, members_dict, frame_it, err_dict, comparison_dict, hit_counter)
    # Write summary to file
    verbosity = args.verbosity
    new_file_base = os.path.basename(args.new_file)
    ref_file_base = os.path.basename(args.reference_file)
    if args.output_file != None:
        summary_filename = args.output_file
    else:
        summary_filename = f"summary_offsets_{new_file_base}_vs_{ref_file_base}.txt"
    with open(summary_filename, "w") as f:
        f.write(summarize_offsets(comparison_dict, err_dict, verbosity, hit_counter, args.modified_output))
    print(f"Summary written to {summary_filename}")

    # Exit with error code if any errors are present in err_dict
    if has_errors(err_dict):
        print('ComparisonError')
        sys.exit(2)
    

if __name__ == "__main__":
    main()