import sys
import zipfile
import random
import string

CRIB = b"ARCHA{"
PRINTABLE = set(range(32, 127))

def read_txt_from_zip(zip_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        for name in z.namelist():
            if name.lower().endswith(".txt"):
                return z.read(name).decode("utf-8", errors="replace")
    raise Exception("No .txt file in zip")

def emoji_to_bits(token):
    bits = ""
    i = 0
    while i < len(token):
        ch = token[i]
        if ch == "🖤":
            bits += "0"
            i += 1
        elif ch == "🐻":
            bits += "1"
            i += 3   # 🐻‍❄️ (ZWJ sequence)
        else:
            i += 1
    return bits

def extract_tokens(text):
    out = []
    for line in text.splitlines():
        for t in line.split():
            b = emoji_to_bits(t)
            if b:
                out.append(b)
    return out

def score_bytes(b):
    return sum(c in PRINTABLE for c in b)

def stage1_decode(tokens):
    uniq = list(set(tokens))
    if len(uniq) != 16:
        print("[!] Expected 16 unique symbols, got", len(uniq))

    best = (0, None)
    hexchars = "0123456789abcdef"

    for _ in range(50000):
        random.shuffle(uniq)
        mapping = dict(zip(uniq, hexchars))
        hexstr = "".join(mapping[t] for t in tokens)
        if len(hexstr) % 2:
            hexstr = hexstr[:-1]
        try:
            raw = bytes.fromhex(hexstr)
        except:
            continue
        s = score_bytes(raw)
        if b"ARCHA" in raw:
            s += 500
        if s > best[0]:
            best = (s, raw)
    return best[1]

def try_xor(cipher):
    for keylen in range(1, 40):
        for pos in range(len(cipher) - len(CRIB)):
            key = [None] * keylen
            ok = True
            for i, c in enumerate(CRIB):
                k = cipher[pos + i] ^ c
                idx = (pos + i) % keylen
                if key[idx] is None:
                    key[idx] = k
                elif key[idx] != k:
                    ok = False
                    break
            if not ok:
                continue

            for i in range(keylen):
                if key[i] is None:
                    key[i] = 0x20

            pt = bytes(cipher[i] ^ key[i % keylen] for i in range(len(cipher)))
            if b"ARCHA{" in pt:
                start = pt.find(b"ARCHA{")
                end = pt.find(b"}", start)
                if end != -1:
                    return pt[start:end+1]
    return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python solve_baby_crypto.py baby_crypto.zip")
        return

    text = read_txt_from_zip(sys.argv[1])
    tokens = extract_tokens(text)

    print("[+] Extracted tokens:", len(tokens))
    cipher = stage1_decode(tokens)

    if not cipher:
        print("[-] Stage1 decode failed")
        return

    flag = try_xor(cipher)
    if flag:
        print("\n[+] FLAG FOUND:")
        print(flag.decode())
    else:
        print("[-] Could not auto recover flag")

if __name__ == "__main__":
    main()
