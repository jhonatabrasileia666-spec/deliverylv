from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old="detail:item.sizeName?`Tamanho ${item.sizeName}`:(category==='pizzas'?'':'Porção escolhida')"
new="detail:item.sizeName?'':(category==='pizzas'?'':'Porção escolhida')"
if old not in s:
    raise SystemExit('size detail marker not found')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
