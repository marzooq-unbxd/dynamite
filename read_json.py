import json
import ast

with open('scripts/faker/asterix/responses/query3.txt') as f:
    t=f.read()


y=ast.literal_eval(t)
z=y['analyzedQuery']
print(2)