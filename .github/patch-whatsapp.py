from pathlib import Path

path = Path('index.html')
data = path.read_bytes()
newline = '\r\n' if b'\r\n' in data else '\n'
text = data.decode('utf-8')

marker = "      const orderId=Array.isArray(data)&&data[0]?data[0].order_id:null;"
if marker not in text:
    raise SystemExit('orderId marker not found')
if 'const whatsappUrl=' in text:
    raise SystemExit('WhatsApp checkout already present')

insert = """      const totalPedido=cart.reduce((sum,item)=>sum+item.price*item.qty,0);
      const tipoPedidoLabel={delivery:'Entrega',pickup:'Retirada',local:'Comer no local'}[checkoutType]||checkoutType;
      const pagamentoPedidoLabel={pix:'Pix',card:'Cartão',cash:'Dinheiro'}[checkoutPayment]||pedido.payment_method||'A confirmar';
      const itensWhatsApp=cart.map(item=>{
        const detalhes=[];
        if(item.category==='pizzas'){
          if(Number.isInteger(item.size)&&sizes[item.size])detalhes.push(sizes[item.size][0]);
          if(item.edge)detalhes.push(`Borda ${item.edge[0]}`);
          if(item.note)detalhes.push(`Obs: ${item.note}`);
        }else if(item.note){
          detalhes.push(`Obs: ${item.note}`);
        }
        return `• ${item.qty}x ${item.name}${detalhes.length?` (${detalhes.join(' · ')})`:''} — ${money(item.price*item.qty)}`;
      }).join('\\n');
      const mensagemWhatsApp=[
        '🍕 *NOVO PEDIDO - DELIVERY LV*',
        orderId?`*Pedido #${orderId}*`:'',
        '',
        `👤 Cliente: ${customerName}`,
        `📦 Tipo: ${tipoPedidoLabel}`,
        checkoutType==='delivery'&&customerAddress?`📍 Endereço: ${customerAddress}`:'',
        `💳 Pagamento: ${checkoutType==='delivery'?pagamentoPedidoLabel:'A confirmar'}`,
        '',
        '*Itens:*',
        itensWhatsApp,
        '',
        `💰 *Total: ${money(totalPedido)}*`
      ].filter(Boolean).join('\\n');
      const whatsappUrl=`https://wa.me/5568992591250?text=${encodeURIComponent(mensagemWhatsApp)}`;"""
insert = insert.replace('\n', newline)
text = text.replace(marker, marker + newline + insert, 1)

toast = "      showToast(orderId?`Pedido #${orderId} enviado para a cozinha`:'Pedido enviado para a cozinha');"
if toast not in text:
    raise SystemExit('success toast marker not found')
text = text.replace(toast, toast + newline + "      window.location.href=whatsappUrl;", 1)

path.write_bytes(text.encode('utf-8'))
