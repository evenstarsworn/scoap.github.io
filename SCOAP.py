import math
from collections import defaultdict

def scoap(inputs, outputs, gates, seq_cells, inpath="input.v"):
    """
    SCOAP analysis function for combinational and sequential circuits.
    Computes:
      - CC0, CC1: Controllability metrics
      - CO: Observability metrics
      - SC0, SC1, SO: Sequential testability
      - FwdLev, BkwdLev: Structural levels
    """

    # Step 0: initialize
    CC0, CC1, CO = {}, {}, {}
    SC0, SC1, SO = {}, {}, {}
    fwd_level, bkwd_level = {}, {}

    # Primary inputs
    for i in inputs:
        CC0[i] = 1.0
        CC1[i] = 1.0
        fwd_level[i] = 0

    # Sequential elements
    for s in seq_cells:
        q = s['output']
        d = s['input']
        CC0[q] = 1.0
        CC1[q] = 1.0
        fwd_level[q] = 0

    # Step 1: forward propagation (controllability)
    for gate_type, out, ins, name in gates:
        ins = list(ins)
        if all(i in CC0 for i in ins):
            if gate_type == 'AND':
                CC0[out] = min(CC0[i] for i in ins) + 1
                CC1[out] = sum(CC1[i] for i in ins) + 1
            elif gate_type == 'NAND':
                CC0[out] = sum(CC1[i] for i in ins) + 1
                CC1[out] = min(CC0[i] for i in ins) + 1
            elif gate_type == 'OR':
                CC0[out] = sum(CC0[i] for i in ins) + 1
                CC1[out] = min(CC1[i] for i in ins) + 1
            elif gate_type == 'NOR':
                CC0[out] = min(CC1[i] for i in ins) + 1
                CC1[out] = sum(CC0[i] for i in ins) + 1
            elif gate_type == 'NOT':
                CC0[out] = CC1[ins[0]] + 1
                CC1[out] = CC0[ins[0]] + 1
            elif gate_type == 'BUF':
                CC0[out] = CC0[ins[0]] + 1
                CC1[out] = CC1[ins[0]] + 1
            elif gate_type == 'XOR':
                if len(ins) == 2:
                    a, b = ins
                    CC0[out] = min(CC0[a] + CC0[b], CC1[a] + CC1[b]) + 1
                    CC1[out] = min(CC0[a] + CC1[b], CC1[a] + CC0[b]) + 1
            elif gate_type == 'XNOR':
                if len(ins) == 2:
                    a, b = ins
                    CC1[out] = min(CC0[a] + CC0[b], CC1[a] + CC1[b]) + 1
                    CC0[out] = min(CC0[a] + CC1[b], CC1[a] + CC0[b]) + 1
            else:
                CC0[out] = 1.0
                CC1[out] = 1.0

            fwd_level[out] = max(fwd_level[i] for i in ins) + 1

    # Step 2: backward propagation (observability)
    for i in outputs:
        CO[i] = 0.0
        bkwd_level[i] = 0

    for gate_type, out, ins, name in reversed(gates):
        if out in CO:
            for j in ins:
                if gate_type in ['AND', 'NAND']:
                    other_ins = [i for i in ins if i != j]
                    CO[j] = CO[out] + sum(CC1[k] for k in other_ins) + 1
                elif gate_type in ['OR', 'NOR']:
                    other_ins = [i for i in ins if i != j]
                    CO[j] = CO[out] + sum(CC0[k] for k in other_ins) + 1
                elif gate_type in ['XOR', 'XNOR']:
                    other_ins = [i for i in ins if i != j]
                    if len(other_ins) == 1:
                        k = other_ins[0]
                        CO[j] = CO[out] + min(CC0[k], CC1[k]) + 1
                else:
                    CO[j] = CO[out] + 1

                bkwd_level[j] = bkwd_level.get(out, 0) + 1

    # Step 3: sequential testability
    for n in set(list(CC0.keys()) + list(CO.keys())):
        SC0[n] = CC0.get(n, math.inf) + CO.get(n, math.inf)
        SC1[n] = CC1.get(n, math.inf) + CO.get(n, math.inf)
        SO[n]  = CO.get(n, math.inf)

    # --- ✅ Proper output building (with guaranteed newlines) ---
    lines = []
    lines.append(f"✅ SCOAP Results for {inpath}")
    header = f"{'Net':<10} {'FwdLev':<8} {'BkwdLev':<8} {'CC0':<8} {'CC1':<8} {'CO':<8} {'SC0':<8} {'SC1':<8} {'SO':<8}"
    lines.append(header)
    lines.append("-" * max(85, len(header)))

    all_nets = sorted(set(list(CC0.keys()) + list(CO.keys())))

    for n in all_nets:
        c0 = CC0.get(n, math.inf)
        c1 = CC1.get(n, math.inf)
        co = CO.get(n, math.inf)
        s0 = SC0.get(n, math.inf)
        s1 = SC1.get(n, math.inf)
        so = SO.get(n, math.inf)
        flev = fwd_level.get(n, "")
        blev = bkwd_level.get(n, "")

        def fmt(x):
            if isinstance(x, float):
                if math.isfinite(x):
                    return f"{x:.1f}"
                else:
                    return "inf"
            return str(x)

        row = f"{n:<10} {str(flev):<8} {str(blev):<8} {fmt(c0):<8} {fmt(c1):<8} {fmt(co):<8} {fmt(s0):<8} {fmt(s1):<8} {fmt(so):<8}"
        lines.append(row)

    output_str = "\n".join(lines) + "\n"

    # Print once (ensures newline formatting survives)
    print(output_str, end="")

    # Save output for debugging / web use
    try:
        with open("scoap_output.txt", "w", encoding="utf-8") as f:
            f.write(output_str)
    except Exception:
        pass

    # return results as well (for API use)
    return {
        "CC0": CC0,
        "CC1": CC1,
        "CO": CO,
        "SC0": SC0,
        "SC1": SC1,
        "SO": SO,
        "fwd_level": fwd_level,
        "bkwd_level": bkwd_level
    }
