`timescale 1ns/1ps
// Self-checking testbench for the MyHDL-generated signed multiply-accumulate.
module tb_mac_check;
  reg clk = 0, rst = 0, clr = 0, en = 0;
  reg signed [7:0] a, b;
  wire signed [31:0] acc;
  integer errors = 0;
  lfpga_mac dut (.clk(clk), .rst(rst), .clr(clr), .en(en), .a(a), .b(b), .acc(acc));
  always #5 clk = ~clk;
  task step; begin @(posedge clk); #1; end endtask
  initial begin
    rst = 1; step; rst = 0;
    clr = 1; en = 0; step; clr = 0;                    // acc <- 0
    if (acc !== 0) begin errors=errors+1; $display("FAIL clr acc=%0d", acc); end
    en = 1;
    a = 3;  b = 4;  step;                               // +12  -> 12
    if (acc !== 12) begin errors=errors+1; $display("FAIL 3*4 acc=%0d", acc); end
    a = 5;  b = -6; step;                               // -30  -> -18
    if (acc !== -18) begin errors=errors+1; $display("FAIL 5*-6 acc=%0d", acc); end
    a = -7; b = -8; step;                               // +56  -> 38
    if (acc !== 38) begin errors=errors+1; $display("FAIL -7*-8 acc=%0d", acc); end
    en = 0; a = 100; b = 100; step;                     // disabled -> unchanged
    if (acc !== 38) begin errors=errors+1; $display("FAIL en=0 acc=%0d", acc); end
    clr = 1; step;                                      // clear -> 0
    if (acc !== 0) begin errors=errors+1; $display("FAIL clr2 acc=%0d", acc); end
    if (errors == 0) $display("TB PASS: mac (signed accumulate + clr + en)");
    else             $display("TB FAIL: mac (%0d errors)", errors);
    $finish;
  end
endmodule
