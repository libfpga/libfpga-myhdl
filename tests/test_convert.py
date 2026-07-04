"""Every block must convert to clean Verilog and VHDL — MyHDL's headline
feature is that these designs drop into a standard synthesis flow."""
import os
import shutil
import subprocess
import tempfile
from myhdl import Signal, intbv, modbv, ResetSignal
from libfpga_myhdl import (sync_bit, reset_sync, fifo_sync,
                           bin2gray, gray2bin, lfsr, mac)


def _convert(inst, name, hdl):
    with tempfile.TemporaryDirectory() as d:
        cwd = os.getcwd()
        os.chdir(d)
        try:
            inst.convert(hdl=hdl)
            ext = "v" if hdl == "Verilog" else "vhd"
            path = os.path.join(d, f"{name}.{ext}")
            assert os.path.isfile(path), f"{name}: no {hdl} output"
            assert os.path.getsize(path) > 0
            # the generated Verilog must actually compile
            if hdl == "Verilog" and shutil.which("iverilog"):
                r = subprocess.run(["iverilog", "-g2012", "-o", "/dev/null",
                                    path], capture_output=True, text=True)
                assert r.returncode == 0, \
                    f"{name}: generated Verilog does not compile:\n{r.stderr}"
        finally:
            os.chdir(cwd)


def _blocks():
    clk = Signal(bool(0))
    rst = ResetSignal(0, active=1, isasync=False)
    ra = ResetSignal(0, active=1, isasync=True)
    yield "sync_bit", sync_bit(clk, Signal(bool(0)), Signal(bool(0)))
    yield "reset_sync", reset_sync(clk, ra, Signal(bool(0)))
    yield "bin2gray", bin2gray(Signal(intbv(0)[8:]), Signal(intbv(0)[8:]))
    yield "gray2bin", gray2bin(Signal(intbv(0)[8:]), Signal(intbv(0)[8:]))
    yield "lfsr", lfsr(clk, rst, Signal(bool(0)), Signal(modbv(0)[8:]))
    yield "mac", mac(clk, rst, Signal(bool(0)), Signal(bool(0)),
                     Signal(intbv(0, min=-128, max=128)),
                     Signal(intbv(0, min=-128, max=128)),
                     Signal(intbv(0, min=-2**31, max=2**31)))
    yield "fifo_sync", fifo_sync(
        clk, rst, Signal(bool(0)), Signal(intbv(0)[8:]),
        Signal(bool(0)), Signal(intbv(0)[8:]),
        Signal(bool(0)), Signal(bool(0)),
        Signal(intbv(0, min=0, max=17)))


def test_all_convert_to_verilog():
    for name, inst in _blocks():
        inst.name = name
        _convert(inst, name, "Verilog")


def test_all_convert_to_vhdl():
    for name, inst in _blocks():
        inst.name = name
        _convert(inst, name, "VHDL")
