import re
from pprint import pprint

PDT_WIDTH = 5
PT_WIDTH = 5
OFFSET_WIDTH = 5
PFN_WIDTH = 7
VADDR_WIDTH = 15
PADDR_WIDTH = 12
PDT_VALID_BIT = 7
PT_VALID_BIT = 7

def get_valid_bit_and_value(x, valid_bit):
    return (x >> valid_bit, x & ~(1 << valid_bit))

def translate(mem, vaddr, pdbr, verbose=True):
    assert vaddr < (1 << VADDR_WIDTH)
    assert pdbr % (1 << PT_WIDTH) == 0
    if verbose:
        print('Virtual Address: {:#x}'.format(vaddr))
    pdt_idx = vaddr >> (PT_WIDTH + OFFSET_WIDTH)
    pt_idx = (vaddr >> OFFSET_WIDTH) & ((1 << PT_WIDTH) - 1)
    offset = vaddr & ((1 << OFFSET_WIDTH) - 1)
    v = mem[pdbr // (1 << PT_WIDTH)][pdt_idx]
    valid, v = get_valid_bit_and_value(v, PDT_VALID_BIT)
    if verbose:
        print(' ' * 2 + '--> pde index: {:#x}  pde contents: (valid {}, pfn {:#x})'.format(pdt_idx, int(valid), v))
    if not valid:
        if verbose:
            print(' ' * 4 + '--> Fault (page directory entry not valid)')
        return None
    v = mem[v][pt_idx]
    valid, v = get_valid_bit_and_value(v, PT_VALID_BIT)
    if verbose:
        print(' ' * 4 + '--> pte index: {:#x}  pte contents: (valid {}, pfn {:#x})'.format(pt_idx, int(valid), v))
    if not valid:
        if verbose:
            print(' ' * 6 + '--> Fault (page table entry not valid)')
        return None
    paddr = (v << OFFSET_WIDTH) + offset
    value = mem[v][offset]
    if verbose:
        print(' ' * 6 + '--> Translates to Physical Address {:#x} --> Value: {:#x}'.format(paddr, value))
    return (paddr, value)

def main():
    with open('03-2-spoc-testdata.md', encoding='utf-8') as file:
        text = file.read()
    prog = re.compile(r'^page (\w{2}): (.*)$', re.MULTILINE)
    mem = []
    for match in prog.finditer(text):
        assert len(mem) == int(match.group(1), 16)
        mem.append([int(s, 16) for s in match.group(2).split()])
        assert len(mem[-1]) == (1 << PT_WIDTH)

    vaddrs = [
        0x6c74,
        0x6b22,
        0x03df,
        0x69dc,
        0x317a,
        0x4546,
        0x2c03,
        0x7fd7,
        0x390e,
        0x748b,
        ]
    pdbr = 0x220
    for vaddr in vaddrs:
        translate(mem, vaddr, pdbr)

if __name__ == '__main__':
    main()