(function installLvPizzaCombo(){
  const isCombo = product => product && product.combo_kind === 'grande_pequena_choco_morango';
  const isComboItem = item => Boolean(item && item.comboPizza);
  const oldOpenProduct = openProduct;
  const oldRenderProduct = renderProduct;
  const oldCurrentPrice = currentPrice;
  const oldCartPayload = cartPayload;
  const oldCartItemDetail = cartItemDetail;
  const oldPromotionCard = promotionCard;
  openProduct = function(productId,preferredSize=''){
    const product=catalogProducts.find(row=>String(row.id)===String(productId));
    if(!isCombo(product))return oldOpenProduct(productId,preferredSize);
    selected={
      id:product.id,name:product.name,ingredients:product.description||'',
      category:categorySlugFor(product),comboPizza:true,pricingMode:'fixed',
      sizes:[],size:0,basePrice:Number(product.base_price||0),
      priceAddition:0,edge:null,drink:null,allowEdges:Boolean(product.allow_edges),qty:1,note:'',flavors:[],
      image:product.image_url||pizzaImage
    };
    renderProduct();
    document.querySelector('#product-overlay').classList.add('show');
  };
  currentPrice=function(){
    if(!selected?.comboPizza)return oldCurrentPrice();
    const extra=(selected.flavors||[]).reduce((sum,item)=>sum+Number(flavorProduct(item.id)?.price_addition||0),0);
    const edge=selected.edge?Number(selected.edge[1]||0):0;
    const drink=selected.drink?Number(selected.drink.price||0):0;
    return Math.round((Number(selected.basePrice)+extra+edge+drink)*100)/100;
  };
  function renderCombo(){
    const chosen=selected.flavors||[];
    const available=pizzaFlavorProducts().filter(product=>productSizesFor(product).some(size=>normalizeSizeName(size.name)==='grande'));
    const cards=available.map(product=>{
      const active=chosen.some(flavor=>String(flavor.id)===String(product.id));
      const extra=Math.max(0,Number(product.price_addition||0));
      return `<button type="button" class="option ${active?'selected':''}" data-combo-pizza-flavor="${product.id}"><strong>${escapeCatalogText(product.name)}</strong><span>${extra?'+ '+money(extra):'Sem acréscimo'}</span></button>`;
    }).join('');
    const edges=selected.allowEdges?productEdges():[];
    const edgeField=edges.length?'<div class="field"><span class="field-label">Borda opcional na pizza grande</span><div class="option-grid"><button type="button" class="option '+(!selected.edge?'selected':'')+'" data-combo-edge="none"><strong>Sem borda</strong><span>Sem acréscimo</span></button>'+edges.map((edge,index)=>'<button type="button" class="option '+(selected.edge&&selected.edge[0]===edge[0]?'selected':'')+'" data-combo-edge="'+index+'"><strong>'+escapeCatalogText(edge[0])+'</strong><span>+ '+money(edge[1])+'</span></button>').join('')+'</div></div>':'';
    const drinks=catalogProducts.filter(product=>categorySlugFor(product)==='bebidas'&&product.pricing_mode!=='sizes');
    const drinkField='<div class="field"><span class="field-label">Refrigerante opcional</span><div class="option-grid"><button type="button" class="option '+(!selected.drink?'selected':'')+'" data-combo-drink="none"><strong>Sem refrigerante</strong><span>Sem acréscimo</span></button>'+drinks.map(product=>'<button type="button" class="option '+(selected.drink&&String(selected.drink.id)===String(product.id)?'selected':'')+'" data-combo-drink="'+product.id+'"><strong>'+escapeCatalogText(product.name)+'</strong><span>+ '+money(Number(product.base_price||0)+Number(product.price_addition||0))+'</span></button>').join('')+'</div></div>';
    const host=document.querySelector('#product-detail');
    host.innerHTML=`<div class="detail-hero"><img class="detail-image" src="${escapeCatalogText(selected.image)}" alt="" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"><div><h3>${escapeCatalogText(selected.name)}</h3><p>Pizza Grande à escolha + Pequena Chocolate com Morango. Valor base ${money(selected.basePrice)}.</p></div></div><div class="field"><span class="field-label">Pizza Pequena inclusa</span><div class="option-grid"><div class="option selected"><strong>Chocolate com Morango</strong><span>Já inclusa na promoção</span></div></div></div><div class="field"><span class="field-label">Escolha os sabores da pizza Grande (1 ou 2) <small style="color:var(--muted)">(${chosen.length}/2)</small></span><div class="option-grid flavor-grid">${cards}</div><small style="display:block;margin-top:8px;color:var(--muted)">Cada sabor especial soma seu adicional separadamente, sem mudar o valor base do combo.</small></div>${edgeField}${drinkField}<div class="field"><span class="field-label">Quantidade de combos</span><div class="quantity"><button class="step" data-combo-pizza-qty="-1"><i data-lucide="minus"></i></button><b>${selected.qty}</b><button class="step" data-combo-pizza-qty="1"><i data-lucide="plus"></i></button></div></div><div class="field"><label class="field-label" for="note">Alguma observação?</label><textarea class="textarea" id="note" placeholder="Ex.: sem cebola">${escapeCatalogText(selected.note||'')}</textarea></div><div class="total-line"><span>Total do combo</span><strong>${money(currentPrice()*selected.qty)}</strong></div><button class="primary" id="add-product" ${chosen.length?'':'disabled'}>Adicionar combo ao pedido <i data-lucide="shopping-bag"></i></button>`;
    lucide.createIcons();
    host.querySelectorAll('[data-combo-pizza-flavor]').forEach(button=>button.onclick=()=>{
      selected.note=host.querySelector('#note')?.value||'';
      const product=flavorProduct(button.dataset.comboPizzaFlavor);
      if(!product)return;
      const index=selected.flavors.findIndex(flavor=>String(flavor.id)===String(product.id));
      if(index>=0)selected.flavors.splice(index,1);
      else if(selected.flavors.length>=2){showToast('A pizza Grande permite até 2 sabores');return}
      else selected.flavors.push(flavorInfo(product));
      renderProduct();
    });
    host.querySelectorAll('[data-combo-pizza-qty]').forEach(button=>button.onclick=()=>{
      selected.note=host.querySelector('#note')?.value||'';
      selected.qty=Math.max(1,Math.min(50,selected.qty+Number(button.dataset.comboPizzaQty)));
      renderProduct();
    });
    host.querySelectorAll('[data-combo-edge]').forEach(button=>button.onclick=()=>{
      selected.note=host.querySelector('#note')?.value||'';
      selected.edge=button.dataset.comboEdge==='none'?null:edges[Number(button.dataset.comboEdge)];
      renderProduct();
    });
    host.querySelectorAll('[data-combo-drink]').forEach(button=>button.onclick=()=>{
      selected.note=host.querySelector('#note')?.value||'';
      const product=button.dataset.comboDrink==='none'?null:catalogProducts.find(row=>String(row.id)===button.dataset.comboDrink);
      selected.drink=product?{id:product.id,name:product.name,price:Number(product.base_price||0)+Number(product.price_addition||0)}:null;
      renderProduct();
    });
    host.querySelector('#add-product').onclick=()=>{
      if(!selected.flavors.length){showToast('Escolha pelo menos um sabor para a Grande');return}
      selected.note=host.querySelector('#note')?.value||'';
      cart.push({...selected,originalName:selected.name,flavors:selected.flavors.map(flavor=>({...flavor})),sizeName:null,price:currentPrice()});
      closeOverlay('product-overlay');
      updateCart();
      showToast('Combo adicionado ao pedido');
    };
  }
  renderProduct=function(){return selected?.comboPizza?renderCombo():oldRenderProduct()};
  cartPayload=async function(){
    const items=await oldCartPayload();
    items.forEach((payload,index)=>{
      const item=cart[index];
      if(isComboItem(item)){
        payload.combo_pizza_flavors=(item.flavors||[]).map(flavor=>flavor.id);
        if(item.edge)payload.edge=item.edge[0];
        if(item.drink)payload.combo_drink_id=item.drink.id;
      }
    });
    return items;
  };
  cartItemDetail=function(item){
    if(!isComboItem(item))return oldCartItemDetail(item);
    const names=(item.flavors||[]).map(flavor=>flavor.name).join(' / ');
    return `Pizza Grande: ${names} · Pizza Pequena: Chocolate com Morango${item.edge?' · Borda '+item.edge[0]:''}${item.drink?' · Bebida '+item.drink.name:''}${item.note?' · '+item.note:''}`;
  };
  promotionCard=function(product){
    if(!isCombo(product))return oldPromotionCard(product);
    const image=product.image_url||pizzaImage;
    return `<button type="button" class="promo-card" data-configure-product="${product.id}" aria-label="Montar combo de duas pizzas"><img src="${image}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"><span class="promo-card-copy"><span class="promo-pill">COMBO 2 PIZZAS</span><h3>${escapeCatalogText(product.name)}</h3><small>Grande à escolha + Pequena Chocolate com Morango · borda e bebida opcionais</small><span class="promo-prices"><strong>${money(product.base_price)} + adicionais</strong></span></span></button>`;
  };
  renderPromotions=function(){
    const host=document.querySelector('#promo-showcase'),track=document.querySelector('#promo-track');
    if(!host||!track)return;
    const promos=catalogProducts.filter(product=>productOnPromotion(product)||isCombo(product))
      .sort((a,b)=>Number(Boolean(isCombo(b)))-Number(Boolean(isCombo(a)))||Number(a.promotion_sort_order||0)-Number(b.promotion_sort_order||0)||Number(a.sort_order||0)-Number(b.sort_order||0));
    if(!promos.length){host.hidden=true;track.innerHTML='';return}
    const base=promos.map(promotionCard).join('');
    const filled=Array.from({length:Math.max(1,Math.ceil(8/promos.length))},()=>base).join('');
    track.innerHTML=`<div class="promo-set">${filled}</div><div class="promo-set" aria-hidden="true">${filled}</div>`;
    host.hidden=false;
  };
})();
