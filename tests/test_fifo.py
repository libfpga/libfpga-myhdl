"""FIFO: random push/pop scoreboard against a Python model."""
import random
from myhdl import block, always, instance, Signal, intbv, ResetSignal, \
                  delay, StopSimulation
from libfpga_myhdl import fifo_sync


def test_fifo_sync_scoreboard():
    random.seed(1)

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        wr_en = Signal(bool(0)); rd_en = Signal(bool(0))
        wr_data = Signal(intbv(0)[8:]); rd_data = Signal(intbv(0)[8:])
        full = Signal(bool(0)); empty = Signal(bool(1))
        count = Signal(intbv(0, min=0, max=17))
        dut = fifo_sync(clk, rst, wr_en, wr_data, rd_en, rd_data,
                        full, empty, count, WIDTH=8, DEPTH=16)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        @instance
        def stim():
            model = []
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            for _ in range(1500):
                yield clk.negedge
                w = random.random() < 0.5
                r = random.random() < 0.5
                wr_en.next = w
                rd_en.next = r
                wr_data.next = random.randint(0, 255)
                yield delay(1)
                # check flags + head against model BEFORE the edge
                assert int(count) == len(model), (int(count), len(model))
                assert bool(full) == (len(model) == 16)
                assert bool(empty) == (len(model) == 0)
                if model:
                    assert int(rd_data) == model[0], (int(rd_data), model[0])
                do_push = w and len(model) < 16
                do_pop = r and len(model) > 0
                dpush_val = int(wr_data)
                yield clk.posedge
                if do_push:
                    model.append(dpush_val)
                if do_pop:
                    model.pop(0)
            raise StopSimulation
        return dut, clk_gen, stim

    tb().run_sim()
