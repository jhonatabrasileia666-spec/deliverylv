from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# 1) Hide voice AI UI without deleting its implementation.
if 'temporary-hide-voice-ai' not in s:
    hidden='''\n<style id="temporary-hide-voice-ai">\n  #voice-toggle,#voice-panel{display:none!important}\n  .open-status.closed{color:#ffb2a3}\n  .open-status.closed .status-dot{background:#ff8f79;box-shadow:0 0 0 4px #ff8f7920}\n  body.store-closed #continue-order{opacity:.55}\n</style>\n'''
    s=s.replace('</head>',hidden+'</head>',1)

# 2) Replace fixed status with dynamic status target.
old='<span class="open-status"><i class="status-dot"></i>Aberto agora</span>'
new='<span class="open-status" id="store-status"><i class="status-dot"></i><span id="store-status-text">Verificando...</span></span>'
if old not in s: raise SystemExit('fixed open status marker not found')
s=s.replace(old,new,1)

# 3) Remove promises not implemented yet.
s=s.replace('Escolha seus sabores, personalize cada detalhe e acompanhe seu pedido em poucos toques.','Escolha seus sabores, personalize cada detalhe e finalize seu pedido em poucos toques.',1)
s=s.replace('Aberto todos os dias para deixar seu momento mais gostoso.','Faça seu pedido pelo cardápio online da Delivery LV.',1)

# 4) Store state in frontend.
old_state="let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogPizzaSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerPhone='', customerAddress='';"
new_state="let cart=[], selected=null, catalogProducts=[], catalogCategories=[], catalogProductSizes=[], catalogPizzaSizes=[], catalogEdges=[], checkoutType='pickup', checkoutPayment='pix', checkoutStep='cart', customerName='', customerPhone='', customerAddress='', storeIsOpen=false, storeStatusReady=false;"
if old_state not in s: raise SystemExit('state marker not found')
s=s.replace(old_state,new_state,1)

helper_marker="  const categoryIcon=slug=>({pizzas:'pizza',esfirras:'croissant',bebidas:'cup-soda'}[slug]||'utensils');\n"
if helper_marker not in s: raise SystemExit('helper insertion marker not found')
store_helpers='''  function applyStoreStatus(){\n    const host=document.querySelector('#store-status'),text=document.querySelector('#store-status-text');\n    if(text)text.textContent=storeStatusReady?(storeIsOpen?'Aberto agora':'Fechado agora'):'Status indisponível';\n    host?.classList.toggle('closed',!storeIsOpen);document.body.classList.toggle('store-closed',!storeIsOpen);\n  }\n  async function loadStoreStatus(){\n    try{\n      const{data,error}=await db.from('store_settings').select('is_open').eq('id',1).single();\n      if(error)throw error;storeIsOpen=Boolean(data?.is_open);storeStatusReady=true;applyStoreStatus();return true;\n    }catch(error){\n      console.error('Erro ao carregar status da loja:',error);storeIsOpen=false;storeStatusReady=false;applyStoreStatus();return false;\n    }\n  }\n'''
if 'async function loadStoreStatus()' not in s:
    s=s.replace(helper_marker,helper_marker+store_helpers,1)

# 5) Load status after catalog and keep it fresh.
old_load='catalogCategories=categories||[];catalogProducts=products||[];catalogProductSizes=sizeRows||[];catalogPizzaSizes=pizzaSizeRows||[];catalogEdges=edgeRows||[];productLookup=null;await loadProductLookup();renderCatalog()'
new_load='catalogCategories=categories||[];catalogProducts=products||[];catalogProductSizes=sizeRows||[];catalogPizzaSizes=pizzaSizeRows||[];catalogEdges=edgeRows||[];productLookup=null;await loadProductLookup();renderCatalog();await loadStoreStatus()'
if old_load not in s: raise SystemExit('loadCatalog final marker not found')
s=s.replace(old_load,new_load,1)

# 6) Recheck open status immediately before creating every order.
old_send='  async function sendOrderToOperation(){\n    if(!cart.length)return;\n'
new_send="  async function sendOrderToOperation(){\n    if(!cart.length)return;\n    const storeStatusOk=await loadStoreStatus();\n    if(!storeStatusOk||!storeIsOpen){showToast(storeStatusReady?'A loja está fechada no momento':'Não foi possível confirmar se a loja está aberta');return}\n"
if old_send not in s: raise SystemExit('sendOrder marker not found')
s=s.replace(old_send,new_send,1)

# 7) Poll store status while menu is open.
old_boot="lucide.createIcons();updateCart();loadCatalog().catch(error=>{console.error('Erro ao carregar catálogo do Supabase:',error);showToast('Não foi possível carregar o cardápio real')});"
new_boot="lucide.createIcons();updateCart();loadCatalog().catch(error=>{console.error('Erro ao carregar catálogo do Supabase:',error);showToast('Não foi possível carregar o cardápio real')});window.setInterval(()=>loadStoreStatus(),30000);"
if old_boot not in s: raise SystemExit('boot marker not found')
s=s.replace(old_boot,new_boot,1)

checks=[
    'id="temporary-hide-voice-ai"',
    'id="store-status-text"',
    'async function loadStoreStatus()',
    'const storeStatusOk=await loadStoreStatus()',
    "db.from('store_settings').select('is_open')",
    'finalize seu pedido em poucos toques',
]
for check in checks:
    if check not in s: raise SystemExit('missing final marker: '+check)
if '>Aberto agora</span><button' in s:
    raise SystemExit('fixed open status remains')

p.write_text(s,encoding='utf-8')
print('cardapio store status + hidden voice AI applied')
