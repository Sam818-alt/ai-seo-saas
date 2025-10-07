import React, {useState} from 'react';
export default function GenerateBlog({onCreate}){
  const [topic, setTopic] = useState('');
  const [language, setLanguage] = useState('English');
  const [translate, setTranslate] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleGenerate(){
    if(!topic) return alert('Enter a topic');
    setLoading(true);
    const res = await fetch('http://localhost:5000/api/blog/generate', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ keyword: topic, language, translate, user_id: 'demo-user' })
    });
    const data = await res.json();
    setLoading(false);
    if(data.blog_id){
      const g = await fetch(`http://localhost:5000/api/blog/${data.blog_id}`);
      const blog = await g.json();
      onCreate(blog);
    } else {
      alert('Generation failed: ' + JSON.stringify(data));
    }
  }

  return (
    <div style={{background:'#fff', padding:12, borderRadius:6}}>
      <h3>Generate Blog</h3>
      <input value={topic} onChange={e=>setTopic(e.target.value)} placeholder="Topic / Keyword" style={{width:400, padding:8}} />
      <select value={language} onChange={e=>setLanguage(e.target.value)} style={{marginLeft:8, padding:8}}>
        <option>English</option>
        <option>Hindi</option>
        <option>Spanish</option>
        <option>French</option>
        <option>German</option>
      </select>
      <label style={{marginLeft:12}}><input type="checkbox" checked={translate} onChange={e=>setTranslate(e.target.checked)} /> Auto-translate</label>
      <div style={{marginTop:8}}><button onClick={handleGenerate} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</button></div>
    </div>
  );
}
