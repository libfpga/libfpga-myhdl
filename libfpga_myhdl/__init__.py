"""libfpga-myhdl: verified FPGA building blocks in MyHDL.

Every block is a @block function that both simulates (Python) and
converts to Verilog/VHDL. See the tests/ suite for self-checking
verification and the conversion checks.
"""
from .cdc import sync_bit, reset_sync
from .fifo import fifo_sync
from .math import bin2gray, gray2bin, lfsr, mac
from .serial import uart_tx, uart_rx, spi_master

__version__ = "0.2.0"
__all__ = ["sync_bit", "reset_sync", "fifo_sync",
           "bin2gray", "gray2bin", "lfsr", "mac",
           "uart_tx", "uart_rx", "spi_master"]
