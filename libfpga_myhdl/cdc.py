"""Clock-domain-crossing primitives."""
from myhdl import (block, always_seq, always, always_comb, Signal,
                   intbv, modbv, concat, ResetSignal)


@block
def sync_bit(clk, d_async, q, STAGES=2):
    """N-flop synchronizer for a single-bit level signal crossing into
    clk's domain. Not for buses: synchronize a gray-coded counter or use
    an async FIFO for multi-bit values."""
    ff = Signal(modbv(0)[STAGES:])

    @always(clk.posedge)
    def seq():
        ff.next = (ff << 1) | d_async

    @always_comb
    def out():
        q.next = ff[STAGES - 1]
    return seq, out


@block
def reset_sync(clk, rst_async, rst_sync, STAGES=2):
    """Reset synchronizer: asynchronous assert, synchronous deassert.
    rst_async and rst_sync are active-high resets. One per clock domain."""
    ff = Signal(intbv(0)[STAGES:])

    @always(clk.posedge, rst_async.posedge)
    def seq():
        if rst_async:
            ff.next = (1 << STAGES) - 1      # all ones = asserted
        else:
            ff.next = (ff << 1) & ((1 << STAGES) - 1)  # shift zeros in

    @always_comb
    def out():
        rst_sync.next = ff[STAGES - 1]
    return seq, out



@block
def pulse_sync(clk_src, clk_dst, rst_dst, pulse_in, pulse_out):
    """Single-cycle pulse crossing from the source domain to clk_dst.
    Toggle-based: pulse_in flips a flag in the source domain; the flag is
    double-synchronized into clk_dst and edge-detected to regenerate a
    one-cycle pulse. pulse_in must be one src-clock wide and pulses must
    be spaced enough for the destination to see each toggle."""
    flag = Signal(bool(0))
    sync = Signal(intbv(0)[3:])       # 2-flop sync + 1 for edge detect

    @always(clk_src.posedge)
    def src():
        if pulse_in:
            flag.next = not flag

    @always_seq(clk_dst.posedge, reset=rst_dst)
    def dst():
        sync.next = concat(sync[2:0], flag)

    @always_comb
    def out():
        pulse_out.next = sync[2] ^ sync[1]     # edge in the synced flag
    return src, dst, out

