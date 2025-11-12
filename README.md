# SCOAP Testability Analyzer (Python)

This repository provides a **Python implementation of SCOAP** (Sandia Controllability/Observability Analysis Program) for combinational and sequential digital circuits.

## 📘 Overview
SCOAP metrics measure:
- **CC0 / CC1** – Controllability of a net being logic 0 or 1.
- **CO** – Observability (ease of propagating a fault to a primary output).
- **SC0 / SC1 / SO** – Sequential testability metrics (accounting for flip-flops).
- **FwdLev / BkwdLev** – Forward and backward structural levels.

## 🧩 Features
- Supports standard Verilog gate-level netlists.
- Handles both **combinational** and **sequential** circuits.
- Implements full **levelization** algorithm.
- Outputs a detailed tabular report.

## 🛠️ Usage
### 1️⃣ Run on a Verilog file:
```bash
python3 SCOAP.py your_circuit.v

