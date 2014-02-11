import os

p = r"e:/music/voice/rhythm"
for root, dirs, files in os.walk(p):
    print(root, dirs, files)
