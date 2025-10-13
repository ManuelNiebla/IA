from model import model

def p_fs_given_ce_si_sample(N=300_000):
    ok = si = 0
    for _ in range(N):
        s = model.sample()
        if s["CE"] == "Si":
            ok += 1
            si += (s["FS"] == "Si")
    return (si / ok) if ok else float("nan")

if __name__ == "__main__":
    p = p_fs_given_ce_si_sample()
    print(f'MUESTREO  P(FS="Si" | CE="Si") = {p:.6f}')
