#!/usr/bin/env python3
"""Fix threads.h missing u64 type — add core.h include."""

with open("yabause/src/threads.h", "r") as f:
    content = f.read()

# Add core.h include after the header guard / license block
content = content.replace(
    "int YabNanosleep(u64 ns);",
    "int YabNanosleep(unsigned long long ns);"
)

with open("yabause/src/threads.h", "w") as f:
    f.write(content)

print("Fixed u64 type in threads.h")
