"""Arithmetic and integrity building blocks."""
from myhdl import (block, always_seq, always, always_comb, Signal, intbv,
                   modbv, ResetSignal)


@block
def bin2gray(b, g):
    """Combinational binary -> Gray. Widths follow the signals."""
    @always_comb
    def comb():
        g.next = b ^ (b >> 1)
    return comb


@block
def gray2bin(g, b):
    """Combinational Gray -> binary (prefix-XOR)."""
    W = len(g)

    @always_comb
    def comb():
        acc = 0
        v = int(g)
        while v:
            acc ^= v
            v >>= 1
        b.next = acc & ((1 << W) - 1)
    return comb


@block
def lfsr(clk, rst, en, q, WIDTH=8, TAPS=0xB8):
    """Maximal-length Fibonacci LFSR (XNOR feedback: resets to zero
    safely). Default TAPS is the width-8 XAPP052 mask; pass your own for
    other widths."""
    sr = Signal(modbv(0)[WIDTH:])

    @always_seq(clk.posedge, reset=rst)
    def seq():
        if en:
            fb = 1
            masked = sr & TAPS
            # XNOR of the tapped bits
            parity = 0
            v = int(masked)
            while v:
                parity ^= (v & 1)
                v >>= 1
            fb = 1 - parity
            sr.next = ((sr << 1) | fb) & ((1 << WIDTH) - 1)

    @always_comb
    def out():
        q.next = sr
    return seq, out


@block
def mac(clk, rst, clr, en, a, b, acc, W=8, ACC_W=32):
    """Signed multiply-accumulate: the atom of every neural network.
    Multiply narrow, accumulate wide. clr zeroes the accumulator."""
    @always_seq(clk.posedge, reset=rst)
    def seq():
        if clr:
            acc.next = 0
        elif en:
            acc.next = acc + a * b
    return seq
