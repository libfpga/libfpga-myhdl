"""Serial: UART tx->rx loopback, SPI master against a behavioral slave."""
import random
from myhdl import (block, always, instance, Signal, intbv, modbv,
                   ResetSignal, delay, StopSimulation)
from libfpga_myhdl import uart_tx, uart_rx, spi_master


def test_uart_loopback():
    """Feed the transmitter's line straight into the receiver; every byte
    sent must be received intact."""
    random.seed(2)
    CPB = 8   # small clks-per-bit for fast sim

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        line = Signal(bool(1))                 # the serial wire (idle high)
        # tx side
        t_valid = Signal(bool(0)); t_ready = Signal(bool(0))
        t_data = Signal(intbv(0)[8:])
        # rx side
        r_data = Signal(intbv(0)[8:]); r_valid = Signal(bool(0))

        u_tx = uart_tx(clk, rst, t_valid, t_ready, t_data, line, CLKS_PER_BIT=CPB)
        u_rx = uart_rx(clk, rst, line, r_data, r_valid, CLKS_PER_BIT=CPB)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        sent = []
        got = []

        @instance
        def collect():
            while True:
                yield clk.posedge
                yield delay(1)
                if r_valid:
                    got.append(int(r_data))

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            for _ in range(6):
                b = random.randint(0, 255)
                # wait until the tx is ready, then present a byte
                while not t_ready:
                    yield clk.posedge
                yield clk.negedge
                t_data.next = b; t_valid.next = 1
                sent.append(b)
                yield clk.negedge; t_valid.next = 0
                # wait for the whole frame (10 bits) plus slack
                for _ in range((CPB * 12)):
                    yield clk.posedge
            # drain
            for _ in range(CPB * 12):
                yield clk.posedge
            assert got == sent, f"loopback mismatch: sent {sent}, got {got}"
            raise StopSimulation
        return u_tx, u_rx, clk_gen, collect, stim

    tb().run_sim()


def test_spi_master():
    """A behavioral mode-0 slave echoes a known byte and checks what it
    received; the master's rx_data must equal the slave's response."""
    random.seed(4)

    @block
    def tb():
        clk = Signal(bool(0)); rst = ResetSignal(0, active=1, isasync=False)
        start = Signal(bool(0))
        tx_data = Signal(intbv(0)[8:]); rx_data = Signal(intbv(0)[8:])
        busy = Signal(bool(0)); done = Signal(bool(0))
        sck = Signal(bool(0)); mosi = Signal(bool(0))
        miso = Signal(bool(0)); cs_n = Signal(bool(1))
        dut = spi_master(clk, rst, start, tx_data, rx_data, busy, done,
                         sck, mosi, miso, cs_n, CLK_DIV=2)

        @always(delay(5))
        def clk_gen():
            clk.next = not clk

        slave_rx = [0]
        slave_tx = [0]

        @instance
        def slave_sample():                    # rising sck: capture mosi
            while True:
                yield sck.posedge
                slave_rx[0] = ((slave_rx[0] << 1) | int(mosi)) & 0xFF

        @instance
        def slave_drive():                     # falling sck: present next bit
            while True:
                yield sck.negedge
                slave_tx[0] = (slave_tx[0] << 1) & 0xFF
                miso.next = (slave_tx[0] >> 7) & 1

        @instance
        def stim():
            rst.next = 1
            yield clk.posedge; yield clk.posedge
            rst.next = 0
            for _ in range(4):
                t = random.randint(0, 255)
                r = random.randint(0, 255)
                slave_rx[0] = 0
                slave_tx[0] = r
                miso.next = (r >> 7) & 1        # present MSB before first edge
                yield clk.negedge
                tx_data.next = t; start.next = 1
                yield clk.negedge; start.next = 0
                while not done:
                    yield clk.posedge
                yield clk.negedge
                assert slave_rx[0] == t, f"slave got {slave_rx[0]:#x}, want {t:#x}"
                assert int(rx_data) == r, f"master got {int(rx_data):#x}, want {r:#x}"
            raise StopSimulation
        return dut, clk_gen, slave_sample, slave_drive, stim

    tb().run_sim()
