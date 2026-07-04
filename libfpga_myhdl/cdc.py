"""Clock-domain-crossing primitives."""
from myhdl import block, always_seq, always, always_comb, Signal, intbv, modbv, ResetSignal


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

