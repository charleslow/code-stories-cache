import sys

with open('/home/charles/code-stories-cache/stories/.tmp/fb8451d3-1df3-4284-a584-7b2386ef0ef6/story.json', 'rb') as f:
    raw = f.read()

# Find the PicoClaw text near the Start command in chapter 13
idx = raw.find(b'PicoClaw')
# Find the second occurrence (first is in title, we want the one in snippet content)
while True:
    next_idx = raw.find(b'PicoClaw', idx + 1)
    if next_idx == -1:
        break
    idx = next_idx

# Show bytes around PicoClaw
start = idx
end = idx + 40
chunk = raw[start:end]
print(f"Raw bytes around last PicoClaw: {chunk}")
print(f"Hex: {chunk.hex()}")

# Also find all occurrences
idx = 0
count = 0
while True:
    idx = raw.find(b'PicoClaw', idx)
    if idx == -1:
        break
    context_bytes = raw[idx:idx+40]
    print(f"\nOccurrence {count} at offset {idx}: {context_bytes}")
    print(f"Hex: {context_bytes.hex()}")
    idx += 1
    count += 1
