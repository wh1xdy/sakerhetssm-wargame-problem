import struct
from elftools.elf.elffile import ELFFile

def analyze_segment(start_address, heap_data):
    end_address = start_address + len(heap_data)
    STRUCT_SIZE = 16

    for offset in range(len(heap_data) - STRUCT_SIZE):
        found_sequence = []
        visited_addresses = set()
        current_address = start_address + offset
        while current_address not in visited_addresses:
            visited_addresses.add(current_address)
            val, next_ptr = struct.unpack_from("=QQ", heap_data, current_address - start_address)
            if 0 <= val <= 128:
                found_sequence.append(chr(val))
            if not (start_address <= next_ptr < end_address):
                break
            current_address = next_ptr
        if len(found_sequence) == 20:
            res = ''.join(found_sequence)
            if res.startswith('ssm{'):
                print(res)
                return


def search_corefile(corefile_path):
    with open(corefile_path, 'rb') as corefile:
        elf = ELFFile(corefile)
        heap_segment = None
        for segment in elf.iter_segments():
            if segment['p_type'] == 'PT_LOAD':
                if segment['p_flags'] & 2:
                    start_addr = segment['p_vaddr']
                    end_addr = start_addr + segment['p_memsz']
                    analyze_segment(start_addr, segment.data())

search_corefile('core')
