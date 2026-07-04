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
pytest                # simulate every block + prove each converts & compiles
```

`tests/test_convert.py` converts every module to Verilog and VHDL and
compiles the Verilog with Icarus — the generated RTL is real, not just
non-empty.

## Roadmap

- **v0.1 + v0.2 — shipped.** The blocks above (UART tx/rx and SPI added
  in v0.2, with a tx->rx loopback and a behavioral-slave test).
- **v0.3** — pulse synchronizer, arbiter, I2C; a co-simulation check that
  the *generated Verilog* passes the same testbench as the MyHDL model.
- Parity with the [Verilog library](https://github.com/libfpga/libfpga)
  where it makes sense.

Want a block prioritized? [Open an issue](https://github.com/libfpga/libfpga-myhdl/issues)
or say so on [@libfpga](https://x.com/libfpga).

## License

MIT · Copyright (c) 2026 Antonio Roldao, Ph.D.
