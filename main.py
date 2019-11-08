from dataclasses import dataclass, fields

@dataclass
class Fun:

    a: int
    b: int

f = Fun(1, 2)

fields(f)

for
