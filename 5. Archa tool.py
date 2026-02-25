#!/usr/bin/env python3
import hashlib

# === SHARDS จาก output ของคุณ ===
shard1 = bytes.fromhex("deadbeef")
shard2 = bytes.fromhex("cafebabe")
shard3 = b"KEY_"
shard4 = bytes.fromhex("e3b0c442")

candidates = []

# 1) ต่อ bytes ตรงๆ
data_bytes = shard1 + shard2 + shard3 + shard4

# 2) ต่อเป็น hex ทั้งหมด
data_hex_all = shard1.hex() + shard2.hex() + shard3.hex() + shard4.hex()

# 3) hex + ascii (KEY_ เป็นตัวอักษร)
data_hex_ascii = shard1.hex() + shard2.hex() + shard3.decode() + shard4.hex()

# 4) ascii ล้วน (เผื่อโจทย์หลอก)
data_ascii = shard1.hex() + shard2.hex() + "KEY_" + shard4.hex()

# --- helper ---
def all_hashes(label, b):
    return {
        "label": label,
        "md5": hashlib.md5(b).hexdigest(),
        "sha1": hashlib.sha1(b).hexdigest(),
        "sha256": hashlib.sha256(b).hexdigest()
    }

# --- คำนวณทุกแบบ ---
results = []

results.append(all_hashes("BYTES(concat)", data_bytes))
results.append(all_hashes("HEX-STRING(all)", data_hex_all.encode()))
results.append(all_hashes("HEX+ASCII(KEY_)", data_hex_ascii.encode()))
results.append(all_hashes("ASCII(all)", data_ascii.encode()))

print("\n================ POSSIBLE FLAGS ================\n")
for r in results:
    print(f"[{r['label']}]")
    print(f"ARCHA{{{r['md5']}}}   <- MD5 (ช่อง 39 ตัว โอกาสสูงสุด)")
    print(f"SHA1   : {r['sha1']}")
    print(f"SHA256 : {r['sha256']}")
    print("-" * 60)

print("\n👉 แนะนำ: เริ่ม submit จาก MD5 ทีละบรรทัดด้านบน")
