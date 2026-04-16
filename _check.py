import ast
with open('main.py', encoding='utf-8') as f:
    src = f.read()
try:
    ast.parse(src)
    print('OK')
except SyntaxError as e:
    print(f'ERROR line {e.lineno}: {e.msg}')
    print(repr(e.text))
