"""Serial peripherals: UART transmitter/receiver and SPI master."""
from myhdl import (block, always_seq, always_comb, Signal, intbv, modbv,
                   ResetSignal, enum)
from math import ceil, log2


@block
def uart_tx(clk, rst, valid, ready, data, tx, CLKS_PER_BIT=868):
    """UART transmitter, 8N1. Accepts a byte when valid && ready; line
    idles high; LSB first. CLKS_PER_BIT = round(f_clk / baud)."""
    t_state = enum('IDLE', 'START', 'DATA', 'STOP')
    state = Signal(t_state.IDLE)
    CW = int(ceil(log2(CLKS_PER_BIT))) + 1
    cnt = Signal(intbv(0)[CW:])
    bit_i = Signal(intbv(0)[3:])
    shifter = Signal(intbv(0)[8:])

    @always_seq(clk.posedge, reset=rst)
    def seq():
        if state == t_state.IDLE:
            tx.next = 1
            cnt.next = 0
            bit_i.next = 0
            if valid:
                shifter.next = data
                tx.next = 0                 # start bit
                state.next = t_state.START
        elif state == t_state.START:
            if cnt == CLKS_PER_BIT - 1:
                cnt.next = 0
                tx.next = shifter[0]
                state.next = t_state.DATA
            else:
                cnt.next = cnt + 1
        elif state == t_state.DATA:
            if cnt == CLKS_PER_BIT - 1:
                cnt.next = 0
                if bit_i == 7:
                    tx.next = 1             # stop bit
                    state.next = t_state.STOP
                else:
                    shifter.next = shifter >> 1
                    tx.next = shifter[1]
                    bit_i.next = bit_i + 1
            else:
                cnt.next = cnt + 1
        else:  # STOP
            if cnt == CLKS_PER_BIT - 1:
                state.next = t_state.IDLE
            else:
                cnt.next = cnt + 1

    @always_comb
    def out():
        ready.next = (state == t_state.IDLE)
    return seq, out


@block
def uart_rx(clk, rst, rx, data, valid, CLKS_PER_BIT=868):
    """UART receiver, 8N1. Samples each bit at its centre; a start edge
    that doesn't survive the half-bit check is rejected. rx must already
    be synchronized to clk (use sync_bit for a pin)."""
    t_state = enum('IDLE', 'START', 'DATA', 'STOP')
    state = Signal(t_state.IDLE)
    CW = int(ceil(log2(CLKS_PER_BIT))) + 1
    cnt = Signal(intbv(0)[CW:])
    bit_i = Signal(intbv(0)[3:])
    shifter = Signal(intbv(0)[8:])

    @always_seq(clk.posedge, reset=rst)
    def seq():
        valid.next = 0
        if state == t_state.IDLE:
            cnt.next = 0
            bit_i.next = 0
            if rx == 0:
                state.next = t_state.START
        elif state == t_state.START:
            if cnt == CLKS_PER_BIT // 2 - 1:
                cnt.next = 0
                if rx == 0:
                    state.next = t_state.DATA
                else:
                    state.next = t_state.IDLE   # glitch
            else:
                cnt.next = cnt + 1
        elif state == t_state.DATA:
            if cnt == CLKS_PER_BIT - 1:
                cnt.next = 0
                shifter.next = (shifter >> 1) | (rx << 7)
                if bit_i == 7:
                    state.next = t_state.STOP
                else:
                    bit_i.next = bit_i + 1
            else:
                cnt.next = cnt + 1
        else:  # STOP
            if cnt == CLKS_PER_BIT - 1:
                cnt.next = 0
                state.next = t_state.IDLE
                if rx == 1:
                    data.next = shifter
                    valid.next = 1
            else:
                cnt.next = cnt + 1
    return seq


@block
def spi_master(clk, rst, start, tx_data, rx_data, busy, done,
               sck, mosi, miso, cs_n, CLK_DIV=4):
    """SPI master, mode 0 (CPOL=0, CPHA=0), 8-bit, MSB first, full duplex.
    sck idles low; mosi changes on falling sck; both sample on rising sck.
    SCK = clk / (2*CLK_DIV)."""
    CW = int(ceil(log2(CLK_DIV))) + 1
    div = Signal(intbv(0)[CW:])
    bitcnt = Signal(intbv(0)[4:])
    shifter = Signal(intbv(0)[8:])
    busy_r = Signal(bool(0))
    sck_r = Signal(bool(0))

    @always_seq(clk.posedge, reset=rst)
    def seq():
        done.next = 0
        if not busy_r:
            sck_r.next = 0
            if start:
                busy_r.next = 1
                cs_n.next = 0
                shifter.next = tx_data
                mosi.next = tx_data[7]
                bitcnt.next = 0
                div.next = 0
        elif div == CLK_DIV - 1:
            div.next = 0
            if not sck_r:
                sck_r.next = 1                       # rising: sample miso
                rx_data.next = ((rx_data << 1) | miso) & 0xFF
            else:
                sck_r.next = 0                       # falling: next bit out
                if bitcnt == 7:
                    busy_r.next = 0
                    cs_n.next = 1
                    done.next = 1
                else:
                    bitcnt.next = bitcnt + 1
                    shifter.next = (shifter << 1) & 0xFF
                    mosi.next = shifter[6]
        else:
            div.next = div + 1

    @always_comb
    def out():
        busy.next = busy_r
        sck.next = sck_r
    return seq, out
