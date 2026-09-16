from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

old="const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;\n      const deliveryCode=Array.isArray(data)&&data[0]?data[0].delivery_code:null;"
new="const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;\n      const orderCode=Array.isArray(data)&&data[0]?data[0].order_code:null;\n      const deliveryCode=Array.isArray(data)&&data[0]?data[0].delivery_code:null;"
if old not in s: raise SystemExit('checkout result marker not found')
s=s.replace(old,new,1)

old="orderId?`*Pedido #${orderId}*`:'',\n        deliveryCode?`🔐 *Código de entrega: ${deliveryCode}*`:''"
new="orderId?`*Pedido #${orderId}*`:'',\n        orderCode?`🧾 *Código do pedido: ${orderCode}*`:'',\n        deliveryCode?`🔐 *Código de entrega: ${deliveryCode}*`:''"
if old not in s: raise SystemExit('whatsapp order marker not found')
s=s.replace(old,new,1)

old="showToast(deliveryCode?`Pedido #${orderId} criado · Código de entrega ${deliveryCode}`:orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');"
new="showToast(orderCode?`Pedido #${orderId} · ${orderCode} criado com sucesso`:orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');"
if old not in s: raise SystemExit('toast marker not found')
s=s.replace(old,new,1)

p.write_text(s,encoding='utf-8')
print('cardapio public order code patched')
