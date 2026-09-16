from pathlib import Path
import re

path = Path('index.html')
text = path.read_text(encoding='utf-8')

old_state = "let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogPizzaSizes=[], catalogEdges=[], selectedPizzaCatalogSize='Pequena', checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerPhone='', customerAddress='', storeIsOpen=false, storeStatusReady=false;"
new_state = "let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogPizzaSizes=[], catalogEdges=[], selectedPizzaCatalogSize='Pequena', checkoutType='pickup', checkoutPayment='pix', checkoutCardType='', cashNeedsChange='no', cashChangeFor='', checkoutStep='cart', customerName='', customerPhone='', customerAddress='', storeIsOpen=false, storeStatusReady=false;"
if old_state not in text:
    raise SystemExit('state marker not found')
text = text.replace(old_state, new_state, 1)

old_money = "const money=value=>Number(value||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});"
new_money = """const money=value=>Number(value||0).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
  const parseMoneyInput=value=>{let raw=String(value||'').trim().replace(/\\s/g,'').replace(/[^0-9.,]/g,'');if(!raw)return NaN;if(raw.includes(','))raw=raw.replace(/\\./g,'').replace(',','.');const parsed=Number(raw);return Number.isFinite(parsed)?parsed:NaN};"""
if old_money not in text:
    raise SystemExit('money marker not found')
text = text.replace(old_money, new_money, 1)

send_fn = r'''  async function sendOrderToOperation(){
    if(!cart.length)return;
    const storeStatusOk=await loadStoreStatus();
    if(!storeStatusOk||!storeIsOpen){showToast(storeStatusReady?'A loja está fechada no momento':'Não foi possível confirmar se a loja está aberta');return}
    customerName=document.querySelector('#customer-name')?.value.trim()||customerName;
    customerPhone=document.querySelector('#customer-phone')?.value.trim()||customerPhone;
    customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;
    cashChangeFor=document.querySelector('#cash-change-for')?.value.trim()||cashChangeFor;
    const checkoutScreen=document.querySelector('[data-checkout-screen="checkout"]');
    const nameInput=document.querySelector('#customer-name');
    const phoneInput=document.querySelector('#customer-phone');
    const addressInput=document.querySelector('#customer-address');
    const changeInput=document.querySelector('#cash-change-for');
    const phoneDigits=customerPhone.replace(/\D/g,'');
    const subtotal=cart.reduce((sum,item)=>sum+item.price*item.qty,0);
    const changeAmount=parseMoneyInput(cashChangeFor);
    nameInput?.classList.toggle('invalid',!customerName);
    phoneInput?.classList.toggle('invalid',phoneDigits.length<8||phoneDigits.length>15);
    addressInput?.classList.toggle('invalid',checkoutType==='delivery'&&!customerAddress);
    changeInput?.classList.toggle('invalid',checkoutType==='delivery'&&checkoutPayment==='cash'&&cashNeedsChange==='yes'&&(!Number.isFinite(changeAmount)||changeAmount<=subtotal));
    checkoutScreen?.classList.remove('checkout-shake');
    void checkoutScreen?.offsetWidth;
    if(!customerName){checkoutScreen?.classList.add('checkout-shake');showToast('Digite seu nome para continuar');nameInput?.focus();return}
    if(phoneDigits.length<8||phoneDigits.length>15){checkoutScreen?.classList.add('checkout-shake');showToast('Digite um telefone válido para contato');phoneInput?.focus();return}
    if(checkoutType==='delivery'&&!customerAddress){checkoutScreen?.classList.add('checkout-shake');showToast('Digite sua localização para a entrega');addressInput?.focus();return}
    if(!checkoutType||!checkoutPayment){showToast('Escolha o tipo e o pagamento do pedido');return}
    if(checkoutType==='delivery'&&checkoutPayment==='card'&&!checkoutCardType){checkoutScreen?.classList.add('checkout-shake');showToast('Escolha débito ou crédito');return}
    if(checkoutType==='delivery'&&checkoutPayment==='cash'&&cashNeedsChange==='yes'&&(!Number.isFinite(changeAmount)||changeAmount<=subtotal)){checkoutScreen?.classList.add('checkout-shake');showToast('Informe um valor de troco maior que o total do pedido');changeInput?.focus();return}
    const button=document.querySelector('#continue-order');
    if(button){button.disabled=true;button.textContent='Enviando pedido...'}
    try{
      const lookup=await loadProductLookup();
      const items=cart.map(item=>{
        const category=item.category||'esfirras';
        const productId=item.id||lookup.get(`${category}|${item.name}`);
        if(!productId)throw new Error(`Produto não encontrado no Supabase: ${category} / ${item.name}`);
        const payload={
          product_id:productId,
          qty:item.qty,
          note:item.note||'',
          detail:item.sizeName?'':(category==='pizzas'?'':'Porção escolhida')
        };
        if(item.sizeName)payload.size=item.sizeName;
        if(category==='pizzas'&&Array.isArray(item.flavors)&&item.flavors.length)payload.flavors=item.flavors.map(flavor=>flavor.id);
        if(item.edge)payload.edge=item.edge[0];
        return payload;
      });
      let paymentMethod='A confirmar';
      if(checkoutType==='delivery'){
        if(checkoutPayment==='card')paymentMethod=checkoutCardType==='credit'?'card_credit':'card_debit';
        else paymentMethod=checkoutPayment;
      }
      const orderNotes=checkoutType==='delivery'&&checkoutPayment==='cash'&&cashNeedsChange==='yes'&&Number.isFinite(changeAmount)?`Troco para ${money(changeAmount)}`:'';
      const pedido={
        customer_name:customerName,
        customer_phone:customerPhone,
        order_type:checkoutType,
        payment_method:paymentMethod,
        customer_address:customerAddress,
        address:customerAddress,
        notes:orderNotes,
        items
      };
      const {data,error}=await db.rpc('criar_pedido',{p_pedido:pedido});
      if(error)throw error;
      const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;
      const orderCode=Array.isArray(data)&&data[0]?data[0].order_code:null;
      const deliveryCode=Array.isArray(data)&&data[0]?data[0].delivery_code:null;
      const serverTotal=Number(Array.isArray(data)&&data[0]?data[0].order_total:NaN);
      const creditFee=checkoutType==='delivery'&&checkoutPayment==='card'&&checkoutCardType==='credit'?5:0;
      const totalPedido=Number.isFinite(serverTotal)?serverTotal:subtotal+creditFee;
      const tipoPedidoLabel={delivery:'Entrega',pickup:'Retirada',local:'Comer no local'}[checkoutType]||checkoutType;
      let pagamentoPedidoLabel='A confirmar';
      if(checkoutType==='delivery'){
        if(checkoutPayment==='pix')pagamentoPedidoLabel='Pix';
        else if(checkoutPayment==='cash')pagamentoPedidoLabel='Dinheiro';
        else if(checkoutPayment==='card')pagamentoPedidoLabel=checkoutCardType==='credit'?'Cartão - Crédito':'Cartão - Débito';
      }
      const itensWhatsApp=cart.map(item=>{
        const detalhes=[];
        if(item.sizeName)detalhes.push(`Tamanho ${item.sizeName}`);
        if(Array.isArray(item.flavors)&&item.flavors.length>1)detalhes.push(`Sabores: ${item.flavors.map(flavor=>flavor.name).join(' / ')}`);
        if(item.edge)detalhes.push(`Borda ${item.edge[0]}`);
        if(item.note)detalhes.push(`Obs: ${item.note}`);
        return `• ${item.qty}x ${item.name}${detalhes.length?` (${detalhes.join(' · ')})`:''} — ${money(item.price*item.qty)}`;
      }).join('\n');
      const mensagemWhatsApp=[
        '🍕 *NOVO PEDIDO - DELIVERY LV*',
        orderId?`*Pedido #${orderId}*`:'',
        orderCode?`🧾 *Código do pedido: ${orderCode}*`:'',
        deliveryCode?`🔐 *Código de entrega: ${deliveryCode}*`:'',
        deliveryCode?'⚠️ Informe este código ao entregador somente quando receber o pedido.':'',
        '',
        `👤 Cliente: ${customerName}`,
        `📞 Telefone: ${customerPhone}`,
        `📦 Tipo: ${tipoPedidoLabel}`,
        checkoutType==='delivery'&&customerAddress?`📍 Endereço: ${customerAddress}`:'',
        `💳 Pagamento: ${pagamentoPedidoLabel}`,
        checkoutType==='delivery'&&checkoutPayment==='card'&&checkoutCardType==='credit'?'💳 Taxa da maquininha: R$ 5,00':'',
        checkoutType==='delivery'&&checkoutPayment==='cash'&&cashNeedsChange==='yes'&&Number.isFinite(changeAmount)?`💵 Troco para: ${money(changeAmount)}`:'',
        '',
        '*Itens:*',
        itensWhatsApp,
        '',
        `💰 *Total: ${money(totalPedido)}*`
      ].filter(Boolean).join('\n');
      const whatsappUrl=`https://wa.me/5568992591250?text=${encodeURIComponent(mensagemWhatsApp)}`;
      cart=[];
      checkoutStep='cart';
      checkoutType='pickup';
      checkoutPayment='pix';
      checkoutCardType='';
      cashNeedsChange='no';
      cashChangeFor='';
      customerName='';
      customerPhone='';
      customerAddress='';
      updateCart();
      closeOverlay('cart-overlay');
      showToast(orderCode?`Pedido #${orderId} · ${orderCode} criado com sucesso`:orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');
      window.location.href=whatsappUrl;
    }catch(error){
      console.error('Erro ao enviar pedido ao Supabase:',error);
      showToast(error.message||'Não foi possível enviar o pedido. Tente novamente.');
      renderCart();
    }
  }'''

text, count = re.subn(r"  async function sendOrderToOperation\(\)\{.*?\n  function cartItemDetail", send_fn + "\n  function cartItemDetail", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'sendOrderToOperation replacement count={count}')

render_fn = r'''  function renderCart(){
    const subtotal=cart.reduce((sum,item)=>sum+item.price*item.qty,0),detail=document.querySelector('#cart-detail');
    if(!cart.length){detail.innerHTML='<div class="empty">Seu carrinho ainda está vazio.<br>Escolha algo delicioso para começar.</div>';return}
    const creditFee=checkoutType==='delivery'&&checkoutPayment==='card'&&checkoutCardType==='credit'?5:0;
    const checkoutTotal=subtotal+creditFee;
    const cardChoice=checkoutPayment==='card'?`<div class="checkout-field"><strong>Débito ou crédito?</strong><div class="checkout-options" style="grid-template-columns:repeat(2,minmax(0,1fr))"><button class="checkout-option ${checkoutCardType==='debit'?'selected':''}" data-checkout-card-type="debit">Débito</button><button class="checkout-option ${checkoutCardType==='credit'?'selected':''}" data-checkout-card-type="credit">Crédito</button></div>${checkoutCardType==='credit'?`<div style="margin-top:8px;color:var(--orange-2);font-size:11px;font-weight:800">Taxa da maquininha: + ${money(5)}</div>`:''}</div>`:'';
    const cashChoice=checkoutPayment==='cash'?`<div class="checkout-field"><strong>Precisa de troco?</strong><div class="checkout-options" style="grid-template-columns:repeat(2,minmax(0,1fr))"><button class="checkout-option ${cashNeedsChange==='no'?'selected':''}" data-cash-change="no">Não</button><button class="checkout-option ${cashNeedsChange==='yes'?'selected':''}" data-cash-change="yes">Sim</button></div>${cashNeedsChange==='yes'?`<div style="margin-top:9px"><input class="checkout-input" id="cash-change-for" value="${escapeCatalogText(cashChangeFor)}" placeholder="Troco para quanto? Ex.: 100,00" inputmode="decimal"><div style="margin-top:6px;color:var(--muted);font-size:10px">Informe o valor que será entregue ao motoboy.</div></div>`:''}</div>`:'';
    const paymentField=checkoutType==='delivery'?`<div class="checkout-field"><strong>Como você vai pagar?</strong><div class="checkout-options">${[['pix','Pix'],['card','Cartão'],['cash','Dinheiro']].map(([value,label])=>`<button class="checkout-option ${checkoutPayment===value?'selected':''}" data-checkout-payment="${value}">${label}</button>`).join('')}</div></div>${cardChoice}${cashChoice}`:'';
    detail.innerHTML=`<div class="checkout-step ${checkoutStep==='cart'?'active':''}" data-checkout-screen="cart"><div class="cart-list">${cart.map((item,index)=>`<div class="cart-item"><div class="cart-item-main"><div><h3>${item.name}</h3><p>${cartItemDetail(item)}</p></div><strong>${money(item.price*item.qty)}</strong></div><div class="cart-controls"><button data-cart-action="minus" data-index="${index}" aria-label="Diminuir"><i data-lucide="minus"></i></button><b>${item.qty}</b><button data-cart-action="plus" data-index="${index}" aria-label="Aumentar"><i data-lucide="plus"></i></button><button class="remove" data-cart-action="remove" data-index="${index}">Remover</button></div></div>`).join('')}</div><div class="total-line"><span>Total do pedido</span><strong>${money(subtotal)}</strong></div><button class="primary" id="go-checkout">Continuar para finalizar <i data-lucide="arrow-right"></i></button></div><div class="checkout-step ${checkoutStep==='checkout'?'active':''}" data-checkout-screen="checkout"><div class="checkout-tabs"><button class="checkout-tab active">Finalizar pedido</button><button class="checkout-tab" id="checkout-summary-tab">${money(checkoutTotal)}</button></div><div class="checkout-fields"><div class="checkout-field"><strong>Seu nome</strong><input class="checkout-input" id="customer-name" value="${customerName}" placeholder="Digite seu nome" autocomplete="name"></div><div class="checkout-field"><strong>Telefone / WhatsApp</strong><input class="checkout-input" id="customer-phone" value="${customerPhone}" placeholder="(68) 99999-9999" inputmode="tel" autocomplete="tel"></div><div class="checkout-field"><strong>Como você quer receber?</strong><div class="checkout-options">${[['delivery','Entrega'],['pickup','Retirada'],['local','Comer no local']].map(([value,label])=>`<button class="checkout-option ${checkoutType===value?'selected':''}" data-checkout-type="${value}">${label}</button>`).join('')}</div>${checkoutType==='delivery'?'<div class="checkout-location"><input class="checkout-input" id="customer-address" value="'+customerAddress+'" placeholder="Digite seu endereço ou localização" autocomplete="street-address"><button type="button" class="gps-button" id="gps-button" title="Usar GPS"><i data-lucide="map-pin"></i> GPS</button></div>':''}</div>${paymentField}</div>${creditFee?`<div class="total-line"><span>Total com taxa de crédito</span><strong>${money(checkoutTotal)}</strong></div>`:''}<button class="primary" id="continue-order">Enviar pedido <i data-lucide="arrow-right"></i></button><button class="checkout-back" id="back-to-cart">Voltar ao carrinho</button></div>`;
    lucide.createIcons();
    const persistCheckoutInputs=()=>{customerName=document.querySelector('#customer-name')?.value.trim()||customerName;customerPhone=document.querySelector('#customer-phone')?.value.trim()||customerPhone;customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;cashChangeFor=document.querySelector('#cash-change-for')?.value.trim()||cashChangeFor};
    document.querySelectorAll('[data-cart-action]').forEach(button=>button.onclick=()=>{const i=Number(button.dataset.index),action=button.dataset.cartAction;if(action==='plus')cart[i].qty++;if(action==='minus')cart[i].qty--;if(action==='remove'||cart[i].qty<=0)cart.splice(i,1);updateCart();document.querySelector('#cart-overlay').classList.add('show')});
    document.querySelector('#go-checkout').onclick=()=>{checkoutStep='checkout';renderCart()};
    document.querySelector('#back-to-cart').onclick=()=>{checkoutStep='cart';renderCart()};
    document.querySelectorAll('[data-checkout-type]').forEach(button=>button.onclick=()=>{persistCheckoutInputs();checkoutType=button.dataset.checkoutType;renderCart()});
    document.querySelectorAll('[data-checkout-payment]').forEach(button=>button.onclick=()=>{persistCheckoutInputs();checkoutPayment=button.dataset.checkoutPayment;if(checkoutPayment!=='card')checkoutCardType='';if(checkoutPayment!=='cash'){cashNeedsChange='no';cashChangeFor=''}renderCart()});
    document.querySelectorAll('[data-checkout-card-type]').forEach(button=>button.onclick=()=>{persistCheckoutInputs();checkoutCardType=button.dataset.checkoutCardType;renderCart()});
    document.querySelectorAll('[data-cash-change]').forEach(button=>button.onclick=()=>{persistCheckoutInputs();cashNeedsChange=button.dataset.cashChange;if(cashNeedsChange==='no')cashChangeFor='';renderCart()});
    document.querySelector('#customer-name')?.addEventListener('input',event=>{customerName=event.target.value});
    document.querySelector('#customer-phone')?.addEventListener('input',event=>{customerPhone=event.target.value});
    document.querySelector('#customer-address')?.addEventListener('input',event=>{customerAddress=event.target.value});
    document.querySelector('#cash-change-for')?.addEventListener('input',event=>{cashChangeFor=event.target.value});
    document.querySelector('#continue-order').onclick=sendOrderToOperation;
  }'''

text, count = re.subn(r"  function renderCart\(\)\{.*?\n  function getLocationFromGPS", render_fn + "\n  function getLocationFromGPS", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'renderCart replacement count={count}')

path.write_text(text, encoding='utf-8')
print('payment patch applied')
