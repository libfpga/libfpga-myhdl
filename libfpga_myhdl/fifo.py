"""Synchronous FIFO (show-ahead / first-word-fall-through)."""
from myhdl import block, always_seq, always_comb, Signal, intbv, ResetSignal
from math import log2


@block
def fifo_sync(clk, rst, wr_en, wr_data, rd_en, rd_data, full, empty, count,
              WIDTH=8, DEPTH=16):
    """Show-ahead synchronous FIFO. rd_data always shows the oldest word
    when not empty; rd_en pops it. Writes when full and reads when empty
    are ignored. DEPTH must be a power of two."""
    assert DEPTH & (DEPTH - 1) == 0, "DEPTH must be a power of two"
    AW = int(log2(DEPTH))
    mem = [Signal(intbv(0)[WIDTH:]) for _ in range(DEPTH)]
    wptr = Signal(intbv(0)[AW:])
    rptr = Signal(intbv(0)[AW:])
    cnt = Signal(intbv(0, min=0, max=DEPTH + 1))

    @always_seq(clk.posedge, reset=rst)
    def seq():
        push = wr_en and not (cnt == DEPTH)
        pop = rd_en and not (cnt == 0)
        if push:
            mem[wptr].next = wr_data
            wptr.next = (wptr + 1) % DEPTH
        if pop:
            rptr.next = (rptr + 1) % DEPTH
        if push and not pop:
            cnt.next = cnt + 1
        elif pop and not push:
            cnt.next = cnt - 1

    @always_comb
    def outputs():
        rd_data.next = mem[rptr]
        full.next = (cnt == DEPTH)
        empty.next = (cnt == 0)
        count.next = cnt
    return seq, outputs
