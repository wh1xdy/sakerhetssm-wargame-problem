from __future__ import annotations
from pwn import remote

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess

from z3 import Distinct, Int, Solver, sat

ROOT = Path(__file__).resolve().parent
CHALLENGE_DIR = ROOT / "container" / "program"
SUBMISSION_FILE = CHALLENGE_DIR / "canonical.ssa"
OUT = Path(__file__).resolve().parent / "reordered.ssa"
INT_MOD = 1 << 63
INT_SIGN = 1 << 62
FIXED_REG_COUNT = 11
FIXED_ADMIN_TOKEN = 31337

LET_RE = re.compile(r"^let\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+);\s*$")


@dataclass
class Def:
    name: str
    rhs: str


def parse_defs(path: Path) -> list[Def]:
    out: list[Def] = []
    for raw in path.read_text(encoding="ascii").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = LET_RE.match(line)
        if m:
            out.append(Def(name=m.group(1), rhs=m.group(2).strip()))
    return out


def rhs_deps(rhs: str) -> list[str]:
    if rhs.startswith("const "):
        return []
    if rhs.startswith("check_admin "):
        return [rhs.split()[1]]
    rest = rhs.split(" ", 1)[1]
    left, right = [x.strip() for x in rest.split(",", 1)]
    return [left, right]


def dep_map(defs: list[Def]) -> dict[str, list[str]]:
    return {d.name: rhs_deps(d.rhs) for d in defs}


def write_reordered(path: Path, defs: list[Def], ordered_names: list[str]) -> None:
    by_name = {d.name: d for d in defs}
    lines = [f"let {n} = {by_name[n].rhs};" for n in ordered_names]
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def wrap_int(x: int) -> int:
    y = x % INT_MOD
    if y >= INT_SIGN:
        y -= INT_MOD
    return y


def _mul_args(rhs: str) -> tuple[str, str]:
    rest = rhs.split(" ", 1)[1]
    a, b = [x.strip() for x in rest.split(",", 1)]
    return a, b


def find_structure(defs):
    by_name = {d.name: d for d in defs}
    deps = dep_map(defs)

    root = defs[-1].name
    gate2 = deps[root][0]
    g2_l, _g2_r = _mul_args(by_name[gate2].rhs)
    gate1 = g2_l
    g1_l, _g1_r = _mul_args(by_name[gate1].rhs)
    gate0 = g1_l
    b0, b1 = _mul_args(by_name[gate0].rhs)

    inners = []
    for b in [b0, b1]:
        inner = deps[b][0]
        inners.append(inner)

    return {
        "root": root,
        "gate0": gate0,
        "gate1": gate1,
        "gate2": gate2,
        "branches": [b0, b1],
        "inners": inners,
    }


def run_with_schedule(defs, schedule: list[str], static_reg: dict[str, int], admin_token: int, reg_count: int) -> int:
    by_name = {d.name: d for d in defs}
    regs = [0] * reg_count
    for op in schedule:
        rhs = by_name[op].rhs
        if rhs.startswith("const "):
            value = wrap_int(int(rhs.split()[1]))
        elif rhs.startswith("check_admin "):
            dep = rhs.split()[1]
            value = admin_token if regs[static_reg[dep]] == admin_token else 0
        elif rhs.startswith("add "):
            rest = rhs.split(" ", 1)[1]
            l, r = [x.strip() for x in rest.split(",", 1)]
            value = wrap_int(regs[static_reg[l]] + regs[static_reg[r]])
        elif rhs.startswith("mul "):
            rest = rhs.split(" ", 1)[1]
            l, r = [x.strip() for x in rest.split(",", 1)]
            value = wrap_int(regs[static_reg[l]] * regs[static_reg[r]])
        else:
            rest = rhs.split(" ", 1)[1]
            l, r = [x.strip() for x in rest.split(",", 1)]
            value = wrap_int(regs[static_reg[l]] + regs[static_reg[r]])
        regs[static_reg[op]] = value
    return regs[static_reg[schedule[-1]]]


def derive_class_map(defs: list[Def], reg_count: int) -> dict[str, int]:
    names = sorted(d.name for d in defs)
    return {name: i % reg_count for i, name in enumerate(names)}


def topo_with_priority(defs, priority: list[str]) -> list[str]:
    names = [d.name for d in defs]
    deps = dep_map(defs)
    users = {n: [] for n in names}
    indeg = {n: len(deps[n]) for n in names}
    for n in names:
        for d in deps[n]:
            users[d].append(n)

    rank = {n: i for i, n in enumerate(priority)}
    root = defs[-1].name
    ready = [n for n in names if indeg[n] == 0]
    out: list[str] = []
    while ready:
        candidates = [n for n in ready if n != root or len(out) == len(names) - 1]
        if not candidates:
            candidates = ready
        candidates.sort(key=lambda n: (0, rank[n]) if n in rank else (1, n))
        cur = candidates[0]
        ready.remove(cur)
        out.append(cur)
        for u in users[cur]:
            indeg[u] -= 1
            if indeg[u] == 0:
                ready.append(u)
    if out[-1] != root:
        out = [n for n in out if n != root] + [root]
    return out


def solve_positions(defs) -> list[str]:
    names = [d.name for d in defs]
    shape = find_structure(defs)
    inner_a, inner_b = shape["inners"]
    outer_a, outer_b = shape["branches"]
    gate0 = shape["gate0"]
    gate1 = shape["gate1"]
    gate2 = shape["gate2"]
    root = shape["root"]

    class_of_var = derive_class_map(defs, FIXED_REG_COUNT)
    token_rhs = f"const {FIXED_ADMIN_TOKEN}"
    token_consts = [d.name for d in defs if d.rhs == token_rhs]
    cand_a = [t for t in token_consts if class_of_var.get(t) == class_of_var.get(inner_a)]
    cand_b = [t for t in token_consts if class_of_var.get(t) == class_of_var.get(inner_b)]

    reg_count = FIXED_REG_COUNT
    admin_token = FIXED_ADMIN_TOKEN
    op_ids = {name: i for i, name in enumerate(sorted(names))}
    static_reg = {name: op_ids[name] % reg_count for name in names}

    class_a_noise = sorted(
        [n for n in names if class_of_var.get(n) == class_of_var.get(inner_a) and n not in {inner_a, outer_a}]
    )
    class_b_noise = sorted(
        [n for n in names if class_of_var.get(n) == class_of_var.get(inner_b) and n not in {inner_b, outer_b}]
    )

    for t_a in sorted(cand_a, key=lambda x: (len(x), x)):
        for t_b in sorted(cand_b, key=lambda x: (len(x), x)):
            if t_a == t_b:
                continue
            critical = [inner_a, t_a, outer_a, inner_b, t_b, outer_b, gate0, gate1, gate2, root]
            cpos = {n: Int(f"k_{i}") for i, n in enumerate(critical)}
            ks = Solver()
            for n in critical:
                ks.add(cpos[n] >= 0, cpos[n] < len(critical))
            ks.add(Distinct([cpos[n] for n in critical]))
            ks.add(cpos[inner_a] < cpos[t_a], cpos[t_a] < cpos[outer_a])
            ks.add(cpos[inner_b] < cpos[t_b], cpos[t_b] < cpos[outer_b])
            ks.add(cpos[outer_a] < cpos[gate0], cpos[outer_b] < cpos[gate0])
            ks.add(cpos[gate0] < cpos[gate1], cpos[gate1] < cpos[gate2], cpos[gate2] < cpos[root])
            if ks.check() != sat:
                continue
            m = ks.model()
            critical_sorted = sorted(critical, key=lambda n: m[cpos[n]].as_long())
            priority = (
                class_a_noise
                + class_b_noise
                + critical_sorted
            )
            ordered = topo_with_priority(defs, priority)
            if run_with_schedule(defs, ordered, static_reg, admin_token, reg_count) == admin_token:
                return ordered

    return topo_with_priority(defs, names)


def main() -> None:
    defs = parse_defs(SUBMISSION_FILE)

    ordered = solve_positions(defs)
    write_reordered(OUT, defs, ordered)

    payload = OUT.read_bytes()
    wire = f"{len(payload)}\n".encode("ascii") + payload
    io = remote('localhost', 50000)
    print(io.recvline().decode())
    io.sendline(wire)
    print(io.recv().decode())


if __name__ == "__main__":
    main()
