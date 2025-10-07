import React from 'react';
export default function Pricing({userId}){
  const plans = [
    {id:'basic', name:'Basic', price:29, desc:'50 blogs / month'},
    {id:'pro', name:'Pro', price:49, desc:'200 blogs / month'},
    {id:'premium', name:'Premium', price:99, desc:'Unlimited blogs'}
  ];

  async function subscribe(planId, provider){
    const res = await fetch('http://localhost:5000/api/payment/create-checkout', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ user_id: userId, plan_id: planId, provider })
    });
    const data = await res.json();
    if(data.url){
      window.open(data.url, '_blank');
    } else if(data.order){
      alert('Razorpay order created. Implement client-side checkout with order details.');
    } else {
      alert('Payment initiation failed: ' + JSON.stringify(data));
    }
  }

  return (
    <div style={{background:'#fff', padding:12, borderRadius:6, marginTop:12}}>
      <h3>Pricing</h3>
      <div style={{display:'flex', gap:12}}>
        {plans.map(p=>(
          <div key={p.id} style={{border:'1px solid #ddd', padding:12, width:200}}>
            <h4>{p.name}</h4>
            <div style={{fontSize:20, fontWeight:700}}>${p.price}/mo</div>
            <div style={{marginTop:8}}>{p.desc}</div>
            <div style={{marginTop:12}}>
              <button onClick={()=>subscribe(p.id, 'stripe')}>Subscribe with Stripe</button>
            </div>
            <div style={{marginTop:6}}>
              <button onClick={()=>subscribe(p.id, 'paypal')}>Pay with PayPal</button>
            </div>
            <div style={{marginTop:6}}>
              <button onClick={()=>subscribe(p.id, 'razorpay')}>Pay with Razorpay</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
