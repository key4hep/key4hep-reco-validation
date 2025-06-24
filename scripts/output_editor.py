import argparse
from podio.root_io import Reader, Writer
from podio.frame import Frame
import edm4hep
from compare_sim_outputs import relations_dict

def parse_args():
    """
    Parse command-line arguments for new and reference files.
    """
    parser = argparse.ArgumentParser(description="Modify EDM4hep output file for testing purposes.")
    parser.add_argument("--input-file", default="output_new.edm4hep.root", help="Output file to be modified")
    parser.add_argument("--output-file", default="output_modified.edm4hep.root", help="Modified output file")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    reader = Reader(args.input_file)
    frame = 1
    collection_name = 'MCParticles'
    member = 'Mass'
    hit = 10    

    scale = 1.5
    offset = 0
    set_val = None

    events = list(reader.get('events'))
    event = events[frame]
    collection = event.get(collection_name)
    current_val = getattr(collection[hit], f'get{member}')()
    if set_val:
        new_val = set_val
    else:
        new_val = current_val * scale + offset
    print(f"Current value: {current_val}, New value: {new_val}")

    new_frame = Frame()

    for name in event.getAvailableCollections():
        if name == collection_name:
            old_coll = event.get(name)
            new_coll = type(old_coll)()
            for n, elem in enumerate(old_coll):
                new_elem = elem.clone()
                if n == hit:
                    print(f'Changing {name}[{hit}] from {getattr(elem, f"get{member}")()} to {new_val}')
                    getattr(new_elem, f'set{member}')(new_val)
                new_coll.push_back(new_elem)
            new_frame.put(new_coll, name)
        else:
            new_frame.put(event.get(name), name)

    writer = Writer(args.output_file)
    for category in reader.categories:
        if category == 'events':
            for i, event in enumerate(events):
                if i == frame:
                    print('New val, final check: ', getattr(new_frame.get(collection_name)[hit], f'get{member}')())

                    MCP = new_frame.get('MCParticles')[1]
                    print(f'New stuff: {[elem.id().index for elem in MCP.getDaughters()]}')

                    MCP_old = event.get('MCParticles')[1]
                    print(f'Old stuff: {[elem.id().index for elem in MCP_old.getDaughters()]}')

                    writer.write_frame(new_frame, 'events')
                else:
                    writer.write_frame(event, 'events')
        else:
            for item in reader.get(category):
                writer.write_frame(item, category)
