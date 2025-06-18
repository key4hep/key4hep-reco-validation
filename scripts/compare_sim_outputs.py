#!/usr/bin/env python
#
# Copyright (c) 2020-2024 Key4hep-Project.
#
# This file is part of Key4hep.
# See https://key4hep.github.io/key4hep-doc/ for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# A simple script to compare the hits from the new and reference output
import argparse
from podio.root_io import Reader
import numpy as np
import os
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Compare hits from new and reference files")
parser.add_argument(
    "--new-file", default="output_calo_digi.root", help="New output file"
)
parser.add_argument(
    "--reference-file", default="output_REC.edm4hep.root", help="Reference output file"
)

# Hard code members for now
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

comparison_dict = {}    # This dictionary will contain comparison results for each collection for each frame.
                        # Continous differences will be stored as the mean of the relative differences of each hit.
                        # Discrete differences will be stored as the proportion of differing to total values.

err_dict = {}
err_loc = {}


args = parser.parse_args()

reader_new = Reader(args.new_file)
reader_reference = Reader(args.reference_file)

events_new = reader_new.get("events")
events_reference = reader_reference.get("events")
print(f"Number of events in new file: {len(events_new)}")
print(f"Number of events in reference file: {len(events_reference)}")


def add_bad_hit(err_dict, frame, collection, member, bad_hit):  # Define function outside the loop to avoid redefinition
    if member not in err_dict[f'Frame[{frame}]'][f'Collection: {collection}']["members"]:
        err_dict[f'Frame[{frame}]'][f'Collection: {collection}']["members"][member] = {"bad_hits": []}
    err_dict[f'Frame[{frame}]'][f'Collection: {collection}']["members"][member]["bad_hits"].append(bad_hit)


def gen_error_string(err_dict):
    error_string = []
    error_string.append("\nErrors found during comparison:\n")
    for frame, frame_errors in err_dict.items():
        frame_has_errors = False
        # Check if frame has general errors
        if "Errors" in frame_errors and frame_errors["Errors"]:
            frame_has_errors = True
        # Check if any collection in the frame has errors
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
            # Print general errors for the frame
            if "Errors" in frame_errors and frame_errors["Errors"]:
                for err in frame_errors["Errors"]:
                    error_string.append(f"  General error: {err}")
            # Print only collections with errors
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


for i, frame_new in tqdm(enumerate(events_new), total=len(events_new)):
    err_dict[f"Frame[{i}]"] = {"Errors": []}
    comparison_dict[f"Frame[{i}]"] = {}
    frame_reference = events_reference[i]
    reference_collections = frame_reference.getAvailableCollections()
    new_collections = frame_new.getAvailableCollections()
    if len(reference_collections) != len(new_collections):
        print(f"Number of collections differ: {len(reference_collections)}(ref) vs {len(new_collections)}(new)")
        missing_in_new = set(reference_collections) - set(new_collections)
        missing_in_reference = set(new_collections) - set(reference_collections)
        if missing_in_new:
            print(f"Collections missing in new: {missing_in_new}")
            err_dict[f"Frame[{i}]"]["Errors"].append(
                {"Collections missing in new": missing_in_new}
            )
        elif missing_in_reference:
            print(f"Collections missing in reference: {missing_in_reference}")
            err_dict[f"Frame[{i}]"]["Errors"].append(
                {"Collections missing in reference": missing_in_reference}
            )
        else:
            print("Collections are different, but no missing collections. Potentially duplicate names.")
            err_dict[f"Frame[{i}]"]["Errors"].append(
                {"Collections are different in length": f"{len(reference_collections)} vs {len(new_collections)}"}
            )
    common_collections = [c for c in reference_collections if c in new_collections]
    for collection in common_collections:
        err_dict[f"Frame[{i}]"][f"Collection: {collection}"] = {"Errors": [], 'members': {}}
        comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"] = {}
        print(f'Checking collection "{collection}"')
        hits_new = frame_new.get(collection)
        hits_reference = frame_reference.get(collection)
        print(f"Checking event {i} with {len(hits_new)} hits")
        if len(hits_new) != len(hits_reference):
            print(
                f"Number of hits differ: {len(hits_new)} vs {len(hits_reference)} for collection {collection}"
            )
            err_dict[f"Frame[{i}]"][f"Collection: {collection}"]["Errors"].append(
                {"Number of hits differ": f"{len(hits_new)} vs {len(hits_reference)}"}
            )
        
        lists_for_stats = {
            "continuous": {},
            "discrete": {},
            "vector": {},
        }

        # print(f"Collection: {collection}")
        # print(f'Collection type: {type(frame_new.get(collection))}')
        for collection_from_dict, members in members_dict.items():
            if collection_from_dict in str(type(frame_new.get(collection))):
                for member in members["continuous"]:
                    # Want to have arrays of relative differences for each continous member and binary differences for discrete members.
                    # 3-Vectors will have the average absolute error on each of their components.
                    lists_for_stats["continuous"][member] = []

                for member in members["discrete"]:
                    lists_for_stats["discrete"][member] = []
                
                for member in members["vector"]:
                    lists_for_stats["vector"][member] = []
                


        for j, (hit_new, hit_reference) in enumerate(zip(hits_new, hits_reference)):
            
            # print(f"Checking hit {j}")
            # Cache getter functions
            new_getters = {member: getattr(hit_new, f'get{member}') for member in lists_for_stats["continuous"].keys()}
            ref_getters = {member: getattr(hit_reference, f'get{member}') for member in lists_for_stats["continuous"].keys()}
            for member in lists_for_stats["continuous"].keys():
                new_val = new_getters[member]()
                ref_val = ref_getters[member]()
                if new_val != ref_val:
                    add_bad_hit(err_dict, i, collection, member, j)
                # Compute relative difference
                lists_for_stats["continuous"][member].append(
                    (new_val - ref_val) / ref_val if ref_val != 0 else 0
                )
            for member in lists_for_stats["discrete"].keys():
                if getattr(hit_new, f'get{member}')() != getattr(hit_reference, f'get{member}')():
                    lists_for_stats["discrete"][member].append(1)
                    add_bad_hit(err_dict, i, collection, member, j)
                else:
                    lists_for_stats["discrete"][member].append(0)
            for member in lists_for_stats["vector"].keys():
                vec_new = getattr(hit_new, f'get{member}')()
                vec_ref = getattr(hit_reference, f'get{member}')()
                # Compute displacement vector
                disp_x = vec_new.x - vec_ref.x
                disp_y = vec_new.y - vec_ref.y
                disp_z = vec_new.z - vec_ref.z
                disp_norm = np.linalg.norm([disp_x, disp_y, disp_z])
                ref_norm = np.linalg.norm([vec_ref.x, vec_ref.y, vec_ref.z])
                # Relative displacement error (sensitive to both magnitude and direction)
                rel_disp_err = disp_norm / ref_norm if ref_norm != 0 else 0
                if rel_disp_err > 0:
                    add_bad_hit(err_dict, i, collection, member, j)
                lists_for_stats["vector"][member].append(rel_disp_err)
        
        # Now compute the statistics for each member
        # print(lists_for_stats)
        for member, values in lists_for_stats["continuous"].items():
            if values:
                mean_rel_diff = np.mean(values)
                comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Continuous: {member}"] = mean_rel_diff
                print(f"Mean relative difference for {member}: {mean_rel_diff}")
            else:
                comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Continuous: {member}"] = None
        for member, values in lists_for_stats["discrete"].items():
            if values:
                proportion_diff = np.mean(values)
                comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Discrete: {member}"] = proportion_diff
                print(f"Proportion of differing values for {member}: {proportion_diff}")
            else:
                comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Discrete: {member}"] = None
        for member, values in lists_for_stats["vector"].items():
            if values:
                mean_rel_disp_err = np.mean(values)
                comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Vector: {member}"] = mean_rel_disp_err
                print(f"Mean relative displacement error for {member}: {mean_rel_disp_err}")
            else:
                comparison_dict[f"Frame[{i}]"][f"Collection: {collection}"][f"Vector: {member}"] = None
        print('\n\n')

def summarize_offsets(comparison_dict, err_dict):
    summary = []
    summary.append("Summary of Offsets\n")
    # Per-collection, per-member averages across all events
    collection_stats = {}

    # First, gather stats for averages
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

    # Print errors first
    summary.append(gen_error_string(err_dict))
    
    # Print averages first
    summary.append("Averages across all events:\n")
    for collection_name, stats in collection_stats.items():
        summary.append(f"{collection_name}:\n")
        for key, values in stats.items():
            if values:
                avg = np.mean(values)
            else:
                avg = None
            summary.append(f"  {key}: {avg}\n")

    # Then print per-frame details
    for frame_key, collections in comparison_dict.items():
        summary.append(f"\n{frame_key}:\n")
        for collection_key, members in collections.items():
            summary.append(f"  {collection_key}:\n")
            for key, value in members.items():
                summary.append(f"    {key}: {value}\n")
    return "".join(summary)

new_file_base = os.path.basename(args.new_file)
ref_file_base = os.path.basename(args.reference_file)
summary_filename = f"summary_offsets_{new_file_base}_vs_{ref_file_base}.txt"

print(gen_error_string(err_dict))

with open(summary_filename, "w") as f:
    f.write(summarize_offsets(comparison_dict, err_dict))

print(f"Summary written to {summary_filename}")


    # for relation_reference, relation_new in zip(
    #     args.reference_relation, args.new_relation
    # ):
    #     print(
    #         f'Checking relation "{relation_reference}" (reference) and "{relation_new}" (new)'
    #     )
    #     relations_new = frame_new.get(relation_new)
    #     relations_reference = frame_reference.get(relation_reference)
    #     print(f"Checking event {i} with {len(relations_new)} relations")
    #     assert len(relations_new) == len(
    #         relations_reference
    #     ), f"Number of relations differ: {len(relations_new)} vs {len(relations_reference)}"

        # # Let's sort the relations from reference since they are not sorted
        # rel = dict(
        #     [
        #         (relation_reference.getFrom().id().index, relation_reference)
        #         for relation_reference in relations_reference
        #     ]
        # )
        # sorted_relations_reference = [r for _, r in sorted(rel.items())]

        # counter = 0
        # id = -1
        # for j, (relation_new, relation_reference) in enumerate(
        #     zip(relations_new, sorted_relations_reference)
        # ):
        #     print(f"Checking relation {j}")
        #     if not args.relation_collections_are_merged:
        #         print(relation_new.getFrom().id().index)
        #         print(relation_reference.getFrom().id().index)
        #         print(relation_new.getTo().id().index)
        #         print(relation_reference.getTo().id().index)
        #         assert (
        #             relation_new.getFrom().id().index
        #             == relation_reference.getFrom().id().index
        #         ), f"From differ for relation {j}: {relation_new.getFrom().id().index} vs {relation_reference.getFrom().id().index}"
        #         assert (
        #             relation_new.getTo().id().index
        #             == relation_reference.getTo().id().index
        #         ), f"To differ for relation {j}: {relation_new.getTo().id().index} vs {relation_reference.getTo().id().index}"
        #     else:
        #         if id == -1:
        #             id = relation_new.getFrom().id().collectionID
        #         elif id != relation_new.getFrom().id().collectionID:
        #             id = relation_new.getFrom().id().collectionID
        #             counter = j
        #         assert (
        #             relation_new.getFrom().id().index + counter
        #             == relation_reference.getFrom().id().index
        #         ), f"From differ for relation {j}: {relation_new.getFrom().id().index} vs {relation_reference.getFrom().id().index}"