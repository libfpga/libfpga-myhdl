# Changelog

## v0.2.0 — 2026-07-04

- `uart_tx`, `uart_rx` (8N1) and `spi_master` (mode 0, full duplex).
- Verified by a UART transmitter->receiver loopback and an SPI behavioral
  slave; both convert to Verilog + VHDL and the Verilog compiles.

## v0.1.0 — 2026-07-04

- CDC (`sync_bit`, `reset_sync`), `fifo_sync`, `bin2gray`/`gray2bin`,
  `lfsr`, `mac`. Self-checking pytest suites + Verilog/VHDL conversion
  checks (generated Verilog compiled with Icarus).
