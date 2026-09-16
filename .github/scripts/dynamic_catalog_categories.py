from pathlib import Path
import re

path=Path('index.html')
s=path.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'{label} not found')
    s=s.replace(old,new,1)

if 'const escapeCatalogText=' not in s:
    old="const money=value=>Number(value||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});"
    new=old+"\n  const escapeCatalogText=value=>String(value??'').replace(/[&<>\\\"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}[char]));\n  const categoryIcon=slug=>({pizzas:'pizza',esfirras:'croissant',bebidas:'cup-soda'}[slug]||'utensils');"
    replace_once(old,new,'money helper')

s=s.replace('.menu-sections .section{display:none}\n    .menu-sections #pizzas{display:block}', '.menu-sections .section{display:none}\n    .menu-sections .section.active{display:block}', 1)

pattern=r"  function pizzaCard\(product\)\{.*?\n  \}\n  function simpleCard"
replacement="""  function catalogCard(product){
    const acrescimo=Number(product.price_addition||0);
    const badge=acrescimo>0?`<span class=\"product-badge\">ACRÉSCIMO: ${money(acrescimo)}</span>`:'';
    const sizeRows=productSizesFor(product);
    const usesSizes=product.pricing_mode==='sizes'||sizeRows.length>0;
    const precoInicial=productStartingPrice(product);
    const priceLabel=usesSizes&&sizeRows.length?`a partir de ${money(precoInicial)}`:money(precoInicial);
    const name=escapeCatalogText(product.name||'Produto');
    const description=escapeCatalogText(product.description||'Produto preparado na hora.');
    const image=product.image_url||pizzaImage;
    return `<article class=\"product\" data-configure-product=\"${product.id}\"><div class=\"product-copy\">${badge}<h3>${name}</h3><p>${description}</p><strong class=\"price\">${priceLabel}</strong></div><img class=\"product-image\" src=\"${image}\" alt=\"${name}\" loading=\"lazy\"></article>`
  }
  function simpleCard"""
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('catalog card block not found')
s=s2

pattern=r"  function renderCatalog\(\)\{.*?\n  \}\n  async function loadCatalog\(\)"
replacement="""  function renderCatalog(){
    const categoriesHost=document.querySelector('.categories');
    const sectionsHost=document.querySelector('.menu-sections');
    if(!categoriesHost||!sectionsHost)return;
    const visibleCategories=catalogCategories.filter(category=>catalogProducts.some(product=>String(product.category_id)===String(category.id)));
    if(!visibleCategories.length){
      categoriesHost.innerHTML='<span class=\"category-kicker\">Cardápio</span>';
      sectionsHost.innerHTML='<div class=\"empty\">Nenhum produto disponível no momento.</div>';
      return;
    }
    categoriesHost.innerHTML='<span class=\"category-kicker\">Cardápio</span>'+visibleCategories.map((category,index)=>`<button class=\"category ${index===0?'active':''}\" data-target=\"${escapeCatalogText(category.slug)}\"><i data-lucide=\"${categoryIcon(category.slug)}\"></i>${escapeCatalogText(category.name||category.slug)}</button>`).join('');
    sectionsHost.innerHTML=visibleCategories.map((category,index)=>{
      const products=catalogProducts.filter(product=>String(product.category_id)===String(category.id));
      return `<section class=\"section ${index===0?'active':''}\" id=\"${escapeCatalogText(category.slug)}\"><div class=\"section-head\"><div><span class=\"eyebrow\">Escolha seu produto</span><h2>${escapeCatalogText(category.name||category.slug)}</h2></div><p>${products.length} ${products.length===1?'opção':'opções'}</p></div><div class=\"product-grid\">${products.map(catalogCard).join('')}</div></section>`;
    }).join('');
    lucide.createIcons();
  }
  async function loadCatalog()"""
s2,n=re.subn(pattern,replacement,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('renderCatalog block not found')
s=s2

old="""    document.querySelectorAll('.category').forEach(tab=>tab.addEventListener('click',()=>{
      const target=tab.dataset.target;
      document.querySelectorAll('.menu-sections .section').forEach(section=>section.style.display=section.id===target?'block':'none');
    },true));"""
new="""    document.addEventListener('click',event=>{
      const tab=event.target.closest('.category[data-target]');
      if(!tab)return;
      const target=tab.dataset.target;
      document.querySelectorAll('.category[data-target]').forEach(item=>item.classList.toggle('active',item===tab));
      document.querySelectorAll('.menu-sections .section').forEach(section=>section.classList.toggle('active',section.id===target));
    });"""
replace_once(old,new,'category click handler')

path.write_text(s,encoding='utf-8')
print('Dynamic catalog categories patch applied')
