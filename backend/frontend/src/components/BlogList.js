import React from 'react';
export default function BlogList({blogs, onSelect}){
  return (
    <div style={{background:'#fff', padding:12, borderRadius:6}}>
      <h3>Your Blogs</h3>
      {blogs.length===0 && <div>No blogs yet</div>}
      <ul>
        {blogs.map(b=>(<li key={b.id} style={{marginBottom:8}}><a href="#" onClick={(e)=>{e.preventDefault(); onSelect(b)}}>{b.title || b.keyword}</a></li>))}
      </ul>
    </div>
  );
}
