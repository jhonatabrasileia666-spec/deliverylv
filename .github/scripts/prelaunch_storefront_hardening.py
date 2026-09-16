from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

if 'lv-store-status-module' in s:
    raise SystemExit('store status module already installed')

# Replace fixed open status with live status hooks.
old='<span class="open-status"><i class="status-dot"></i>Aberto agora</span>'
new='<span class="open-status" id="store-status"><i class="status-dot" id="store-status-dot"></i><span id="store-status-text">Verificando...</span></span>'
if old not in s: raise SystemExit('fixed open status marker not found')
s=s.replace(old,new,1)

# Hide voice AI UI without deleting implementation.
s=s.replace('<button class="voice-button" id="voice-toggle" aria-label="Abrir assistente por voz">','<button class="voice-button" id="voice-toggle" hidden aria-hidden="true" aria-label="Abrir assistente por voz">',1)
s=s.replace('<div class="voice-panel" id="voice-panel">','<div class="voice-panel" id="voice-panel" hidden aria-hidden="true">',1)

# Ensure a fresh store-state check before submitting an order.
old='''  async function sendOrderToOperation(){
    if(!cart.length)return;
'''
new='''  async function sendOrderToOperation(){
    if(!cart.length)return;
    const liveStoreState=await window.LVStoreStatus?.refresh?.({silent:true});
    if(liveStoreState===false){showToast('A loja está fechada no momento');return}
'''
if old not in s: raise SystemExit('send order marker not found')
s=s.replace(old,new,1)

# Keep checkout button synchronized even after cart rerenders.
old_tail="document.querySelector('#continue-order').onclick=sendOrderToOperation}"
new_tail="const continueButton=document.querySelector('#continue-order');if(continueButton){continueButton.onclick=sendOrderToOperation;window.LVStoreStatus?.syncCheckout?.()}}"
if old_tail not in s: raise SystemExit('render cart tail marker not found')
s=s.replace(old_tail,new_tail,1)

module=r'''
<style id="lv-store-status-styles">
  .status-dot.closed{background:#ff6b5b;box-shadow:0 0 0 4px #ff6b5b1c}
  .open-status.closed{color:#ffb0a0}
  #continue-order:disabled{opacity:.58;cursor:not-allowed;background:#6f655e;color:#ddd4ca}
</style>
<script id="lv-store-status-module">
(()=>{
  let isOpen=null,loading=false;
  const status=document.querySelector('#store-status');
  const dot=document.querySelector('#store-status-dot');
  const text=document.querySelector('#store-status-text');

  function paint(){
    if(text)text.textContent=isOpen===true?'Aberto agora':isOpen===false?'Fechado agora':'Verificando...';
    status?.classList.toggle('closed',isOpen===false);
    dot?.classList.toggle('closed',isOpen===false);
    syncCheckout();
  }
  function syncCheckout(){
    const button=document.querySelector('#continue-order');if(!button)return;
    button.disabled=isOpen===false;
    if(isOpen===false)button.innerHTML='Loja fechada no momento';
    else if(button.textContent?.includes('Loja fechada'))button.innerHTML='Enviar pedido <i data-lucide="arrow-right"></i>';
    if(window.lucide)lucide.createIcons();
  }
  async function refresh({silent=false}={}){
    if(loading)return isOpen;
    loading=true;
    try{
      const{data,error}=await db.from('store_settings').select('is_open').eq('id',1).single();
      if(error)throw error;
      isOpen=Boolean(data?.is_open);paint();return isOpen;
    }catch(error){
      console.error('Erro ao verificar estado da loja:',error);
      if(!silent&&typeof showToast==='function')showToast('Não foi possível verificar o horário da loja');
      return null;
    }finally{loading=false}
  }
  window.LVStoreStatus={refresh,syncCheckout,get isOpen(){return isOpen}};
  refresh();
  window.setInterval(()=>refresh({silent:true}),30000);
})();
</script>
'''
if '</body>' not in s: raise SystemExit('body end not found')
s=s.replace('</body>',module+'\n</body>',1)

checks=['id="store-status"','id="lv-store-status-module"','liveStoreState===false','voice-toggle" hidden','voice-panel" id="voice-panel" hidden']
for c in checks:
    if c not in s: raise SystemExit('missing marker: '+c)
if '>Aberto agora</span><button class="icon-btn"' in s:
    raise SystemExit('fixed open status still present')

p.write_text(s,encoding='utf-8')
print('storefront prelaunch hardening applied')
