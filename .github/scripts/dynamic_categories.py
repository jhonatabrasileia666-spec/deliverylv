from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

# Add thumbnail styling for products that use a single fixed price.
css_marker = '.simple-card h3{margin:0 0 4px;font-size:15px}'
if css_marker not in text:
    raise SystemExit('simple-card css marker not found')
text = text.replace(css_marker, '.simple-thumb{width:74px;height:74px;flex:none;object-fit:cover;border-radius:11px}.simple-card-copy{flex:1;min-width:0}'+css_marker, 1)

# Replace only the fixed/simple card renderer so photos appear when available.
old_simple = '''  function simpleCard(product,category){
    const sizeRows=productSizesFor(product), configurable=product.pricing_mode==='sizes'||sizeRows.length>0||product.allow_edges;
    const price=productStartingPrice(product);
    const priceLabel=configurable&&sizeRows.length?`a partir de ${money(price)}`:money(price);
    const button=configurable?`<button class="quick-add" data-configure-product="${product.id}" aria-label="Escolher opções de ${product.name}"><i data-lucide="sliders-horizontal"></i></button>`:`<button class="quick-add" data-quick="${product.name}" data-product-id="${product.id}" data-category="${category}" data-price="${price}" aria-label="Adicionar ${product.name}"><i data-lucide="plus"></i></button>`;
    return `<div class="simple-card"><div><h3>${product.name}</h3><p>${product.description||'Escolha sua quantidade no pedido'}</p></div><strong class="simple-price">${priceLabel}</strong>${button}</div>`
  }'''
new_simple = '''  function simpleCard(product,category){
    const sizeRows=productSizesFor(product), configurable=product.pricing_mode==='sizes'||sizeRows.length>0||product.allow_edges;
    const price=productStartingPrice(product);
    const priceLabel=configurable&&sizeRows.length?`a partir de ${money(price)}`:money(price);
    const button=configurable?`<button class="quick-add" data-configure-product="${product.id}" aria-label="Escolher opções de ${product.name}"><i data-lucide="sliders-horizontal"></i></button>`:`<button class="quick-add" data-quick="${product.name}" data-product-id="${product.id}" data-category="${category}" data-price="${price}" aria-label="Adicionar ${product.name}"><i data-lucide="plus"></i></button>`;
    const image=product.image_url?`<img class="simple-thumb" src="${product.image_url}" alt="${product.name}" loading="lazy">`:'';
    return `<div class="simple-card">${image}<div class="simple-card-copy"><h3>${product.name}</h3><p>${product.description||'Escolha sua quantidade no pedido'}</p></div><strong class="simple-price">${priceLabel}</strong>${button}</div>`
  }'''
if old_simple not in text:
    raise SystemExit('simpleCard marker not found')
text = text.replace(old_simple, new_simple, 1)

# Make every active database category visible in the customer menu.
pattern = re.compile(r'''  function renderCatalog\(\)\{.*?\n  \}\n  async function loadCatalog\(\)\{''', re.S)
replacement = '''  function renderCatalog(){
    const byCategory=new Map(catalogCategories.map(category=>[category.slug,[]]));
    catalogProducts.forEach(product=>{const category=categoryForProduct(product);if(category){if(!byCategory.has(category.slug))byCategory.set(category.slug,[]);byCategory.get(category.slug).push(product)}});
    const pizzasFromDb=byCategory.get('pizzas')||[];
    document.querySelector('#pizza-grid').innerHTML=pizzasFromDb.map(pizzaCard).join('')||'<div class="empty">Nenhuma pizza cadastrada.</div>';
    document.querySelector('#savory-list').innerHTML=(byCategory.get('esfirras')||[]).map(product=>simpleCard(product,'esfirras')).join('')||'<div class="empty">Nenhuma esfirra cadastrada.</div>';
    document.querySelector('#sweet-list').innerHTML='';
    document.querySelector('#drink-list').innerHTML=(byCategory.get('bebidas')||[]).map(product=>simpleCard(product,'bebidas')).join('')||'<div class="empty">Nenhuma bebida cadastrada.</div>';

    const coreSlugs=new Set(['pizzas','esfirras','bebidas']);
    const nav=document.querySelector('.categories');
    const sections=document.querySelector('.menu-sections');
    nav.querySelectorAll('[data-dynamic-category]').forEach(node=>node.remove());
    sections.querySelectorAll('[data-dynamic-section]').forEach(node=>node.remove());
    catalogCategories.filter(category=>!coreSlugs.has(category.slug)).forEach(category=>{
      const target=`category-${category.slug}`;
      const products=byCategory.get(category.slug)||[];
      nav.insertAdjacentHTML('beforeend',`<button class="category" data-dynamic-category data-target="${target}"><i data-lucide="utensils"></i>${category.name||category.slug}</button>`);
      sections.insertAdjacentHTML('beforeend',`<section class="section" id="${target}" data-dynamic-section><div class="section-head"><div><span class="eyebrow">Cardápio</span><h2>${category.name||category.slug}</h2></div><p>Escolha seu favorito</p></div><div id="category-list-${category.slug}">${products.map(product=>simpleCard(product,category.slug)).join('')||'<div class="empty">Nenhum produto cadastrado.</div>'}</div></section>`);
    });
    document.querySelectorAll('.category').forEach(button=>button.onclick=()=>{document.querySelectorAll('.category').forEach(item=>item.classList.remove('active'));button.classList.add('active');document.querySelector('#'+button.dataset.target)?.scrollIntoView({behavior:'smooth',block:'start'})});
    lucide.createIcons()
  }
  async function loadCatalog(){'''
text, count = pattern.subn(replacement, text, count=1)
if count != 1:
    raise SystemExit('renderCatalog block not found')

path.write_text(text, encoding='utf-8')
print('dynamic categories applied')
