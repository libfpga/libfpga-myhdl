# Changelog

## v0.3.0 — 2026-07-04

- `pulse_sync` (single-cycle pulse CDC) and `arbiter_rr` (round-robin
  arbiter).
- **Co-simulation checks** (`tests/test_cosim.py`): the generated Verilog
  is run through Icarus and driven by the MyHDL testbench, proving it
  behaves identically to the model. Uses MyHDL's VPI bridge; CI builds it.

## v0.2.0 — 2026-07-04

- `uart_tx`, `uart_rx` (8N1) and `spi_master` (mode 0, full duplex).
- Verified by a UART transmitter->receiver loopback and an SPI behavioral
  slave; both convert to Verilog + VHDL and the Verilog compiles.

## v0.1.0 — 2026-07-04

- CDC (`sync_bit`, `reset_sync`), `fifo_sync`, `bin2gray`/`gray2bin`,
  `lfsr`, `mac`. Self-checking pytest suites + Verilog/VHDL conversion
  checks (generated Verilog compiled with Icarus).
