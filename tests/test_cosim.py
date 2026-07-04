"""Co-simulation: drive the GENERATED Verilog from the MyHDL testbench and
assert it matches the model. The headline guarantee of this library."""
import os
import random
import pytest
from myhdl import (block, always, instance, Signal, intbv, modbv,
                   ResetSignal, delay, StopSimulation, Cosimulation)
from libfpga_myhdl import mac, lfsr, arbiter_rr
from tests import cosim

pytestmark = pytest.mark.skipif(not cosim.have_cosim(),
                                reason="iverilog-vpi / myhdl VPI unavailable")


def test_cosim_mac():
    clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
    clr = Signal(bool(0)); en = Signal(bool(0))
    a = Signal(intbv(0, min=-128, max=128)); b = Signal(intbv(0, min=-128, max=128))
    acc = Signal(intbv(0, min=-2**31, max=2**31))
    _, vvp = cosim.build(
        mac(clk, rst, clr, en, a, b, acc), "mac", '''
`timescale 1ns/1ps
module tb_mac;
  reg clk, rst, clr, en; reg signed [7:0] a, b; wire signed [31:0] acc;
  mac dut(.clk(clk),.rst(rst),.clr(clr),.en(en),.a(a),.b(b),.acc(acc));
  initial begin $from_myhdl(clk,rst,clr,en,a,b); $to_myhdl(acc); end
endmodule''')

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        clr = Signal(bool(0)); en = Signal(bool(0))
        a = Signal(intbv(0, min=-128, max=128)); b = Signal(intbv(0, min=-128, max=128))
        acc = Signal(intbv(0, min=-2**31, max=2**31))
        dut = Cosimulation(cosim.command("mac", vvp),
                           clk=clk, rst=rst, clr=clr, en=en, a=a, b=b, acc=acc)

        @always(delay(5))
        def clkgen():
            clk.next = not clk

        @instance
        def stim():
            random.seed(11)
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            yield clk.negedge; clr.next = 1
            yield clk.posedge
            yield clk.negedge; clr.next = 0; en.next = 1
            model = 0
            for _ in range(10):
                av = random.randint(-128, 127); bv = random.randint(-128, 127)
                a.next = av; b.next = bv; model += av * bv
                yield clk.posedge; yield clk.negedge
            en.next = 0
            yield delay(1)
            assert int(acc) == model, (int(acc), model)
            raise StopSimulation
        return dut, clkgen, stim

    tb().run_sim()


def test_cosim_lfsr():
    clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
    en = Signal(bool(0)); q = Signal(modbv(0)[8:])
    _, vvp = cosim.build(
        lfsr(clk, rst, en, q, WIDTH=8, TAPS=0xB8), "lfsr", '''
`timescale 1ns/1ps
module tb_lfsr;
  reg clk, rst, en; wire [7:0] q;
  lfsr dut(.clk(clk),.rst(rst),.en(en),.q(q));
  initial begin $from_myhdl(clk,rst,en); $to_myhdl(q); end
endmodule''')

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        en = Signal(bool(0)); q = Signal(modbv(0)[8:])
        dut = Cosimulation(cosim.command("lfsr", vvp),
                           clk=clk, rst=rst, en=en, q=q)

        @always(delay(5))
        def clkgen():
            clk.next = not clk

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0; en.next = 1
            yield clk.negedge
            # the real Verilog must run the full maximal period back to 0
            seen0 = False
            for i in range(1, 256):
                yield clk.posedge; yield delay(1)
                if int(q) == 0 and i < 255:
                    seen0 = True
            assert int(q) == 0, f"generated LFSR period wrong (q={int(q)})"
            assert not seen0, "generated LFSR revisited 0 early"
            raise StopSimulation
        return dut, clkgen, stim

    tb().run_sim()


def test_cosim_arbiter():
    clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
    req = Signal(intbv(0)[4:]); grant = Signal(intbv(0)[4:])
    _, vvp = cosim.build(
        arbiter_rr(clk, rst, req, grant, N=4), "arbiter_rr", '''
`timescale 1ns/1ps
module tb_arbiter_rr;
  reg clk, rst; reg [3:0] req; wire [3:0] grant;
  arbiter_rr dut(.clk(clk),.rst(rst),.req(req),.grant(grant));
  initial begin $from_myhdl(clk,rst,req); $to_myhdl(grant); end
endmodule''')

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        req = Signal(intbv(0)[4:]); grant = Signal(intbv(0)[4:])
        dut = Cosimulation(cosim.command("arbiter_rr", vvp),
                           clk=clk, rst=rst, req=req, grant=grant)

        @always(delay(5))
        def clkgen():
            clk.next = not clk

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            counts = [0, 0, 0, 0]
            req.next = 0b1111
            for _ in range(40):
                yield clk.posedge; yield delay(1)
                g = int(grant)
                assert g and (g & (g - 1)) == 0, f"generated grant not one-hot: {g}"
                for i in range(4):
                    if g & (1 << i):
                        counts[i] += 1
            assert min(counts) > 0 and max(counts) - min(counts) <= 1, counts
            raise StopSimulation
        return dut, clkgen, stim

    tb().run_sim()
