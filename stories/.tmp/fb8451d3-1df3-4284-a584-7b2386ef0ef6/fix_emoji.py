import json

story_path = '/home/charles/code-stories-cache/stories/.tmp/fb8451d3-1df3-4284-a584-7b2386ef0ef6/story.json'

# Read raw bytes
with open(story_path, 'rb') as f:
    raw = f.read()

# Replace the wrong escape sequence: \\udde0 -> \\udd9e
# In the file, this is the literal bytes for the string "udde0" -> "udd9e"
old = b'\\\\udde0'
new = b'\\\\udd9e'

count = raw.count(old)
print(f"Found {count} occurrence(s) of {old}")

if count == 1:
    raw = raw.replace(old, new, 1)
    with open(story_path, 'wb') as f:
        f.write(raw)
    print("Fixed successfully!")
else:
    print("ERROR: Expected exactly 1 occurrence, aborting.")

# Verify
with open(story_path, 'rb') as f:
    verify = f.read()
idx = verify.find(b'PicoClaw')
while True:
    next_idx = verify.find(b'PicoClaw', idx + 1)
    if next_idx == -1:
        break
    idx = next_idx
print(f"Verification - bytes around last PicoClaw: {verify[idx:idx+40]}")
