(function installLvDuasGrandes(){
  const KIND='duas_grandes_calabresa_frango';
  const OTHER_COMBO='grande_pequena_choco_morango';
  const isCombo=product=>product?.combo_kind===KIND;
  const isComboCart=item=>Boolean(item?.comboDuasGrandes);
  const allowedFlavors=()=>pizzaFlavorProducts().filter(product=>
    ['calabresa','frango'].includes(normalizeProductName(product.name)) &&
    productSizesFor(product).some(size=>normalizeSizeName(size.name)==='grande')
  );
  const oldOpenProduct=openProduct;
  const oldRenderProduct=renderProduct;
  const oldCurrentPrice=currentPrice;
  const oldCartPayload=cartPayload;
  const oldCartItemDetail=cartItemDetail;
  const oldPromotionCard=promotionCard;

  openProduct=function(productId,preferredSize=''){
    const product=catalogProducts.find(row=>String(row.id)===String(productId));
    if(!isCombo(product))return oldOpenProduct(productId,preferredSize);
    selected={
      id:product.id,name:product.name,originalName:product.name,
      ingredients:product.description||'',category:categorySlugFor(product),
      comboDuasGrandes:true,pricingMode:'fixed',basePrice:Number(product.base_price||0),
      pizzas:[{flavorId:null,flavorName:'',edge:null},{flavorId:null,flavorName:'',edge:null}],
      drink:null,qty:1,note:'',edge:null,image:product.image_url||pizzaImage
    };
    renderProduct();
    document.querySelector('#product-overlay').classList.add('show');
  };

  currentPrice=function(){
    if(!selected?.comboDuasGrandes)return oldCurrentPrice();
    const bordas=selected.pizzas.reduce((total,pizza)=>total+Number(pizza.edge?.[1]||0),0);
    return Math.round((selected.basePrice+bordas+Number(selected.drink?.price||0))*100)/100;
  };

  function renderDuasGrandes(){
    const host=document.querySelector('#product-detail');
    if(!host)return;
    const flavors=allowedFlavors();
    const edges=productEdges();
    const drinks=catalogProducts.filter(product=>
      categorySlugFor(product)==='bebidas'&&product.pricing_mode!=='sizes'
    );
    const pizzaFields=selected.pizzas.map((pizza,i)=>{
      const flavorOptions=flavors.map(product=>
        '<button type="button" class="option '+(String(pizza.flavorId)===String(product.id)?'selected':'')+
        '" data-duas-flavor="'+i+'" data-duas-flavor-id="'+product.id+'"><strong>'+
        escapeCatalogText(product.name)+'</strong><span>Incluso</span></button>'
      ).join('');
      const edgeOptions='<button type="button" class="option '+(!pizza.edge?'selected':'')+
        '" data-duas-edge="'+i+'" data-duas-edge-index="none"><strong>Sem borda</strong><span>Sem acréscimo</span></button>'+
        edges.map((edge,index)=>
          '<button type="button" class="option '+(pizza.edge&&pizza.edge[0]===edge[0]?'selected':'')+
          '" data-duas-edge="'+i+'" data-duas-edge-index="'+index+'"><strong>'+
          escapeCatalogText(edge[0])+'</strong><span>+ '+money(edge[1])+'</span></button>'
        ).join('');
      return '<div class="field"><span class="field-label">Pizza '+(i+1)+' · Grande · escolha 1 sabor</span>'+
        '<div class="option-grid flavor-grid">'+flavorOptions+'</div></div>'+
        '<div class="field"><span class="field-label">Borda da pizza '+(i+1)+' (opcional)</span>'+
        '<div class="option-grid">'+edgeOptions+'</div></div>';
    }).join('');
    const drinkOptions='<button type="button" class="option '+(!selected.drink?'selected':'')+
      '" data-duas-drink="none"><strong>Sem refrigerante</strong><span>Sem acréscimo</span></button>'+
      drinks.map(product=>{
        const price=Number(product.base_price||0)+Number(product.price_addition||0);
        return '<button type="button" class="option '+(selected.drink&&String(selected.drink.id)===String(product.id)?'selected':'')+
          '" data-duas-drink="'+product.id+'"><strong>'+escapeCatalogText(product.name)+
          '</strong><span>+ '+money(price)+'</span></button>';
      }).join('');
    host.innerHTML='<div class="detail-hero"><img class="detail-image" src="'+escapeCatalogText(selected.image)+
      '" alt="" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()"><div><h3>'+
      escapeCatalogText(selected.name)+'</h3><p>2 pizzas Grandes por '+money(selected.basePrice)+
      '. Escolha Calabresa ou Frango para cada pizza. Bordas e refrigerante cobrados à parte.</p></div></div>'+
      pizzaFields+'<div class="field"><span class="field-label">Refrigerante (opcional)</span>'+
      '<div class="option-grid">'+drinkOptions+'</div></div>'+
      '<div class="field"><span class="field-label">Quantidade de combos</span><div class="quantity">'+
      '<button class="step" type="button" data-duas-qty="-1"><i data-lucide="minus"></i></button><b>'+selected.qty+
      '</b><button class="step" type="button" data-duas-qty="1"><i data-lucide="plus"></i></button></div></div>'+
      '<div class="field"><label class="field-label" for="note">Alguma observação?</label>'+
      '<textarea class="textarea" id="note" placeholder="Ex.: sem cebola">'+escapeCatalogText(selected.note||'')+'</textarea></div>'+
      '<div class="total-line"><span>Total do combo</span><strong>'+money(currentPrice()*selected.qty)+'</strong></div>'+
      '<button class="primary" type="button" id="add-product" '+(selected.pizzas.every(p=>p.flavorId)?'':'disabled')+
      '>Adicionar combo ao pedido <i data-lucide="shopping-bag"></i></button>';
    lucide.createIcons();
    const persistNote=()=>{selected.note=host.querySelector('#note')?.value||'';};
    host.querySelectorAll('[data-duas-flavor]').forEach(button=>button.onclick=()=>{
      persistNote();
      const idx=Number(button.dataset.duasFlavor);
      const product=flavors.find(row=>String(row.id)===String(button.dataset.duasFlavorId));
      if(!product)return;
      selected.pizzas[idx].flavorId=product.id;
      selected.pizzas[idx].flavorName=product.name;
      renderProduct();
    });
    host.querySelectorAll('[data-duas-edge]').forEach(button=>button.onclick=()=>{
      persistNote();
      const idx=Number(button.dataset.duasEdge);
      selected.pizzas[idx].edge=button.dataset.duasEdgeIndex==='none'
        ?null:edges[Number(button.dataset.duasEdgeIndex)];
      renderProduct();
    });
    host.querySelectorAll('[data-duas-drink]').forEach(button=>button.onclick=()=>{
      persistNote();
      const product=button.dataset.duasDrink==='none'?null:
        drinks.find(row=>String(row.id)===String(button.dataset.duasDrink));
      selected.drink=product?{id:product.id,name:product.name,
        price:Number(product.base_price||0)+Number(product.price_addition||0)}:null;
      renderProduct();
    });
    host.querySelectorAll('[data-duas-qty]').forEach(button=>button.onclick=()=>{
      persistNote();
      selected.qty=Math.max(1,Math.min(50,selected.qty+Number(button.dataset.duasQty)));
      renderProduct();
    });
    host.querySelector('#add-product').onclick=()=>{
      if(!selected.pizzas.every(p=>p.flavorId)){
        showToast('Escolha um sabor para cada uma das duas pizzas');return;
      }
      persistNote();
      cart.push({...selected,
        pizzas:selected.pizzas.map(p=>({...p,edge:p.edge?[...p.edge]:null})),
        drink:selected.drink?{...selected.drink}:null,
        price:currentPrice()
      });
      closeOverlay('product-overlay');
      updateCart();
      showToast('Combo de duas pizzas adicionado');
    };
  }
  renderProduct=function(){return selected?.comboDuasGrandes?renderDuasGrandes():oldRenderProduct();};

  cartPayload=async function(){
    const items=await oldCartPayload();
    items.forEach((payload,index)=>{
      const item=cart[index];
      if(!isComboCart(item))return;
      payload.combo_pizza_flavors=item.pizzas.map(p=>p.flavorId);
      payload.combo_pizza_edges=item.pizzas.map(p=>p.edge?p.edge[0]:null);
      if(item.drink)payload.combo_drink_id=item.drink.id;
    });
    return items;
  };
  cartItemDetail=function(item){
    if(!isComboCart(item))return oldCartItemDetail(item);
    const details=item.pizzas.map((pizza,index)=>
      'Pizza '+(index+1)+': Grande '+pizza.flavorName+
      (pizza.edge?' · Borda '+pizza.edge[0]:' · Sem borda')
    );
    if(item.drink)details.push('Refrigerante: '+item.drink.name);
    if(item.note)details.push(item.note);
    return details.join(' | ');
  };
  promotionCard=function(product){
    if(!isCombo(product))return oldPromotionCard(product);
    const image=product.image_url||pizzaImage;
    return '<button type="button" class="promo-card" data-configure-product="'+product.id+
      '" aria-label="Montar combo de duas pizzas grandes"><img src="'+escapeCatalogText(image)+
      '" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.remove()">'+
      '<span class="promo-card-copy"><span class="promo-pill">2 PIZZAS GRANDES</span><h3>'+
      escapeCatalogText(product.name)+'</h3><small>Calabresa ou Frango · bordas individuais e refrigerante opcionais</small>'+
      '<span class="promo-prices"><strong>'+money(product.base_price)+' + opcionais</strong></span></span></button>';
  };
  renderPromotions=function(){
    const host=document.querySelector('#promo-showcase'),track=document.querySelector('#promo-track');
    if(!host||!track)return;
    const promos=catalogProducts.filter(product=>
      productOnPromotion(product)||product.combo_kind===OTHER_COMBO||isCombo(product)
    ).sort((a,b)=>
      Number(isCombo(b))-Number(isCombo(a))||
      Number(b.combo_kind===OTHER_COMBO)-Number(a.combo_kind===OTHER_COMBO)||
      Number(a.promotion_sort_order||0)-Number(b.promotion_sort_order||0)||
      Number(a.sort_order||0)-Number(b.sort_order||0)
    );
    if(!promos.length){host.hidden=true;track.innerHTML='';return;}
    const cards=promos.map(promotionCard).join('');
    const filled=Array.from({length:Math.max(1,Math.ceil(8/promos.length))},()=>cards).join('');
    track.innerHTML='<div class="promo-set">'+filled+'</div><div class="promo-set" aria-hidden="true">'+filled+'</div>';
    host.hidden=false;
  };
})();
