# libfpga-myhdl

[![CI](https://github.com/libfpga/libfpga-myhdl/actions/workflows/ci.yml/badge.svg)](https://github.com/libfpga/libfpga-myhdl/actions/workflows/ci.yml)

**Verified FPGA building blocks in [MyHDL](https://www.myhdl.org/) — hardware
described in Python.**

The Python companion to [libfpga](https://github.com/libfpga/libfpga). Each
block is a MyHDL `@block` that:

- **simulates** in pure Python, with a self-checking `unittest`/`pytest` suite;
- **converts** to clean Verilog *and* VHDL — verified in CI to compile;

so you can develop and test in Python, then drop the generated RTL into
Vivado, Quartus, or the open Yosys flow like any other design.

Try MyHDL in your browser first: **[libfpga.com/learn/myhdl](https://libfpga.com/learn/myhdl)**,
and read the [intro](https://libfpga.com/blog/myhdl-intro).

## Modules

| Block | What it is |
|---|---|
| `sync_bit` | N-flop synchronizer for a single-bit CDC level signal |
| `reset_sync` | reset synchronizer: async assert, sync deassert |
| `fifo_sync` | synchronous show-ahead FIFO with count |
| `bin2gray` / `gray2bin` | binary ↔ Gray converters |
| `lfsr` | maximal-length Fibonacci LFSR |
| `mac` | signed multiply-accumulate (the neural-net atom) |
| `uart_tx` / `uart_rx` | UART transmitter / receiver, 8N1 |
| `spi_master` | SPI master, mode 0, full duplex |
| `pulse_sync` | single-cycle pulse across clock domains |
| `arbiter_rr` | round-robin arbiter (one-hot, fair) |

## Use it

```python
from myhdl import Signal, intbv, ResetSignal
from libfpga_myhdl import fifo_sync

# instantiate, simulate, or convert:
fifo = fifo_sync(clk, rst, wr_en, wr_data, rd_en, rd_data,
                 full, empty, count, WIDTH=8, DEPTH=16)
fifo.convert(hdl="Verilog")     # -> fifo_sync.v, ready for synthesis
```

## Verify

```sh
pip install myhdl pytest
pytest                # simulate + convert + compile + co-simulate
```

Three levels of assurance, all in CI:

1. **Simulation** — each block runs in Python against a self-checking
   testbench (`tests/test_*.py`).
2. **Conversion + compile** — every block converts to Verilog *and* VHDL,
   and the Verilog is compiled with Icarus (`tests/test_convert.py`).
3. **Co-simulation** — the strongest check: the *generated Verilog* is run
   through Icarus and driven by the MyHDL testbench, asserting it behaves
   **identically to the model** on the same stimulus (`tests/test_cosim.py`,
   via MyHDL's VPI bridge). If conversion ever introduced a semantic gap,
   this fails.

## Roadmap

- **v0.1 – v0.3 — shipped.** The blocks above, plus (v0.3) the
  co-simulation check.
- **v0.4** — I2C master, width converters, more cosim coverage.
- Parity with the [Verilog library](https://github.com/libfpga/libfpga)
  where it makes sense.

Want a block prioritized? [Open an issue](https://github.com/libfpga/libfpga-myhdl/issues)
or say so on [@libfpga](https://x.com/libfpga).

## License

MIT · Copyright (c) 2026 Antonio Roldao, Ph.D.
