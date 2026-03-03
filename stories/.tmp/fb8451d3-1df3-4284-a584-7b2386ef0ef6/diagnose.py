import json

with open('/home/charles/code-stories-cache/stories/.tmp/fb8451d3-1df3-4284-a584-7b2386ef0ef6/story.json') as f:
    data = json.load(f)

ch13 = data['chapters'][13]
print(f"Chapter label: {ch13['label']}")
print(f"Number of snippets: {len(ch13['snippets'])}")

for i, s in enumerate(ch13['snippets']):
    if 'PicoClaw' in s['content']:
        idx = s['content'].index('PicoClaw')
        snippet = s['content'][idx:idx+20]
        print(f"Snippet index: {i}")
        print(f"Current: {repr(snippet)}")
        for ch in snippet:
            if ord(ch) > 127:
                print(f"  Found non-ASCII char: U+{ord(ch):04X} = {ch}")
