const escapeHtml=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let entries=[];
function render(){
  const query=document.querySelector('#docs-search').value.toLowerCase();
  document.querySelector('#endpoints').innerHTML=entries.filter(e=>(e.path+' '+e.op.summary).toLowerCase().includes(query)).map(e=>'<details class="endpoint" data-index="'+e.index+'"><summary><span class="method">'+e.method.toUpperCase()+'</span><code>'+escapeHtml(e.path)+'</code><span>'+escapeHtml(e.op.summary)+'</span></summary>'+(e.op.parameters||[]).map(p=>'<label>'+escapeHtml(p.name)+'<input data-param="'+escapeHtml(p.name)+'" placeholder="Enter '+escapeHtml(p.name)+'"></label>').join('')+(e.method==='post'?'<textarea aria-label="JSON request body">'+escapeHtml(JSON.stringify(e.op.requestBody?.content?.['application/json']?.example||{},null,2))+'</textarea>':'')+'<details><summary>Request schema</summary><pre>'+escapeHtml(JSON.stringify(e.op.requestBody?.content?.['application/json']?.schema||e.op.parameters||{},null,2))+'</pre></details><div class="execute-row"><button class="primary-btn" data-execute>Execute '+e.method.toUpperCase()+'</button><small>'+(e.method==='post'?'This action uses your current workspace.':'Read request')+'</small></div><pre class="api-result" aria-live="polite">Response will appear here.</pre></details>').join('');
}
fetch('/openapi.json').then(r=>r.json()).then(spec=>{for(const [path,methods] of Object.entries(spec.paths))for(const [method,op] of Object.entries(methods))entries.push({path,method,op,index:entries.length});render();}).catch(()=>{document.querySelector('#endpoints').textContent='Could not load the API contract.';});
document.querySelector('#docs-search').addEventListener('input',render);
document.addEventListener('click',async event=>{
  const button=event.target.closest('[data-execute]');if(!button)return;
  const node=button.closest('.endpoint'),entry=entries[Number(node.dataset.index)],output=node.querySelector('.api-result');button.disabled=true;
  try{
    let path=entry.path;node.querySelectorAll('[data-param]').forEach(input=>{if(!input.value.trim())throw Error('Fill in '+input.dataset.param);path=path.replace('{'+input.dataset.param+'}',encodeURIComponent(input.value.trim()));});
    let body;if(entry.method==='post')body=JSON.stringify(JSON.parse(node.querySelector('textarea').value));
    const response=await fetch(path,{method:entry.method.toUpperCase(),headers:body?{'Content-Type':'application/json'}:{},body});
    if(response.headers.get('content-type')?.includes('json'))output.textContent='HTTP '+response.status+'\n'+JSON.stringify(await response.json(),null,2);
    else{const blob=await response.blob();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='atlas-download';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);output.textContent='HTTP '+response.status+' — File downloaded.';}
  }catch(error){output.textContent=error.message;}finally{button.disabled=false;}
});
