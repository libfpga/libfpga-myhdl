"""Round-robin arbiter: one-hot grant, subset of req, no starvation."""
import random
from myhdl import (block, always, instance, Signal, intbv, ResetSignal,
                   delay, StopSimulation)
from libfpga_myhdl import arbiter_rr


def test_arbiter_rr_onehot_and_fair():
    random.seed(5)

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        req = Signal(intbv(0)[4:]); grant = Signal(intbv(0)[4:])
        dut = arbiter_rr(clk, rst, req, grant, N=4)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            grants_per_line = [0, 0, 0, 0]
            # all four always requesting: must rotate through all of them
            req.next = 0b1111
            for _ in range(40):
                yield clk.posedge
                yield delay(1)
                g = int(grant)
                assert g and (g & (g - 1)) == 0, f"grant not one-hot: {g:04b}"
                assert (g & ~int(req)) == 0, "granted a non-requester"
                for i in range(4):
                    if g & (1 << i):
                        grants_per_line[i] += 1
            # round-robin fairness: everyone served roughly equally
            assert min(grants_per_line) > 0, f"starvation: {grants_per_line}"
            assert max(grants_per_line) - min(grants_per_line) <= 1, \
                f"unfair: {grants_per_line}"
            # no request -> no grant
            req.next = 0
            yield clk.posedge; yield delay(1)
            assert int(grant) == 0
            raise StopSimulation
        return dut, clk_gen, stim

    tb().run_sim()
