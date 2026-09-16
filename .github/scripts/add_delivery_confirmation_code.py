from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;"
new="const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;\n      const deliveryCode=Array.isArray(data)&&data[0]?data[0].delivery_code:null;"
if old not in s: raise SystemExit('orderId marker not found')
s=s.replace(old,new,1)

old="orderId?`*Pedido #${orderId}*`:'',"
new="orderId?`*Pedido #${orderId}*`:'',\n        deliveryCode?`🔐 *Código de entrega: ${deliveryCode}*`:'',\n        deliveryCode?'Guarde este código e informe somente ao entregador quando o pedido chegar.':'',"
if old not in s: raise SystemExit('whatsapp marker not found')
s=s.replace(old,new,1)

old="showToast(orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');\n      window.location.href=whatsappUrl;"
new="showToast(orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');\n      if(deliveryCode){window.alert(`Seu código de entrega é ${deliveryCode}.\\n\\nGuarde este código e informe somente ao entregador quando o pedido chegar.`)}\n      window.location.href=whatsappUrl;"
if old not in s: raise SystemExit('redirect marker not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('cardapio patched')
