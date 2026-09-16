from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'data-flavor-id' in s and 'catalogPizzaSizes' in s:
    raise SystemExit('multi flavor UI already present')

# variables
old="let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerPhone='', customerAddress='';"
new="let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogPizzaSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerPhone='', customerAddress='';"
if old not in s: raise SystemExit('vars marker not found')
s=s.replace(old,new,1)

# helpers after categoryForProduct
old="const categoryForProduct=product=>catalogCategories.find(category=>category.id===product?.category_id);"
new="""const categoryForProduct=product=>catalogCategories.find(category=>category.id===product?.category_id);
  const normalizeSizeName=value=>String(value||'').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase().trim();
  const pizzaSizeRule=name=>catalogPizzaSizes.find(row=>normalizeSizeName(row.name)===normalizeSizeName(name));
  const selectedMaxFlavors=()=>selected?.category==='pizzas'?Math.max(1,Number(pizzaSizeRule(selected.sizes?.[selected.size]?.name)?.max_flavors||1)):1;
  const flavorProduct=id=>catalogProducts.find(product=>String(product.id)===String(id));
  const flavorInfo=product=>({id:product.id,name:product.name,priceAddition:Number(product.price_addition||0)});
  const pizzaFlavorProducts=()=>catalogProducts.filter(product=>categorySlugFor(product)==='pizzas');
  const flavorSizePrice=(flavorId,sizeName)=>{const row=catalogProductSizes.find(size=>String(size.product_id)===String(flavorId)&&normalizeSizeName(size.name)===normalizeSizeName(sizeName)&&size.active!==false);const product=flavorProduct(flavorId);return Number(row?.price||0)+Number(product?.price_addition||0)};"""
if old not in s: raise SystemExit('helper marker not found')
s=s.replace(old,new,1)

# loadCatalog promise
old="""const[{data:categories,error:categoryError},{data:products,error:productError},{data:sizeRows,error:sizeError},{data:edgeRows,error:edgeError}]=await Promise.all([
      db.from('categories').select('id,slug,name').eq('active',true).order('sort_order'),
      db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges').eq('active',true).order('sort_order'),
      db.from('product_sizes').select('product_id,name,price,active,sort_order').eq('active',true).order('sort_order'),
      db.from('pizza_edges').select('name,price,active,sort_order').eq('active',true).order('sort_order')
    ]);
    if(categoryError||productError||sizeError||edgeError)throw categoryError||productError||sizeError||edgeError;
    catalogCategories=categories||[];catalogProducts=products||[];catalogProductSizes=sizeRows||[];catalogEdges=edgeRows||[];productLookup=null;await loadProductLookup();renderCatalog()"""
new="""const[{data:categories,error:categoryError},{data:products,error:productError},{data:sizeRows,error:sizeError},{data:pizzaSizeRows,error:pizzaSizeError},{data:edgeRows,error:edgeError}]=await Promise.all([
      db.from('categories').select('id,slug,name').eq('active',true).order('sort_order'),
      db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges').eq('active',true).order('sort_order'),
      db.from('product_sizes').select('product_id,name,price,active,sort_order').eq('active',true).order('sort_order'),
      db.from('pizza_sizes').select('name,max_flavors,active,sort_order').eq('active',true).order('sort_order'),
      db.from('pizza_edges').select('name,price,active,sort_order').eq('active',true).order('sort_order')
    ]);
    if(categoryError||productError||sizeError||pizzaSizeError||edgeError)throw categoryError||productError||sizeError||pizzaSizeError||edgeError;
    catalogCategories=categories||[];catalogProducts=products||[];catalogProductSizes=sizeRows||[];catalogPizzaSizes=pizzaSizeRows||[];catalogEdges=edgeRows||[];productLookup=null;await loadProductLookup();renderCatalog()"""
if old not in s: raise SystemExit('loadCatalog marker not found')
s=s.replace(old,new,1)

# selected init
old="selected={id:product.id,name:product.name,ingredients:product.description||'',category,pricingMode,sizes:configuredSizes,size:0,basePrice:Number(product.base_price||0),edge:null,qty:1,note:'',priceAddition:Number(product.price_addition||0),allowEdges:Boolean(product.allow_edges),image:product.image_url||pizzaImage};"
new="selected={id:product.id,name:product.name,ingredients:product.description||'',category,pricingMode,sizes:configuredSizes,size:0,basePrice:Number(product.base_price||0),edge:null,qty:1,note:'',priceAddition:Number(product.price_addition||0),allowEdges:Boolean(product.allow_edges),image:product.image_url||pizzaImage,flavors:category==='pizzas'?[flavorInfo(product)]:[]};"
if old not in s: raise SystemExit('selected marker not found')
s=s.replace(old,new,1)

# currentPrice
old="""function currentPrice(){
    const base=selected.pricingMode==='sizes'?Number(selected.sizes[selected.size]?.price||0):Number(selected.basePrice||0);
    return base+(selected.edge?Number(selected.edge[1]||0):0)+Number(selected.priceAddition||0)
  }"""
new="""function currentPrice(){
    const sizeName=selected.sizes?.[selected.size]?.name;
    const base=selected.pricingMode==='sizes'?Number(selected.sizes[selected.size]?.price||0):Number(selected.basePrice||0);
    const flavorBase=selected.category==='pizzas'&&selected.flavors?.length?Math.max(...selected.flavors.map(flavor=>flavorSizePrice(flavor.id,sizeName))):base+Number(selected.priceAddition||0);
    return (selected.category==='pizzas'?flavorBase:base+Number(selected.priceAddition||0))+(selected.edge?Number(selected.edge[1]||0):0)
  }"""
if old not in s: raise SystemExit('price marker not found')
s=s.replace(old,new,1)

# renderProduct flavor field and event handlers
old="""const edgeOptions=productEdges();
    const edgeField=selected.allowEdges?`<div class=\"field\"><span class=\"field-label\">Borda opcional</span><div class=\"option-grid\"><button class=\"option ${!selected.edge?'selected':''}\" data-edge=\"none\"><strong>Sem borda</strong><span>Sem acréscimo</span></button>${edgeOptions.map((edge,i)=>`<button class=\"option ${selected.edge&&selected.edge[0]===edge[0]?'selected':''}\" data-edge=\"${i}\"><strong>${edge[0]}</strong><span>+ ${money(edge[1])}</span></button>`).join('')}</div></div>`:'';
    document.querySelector('#product-detail').innerHTML=`<div class=\"detail-hero\"><img class=\"detail-image\" src=\"${selected.image}\" alt=\"${selected.name}\"><div><h3>${selected.name}</h3><p>${selected.ingredients}</p></div></div>${sizeField}${edgeField}<div class=\"field\"><span class=\"field-label\">Quantidade</span>"""
new="""const edgeOptions=productEdges();
    const edgeField=selected.allowEdges?`<div class=\"field\"><span class=\"field-label\">Borda opcional</span><div class=\"option-grid\"><button class=\"option ${!selected.edge?'selected':''}\" data-edge=\"none\"><strong>Sem borda</strong><span>Sem acréscimo</span></button>${edgeOptions.map((edge,i)=>`<button class=\"option ${selected.edge&&selected.edge[0]===edge[0]?'selected':''}\" data-edge=\"${i}\"><strong>${edge[0]}</strong><span>+ ${money(edge[1])}</span></button>`).join('')}</div></div>`:'';
    const maxFlavors=selectedMaxFlavors();
    const flavorField=selected.category==='pizzas'&&maxFlavors>1?`<div class=\"field\"><span class=\"field-label\">Sabores · escolha até ${maxFlavors} <small style=\"color:var(--muted);font-weight:600\">(${selected.flavors.length}/${maxFlavors})</small></span><div class=\"option-grid flavor-grid\">${pizzaFlavorProducts().map(product=>{const active=selected.flavors.some(flavor=>String(flavor.id)===String(product.id));const addition=Number(product.price_addition||0);return `<button type=\"button\" class=\"option ${active?'selected':''}\" data-flavor-id=\"${product.id}\"><strong>${escapeCatalogText(product.name)}</strong><span>${addition>0?`+ ${money(addition)}`:'Sem acréscimo'}</span></button>`}).join('')}</div></div>`:'';
    document.querySelector('#product-detail').innerHTML=`<div class=\"detail-hero\"><img class=\"detail-image\" src=\"${selected.image}\" alt=\"${selected.name}\"><div><h3>${selected.name}</h3><p>${selected.ingredients}</p></div></div>${sizeField}${flavorField}${edgeField}<div class=\"field\"><span class=\"field-label\">Quantidade</span>"""
if old not in s: raise SystemExit('render marker not found')
s=s.replace(old,new,1)

old="document.querySelectorAll('[data-size]').forEach(button=>button.onclick=()=>{selected.size=Number(button.dataset.size);renderProduct()});"
new="document.querySelectorAll('[data-size]').forEach(button=>button.onclick=()=>{selected.note=document.querySelector('#note')?.value||selected.note;selected.size=Number(button.dataset.size);const max=selectedMaxFlavors();if(selected.flavors?.length>max)selected.flavors=selected.flavors.slice(0,max);renderProduct()});"
if old not in s: raise SystemExit('size handler marker not found')
s=s.replace(old,new,1)

old="document.querySelectorAll('[data-edge]').forEach(button=>button.onclick=()=>{selected.edge=button.dataset.edge==='none'?null:edgeOptions[Number(button.dataset.edge)];renderProduct()});"
new="""document.querySelectorAll('[data-flavor-id]').forEach(button=>button.onclick=()=>{selected.note=document.querySelector('#note')?.value||selected.note;const id=button.dataset.flavorId;const index=selected.flavors.findIndex(flavor=>String(flavor.id)===String(id));if(index>=0){if(selected.flavors.length===1){showToast('Escolha pelo menos um sabor');return}selected.flavors.splice(index,1)}else{const max=selectedMaxFlavors();if(selected.flavors.length>=max){showToast(`Este tamanho permite até ${max} sabores`);return}const product=flavorProduct(id);if(product)selected.flavors.push(flavorInfo(product))}renderProduct()});
    document.querySelectorAll('[data-edge]').forEach(button=>button.onclick=()=>{selected.note=document.querySelector('#note')?.value||selected.note;selected.edge=button.dataset.edge==='none'?null:edgeOptions[Number(button.dataset.edge)];renderProduct()});"""
if old not in s: raise SystemExit('edge handler marker not found')
s=s.replace(old,new,1)

# add to cart
old="document.querySelector('#add-product').onclick=()=>{selected.note=document.querySelector('#note').value;const sizeName=selected.pricingMode==='sizes'?selected.sizes[selected.size]?.name:null;cart.push({...selected,sizeName,price:currentPrice()});closeOverlay('product-overlay');updateCart();showToast('Adicionado ao pedido')}"
new="document.querySelector('#add-product').onclick=()=>{selected.note=document.querySelector('#note').value;const sizeName=selected.pricingMode==='sizes'?selected.sizes[selected.size]?.name:null;const cartName=selected.category==='pizzas'&&selected.flavors?.length>1?`Pizza ${selected.flavors.length} sabores`:selected.name;cart.push({...selected,name:cartName,originalName:selected.name,flavors:(selected.flavors||[]).map(flavor=>({...flavor})),sizeName,price:currentPrice()});closeOverlay('product-overlay');updateCart();showToast('Adicionado ao pedido')}"
if old not in s: raise SystemExit('add marker not found')
s=s.replace(old,new,1)

# payload flavors
old="if(item.sizeName)payload.size=item.sizeName;\n        if(item.edge)payload.edge=item.edge[0];"
new="if(item.sizeName)payload.size=item.sizeName;\n        if(category==='pizzas'&&Array.isArray(item.flavors)&&item.flavors.length)payload.flavors=item.flavors.map(flavor=>flavor.id);\n        if(item.edge)payload.edge=item.edge[0];"
if old not in s: raise SystemExit('payload marker not found')
s=s.replace(old,new,1)

# WhatsApp and cart details
old="if(item.sizeName)detalhes.push(`Tamanho ${item.sizeName}`);\n        if(item.edge)detalhes.push(`Borda ${item.edge[0]}`);"
new="if(item.sizeName)detalhes.push(`Tamanho ${item.sizeName}`);\n        if(Array.isArray(item.flavors)&&item.flavors.length>1)detalhes.push(`Sabores: ${item.flavors.map(flavor=>flavor.name).join(' / ')}`);\n        if(item.edge)detalhes.push(`Borda ${item.edge[0]}`);"
if old not in s: raise SystemExit('whatsapp detail marker not found')
s=s.replace(old,new,1)

old="function cartItemDetail(item){const details=[];if(item.sizeName)details.push('Tamanho '+item.sizeName);if(item.edge)details.push('Borda '+item.edge[0]);if(item.note)details.push(item.note);return details.length?details.join(' · '):'Porção escolhida'}"
new="function cartItemDetail(item){const details=[];if(item.sizeName)details.push('Tamanho '+item.sizeName);if(Array.isArray(item.flavors)&&item.flavors.length>1)details.push('Sabores: '+item.flavors.map(flavor=>flavor.name).join(' / '));if(item.edge)details.push('Borda '+item.edge[0]);if(item.note)details.push(item.note);return details.length?details.join(' · '):'Porção escolhida'}"
if old not in s: raise SystemExit('cart detail marker not found')
s=s.replace(old,new,1)

# flavor grid css
style="""
<style id=\"multi-flavor-pizza-styles\">
  .flavor-grid{max-height:280px;overflow:auto;padding:2px;scrollbar-width:thin}.flavor-grid .option{min-height:58px}.flavor-grid .option.selected{box-shadow:inset 3px 0 var(--orange)}
  @media(max-width:520px){.flavor-grid{grid-template-columns:1fr;max-height:300px}}
</style>
"""
if '</head>' not in s: raise SystemExit('head marker missing')
s=s.replace('</head>',style+'</head>',1)

# validation
required=['catalogPizzaSizes','max_flavors','data-flavor-id','payload.flavors','Pizza ${selected.flavors.length} sabores','multi-flavor-pizza-styles']
for marker in required:
    if marker not in s: raise SystemExit('missing '+marker)

p.write_text(s,encoding='utf-8')
print('multi-flavor pizza UI added')
