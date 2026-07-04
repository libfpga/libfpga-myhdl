"""Stream / dataflow helpers."""
from myhdl import block, always_seq, always_comb, Signal, intbv, ResetSignal


@block
def arbiter_rr(clk, rst, req, grant, N=4):
    """Round-robin arbiter. Grants exactly one requester per cycle
    (one-hot), rotating priority so no requester starves. grant is
    registered (one cycle after req). Priority starts just past the last
    grant."""
    ptr = Signal(intbv(0, min=0, max=N))     # next index to favour

    @always_seq(clk.posedge, reset=rst)
    def seq():
        grant_v = intbv(0)[N:]
        nptr = intbv(0, min=0, max=N)
        nptr[:] = ptr                        # default: keep current pointer
        found = False
        # scan N positions starting at ptr, wrapping; take the first hit
        for k in range(N):
            idx = (ptr + k) % N
            if req[idx] and not found:
                grant_v[idx] = 1
                nptr[:] = (idx + 1) % N
                found = True
        grant.next = grant_v
        ptr.next = nptr
    return seq
