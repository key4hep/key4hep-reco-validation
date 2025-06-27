import argparse
from podio.root_io import Reader, Writer

def parse_args():
    """
    Parse command-line arguments for modifying EDM4hep output file.
    """
    parser = argparse.ArgumentParser(description="Modify EDM4hep output file for testing purposes.")
    parser.add_argument("--input-file", default="output_new.edm4hep.root", help="Output file to be modified")
    parser.add_argument("--output-file", default="output_modified.edm4hep.root", help="Modified output file")

    parser.add_argument("--frame", type=int, default=1, help="Event frame to modify")
    parser.add_argument("--collection-name", default="MCParticles", help="Collection to modify")
    parser.add_argument("--member", default="Mass", help="Member variable to modify")
    parser.add_argument("--hit", type=int, default=10, help="Index of the hit to modify")

    parser.add_argument("--scale", type=float, default=1.5, help="Scaling factor for the member value")
    parser.add_argument("--offset", type=float, default=0.0, help="Offset to add to the scaled value")
    parser.add_argument("--set-val", type=float, default=None, help="Value to set instead of scaling")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    reader = Reader(args.input_file)
    frame = args.frame
    if frame < 0 or frame >= len(reader.get('events')):
        raise ValueError(f"Frame {frame} is out of bounds for the number of events in the input file.")
    collection_name = args.collection_name
    member = args.member
    hit = args.hit

    scale = args.scale
    offset = args.offset
    set_val = args.set_val

    events = list(reader.get('events'))
    event = events[frame]
    collection = event.get(collection_name)
    current_val = getattr(collection[hit], f'get{member}')()
    if set_val:
        new_val = set_val
    else:
        new_val = current_val * scale + offset

    for n_event, event in enumerate(events):
        old_coll = event.get(collection_name)
        new_coll = type(old_coll)()
        for n, elem in enumerate(old_coll):
            new_elem = elem.clone()
            if n == hit and n_event == frame:
                print(f'Changing {collection_name}[{hit}]\'s {member.lower()} from {getattr(elem, f"get{member}")()} to {new_val}')
                getattr(new_elem, f'set{member}')(new_val)
            new_coll.push_back(new_elem)
        event.put(new_coll, collection_name + "_modified")

    writer = Writer(args.output_file)
    for category in reader.categories:
        if category == 'events':
            for i, event in enumerate(events):
                if i == frame:
                    print('New val, final check: ', getattr(event.get(collection_name + "_modified")[hit], f'get{member}')())
                    writer.write_frame(event, 'events')
                else:
                    writer.write_frame(event, 'events')
        else:
            for item in reader.get(category):
                writer.write_frame(item, category)
