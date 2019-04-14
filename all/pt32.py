
class PageTableStage:
    def __init__(self, mem, get_index, get_offset=None):
        self._get_index = get_index
        if get_offset is not None:
            self._get_offset = get_offset

    def get_index(self, vaddr):
        return self._get_index(vaddr)

    def get_offset(self, vaddr):
        return self._get_offset(vaddr)

    def get_entry(self, base, idx):
        if 0x300 <= idx <= 0x363:
            return self.make_entry((idx - 0x300 + 1) << 12, True, True)
        raise KeyError('Unknown entry for index {:#010x}'.format(idx))

    def next_base(self, entry):
        return (entry >> 20) << 12

    def is_valid(self, entry):
        return entry & 1

    def is_writable(self, entry):
        return (entry >> 1) & 1

    def make_entry(self, next_base, writable, valid):
        return next_base + (2 if writable else 0) + (1 if valid else 0)

def translate(vaddr, paddr, pdbr):
    pdt = PageTableStage(None, lambda vaddr: vaddr >> 22)
    dt = PageTableStage(None, lambda vaddr: (vaddr >> 12) & ((1 << 10) - 1), 
                        lambda vaddr: vaddr & ((1 << 12) - 1))

    pde_idx = pdt.get_index(vaddr)
    pde_ctx = pdt.get_entry(pdbr, pde_idx)
    pte_base = pdt.next_base(pde_ctx)
    pte_idx = dt.get_index(vaddr)

    # Infer backwards
    pa_offset = dt.get_offset(vaddr)
    pa_base = paddr - pa_offset
    pte_ctx = dt.make_entry(pa_base, True, True)

    print('va {:#010x}, pa {:#010x}, pde_idx {:#010x}, pde_ctx {:#010x}, pte_idx {:#010x}, pte_ctx {:#010x}'
          .format(vaddr, paddr, pde_idx, pde_ctx, pte_idx, pte_ctx))

def main():
    vaddrs = [
        0xc2265b1f,
        0xcc386bbc,
        0xc7ed4d57,
        0xca6cecc0,
        0xc18072e8,
        0xcd5f4b3a,
        0xcc324c99,
        0xc7204e52,
        0xc3a90293,
        0xce6c3f32,
        ]
    paddrs = [
        0x0d8f1b1f,
        0x0414cbbc,
        0x07311d57,
        0x0c9e9cc0,
        0x007412e8,
        0x06ec9b3a,
        0x0008ac99,
        0x0b8b6e52,
        0x0f1fd293,
        0x007d4f32,
        ]
    pdbr = 0x0
    for va, pa in zip(vaddrs, paddrs):
        translate(va, pa, pdbr)

if __name__ == '__main__':
    main()