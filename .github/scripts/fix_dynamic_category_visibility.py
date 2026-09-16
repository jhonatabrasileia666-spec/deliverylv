from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')
old = "document.querySelectorAll('.category').forEach(button=>button.onclick=()=>{document.querySelectorAll('.category').forEach(item=>item.classList.remove('active'));button.classList.add('active');document.querySelector('#'+button.dataset.target)?.scrollIntoView({behavior:'smooth',block:'start'})});"
new = "document.querySelectorAll('.category').forEach(button=>button.onclick=()=>{document.querySelectorAll('.category').forEach(item=>item.classList.remove('active'));button.classList.add('active');const target=button.dataset.target;document.querySelectorAll('.menu-sections .section').forEach(section=>section.style.display=section.id===target?'block':'none');document.querySelector('#'+target)?.scrollIntoView({behavior:'smooth',block:'start'})});"
if old not in text:
    raise SystemExit('dynamic category click marker not found')
text = text.replace(old,new,1)
path.write_text(text,encoding='utf-8')
print('dynamic category visibility fixed')
