from PIL import Image
from collections import Counter
img = Image.open('logos/Answer_Logo.png').convert('RGBA')
img = img.resize((200,200))
counts = Counter()
for r,g,b,a in img.getdata():
    if a < 128: continue
    if r>240 and g>240 and b>240: continue
    if r<10 and g<10 and b<10: continue
    counts[(r,g,b)] += 1
for c in counts.most_common(10):
    print(c)
