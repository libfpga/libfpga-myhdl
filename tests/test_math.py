"""Math: gray roundtrip, LFSR period, MAC dot products."""
import random
from myhdl import block, always, instance, Signal, intbv, modbv, \
                  ResetSignal, delay, StopSimulation
from libfpga_myhdl import bin2gray, gray2bin, lfsr, mac


def test_gray_roundtrip_and_adjacency():
    @block
    def tb():
        b = Signal(intbv(0)[8:]); g = Signal(intbv(0)[8:])
        b2 = Signal(intbv(0)[8:]); gnext = Signal(intbv(0)[8:])
        bn = Signal(intbv(0)[8:])
        u1 = bin2gray(b, g)
        u2 = gray2bin(g, b2)
        u3 = bin2gray(bn, gnext)

        @instance
        def stim():
            for i in range(256):
                b.next = i
                bn.next = (i + 1) % 256
                yield delay(1)
                assert int(b2) == i, "gray roundtrip failed at %d" % i
                diff = int(g) ^ int(gnext)
                assert diff and (diff & (diff - 1)) == 0, \
                    "adjacent codes differ in != 1 bit at %d" % i
            raise StopSimulation
        return u1, u2, u3, stim

    tb().run_sim()


def test_lfsr_full_period():
    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        q = Signal(modbv(0)[8:])
        dut = lfsr(clk, rst, Signal(bool(1)), q, WIDTH=8, TAPS=0xB8)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            yield clk.negedge
            # from 0, an 8-bit maximal LFSR returns to 0 after 2^8-1 steps
            revisited = 0
            for i in range(1, 256):
                yield clk.posedge
                yield delay(1)
                if int(q) == 0 and i < 255:
                    revisited += 1
            assert int(q) == 0, "period != 255 (q=%d)" % int(q)
            assert revisited == 0, "revisited zero early"
            raise StopSimulation
        return dut, clk_gen, stim

    tb().run_sim()


def test_mac_dot_products():
    random.seed(3)

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        clr = Signal(bool(0)); en = Signal(bool(0))
        a = Signal(intbv(0, min=-128, max=128))
        b = Signal(intbv(0, min=-128, max=128))
        acc = Signal(intbv(0, min=-2**31, max=2**31))
        dut = mac(clk, rst, clr, en, a, b, acc)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            for _ in range(15):
                yield clk.negedge; clr.next = 1; en.next = 0
                yield clk.posedge
                yield clk.negedge; clr.next = 0; en.next = 1
                model = 0
                n = random.randint(1, 12)
                for _ in range(n):
                    av = random.randint(-128, 127)
                    bv = random.randint(-128, 127)
                    a.next = av; b.next = bv
                    model += av * bv
                    yield clk.posedge
                    yield clk.negedge
                en.next = 0
                yield delay(1)
                assert int(acc) == model, (int(acc), model)
            raise StopSimulation
        return dut, clk_gen, stim

    tb().run_sim()
