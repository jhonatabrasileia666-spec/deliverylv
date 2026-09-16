from pathlib import Path

path=Path('index.html')
s=path.read_text(encoding='utf-8')

old="const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;"
new="const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;\n      const deliveryCode=Array.isArray(data)&&data[0]?data[0].delivery_code:null;"
if 'const deliveryCode=Array.isArray(data)' not in s:
    if old not in s: raise SystemExit('order id anchor not found')
    s=s.replace(old,new,1)

old="orderId?`*Pedido #${orderId}*`:'',\n        '',"
new="orderId?`*Pedido #${orderId}*`:'',\n        deliveryCode?`🔐 *Código de entrega: ${deliveryCode}*`:'',\n        deliveryCode?'⚠️ Informe este código ao entregador somente quando receber o pedido.':'',\n        '',"
if 'Código de entrega: ${deliveryCode}' not in s:
    if old not in s: raise SystemExit('whatsapp message anchor not found')
    s=s.replace(old,new,1)

old="showToast(orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');"
new="showToast(deliveryCode?`Pedido #${orderId} criado · Código de entrega ${deliveryCode}`:orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');"
if 'Código de entrega ${deliveryCode}' not in s:
    if old not in s: raise SystemExit('toast anchor not found')
    s=s.replace(old,new,1)

path.write_text(s,encoding='utf-8')
print('Customer delivery code UI applied')
