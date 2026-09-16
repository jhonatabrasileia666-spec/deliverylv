from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')

start = text.find('  let productLookup=null;')
end = text.find('  function updateCart(){', start)
if start < 0 or end < 0:
    raise SystemExit('catalog javascript block not found')

new_block = r'''  let productLookup=null;
  async function loadProductLookup(){
    if(productLookup)return productLookup;
    const [categoryResult,productResult]=await Promise.all([
      db.from('categories').select('id,slug').eq('active',true),
      db.from('products').select('id,name,category_id').eq('active',true)
    ]);
    if(categoryResult.error)throw categoryResult.error;
    if(productResult.error)throw productResult.error;
    const slugByCategoryId=new Map(categoryResult.data.map(category=>[category.id,category.slug]));
    productLookup=new Map();
    productResult.data.forEach(product=>{const slug=slugByCategoryId.get(product.category_id);if(slug)productLookup.set(`${slug}|${product.name}`,product.id)});
    return productLookup;
  }
  let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerAddress='';
  const money=value=>Number(value||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
  const pizzaImage="https://images.unsplash.com/photo-1594007654729-407eedc4be65?auto=format&fit=crop&w=360&q=80";
  const categoryForProduct=product=>catalogCategories.find(category=>category.id===product?.category_id);
  const categorySlugFor=product=>categoryForProduct(product)?.slug||'';
  function productSizesFor(product){
    const own=catalogProductSizes.filter(size=>String(size.product_id)===String(product?.id)&&size.active!==false).sort((a,b)=>Number(a.sort_order||0)-Number(b.sort_order||0));
    if(own.length)return own.map(size=>({name:size.name,price:Number(size.price||0)}));
    if(categorySlugFor(product)==='pizzas')return sizes.map(size=>({name:size[0],price:Number(size[1])}));
    return [];
  }
  function productEdges(){const rows=catalogEdges.length?catalogEdges.map(edge=>[edge.name,Number(edge.price||0)]):edges;return rows.filter(edge=>edge[0])}
  function productStartingPrice(product){const sizeRows=productSizesFor(product);const base=(product.pricing_mode==='sizes'||sizeRows.length)&&sizeRows.length?Math.min(...sizeRows.map(size=>Number(size.price||0))):Number(product.base_price||0);return base+Number(product.price_addition||0)}
  function pizzaCard(product){
    const acrescimo=Number(product.price_addition||0);
    const badge=acrescimo>0?`<span class="product-badge">ACRÉSCIMO: ${money(acrescimo)}</span>`:'';
    const precoInicial=productStartingPrice(product);
    return `<article class="product" data-configure-product="${product.id}"><div class="product-copy">${badge}<h3>${product.name}</h3><p>${product.description||'Produto preparado na hora.'}</p><strong class="price">a partir de ${money(precoInicial)}</strong></div><img class="product-image" src="${product.image_url||pizzaImage}" alt="${product.name}" loading="lazy"></article>`
  }
  function simpleCard(product,category){
    const sizeRows=productSizesFor(product), configurable=product.pricing_mode==='sizes'||sizeRows.length>0||product.allow_edges;
    const price=productStartingPrice(product);
    const priceLabel=configurable&&sizeRows.length?`a partir de ${money(price)}`:money(price);
    const button=configurable?`<button class="quick-add" data-configure-product="${product.id}" aria-label="Escolher opções de ${product.name}"><i data-lucide="sliders-horizontal"></i></button>`:`<button class="quick-add" data-quick="${product.name}" data-product-id="${product.id}" data-category="${category}" data-price="${price}" aria-label="Adicionar ${product.name}"><i data-lucide="plus"></i></button>`;
    return `<div class="simple-card"><div><h3>${product.name}</h3><p>${product.description||'Escolha sua quantidade no pedido'}</p></div><strong class="simple-price">${priceLabel}</strong>${button}</div>`
  }
  function renderCatalog(){
    const byCategory=new Map(catalogCategories.map(category=>[category.slug,[]]));
    catalogProducts.forEach(product=>{const category=categoryForProduct(product);if(category){if(!byCategory.has(category.slug))byCategory.set(category.slug,[]);byCategory.get(category.slug).push(product)}});
    const pizzasFromDb=byCategory.get('pizzas')||[];
    document.querySelector('#pizza-grid').innerHTML=pizzasFromDb.map(pizzaCard).join('')||'<div class="empty">Nenhuma pizza cadastrada.</div>';
    const foodCategories=['esfirras','lanches','caldos','porcoes'];
    const foods=foodCategories.flatMap(slug=>(byCategory.get(slug)||[]).map(product=>({product,category:slug})));
    document.querySelector('#savory-list').innerHTML=foods.map(({product,category})=>simpleCard(product,category)).join('')||'<div class="empty">Nenhum produto cadastrado.</div>';
    document.querySelector('#sweet-list').innerHTML='';
    document.querySelector('#drink-list').innerHTML=(byCategory.get('bebidas')||[]).map(product=>simpleCard(product,'bebidas')).join('')||'<div class="empty">Nenhuma bebida cadastrada.</div>';
    lucide.createIcons()
  }
  async function loadCatalog(){
    const[{data:categories,error:categoryError},{data:products,error:productError},{data:sizeRows,error:sizeError},{data:edgeRows,error:edgeError}]=await Promise.all([
      db.from('categories').select('id,slug,name').eq('active',true).order('sort_order'),
      db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges').eq('active',true).order('sort_order'),
      db.from('product_sizes').select('product_id,name,price,active,sort_order').eq('active',true).order('sort_order'),
      db.from('pizza_edges').select('name,price,active,sort_order').eq('active',true).order('sort_order')
    ]);
    if(categoryError||productError||sizeError||edgeError)throw categoryError||productError||sizeError||edgeError;
    catalogCategories=categories||[];catalogProducts=products||[];catalogProductSizes=sizeRows||[];catalogEdges=edgeRows||[];productLookup=null;await loadProductLookup();renderCatalog()
  }
  function openProduct(productId){
    const product=catalogProducts.find(item=>String(item.id)===String(productId));if(!product)return;
    const category=categorySlugFor(product);
    const configuredSizes=productSizesFor(product);
    const pricingMode=(product.pricing_mode==='sizes'||configuredSizes.length)?'sizes':'fixed';
    if(pricingMode==='sizes'&&!configuredSizes.length){showToast('Este produto ainda não tem tamanhos disponíveis');return}
    selected={id:product.id,name:product.name,ingredients:product.description||'',category,pricingMode,sizes:configuredSizes,size:0,basePrice:Number(product.base_price||0),edge:null,qty:1,note:'',priceAddition:Number(product.price_addition||0),allowEdges:Boolean(product.allow_edges),image:product.image_url||pizzaImage};
    renderProduct();document.querySelector('#product-overlay').classList.add('show')
  }
  function currentPrice(){
    const base=selected.pricingMode==='sizes'?Number(selected.sizes[selected.size]?.price||0):Number(selected.basePrice||0);
    return base+(selected.edge?Number(selected.edge[1]||0):0)+Number(selected.priceAddition||0)
  }
  function renderProduct(){
    const sizeField=selected.pricingMode==='sizes'?`<div class="field"><span class="field-label">Tamanho</span><div class="option-grid">${selected.sizes.map((size,i)=>`<button class="option ${i===selected.size?'selected':''}" data-size="${i}"><strong>${size.name}</strong><span>${money(size.price)}</span></button>`).join('')}</div></div>`:'';
    const edgeOptions=productEdges();
    const edgeField=selected.allowEdges?`<div class="field"><span class="field-label">Borda opcional</span><div class="option-grid"><button class="option ${!selected.edge?'selected':''}" data-edge="none"><strong>Sem borda</strong><span>Sem acréscimo</span></button>${edgeOptions.map((edge,i)=>`<button class="option ${selected.edge&&selected.edge[0]===edge[0]?'selected':''}" data-edge="${i}"><strong>${edge[0]}</strong><span>+ ${money(edge[1])}</span></button>`).join('')}</div></div>`:'';
    document.querySelector('#product-detail').innerHTML=`<div class="detail-hero"><img class="detail-image" src="${selected.image}" alt="${selected.name}"><div><h3>${selected.name}</h3><p>${selected.ingredients}</p></div></div>${sizeField}${edgeField}<div class="field"><span class="field-label">Quantidade</span><div class="quantity"><button class="step" data-product-qty="-1"><i data-lucide="minus"></i></button><b>${selected.qty}</b><button class="step" data-product-qty="1"><i data-lucide="plus"></i></button></div></div><div class="field"><label class="field-label" for="note">Alguma observação?</label><textarea class="textarea" id="note" placeholder="Ex.: sem cebola">${selected.note}</textarea></div><div class="total-line"><span>Total</span><strong>${money(currentPrice()*selected.qty)}</strong></div><button class="primary" id="add-product">Adicionar ao pedido <i data-lucide="shopping-bag"></i></button>`;
    lucide.createIcons();
    document.querySelectorAll('[data-size]').forEach(button=>button.onclick=()=>{selected.size=Number(button.dataset.size);renderProduct()});
    document.querySelectorAll('[data-edge]').forEach(button=>button.onclick=()=>{selected.edge=button.dataset.edge==='none'?null:edgeOptions[Number(button.dataset.edge)];renderProduct()});
    document.querySelectorAll('[data-product-qty]').forEach(button=>button.onclick=()=>{selected.qty=Math.max(1,selected.qty+Number(button.dataset.productQty));renderProduct()});
    document.querySelector('#add-product').onclick=()=>{selected.note=document.querySelector('#note').value;const sizeName=selected.pricingMode==='sizes'?selected.sizes[selected.size]?.name:null;cart.push({...selected,sizeName,price:currentPrice()});closeOverlay('product-overlay');updateCart();showToast('Adicionado ao pedido')}
  }
  function addQuick(name,price,category,productId){if(!productId){showToast('Produto ainda não está disponível');return}const existing=cart.find(item=>String(item.id)===String(productId)&&!item.sizeName&&!item.edge);if(existing)existing.qty++;else cart.push({id:Number(productId),name,ingredients:'Item escolhido no cardápio',category,qty:1,price,basePrice:price,pricingMode:'fixed',sizeName:null,edge:null,note:''});updateCart();showToast('Adicionado ao pedido')}
'''
text = text[:start] + new_block + text[end:]

# Pedido: usa o ID real e aceita tamanho em qualquer categoria.
old_product_id = "        const productId=lookup.get(`${category}|${item.name}`);"
new_product_id = "        const productId=item.id||lookup.get(`${category}|${item.name}`);"
if old_product_id not in text:
    raise SystemExit('product id lookup marker not found')
text = text.replace(old_product_id, new_product_id, 1)

old_payload = """        const payload={
          product_id:productId,
          qty:item.qty,
          note:item.note||'',
          detail:category==='pizzas'?'':'Porção escolhida'
        };
        if(category==='pizzas'){
          payload.size=sizes[item.size][0];
          payload.edge=item.edge?item.edge[0]:null;
        }"""
new_payload = """        const payload={
          product_id:productId,
          qty:item.qty,
          note:item.note||'',
          detail:item.sizeName?`Tamanho ${item.sizeName}`:(category==='pizzas'?'':'Porção escolhida')
        };
        if(item.sizeName)payload.size=item.sizeName;
        if(item.edge)payload.edge=item.edge[0];"""
if old_payload not in text:
    raise SystemExit('order payload marker not found')
text = text.replace(old_payload, new_payload, 1)

old_whatsapp = """        if(item.category==='pizzas'){
          if(Number.isInteger(item.size)&&sizes[item.size])detalhes.push(sizes[item.size][0]);
          if(item.edge)detalhes.push(`Borda ${item.edge[0]}`);
          if(item.note)detalhes.push(`Obs: ${item.note}`);
        }else if(item.note){
          detalhes.push(`Obs: ${item.note}`);
        }"""
new_whatsapp = """        if(item.sizeName)detalhes.push(`Tamanho ${item.sizeName}`);
        if(item.edge)detalhes.push(`Borda ${item.edge[0]}`);
        if(item.note)detalhes.push(`Obs: ${item.note}`);"""
if old_whatsapp not in text:
    raise SystemExit('whatsapp detail marker not found')
text = text.replace(old_whatsapp, new_whatsapp, 1)

# Carrinho: mostra tamanho/borda para qualquer produto configurável.
render_marker = '  function renderCart(){'
if render_marker not in text:
    raise SystemExit('renderCart marker not found')
helper = "  function cartItemDetail(item){const details=[];if(item.sizeName)details.push('Tamanho '+item.sizeName);if(item.edge)details.push('Borda '+item.edge[0]);if(item.note)details.push(item.note);return details.length?details.join(' · '):'Porção escolhida'}\n"
text = text.replace(render_marker, helper + render_marker, 1)
old_cart_detail = "${item.category==='pizzas'?`${sizes[item.size][0]}${item.edge?' · Borda '+item.edge[0]:''}${item.note?' · '+item.note:''}`:'Porção escolhida'}"
new_cart_detail = "${cartItemDetail(item)}"
if old_cart_detail not in text:
    raise SystemExit('cart item detail marker not found')
text = text.replace(old_cart_detail, new_cart_detail, 1)

# Clique: qualquer produto configurável abre o mesmo modal.
old_listener = "document.addEventListener('click',event=>{const pizza=event.target.closest('[data-pizza]');if(pizza)openProduct(Number(pizza.dataset.pizza));const quick=event.target.closest('[data-quick]');if(quick)addQuick(quick.dataset.quick,Number(quick.dataset.price),quick.dataset.category,quick.dataset.productId);"
new_listener = "document.addEventListener('click',event=>{const configurable=event.target.closest('[data-configure-product]');if(configurable)openProduct(configurable.dataset.configureProduct);const quick=event.target.closest('[data-quick]');if(quick)addQuick(quick.dataset.quick,Number(quick.dataset.price),quick.dataset.category,quick.dataset.productId);"
if old_listener not in text:
    raise SystemExit('catalog click listener marker not found')
text = text.replace(old_listener, new_listener, 1)

for marker in ['catalogProductSizes','data-configure-product','item.sizeName','product_sizes','pricing_mode','allow_edges']:
    if marker not in text:
        raise SystemExit(f'missing expected marker: {marker}')

path.write_text(text, encoding='utf-8')
