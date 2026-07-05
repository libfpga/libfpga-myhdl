"""Regenerate verilog/lfpga_mac.v from the MyHDL model, so the LibFPGA
registry can verify the *generated* RTL (lint + synth + testbench). The
hand-written self-checking testbench lives in verilog/tb_mac.v."""
import os
from myhdl import Signal, intbv, ResetSignal
from libfpga_myhdl.math import mac

os.makedirs("verilog", exist_ok=True)
os.chdir("verilog")
mac(Signal(bool(0)), ResetSignal(0, active=1, isasync=False),
    Signal(bool(0)), Signal(bool(0)),
    Signal(intbv(0, min=-128, max=128)),
    Signal(intbv(0, min=-128, max=128)),
    Signal(intbv(0, min=-2**31, max=2**31))).convert(hdl="Verilog", name="lfpga_mac")
print("wrote verilog/lfpga_mac.v")
