"""CDC: bit synchronizer latency, reset synchronizer behavior."""
from myhdl import block, always, instance, Signal, intbv, ResetSignal, \
                  delay, StopSimulation
from libfpga_myhdl import sync_bit, reset_sync


def test_sync_bit_propagates():
    @block
    def tb():
        clk = Signal(bool(0)); d = Signal(bool(0)); q = Signal(bool(0))
        dut = sync_bit(clk, d, q, STAGES=2)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        @instance
        def stim():
            errors = [0]
            yield clk.negedge
            d.next = 1
            # after STAGES(+1) rising edges q must be 1
            for _ in range(3):
                yield clk.posedge
            yield delay(1)
            assert q == 1, "sync_bit did not propagate a rising level"
            d.next = 0
            for _ in range(3):
                yield clk.posedge
            yield delay(1)
            assert q == 0, "sync_bit did not propagate a falling level"
            raise StopSimulation
        return dut, clk_gen, stim

    tb().run_sim()


def test_reset_sync_async_assert_sync_deassert():
    @block
    def tb():
        clk = Signal(bool(0))
        ra = ResetSignal(0, active=1, isasync=True)
        rs = Signal(bool(0))
        dut = reset_sync(clk, ra, rs, STAGES=2)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        @instance
        def stim():
            # come out of power-up
            for _ in range(4):
                yield clk.posedge
            yield delay(1)
            assert rs == 0, "reset should be deasserted after some clocks"
            # assert asynchronously (mid-cycle, no edge needed)
            yield delay(2)
            ra.next = 1
            yield delay(1)
            assert rs == 1, "reset did not assert asynchronously"
            # release: must take STAGES edges to deassert
            ra.next = 0
            yield clk.posedge; yield delay(1)
            assert rs == 1, "reset deasserted too early"
            yield clk.posedge; yield delay(1)
            assert rs == 0, "reset did not deassert on the second edge"
            raise StopSimulation
        return dut, clk_gen, stim

    tb().run_sim()
