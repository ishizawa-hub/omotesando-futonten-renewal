(function(){
  'use strict';
  var CART_KEY='oft_cart';
  function getCart(){try{return JSON.parse(localStorage.getItem(CART_KEY))||[];}catch(e){return[];}}
  function saveCart(c){localStorage.setItem(CART_KEY,JSON.stringify(c));updateBadge();}
  function addToCart(item){
    var c=getCart();
    var ex=c.find(function(x){return x.id===item.id&&x.size===item.size&&x.color===item.color;});
    if(ex){ex.qty=Math.min(10,ex.qty+item.qty);}else{c.push(item);}
    saveCart(c);openDrawer();showToast();
  }
  function removeItem(i){var c=getCart();c.splice(i,1);saveCart(c);renderDrawer();}
  function updateQty(i,d){var c=getCart();c[i].qty=Math.max(1,Math.min(10,c[i].qty+d));saveCart(c);renderDrawer();}
  function cartTotal(){return getCart().reduce(function(s,x){return s+x.price*x.qty;},0);}
  function cartCount(){return getCart().reduce(function(s,x){return s+x.qty;},0);}
  function updateBadge(){
    var n=cartCount();
    document.querySelectorAll('.header-actions a').forEach(function(el){
      if(el.textContent.match(/^CART\(\d+\)$/)){el.textContent='CART('+n+')';}
    });
  }
  function createDrawer(){
    if(document.getElementById('cartDrawer'))return;
    var ov=document.createElement('div');ov.id='cartOverlay';
    ov.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,0.4);z-index:9998;opacity:0;visibility:hidden;transition:opacity .3s,visibility .3s;cursor:pointer';
    ov.onclick=closeDrawer;
    var dr=document.createElement('div');dr.id='cartDrawer';
    dr.style.cssText='position:fixed;top:0;right:0;width:420px;max-width:90vw;height:100vh;background:#fff;z-index:9999;transform:translateX(100%);transition:transform .35s cubic-bezier(.4,0,.2,1);display:flex;flex-direction:column;box-shadow:-8px 0 32px rgba(0,0,0,.12)';
    dr.innerHTML='<div id="cartDrawerContent" style="display:flex;flex-direction:column;height:100vh"></div>';
    document.body.appendChild(ov);document.body.appendChild(dr);
  }
  function openDrawer(){
    createDrawer();renderDrawer();
    requestAnimationFrame(function(){
      document.getElementById('cartOverlay').style.opacity='1';
      document.getElementById('cartOverlay').style.visibility='visible';
      document.getElementById('cartDrawer').style.transform='translateX(0)';
      document.body.style.overflow='hidden';
    });
  }
  function closeDrawer(){
    var o=document.getElementById('cartOverlay'),d=document.getElementById('cartDrawer');
    if(o){o.style.opacity='0';o.style.visibility='hidden';}
    if(d){d.style.transform='translateX(100%)';}
    document.body.style.overflow='';
  }
  function getPrefix(){
    var p=location.pathname.split('/').filter(Boolean);
    if(p.length>0&&p[p.length-1].indexOf('.')!==-1)p.pop();
    var pr='';for(var i=0;i<p.length;i++){if(p[i]!=='site-a')pr+='../';}
    return pr||'./';
  }
  function renderDrawer(){
    var el=document.getElementById('cartDrawerContent');if(!el)return;
    var cart=getCart(),total=cartTotal(),count=cartCount(),px=getPrefix(),h='';
    h+='<div style="padding:20px 24px;border-bottom:1px solid #E5E5E5;display:flex;justify-content:space-between;align-items:center">';
    h+='<h2 style="font-family:DM Sans,sans-serif;font-size:16px;font-weight:700;letter-spacing:.1em">CART <span style="font-weight:400;color:#6B6B6B">('+count+')</span></h2>';
    h+='<button onclick="window._cartClose()" style="background:none;border:none;cursor:pointer;font-size:24px;color:#999;padding:4px;line-height:1">&times;</button></div>';
    if(!cart.length){
      h+='<div style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 24px;text-align:center">';
      h+='<svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#ddd" stroke-width="1.5"><circle cx="9" cy="21" r="1"/><circle cx="20" cy="21" r="1"/><path d="M1 1h4l2.68 13.39a2 2 0 002 1.61h9.72a2 2 0 002-1.61L23 6H6"/></svg>';
      h+='<p style="margin-top:16px;font-size:15px;color:#888">\u30AB\u30FC\u30C8\u306F\u7A7A\u3067\u3059</p>';
      h+='<a href="'+px+'products/index.html" style="display:inline-block;margin-top:20px;padding:12px 32px;background:#C9A96E;color:#fff;font-size:13px;font-weight:600;letter-spacing:.08em;text-decoration:none">\u5546\u54C1\u3092\u898B\u308B</a></div>';
    }else{
      h+='<div style="flex:1;overflow-y:auto;padding:0">';
      cart.forEach(function(item,idx){
        h+='<div style="display:grid;grid-template-columns:88px 1fr;gap:14px;padding:16px 24px;border-bottom:1px solid #F0F0F0;align-items:start">';
        h+='<div style="width:88px;height:88px;background:#F7F7F7;border-radius:4px;overflow:hidden">';
        if(item.image)h+='<img src="'+item.image+'" style="width:100%;height:100%;object-fit:cover">';
        h+='</div><div>';
        h+='<p style="font-size:13px;font-weight:600;line-height:1.5;margin-bottom:4px">'+item.name;
        if(item.isRental)h+=' <span style="display:inline-block;background:#C9A96E;color:#fff;font-size:9px;font-weight:700;letter-spacing:.08em;padding:2px 6px;border-radius:2px;vertical-align:middle">レンタル</span>';
        h+='</p>';
        var m=[];if(item.size)m.push(item.size);if(item.color)m.push(item.color);if(item.isRental)m.push('月額制');
        if(m.length)h+='<p style="font-size:11px;color:#888;margin-bottom:8px">'+m.join(' / ')+'</p>';
        h+='<div style="display:flex;align-items:center;justify-content:space-between">';
        h+='<div style="display:flex;align-items:center;gap:0">';
        h+='<button onclick="window._cartQty('+idx+',-1)" style="width:28px;height:28px;border:1px solid #E5E5E5;background:#fff;cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center">\u2212</button>';
        h+='<span style="width:32px;height:28px;border-top:1px solid #E5E5E5;border-bottom:1px solid #E5E5E5;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600">'+item.qty+'</span>';
        h+='<button onclick="window._cartQty('+idx+',1)" style="width:28px;height:28px;border:1px solid #E5E5E5;background:#fff;cursor:pointer;font-size:14px;display:flex;align-items:center;justify-content:center">+</button></div>';
        h+='<span style="font-family:DM Sans,sans-serif;font-size:15px;font-weight:700">&yen;'+(item.price*item.qty).toLocaleString()+'</span></div>';
        h+='<button onclick="window._cartRm('+idx+')" style="background:none;border:none;cursor:pointer;font-size:11px;color:#999;margin-top:6px;padding:0">\u524A\u9664</button>';
        h+='</div></div>';
      });
      h+='</div>';
      h+='<div style="border-top:1px solid #E5E5E5;padding:20px 24px">';
      h+='<div style="display:flex;justify-content:space-between;margin-bottom:6px"><span style="font-size:13px;color:#6B6B6B">\u5C0F\u8A08</span><span style="font-family:DM Sans,sans-serif;font-size:15px;font-weight:700">&yen;'+total.toLocaleString()+'</span></div>';
      h+='<div style="display:flex;justify-content:space-between;margin-bottom:16px"><span style="font-size:12px;color:#999">\u9001\u6599</span><span style="font-size:12px;color:#999">\u7121\u6599</span></div>';
      h+='<a href="'+px+'checkout/index.html" style="display:block;width:100%;padding:16px;background:#C9A96E;color:#fff;text-align:center;font-size:14px;font-weight:600;letter-spacing:.08em;text-decoration:none">\u3054\u8CFC\u5165\u624B\u7D9A\u304D\u3078</a>';
      h+='<a href="'+px+'products/index.html" style="display:block;text-align:center;margin-top:12px;font-size:12px;color:#C9A96E;text-decoration:none">\u8CB7\u3044\u7269\u3092\u7D9A\u3051\u308B</a></div>';
    }
    el.innerHTML=h;
  }
  function showToast(){
    var t=document.createElement('div');
    t.style.cssText='position:fixed;top:90px;right:440px;background:#2D2D2D;color:#fff;padding:12px 24px;font-size:13px;font-weight:500;z-index:10000;border-radius:4px;opacity:0;transform:translateY(-10px);transition:opacity .3s,transform .3s;display:flex;align-items:center;gap:8px';
    t.innerHTML='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2.5"><path d="M20 6L9 17l-5-5"/></svg> \u30AB\u30FC\u30C8\u306B\u8FFD\u52A0\u3057\u307E\u3057\u305F';
    document.body.appendChild(t);
    requestAnimationFrame(function(){t.style.opacity='1';t.style.transform='translateY(0)';});
    setTimeout(function(){t.style.opacity='0';setTimeout(function(){t.remove();},300);},2500);
  }
  window._cartAdd=addToCart;window._cartRm=removeItem;window._cartQty=updateQty;
  window._cartOpen=openDrawer;window._cartClose=closeDrawer;
  window._cartGet=getCart;window._cartTotal=cartTotal;window._cartCount=cartCount;
  if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',updateBadge);}else{updateBadge();}
  document.addEventListener('click',function(e){
    var lk=e.target.closest('a');
    if(lk&&lk.textContent.match(/^CART\(\d+\)$/)){e.preventDefault();openDrawer();}
  });
})();
