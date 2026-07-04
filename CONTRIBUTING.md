# Contributing

Every block needs:

1. A MyHDL `@block` in `libfpga_myhdl/` — synthesizable style, docstring
   stating what it is and when to use it.
2. A **self-checking test** in `tests/` (simulate against a Python model,
   `assert` the results).
3. Inclusion in `tests/test_convert.py` so its Verilog + VHDL conversion
   is checked and the Verilog is compiled.
4. For non-trivial logic, a co-simulation test in `tests/test_cosim.py`
   that drives the generated Verilog and asserts it matches the model.

Style: internal generator functions must not use Verilog/SystemVerilog
keywords as names (`logic`, `reg`, `wire`…) — MyHDL turns them into block
labels and signal names, and the generated RTL must compile. Prefer
`seq` / `comb` for the process, `sr` / `state` for registers.

Run `pytest` before pushing — it is exactly what CI runs.
