from pathlib import Path
import re

path=Path('index.html')
s=path.read_text(encoding='utf-8')

def rep(old,new,label):
    global s
    if old not in s:
        raise SystemExit(f'anchor not found: {label}')
    s=s.replace(old,new,1)

rep("  const productOnPromotion=product=>Boolean(product?.promotion_active)&&promotionDiscount(product)>0;\n  const applyProductPromotion=(product,value)=>productOnPromotion(product)?Math.round((Number(value||0)*(1-promotionDiscount(product)/100))*100)/100:Number(value||0);",
"  const productOnPromotion=product=>Boolean(product?.promotion_active)&&promotionDiscount(product)>0;\n  const promotionApplies=(product,sizeName='')=>{if(!productOnPromotion(product))return false;const target=String(product?.promotion_size||'').trim();if(!target)return true;return normalizeSizeName(target)===normalizeSizeName(sizeName)};\n  const applyProductPromotion=(product,value,sizeName='')=>promotionApplies(product,sizeName)?Math.round((Number(value||0)*(1-promotionDiscount(product)/100))*100)/100:Number(value||0);",
'promo helpers')

rep("  const flavorSizePrice=(flavorId,sizeName)=>{const row=catalogProductSizes.find(size=>String(size.product_id)===String(flavorId)&&normalizeSizeName(size.name)===normalizeSizeName(sizeName)&&size.active!==false);const product=flavorProduct(flavorId);const regular=Number(row?.price||0)+Number(product?.price_addition||0);return applyProductPromotion(product,regular)};",
"  const flavorSizePrice=(flavorId,sizeName)=>{const row=catalogProductSizes.find(size=>String(size.product_id)===String(flavorId)&&normalizeSizeName(size.name)===normalizeSizeName(sizeName)&&size.active!==false);const product=flavorProduct(flavorId);const regular=Number(row?.price||0)+Number(product?.price_addition||0);return applyProductPromotion(product,regular,sizeName)};",
'flavor promo size')

rep("  function productStartingPrice(product){return applyProductPromotion(product,productRegularStartingPrice(product))}",
"  function productStartingPrice(product){const sizeRows=productSizesFor(product),addition=Number(product.price_addition||0);if((product.pricing_mode==='sizes'||sizeRows.length)&&sizeRows.length)return Math.min(...sizeRows.map(size=>applyProductPromotion(product,Number(size.price||0)+addition,size.name)));return applyProductPromotion(product,Number(product.base_price||0)+addition,'')}",
'starting price')

pattern=re.compile(r"  function catalogCard\(product\)\{.*?\n  \}\n  function simpleCard",re.S)
new=r'''  function catalogCard(product){
    const acrescimo=Number(product.price_addition||0);
    const sizeRows=productSizesFor(product);
    const usesSizes=product.pricing_mode==='sizes'||sizeRows.length>0;
    const selectedPizzaRow=categorySlugFor(product)==='pizzas'?pizzaCatalogSizeRow(product):null;
    const activePromo=selectedPizzaRow?promotionApplies(product,selectedPizzaRow.name):(!usesSizes&&promotionApplies(product,''));
    const discount=promotionDiscount(product);
    const badges=(activePromo?`<span class="product-badge promo-badge">PROMO -${Number(discount.toFixed(2))}%${selectedPizzaRow?` · ${escapeCatalogText(selectedPizzaRow.name)}`:''}</span>`:'')+(acrescimo>0?`<span class="product-badge">ACRÉSCIMO: ${money(acrescimo)}</span>`:'');
    const regularPrice=selectedPizzaRow?Number(selectedPizzaRow.price||0)+acrescimo:productRegularStartingPrice(product);
    const precoInicial=selectedPizzaRow?applyProductPromotion(product,regularPrice,selectedPizzaRow.name):productStartingPrice(product);
    const prefix=!selectedPizzaRow&&usesSizes&&sizeRows.length?'a partir de ':'';
    const priceLabel=activePromo?`${prefix}<span class="promo-price-old"><del>${money(regularPrice)}</del></span>${money(precoInicial)}`:`${prefix}${money(precoInicial)}`;
    const name=escapeCatalogText(product.name||'Produto');
    const description=escapeCatalogText(product.description||'Produto preparado na hora.');
    const image=product.image_url||pizzaImage;
    return `<article class="product" data-configure-product="${product.id}"><div class="product-copy">${badges}<h3>${name}</h3><p>${description}</p><strong class="price">${priceLabel}</strong></div><img class="product-image" src="${image}" alt="${name}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"></article>`
  }
  function simpleCard'''
s,count=pattern.subn(new,s,count=1)
if count!=1: raise SystemExit('catalogCard not found')

pattern=re.compile(r"  function promotionCard\(product\)\{.*?\n  \}\n  function renderPromotions",re.S)
new=r'''  function promotionCard(product){
    const sizeRows=productSizesFor(product);
    const promoSize=String(product.promotion_size||'').trim();
    const chosenRow=sizeRows.find(size=>normalizeSizeName(size.name)===normalizeSizeName(promoSize))||null;
    const regular=chosenRow?Number(chosenRow.price||0)+Number(product.price_addition||0):productRegularStartingPrice(product);
    const promotional=applyProductPromotion(product,regular,chosenRow?.name||'');
    const sizeLabel=chosenRow?`Tamanho ${escapeCatalogText(chosenRow.name)}`:'Preço promocional';
    const image=product.image_url||pizzaImage;
    return `<button type="button" class="promo-card" data-configure-product="${product.id}" ${chosenRow?`data-promotion-size="${escapeCatalogText(chosenRow.name)}"`:''} aria-label="Ver promoção de ${escapeCatalogText(product.name)}"><img src="${image}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"><span class="promo-card-copy"><span class="promo-pill">-${Number(promotionDiscount(product).toFixed(2))}%</span><h3>${escapeCatalogText(product.name)}</h3><small>${sizeLabel}</small><span class="promo-prices"><del>${money(regular)}</del><strong>${money(promotional)}</strong></span></span></button>`;
  }
  function renderPromotions'''
s,count=pattern.subn(new,s,count=1)
if count!=1: raise SystemExit('promotionCard not found')

rep("db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges,promotion_active,promotion_discount,promotion_sort_order').eq('active',true).order('sort_order')",
"db.from('products').select('id,category_id,name,description,base_price,price_addition,image_url,active,sort_order,pricing_mode,allow_edges,promotion_active,promotion_discount,promotion_sort_order,promotion_size').eq('active',true).order('sort_order')",
'load promotion_size')

rep("  function openProduct(productId){","  function openProduct(productId,preferredSize=''){",'openProduct signature')
rep("    const initialSizeIndex=category==='pizzas'?configuredSizes.findIndex(size=>normalizeSizeName(size.name)===normalizeSizeName(selectedPizzaCatalogSize)):0;",
"    const requestedSize=preferredSize||(category==='pizzas'?selectedPizzaCatalogSize:'');\n    const initialSizeIndex=requestedSize?configuredSizes.findIndex(size=>normalizeSizeName(size.name)===normalizeSizeName(requestedSize)):0;",
'preferred promo size')
rep("promotion_active:Boolean(product.promotion_active),promotion_discount:Number(product.promotion_discount||0),image:product.image_url||pizzaImage",
"promotion_active:Boolean(product.promotion_active),promotion_discount:Number(product.promotion_discount||0),promotion_size:product.promotion_size||'',image:product.image_url||pizzaImage",
'selected promo size')

pattern=re.compile(r"  function currentPrice\(\)\{.*?\n  \}\n  function renderProduct",re.S)
new=r'''  function currentPrice(){
    const sizeName=selected.sizes?.[selected.size]?.name;
    const base=selected.pricingMode==='sizes'?Number(selected.sizes[selected.size]?.price||0):Number(selected.basePrice||0);
    const discountable=selected.category==='pizzas'&&selected.flavors?.length?Math.max(...selected.flavors.map(flavor=>flavorSizePrice(flavor.id,sizeName))):applyProductPromotion(selected,base+Number(selected.priceAddition||0),sizeName||'');
    return discountable+(selected.edge?Number(selected.edge[1]||0):0)
  }
  function renderProduct'''
s,count=pattern.subn(new,s,count=1)
if count!=1: raise SystemExit('currentPrice not found')

rep("const configurable=event.target.closest('[data-configure-product]');if(configurable)openProduct(configurable.dataset.configureProduct);",
"const configurable=event.target.closest('[data-configure-product]');if(configurable)openProduct(configurable.dataset.configureProduct,configurable.dataset.promotionSize||'');",
'promo click size')

path.write_text(s,encoding='utf-8')
print('promotion size storefront patch applied')
