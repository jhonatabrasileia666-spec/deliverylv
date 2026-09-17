from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise SystemExit(f'anchor not found: {label}')
    s = s.replace(old, new, 1)

promo_css = r'''.promo-showcase{width:100vw;margin-left:calc(50% - 50vw);padding:6px 0 28px;overflow:hidden}.promo-head{max-width:1180px;margin:0 auto 14px;padding:0 20px;display:flex;align-items:end;justify-content:space-between;gap:18px}.promo-head h2{margin:5px 0 0;font-family:"Barlow Condensed";font-size:38px;line-height:.92;text-transform:uppercase}.promo-head p{margin:0;color:var(--muted);font-size:11px}.promo-viewport{width:100%;overflow:hidden;mask-image:linear-gradient(90deg,transparent,#000 4%,#000 96%,transparent);-webkit-mask-image:linear-gradient(90deg,transparent,#000 4%,#000 96%,transparent)}.promo-track{display:flex;gap:12px;width:max-content;padding:2px 0;will-change:transform;animation:promoMarquee 34s linear infinite}.promo-track:hover{animation-play-state:paused}.promo-set{display:flex;gap:12px;flex:none}.promo-card{position:relative;width:282px;height:158px;flex:none;overflow:hidden;border:1px solid #ff5a1660;border-radius:18px;background:#211914;text-align:left;box-shadow:0 12px 30px #0005}.promo-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.55}.promo-card:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,#120d0acc 15%,#120d0a78 62%,#120d0a35)}.promo-card-copy{position:relative;z-index:2;height:100%;display:flex;flex-direction:column;align-items:flex-start;padding:15px}.promo-pill{display:inline-flex;padding:5px 8px;border-radius:99px;background:var(--orange);color:#1b110b;font-size:9px;font-weight:900;letter-spacing:.06em}.promo-card h3{max-width:185px;margin:10px 0 4px;font-size:16px;line-height:1.05}.promo-card small{color:#ddd0c6;font-size:9px}.promo-prices{display:flex;align-items:baseline;gap:8px;margin-top:auto}.promo-prices del{color:#b5aaa1;font-size:11px}.promo-prices strong{color:#fff;font-family:"Barlow Condensed";font-size:25px;line-height:1}.promo-card:hover{border-color:var(--orange);transform:translateY(-2px)}.promo-price-old{margin-right:7px;color:#887f78;font-size:11px;font-weight:600}.product-copy .product-badge.promo-badge{background:#d9f15c18;border-color:#d9f15c88;color:var(--lime)}@keyframes promoMarquee{from{transform:translateX(0)}to{transform:translateX(calc(-50% - 6px))}}@media(max-width:600px){.promo-showcase{padding-bottom:22px}.promo-head h2{font-size:33px}.promo-head p{display:none}.promo-card{width:245px;height:145px}.promo-card h3{max-width:160px}.promo-track{animation-duration:28s}}@media(prefers-reduced-motion:reduce){.promo-track{animation:none;transform:none;overflow-x:auto}}'''
replace_once('    .menu-layout{display:block}', '    '+promo_css+'\n    .menu-layout{display:block}', 'promo css')

promo_html = '''      <section class="promo-showcase" id="promo-showcase" hidden><div class="promo-head"><div><span class="eyebrow">Ofertas da casa</span><h2>Promoções</h2></div><p>Toque em uma oferta para pedir</p></div><div class="promo-viewport"><div class="promo-track" id="promo-track"></div></div></section>\n'''
replace_once('      <div class="menu-layout">', promo_html+'      <div class="menu-layout">', 'promo html')

old_flavor = "  const flavorProduct=id=>catalogProducts.find(product=>String(product.id)===String(id));\n  const flavorInfo=product=>({id:product.id,name:product.name,priceAddition:Number(product.price_addition||0)});\n  const pizzaFlavorProducts=()=>catalogProducts.filter(product=>categorySlugFor(product)==='pizzas');\n  const flavorSizePrice=(flavorId,sizeName)=>{const row=catalogProductSizes.find(size=>String(size.product_id)===String(flavorId)&&normalizeSizeName(size.name)===normalizeSizeName(sizeName)&&size.active!==false);const product=flavorProduct(flavorId);return Number(row?.price||0)+Number(product?.price_addition||0)};"
new_flavor = "  const flavorProduct=id=>catalogProducts.find(product=>String(product.id)===String(id));\n  const promotionDiscount=product=>Math.max(0,Math.min(99.99,Number(product?.promotion_discount||0)));\n  const productOnPromotion=product=>Boolean(product?.promotion_active)&&promotionDiscount(product)>0;\n  const applyProductPromotion=(product,value)=>productOnPromotion(product)?Math.round((Number(value||0)*(1-promotionDiscount(product)/100))*100)/100:Number(value||0);\n  const flavorInfo=product=>({id:product.id,name:product.name,priceAddition:Number(product.price_addition||0)});\n  const pizzaFlavorProducts=()=>catalogProducts.filter(product=>categorySlugFor(product)==='pizzas');\n  const flavorSizePrice=(flavorId,sizeName)=>{const row=catalogProductSizes.find(size=>String(size.product_id)===String(flavorId)&&normalizeSizeName(size.name)===normalizeSizeName(sizeName)&&size.active!==false);const product=flavorProduct(flavorId);const regular=Number(row?.price||0)+Number(product?.price_addition||0);return applyProductPromotion(product,regular)};"
replace_once(old_flavor,new_flavor,'promotion price helpers')

old_start = "  function productStartingPrice(product){const sizeRows=productSizesFor(product);const base=(product.pricing_mode==='sizes'||sizeRows.length)&&sizeRows.length?Math.min(...sizeRows.map(size=>Number(size.price||0))):Number(product.base_price||0);return base+Number(product.price_addition||0)}"
new_start = "  function productRegularStartingPrice(product){const sizeRows=productSizesFor(product);const base=(product.pricing_mode==='sizes'||sizeRows.length)&&sizeRows.length?Math.min(...sizeRows.map(size=>Number(size.price||0))):Number(product.base_price||0);return base+Number(product.price_addition||0)}\n  function productStartingPrice(product){return applyProductPromotion(product,productRegularStartingPrice(product))}"
replace_once(old_start,new_start,'starting price')

pattern = re.compile(r"  function catalogCard\(product\)\{.*?\n  \}\n  function simpleCard", re.S)
new_card = r'''  function catalogCard(product){
    const acrescimo=Number(product.price_addition||0);
    const promo=productOnPromotion(product),discount=promotionDiscount(product);
    const badges=(promo?`<span class="product-badge promo-badge">PROMO -${Number(discount.toFixed(2))}%</span>`:'')+(acrescimo>0?`<span class="product-badge">ACRÉSCIMO: ${money(acrescimo)}</span>`:'');
    const sizeRows=productSizesFor(product);
    const usesSizes=product.pricing_mode==='sizes'||sizeRows.length>0;
    const selectedPizzaRow=categorySlugFor(product)==='pizzas'?pizzaCatalogSizeRow(product):null;
    const regularPrice=selectedPizzaRow?Number(selectedPizzaRow.price||0)+acrescimo:productRegularStartingPrice(product);
    const precoInicial=applyProductPromotion(product,regularPrice);
    const prefix=!selectedPizzaRow&&usesSizes&&sizeRows.length?'a partir de ':'';
    const priceLabel=promo?`${prefix}<span class="promo-price-old"><del>${money(regularPrice)}</del></span>${money(precoInicial)}`:`${prefix}${money(precoInicial)}`;
    const name=escapeCatalogText(product.name||'Produto');
    const description=escapeCatalogText(product.description||'Produto preparado na hora.');
    const image=product.image_url||pizzaImage;
    return `<article class="product" data-configure-product="${product.id}"><div class="product-copy">${badges}<h3>${name}</h3><p>${description}</p><strong class="price">${priceLabel}</strong></div><img class="product-image" src="${image}" alt="${name}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"></article>`
  }
  function simpleCard'''
s, count = pattern.subn(new_card, s, count=1)
if count != 1:
    raise SystemExit('anchor not found: catalogCard')

promo_functions = r'''  function promotionCard(product){
    const category=categorySlugFor(product);
    const sizeRows=productSizesFor(product);
    const chosenRow=category==='pizzas'?(pizzaCatalogSizeRow(product)||sizeRows[0]):null;
    const regular=chosenRow?Number(chosenRow.price||0)+Number(product.price_addition||0):productRegularStartingPrice(product);
    const promotional=applyProductPromotion(product,regular);
    const sizeLabel=chosenRow?`Tamanho ${escapeCatalogText(chosenRow.name)}`:(sizeRows.length?'A partir de':'Preço promocional');
    const image=product.image_url||pizzaImage;
    return `<button type="button" class="promo-card" data-configure-product="${product.id}" aria-label="Ver promoção de ${escapeCatalogText(product.name)}"><img src="${image}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"><span class="promo-card-copy"><span class="promo-pill">-${Number(promotionDiscount(product).toFixed(2))}%</span><h3>${escapeCatalogText(product.name)}</h3><small>${sizeLabel}</small><span class="promo-prices"><del>${money(regular)}</del><strong>${money(promotional)}</strong></span></span></button>`;
  }
  function renderPromotions(){
    const host=document.querySelector('#promo-showcase'),track=document.querySelector('#promo-track');
    if(!host||!track)return;
    const promos=catalogProducts.filter(productOnPromotion).sort((a,b)=>Number(a.promotion_sort_order||0)-Number(b.promotion_sort_order||0)||Number(a.sort_order||0)-Number(b.sort_order||0)||String(a.name||'').localeCompare(String(b.name||''),'pt-BR'));
    if(!promos.length){host.hidden=true;track.innerHTML='';return}
    const base=promos.map(promotionCard).join('');
    const repeats=Math.max(1,Math.ceil(8/promos.length));
    const filled=Array.from({length:repeats},()=>base).join('');
    track.innerHTML=`<div class="promo-set">${filled}</div><div class="promo-set" aria-hidden="true">${filled}</div>`;
    host.hidden=false;
  }
'''
replace_once('  function renderCatalog(){', promo_functions+'  function renderCatalog(){', 'render promotions functions')

replace_once('    lucide.createIcons();\n  }\n  async function loadCatalog(){', '    renderPromotions();\n    lucide.createIcons();\n  }\n  async function loadCatalog(){', 'render promotions call')

replace_once("db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges').eq('active',true).order('sort_order')", "db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges,promotion_active,promotion_discount,promotion_sort_order').eq('active',true).order('sort_order')", 'load promo columns')

old_selected = "    selected={id:product.id,name:product.name,ingredients:product.description||'',category,pricingMode,sizes:configuredSizes,size:initialSizeIndex>=0?initialSizeIndex:0,basePrice:Number(product.base_price||0),edge:null,qty:1,note:'',priceAddition:Number(product.price_addition||0),allowEdges:Boolean(product.allow_edges),image:product.image_url||pizzaImage,flavors:category==='pizzas'?[flavorInfo(product)]:[]};"
new_selected = "    selected={id:product.id,name:product.name,ingredients:product.description||'',category,pricingMode,sizes:configuredSizes,size:initialSizeIndex>=0?initialSizeIndex:0,basePrice:Number(product.base_price||0),edge:null,qty:1,note:'',priceAddition:Number(product.price_addition||0),allowEdges:Boolean(product.allow_edges),promotion_active:Boolean(product.promotion_active),promotion_discount:Number(product.promotion_discount||0),image:product.image_url||pizzaImage,flavors:category==='pizzas'?[flavorInfo(product)]:[]};"
replace_once(old_selected,new_selected,'selected promo state')

pattern = re.compile(r"  function currentPrice\(\)\{.*?\n  \}\n  function renderProduct", re.S)
new_current = r'''  function currentPrice(){
    const sizeName=selected.sizes?.[selected.size]?.name;
    const base=selected.pricingMode==='sizes'?Number(selected.sizes[selected.size]?.price||0):Number(selected.basePrice||0);
    const discountable=selected.category==='pizzas'&&selected.flavors?.length?Math.max(...selected.flavors.map(flavor=>flavorSizePrice(flavor.id,sizeName))):applyProductPromotion(selected,base+Number(selected.priceAddition||0));
    return discountable+(selected.edge?Number(selected.edge[1]||0):0)
  }
  function renderProduct'''
s, count = pattern.subn(new_current, s, count=1)
if count != 1:
    raise SystemExit('anchor not found: currentPrice')

path.write_text(s, encoding='utf-8')
print('storefront promotion patch applied')
