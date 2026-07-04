"""Co-simulation helper: build MyHDL's Icarus VPI and drive the
*generated Verilog* from a MyHDL testbench.

This is what makes libfpga-myhdl trustworthy: we don't just check that a
block simulates in Python and that it *converts* to Verilog — we run the
converted Verilog through Icarus and assert it behaves identically to the
model, on the same stimulus. If the two ever diverge (a conversion bug, a
subtle semantic gap), the cosim test fails.
"""
import os
import shutil
import subprocess
import tempfile

_VPI_SRC = "/usr/share/myhdl/cosimulation/icarus"
_vpi_path = None


def have_cosim():
    """True if we can build/He VPI (needs iverilog-vpi + the myhdl sources)."""
    return (shutil.which("iverilog-vpi") is not None
            and os.path.isdir(_VPI_SRC)
            and shutil.which("iverilog") is not None)


def vpi():
    """Build myhdl.vpi once (cached for the test session); return its dir."""
    global _vpi_path
    if _vpi_path and os.path.isfile(os.path.join(_vpi_path, "myhdl.vpi")):
        return _vpi_path
    d = tempfile.mkdtemp(prefix="myhdl-vpi-")
    subprocess.run(
        ["iverilog-vpi", os.path.join(_VPI_SRC, "myhdl.c"),
         os.path.join(_VPI_SRC, "myhdl_table.c")],
        cwd=d, check=True, capture_output=True)
    _vpi_path = d
    return d


def build(module_inst, name, tb_verilog):
    """Convert module_inst to Verilog, write the cosim testbench, compile.
    Returns (workdir, vvp_path). tb_verilog is the Verilog testbench source
    with the $from_myhdl/$to_myhdl calls."""
    work = tempfile.mkdtemp(prefix="cosim-")
    cwd = os.getcwd()
    os.chdir(work)
    try:
        module_inst.name = name
        module_inst.convert(hdl="Verilog")
        with open(f"tb_{name}.v", "w") as f:
            f.write(tb_verilog)
        r = subprocess.run(
            ["iverilog", "-o", f"{name}.vvp", f"{name}.v", f"tb_{name}.v"],
            capture_output=True, text=True)
        assert r.returncode == 0, f"cosim compile failed:\n{r.stderr}"
        return work, os.path.join(work, f"{name}.vvp")
    finally:
        os.chdir(cwd)


def command(name, vvp):
    """The vvp command string for myhdl.Cosimulation."""
    return f"vvp -M {vpi()} -m myhdl {vvp}"
