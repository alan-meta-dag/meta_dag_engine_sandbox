import sys, os, random, pathlib

def load_seed(path):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for l in f:
            l = l.strip()
            if l:
                lines.append(l)
    return lines


# ====== 基本 fuzz 種類（非語意改寫，不破壞 prompt） ======
def fuzz_one(line):
    variants = []

    # 1) 加入前置空白／換行
    variants.append(" " + line)
    variants.append("\t" + line)

    # 2) 加入後置空白
    variants.append(line + " ")
    variants.append(line + "\t")

    # 3) 加上 harmless noise token
    variants.append(f"[NOISE]{line}")
    variants.append(f"{line}[NOISE]")

    # 4) 加符號 padding
    variants.append("※" + line)
    variants.append(line + "※")

    # 5) 加括號
    variants.append("(" + line + ")")
    variants.append("【" + line + "】")

    # 6) unicode 變體
    variants.append("​" + line)   # zero-width space
    variants.append(line + "​")   # zero-width space

    # 7) duplicate
    variants.append(line + " " + line)

    # 保留原句
    variants.append(line)

    return list(set(variants))   # 去重


def build_corpus(seed_lines, target_count=2000):
    all_variants = []

    for line in seed_lines:
        fv = fuzz_one(line)
        all_variants.extend(fv)

    # 去重
    all_variants = list(set(all_variants))

    # 不夠 → 隨機補滿
    if len(all_variants) < target_count:
        while len(all_variants) < target_count:
            all_variants.append(random.choice(all_variants))

    # 太多 → 截斷
    return all_variants[:target_count]


def main():
    if len(sys.argv) < 3:
        print("Usage: py generate_tul_corpus.py <seed_file> <count>")
        return

    seed_path = sys.argv[1]
    count = int(sys.argv[2])

    seed_lines = load_seed(seed_path)
    print(f"[INFO] Seed loaded: {len(seed_lines)} lines")

    corpus = build_corpus(seed_lines, count)

    out_dir = pathlib.Path("tests/pressure_cases_tul_full")
    out_dir.mkdir(exist_ok=True, parents=True)

    out_file = out_dir / f"TUL_{count}.txt"

    with open(out_file, "w", encoding="utf-8") as f:
        for l in corpus:
            f.write(l + "\n")

    print(f"[DONE] Generated {len(corpus)} lines")
    print(f"[OUT]  {out_file}")


if __name__ == "__main__":
    main()
