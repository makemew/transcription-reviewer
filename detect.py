import chardet

file = r"data.csv"  

with open(file, "rb") as f:
    raw = f.read(100000)

print(chardet.detect(raw))