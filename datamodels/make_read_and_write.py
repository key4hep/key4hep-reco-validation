"""Generate C++ code from the EDM4hep yaml file"""
import yaml
import random
import string

random.seed(1000007)

# Variable name length
LENGTH = 5

with open('EDM4hep/edm4hep.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)


def generate_variable_name(length):
    # Define the characters allowed in the variable name
    letters = string.ascii_lowercase

    return ''.join(random.choice(letters) for _ in range(length))


def get_type_and_member(line):
    """Get the type and member name from a line of the edm4hep.yaml file describing a data type.
    """
    if '/' in line:
        line = line[:line.find('/')]
    line = line.strip()
    if line.startswith('std::array'):
        typ = line[:line.find('>')+1].replace(' ', '')
        member = line[line.find('>')+1:].strip()
    else:
        typ = line.split()[0]
        member = line.split()[1]
    return typ, member

def get_value(typ):
    """Get random values for a given type, e.g. int, float, double, edm4hep::Vector3f std::array<float, 3>.
    """
    if typ.startswith('edm4hep::'):
        comp = config['components'][typ]
        ls = []
        for member in comp['Members']:
            member_typ, member_name = get_type_and_member(member)
            ls.append(f'{get_value(member_typ)}')
        value = f'{{ {", ".join(ls)} }}'
        if typ == 'edm4hep::ObjectID':
            value = f'{{ {value} }}'

    elif typ.startswith('std::array'):
        internal_type = typ[typ.find('<')+1:typ.find(',')]
        num = typ[typ.find(',')+1:typ.find('>')].strip()
        if internal_type == 'float' or internal_type == 'double':
            value = f'{{ {", ".join([str(random.randint(0, 100)) for _ in range(int(num))])} }}'
        else:
            # 3 numbers per element
            ls = []
            for i in range(int(num)):
                ls.append(f'{{ {", ".join([str(random.randint(0, 100)) for _ in range(3)])} }}')
            value = f'{{{{ {", ".join(ls)} }}}}'
    else:
        value = random.randint(0, 100)
    return value


header = """
#include "podio/ROOTFrameWriter.h"
#include "podio/ROOTFrameReader.h"
#include "podio/Frame.h"

#include <string>
#include <tuple>
#include <vector>
""".split('\n')
body_writer = """
void write_frames(const std::string& filename) {
  podio::ROOTFrameWriter writer(filename);

  podio::Frame frame;""".split('\n')
body_reader = """
bool read_frames(const std::string& filename) {
  podio::ROOTFrameReader reader;
  reader.openFile(filename);
  int ret = 0;

  podio::Frame frame(reader.readNextEntry("events"));""".split('\n')

edm4hep_types = ['Vector3f', 'Vector3d', 'Vector2i', 'Vector2f', 'Quantity', 'Hypothesis']

for cl in config['datatypes']:
    collection_name = generate_variable_name(LENGTH)
    variable_name = generate_variable_name(LENGTH)
    collection = cl.split('::')[-1] + 'Collection'
    header.append(f'#include "edm4hep/{collection}.h"')
    body_writer.append(f'  auto {collection_name} = edm4hep::{collection}();')
    body_writer.append(f'  auto {variable_name} = {collection_name}.create();')
    body_reader.append(f'  auto& {collection_name} = frame.get<edm4hep::{collection}>("{collection}");')
    body_reader.append(f'  auto {variable_name} = {collection_name}[0];')

    all_members = list(config['datatypes'][cl]['Members'])
    is_not_vector = set(all_members)
    if 'VectorMembers' in config['datatypes'][cl]:
        all_members += config['datatypes'][cl]['VectorMembers']

    for original_member_line in all_members:

        typ, member = get_type_and_member(original_member_line)
        value = get_value(typ)

        if original_member_line in is_not_vector:
            body_writer.append(f'  {variable_name}.set{member[0].upper() + member[1:]}({value});')
        else:
            body_writer.append(f'  {variable_name}.addTo{member[0].upper() + member[1:]}({value});')

        # The reader is a bit more complicated because for the edm4hep types
        # there is not a == comparator so members have to be compared one by one
        if original_member_line in is_not_vector:
            for elem in edm4hep_types:
                if elem in typ:
                    # Iterate num times in the case of an std::array to read each element and each member
                    num = int(typ.split(',')[1][:-1]) if typ.startswith('std::array') else 1
                    typ_members = config['components'][f'edm4hep::{elem}']['Members']
                    for i in range(num):
                        modifier = f'[{i}]' if typ.startswith('std::array') else ''
                        for m in typ_members:
                            m_typ = m.split()[0]
                            m_name = m.split()[1]
                            body_reader.append(f'  if ({variable_name}.get{member[0].upper() + member[1:]}(){modifier}.{m_name} != {typ}({value}){modifier}.{m_name}) {{')
                            body_reader.append(f'    std::cout << "Error: {variable_name}.get{member[0].upper() + member[1:]}() != {value}" << std::endl;')
                            body_reader.append(f'    ret = 1;')
                            body_reader.append(f'  }}')
                    break
            else:
                body_reader.append(f'  if ({variable_name}.get{member[0].upper() + member[1:]}() != {typ}({value})) {{')
                body_reader.append(f'    std::cout << "Error: {variable_name}.get{member[0].upper() + member[1:]}() != {value}" << std::endl;')
                body_reader.append(f'    ret = 1;')
                body_reader.append(f'  }}')
        else:
            if typ.startswith('edm4hep::'):
                for elem in edm4hep_types:
                    if elem in typ:
                        typ_members = config['components'][f'edm4hep::{elem}']['Members']
                        for m in typ_members:
                            m_typ = m.split()[0]
                            m_name = m.split()[1]

                            body_reader.append(f'  if ({variable_name}.get{member[0].upper() + member[1:]}(0).{m_name} != {typ}({value}).{m_name}) {{')
                            body_reader.append(f'    std::cout << "Error: {variable_name}.get{member[0].upper() + member[1:]}(0) != {value}" << std::endl;')
                            body_reader.append(f'    ret = 1;')
                            body_reader.append(f'  }}')
            else:
                body_reader.append(f'  if ({variable_name}.get{member[0].upper() + member[1:]}(0) != {typ}({value})) {{')
                body_reader.append(f'    std::cout << "Error: {variable_name}.get{member[0].upper() + member[1:]}(0) != {value}" << std::endl;')
                body_reader.append(f'    ret = 1;')
                body_reader.append(f'  }}')

    body_writer.append(f'  frame.put(std::move({collection_name}), "{collection}");\n')

body_writer.extend("""
  writer.writeFrame(frame, "events");
  writer.finish();
}

int main () {
  write_frames("test.root");
  return 0;
}""".split('\n'))

body_reader.extend("""
  return ret;
}
int main () {
  return read_frames("test.root");
}""".split('\n'))


with open('write.cpp', 'w') as f:
    f.write('\n'.join(header))
    f.write('\n'.join(body_writer))

with open('read.cpp', 'w') as f:
    f.write('\n'.join(header))
    f.write('\n'.join(body_reader))
