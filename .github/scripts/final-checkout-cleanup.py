from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# State
old="let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerAddress='';"
new="let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerPhone='', customerAddress='';"
if old not in s: raise SystemExit('checkout state marker not found')
s=s.replace(old,new,1)

# Read + validate phone
old="""    customerName=document.querySelector('#customer-name')?.value.trim()||customerName;
    customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;
    const checkoutScreen=document.querySelector('[data-checkout-screen=\"checkout\"]');
    const nameInput=document.querySelector('#customer-name');
    const addressInput=document.querySelector('#customer-address');
    nameInput?.classList.toggle('invalid',!customerName);
    addressInput?.classList.toggle('invalid',checkoutType==='delivery'&&!customerAddress);
"""
new="""    customerName=document.querySelector('#customer-name')?.value.trim()||customerName;
    customerPhone=document.querySelector('#customer-phone')?.value.trim()||customerPhone;
    customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;
    const checkoutScreen=document.querySelector('[data-checkout-screen=\"checkout\"]');
    const nameInput=document.querySelector('#customer-name');
    const phoneInput=document.querySelector('#customer-phone');
    const addressInput=document.querySelector('#customer-address');
    const phoneDigits=customerPhone.replace(/\\D/g,'');
    nameInput?.classList.toggle('invalid',!customerName);
    phoneInput?.classList.toggle('invalid',phoneDigits.length<8||phoneDigits.length>15);
    addressInput?.classList.toggle('invalid',checkoutType==='delivery'&&!customerAddress);
"""
if old not in s: raise SystemExit('checkout input markers not found')
s=s.replace(old,new,1)

old="""    if(!customerName){checkoutScreen?.classList.add('checkout-shake');showToast('Digite seu nome para continuar');nameInput?.focus();return}
    if(checkoutType==='delivery'&&!customerAddress){checkoutScreen?.classList.add('checkout-shake');showToast('Digite sua localização para a entrega');addressInput?.focus();return}
"""
new="""    if(!customerName){checkoutScreen?.classList.add('checkout-shake');showToast('Digite seu nome para continuar');nameInput?.focus();return}
    if(phoneDigits.length<8||phoneDigits.length>15){checkoutScreen?.classList.add('checkout-shake');showToast('Digite um telefone válido para contato');phoneInput?.focus();return}
    if(checkoutType==='delivery'&&!customerAddress){checkoutScreen?.classList.add('checkout-shake');showToast('Digite sua localização para a entrega');addressInput?.focus();return}
"""
if old not in s: raise SystemExit('checkout validation marker not found')
s=s.replace(old,new,1)

# Payload
old="""      const pedido={
        customer_name:customerName,
        order_type:checkoutType,
"""
new="""      const pedido={
        customer_name:customerName,
        customer_phone:customerPhone,
        order_type:checkoutType,
"""
if old not in s: raise SystemExit('pedido payload marker not found')
s=s.replace(old,new,1)

# WhatsApp
old="""        `👤 Cliente: ${customerName}`,
        `📦 Tipo: ${tipoPedidoLabel}`,
"""
new="""        `👤 Cliente: ${customerName}`,
        `📞 Telefone: ${customerPhone}`,
        `📦 Tipo: ${tipoPedidoLabel}`,
"""
if old not in s: raise SystemExit('whatsapp customer marker not found')
s=s.replace(old,new,1)

# Reset
old="""      customerName='';
      customerAddress='';
"""
new="""      customerName='';
      customerPhone='';
      customerAddress='';
"""
if old not in s: raise SystemExit('checkout reset marker not found')
s=s.replace(old,new,1)

# UI field and mojibake
old='<div class="checkout-fields"><div class="checkout-field"><strong>Seu nome</strong><input class="checkout-input" id="customer-name" value="${customerName}" placeholder="Digite seu nome" autocomplete="name"></div><div class="checkout-field"><strong>Como vocÃª quer receber?</strong>'
new='<div class="checkout-fields"><div class="checkout-field"><strong>Seu nome</strong><input class="checkout-input" id="customer-name" value="${customerName}" placeholder="Digite seu nome" autocomplete="name"></div><div class="checkout-field"><strong>Telefone / WhatsApp</strong><input class="checkout-input" id="customer-phone" value="${customerPhone}" placeholder="(68) 99999-9999" inputmode="tel" autocomplete="tel"></div><div class="checkout-field"><strong>Como você quer receber?</strong>'
if old not in s: raise SystemExit('checkout UI marker not found')
s=s.replace(old,new,1)

# Preserve phone across rerenders
s=s.replace("customerName=document.querySelector('#customer-name')?.value.trim()||customerName;customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;checkoutType=button.dataset.checkoutType;", "customerName=document.querySelector('#customer-name')?.value.trim()||customerName;customerPhone=document.querySelector('#customer-phone')?.value.trim()||customerPhone;customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;checkoutType=button.dataset.checkoutType;", 1)
s=s.replace("customerName=document.querySelector('#customer-name')?.value.trim()||customerName;customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;checkoutPayment=button.dataset.checkoutPayment;", "customerName=document.querySelector('#customer-name')?.value.trim()||customerName;customerPhone=document.querySelector('#customer-phone')?.value.trim()||customerPhone;customerAddress=document.querySelector('#customer-address')?.value.trim()||customerAddress;checkoutPayment=button.dataset.checkoutPayment;", 1)
old="document.querySelector('#customer-name')?.addEventListener('input',event=>{customerName=event.target.value});document.querySelector('#customer-address')?.addEventListener('input',event=>{customerAddress=event.target.value});"
new="document.querySelector('#customer-name')?.addEventListener('input',event=>{customerName=event.target.value});document.querySelector('#customer-phone')?.addEventListener('input',event=>{customerPhone=event.target.value});document.querySelector('#customer-address')?.addEventListener('input',event=>{customerAddress=event.target.value});"
if old not in s: raise SystemExit('checkout listener marker not found')
s=s.replace(old,new,1)

checks=['customer_phone:customerPhone','id="customer-phone"','Telefone / WhatsApp','Como você quer receber?','phoneDigits.length<8','📞 Telefone: ${customerPhone}']
for marker in checks:
    if marker not in s: raise SystemExit('missing final marker: '+marker)
if 'Como vocÃª quer receber?' in s: raise SystemExit('mojibake remains')

p.write_text(s,encoding='utf-8')
print('checkout phone + visual text cleanup applied')
