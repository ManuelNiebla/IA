from itertools import product
from model import model

names = [s.name for s in model.states]
dom = {"CE":["Si","No"], "ACT":["Si","No"], "MF":["Si","No"], "SC":["Si","No"], "FS":["Si","No"]}

def row(assign):
    return [assign[n] for n in names]

def evidence_probability(evid):
    p = 0.0
    grids = [dom[n] for n in names]
    for vals in product(*grids):
        a = {n: v for n, v in zip(names, vals)}
        if all(a[k] == v for k, v in evid.items()):
            p += model.probability([row(a)])
    return p

def query_probability(var, val, evid=None):
    evid = evid or {}
    pe = evidence_probability(evid)
    if pe == 0.0:
        return 0.0
    pj = evidence_probability({**evid, var: val})
    return pj / pe

if __name__ == "__main__":
    p = query_probability("FS", "Si", {"CE": "Si"})
    print(f'ENUMERACIÓN  P(FS="Si" | CE="Si") = {p:.6f}')  # ≈ 0.769200
