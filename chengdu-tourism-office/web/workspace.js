/* General company workspace: one catalog, typed forms, durable runs and connections. */
const workspace = {skills:[], files:[], runs:[], records:[], query:"", category:"All", activeSkill:null, formData:null, peoplePicker:null};
const categoryIcons = {"Office files":"file","Communication":"mail","Finance":"board","People":"people","Sales":"globe","Operations":"board","Governance":"shield","Knowledge":"search","Data":"board","Marketing":"sparkle","Google Workspace":"globe","Integrations":"globe","Tourism template":"globe"};
const effectLabel = effect => ["remote_write","reviewed_write"].includes(effect) ? "Review before action" : effect === "remote_read" ? "Connected account" : "Works locally";
const fileLink = f => '<a class="artifact-link" href="'+safe(f.url||('/api/files/'+f.id+'/download'))+'">'+icon("download")+safe(f.name)+'</a>';
const dateLabel = value => new Date(value).toLocaleString(undefined,{month:"short",day:"numeric",hour:"2-digit",minute:"2-digit"});

async function loadCatalog(){
  if(!workspace.skills.length)workspace.skills=await api('/api/skills');
  return workspace.skills;
}
window.renderWorkspaceView = async function(view){
  if(!["skills","activity","files","connections"].includes(view))return;
  const target=$('#view-'+view);
  target.innerHTML='<div class="loading-state">Loading your workspace…</div>';
  try{
    if(view==="skills"){await loadCatalog();if(state.view===view)renderSkills();}
    if(view==="activity"){
      [workspace.runs,workspace.records]=await Promise.all([api('/api/runs'),api('/api/records')]);
      if(state.view===view)renderActivity();
    }
    if(view==="files"){
      [workspace.files,workspace.records]=await Promise.all([api('/api/files'),api('/api/records')]);
      if(state.view===view)renderFiles();
    }
    if(view==="connections"){
      const connections=await api('/api/connections');if(state.view===view)renderConnections(connections);
    }
  }catch(error){target.innerHTML='<div class="empty-state"><h2>Could not load this page</h2><p>'+safe(error.message)+'</p><button data-refresh-workspace class="secondary-btn">Try again</button></div>';}
};

function renderSkills(){
  const categories=['All',...new Set(workspace.skills.map(s=>s.category))];
  const selected=workspace.skills.filter(s=>(workspace.category==='All'||s.category===workspace.category)&&(s.title+' '+s.description+' '+s.category).toLowerCase().includes(workspace.query.toLowerCase()));
  $('#view-skills').innerHTML=pageHeading('YOUR TEAM’S TOOLBOX','Good at the things that fill your day.','Practical skills for files, people, projects and the work in between.')+
    '<div class="catalog-summary"><span class="tag ok">'+workspace.skills.length+' executable skills</span><span>Local tools are ready. Connect accounts when you need them.</span></div><div class="catalog-controls"><input id="skill-search" type="search" class="search-input" placeholder="Search skills, like Excel or onboarding…" aria-label="Search skills" value="'+safe(workspace.query)+'"><select id="skill-category" aria-label="Skill category">'+categories.map(c=>'<option '+(c===workspace.category?'selected':'')+'>'+safe(c)+'</option>').join('')+'</select></div><div class="skill-grid">'+selected.map(s=>
      '<article class="skill-card"><div class="skill-card-top"><span class="skill-symbol">'+icon(categoryIcons[s.category])+'</span><span class="skill-category">'+safe(s.category)+'</span></div><h3>'+safe(s.title)+'</h3><p>'+safe(s.description)+'</p><div class="skill-card-footer"><small>'+safe(effectLabel(s.effect))+'</small><button class="text-link" data-skill="'+safe(s.id)+'">Open skill →</button></div></article>').join('')+'</div>'+(selected.length?'':'<div class="empty-state"><p>No skills match your search.</p></div>');
}

function defaultValue(schema){
  if(schema.default!==undefined)return schema.default;
  if(schema.type==='object')return Object.fromEntries(Object.entries(schema.properties||{}).map(([k,s])=>[k,defaultValue(s)]));
  if(schema.type==='array')return [];
  if(schema.type==='boolean')return false;
  if(schema.type==='number'||schema.type==='integer')return schema.minimum??0;
  return schema.enum?.[0]||'';
}
function fieldMarkup(schema,value,path,labelText){
  const labelHtml='<span class="field-label">'+safe(schema.title||labelText||'Value')+'</span>';
  const attr=' data-field-path="'+safe(path)+'"';
  if(schema.type==='object'&&schema.properties)return '<div class="schema-object"'+attr+'>'+Object.entries(schema.properties).map(([key,s])=>'<div class="schema-field">'+fieldMarkup(s,value?.[key],path?path+'.'+key:key,key.replaceAll('_',' '))+'</div>').join('')+'</div>';
  if(schema.type==='array'){
    const values=Array.isArray(value)?value:[];
    return '<fieldset class="array-field"'+attr+'><legend>'+safe(schema.title||labelText)+'</legend><div class="array-items">'+values.map((v,i)=>'<div class="array-item"><span class="row-number">'+(i+1)+'</span><div>'+fieldMarkup(schema.items,v,path+'.'+i,'Value')+'</div><button type="button" class="remove-row" data-remove-row="'+safe(path)+'" data-row-index="'+i+'" aria-label="Remove row '+(i+1)+'">×</button></div>').join('')+'</div><button type="button" class="text-link" data-add-row="'+safe(path)+'">＋ Add '+(schema.items.type==='object'?'item':'row')+'</button></fieldset>';
  }
  if(schema.type==='object')return '<label>'+labelHtml+'<textarea class="field-value code-input" data-json="true"'+attr+' rows="9">'+safe(JSON.stringify(value||{},null,2))+'</textarea></label>';
  if(Array.isArray(schema.type))return '<label>'+labelHtml+'<input class="field-value" data-kind="cell"'+attr+' value="'+safe(value??'')+'"></label>';
  if(schema.type==='boolean')return '<label class="check-field"><input class="field-value" type="checkbox" data-kind="boolean"'+attr+' '+(value?'checked':'')+'>'+labelHtml+'</label>';
  if(path.endsWith('file_id'))return '<label>'+labelHtml+'<select class="field-value" data-kind="string"'+attr+'><option value="">Select a workspace file…</option>'+workspace.files.map(f=>'<option value="'+safe(f.id)+'" '+(f.id===value?'selected':'')+'>'+safe(f.name)+'</option>').join('')+'</select><small>Upload files in Files & knowledge first.</small></label>';
  if(schema.enum)return '<label>'+labelHtml+'<select class="field-value"'+attr+'>'+schema.enum.map(x=>'<option '+(x===value?'selected':'')+'>'+safe(x)+'</option>').join('')+'</select></label>';
  const numeric=['integer','number'].includes(schema.type);
  const multiline=!numeric&&(/body|content|notes|text|guidance|details|timeline|description|evidence|rationale/.test(path));
  const limits=(schema.minimum!==undefined?' min="'+schema.minimum+'"':'')+(schema.maximum!==undefined?' max="'+schema.maximum+'"':'')+(schema.maxLength?' maxlength="'+schema.maxLength+'"':'');
  return '<label>'+labelHtml+(multiline?'<textarea rows="3" class="field-value"'+attr+limits+'>'+safe(value??'')+'</textarea>':'<input class="field-value"'+attr+' data-kind="'+safe(schema.type)+'" type="'+(numeric?'number':'text')+'"'+(numeric?' step="'+(schema.type==='integer'?'1':'any')+'"':'')+limits+' value="'+safe(value??'')+'">')+'</label>';
}
function pathGet(object,path){return path.split('.').filter(Boolean).reduce((o,k)=>o?.[k],object);}
function pathSet(object,path,value){const keys=path.split('.').filter(Boolean);if(!keys.length)return value;let parent=object;for(const key of keys.slice(0,-1))parent=parent[key];parent[keys.at(-1)]=value;return object;}
function readForm(container,base){
  let result=structuredClone(base);
  container.querySelectorAll('.field-value').forEach(el=>{
    let v=el.type==='checkbox'?el.checked:el.value;
    if(el.dataset.json)v=JSON.parse(v);
    else if(['number','integer'].includes(el.dataset.kind)){if(v==='')throw Error('Fill in every numeric field.');v=Number(v);}
    else if(el.dataset.kind==='cell'&&/^-?(?:0|[1-9]\d*)(?:\.\d+)?$/.test(v))v=Number(v);
    result=pathSet(result,el.dataset.fieldPath,v);
  });
  return result;
}
function schemaAt(schema,path){for(const key of path.split('.').filter(Boolean))schema=schema.type==='array'?schema.items:schema.properties[key];return schema;}

async function openSkill(id,personId='atlas'){
  try{
    [workspace.activeSkill,workspace.files]=await Promise.all([api('/api/skills/'+id),api('/api/files')]);
    workspace.formData=structuredClone(workspace.activeSkill.example);workspace.peoplePicker=personId;
    renderSkillDialog();$('#skill-dialog').showModal();
  }catch(error){notice(error.message,true);}
}
function renderSkillDialog(){
  const s=workspace.activeSkill;
  const people=[ATLAS,...state.company.people.filter(p=>p.available&&p.skills.includes(s.id))];
  $('#skill-dialog').innerHTML='<form id="execute-skill-form"><div class="dialog-heading"><div><span class="eyebrow">'+safe(s.category)+'</span><h2>'+safe(s.title)+'</h2></div><button type="button" data-close="skill-dialog" class="icon-btn" aria-label="Close">×</button></div><p class="muted">'+safe(s.description)+'</p><div class="skill-detail-meta"><span class="tag">'+safe(effectLabel(s.effect))+'</span><select id="skill-person" aria-label="Assign skill to colleague">'+people.map(p=>'<option value="'+safe(p.id)+'" '+(p.id===workspace.peoplePicker?'selected':'')+'>'+safe(p.name)+' · '+safe(p.role)+'</option>').join('')+'</select></div><p class="example-caption">Example inputs are shown to explain the format. Replace them with your own information.</p><div id="skill-fields">'+fieldMarkup(s.input_schema,workspace.formData,'','Inputs')+'</div><details class="skill-instructions"><summary>Skill instructions & supporting files</summary><p><code>skills/'+safe(s.id)+'/SKILL.md</code><br><code>skills/'+safe(s.id)+'/scripts/run.py</code></p><pre>'+safe(s.instructions)+'</pre></details><p class="form-error" id="skill-form-error" role="alert"></p><div class="dialog-actions"><button type="button" data-close="skill-dialog" class="secondary-btn">Cancel</button><button class="primary-btn" id="execute-skill">'+(effectLabel(s.effect)==='Review before action'?'Prepare for review':'Run skill')+'</button></div></form>';
}

function renderActivity(){
  const pending=workspace.runs.filter(r=>r.status==='awaiting_approval').length;
  $('#view-activity').innerHTML=pageHeading('WORK, WITH A RECORD','See what your team has done.','Review proposed actions, open results, and keep track of responsibilities.','<button data-refresh-workspace class="secondary-btn">Refresh</button>')+
    '<div class="activity-metrics"><div><strong>'+workspace.runs.length+'</strong><span>Recorded runs</span></div><div><strong>'+pending+'</strong><span>Awaiting your review</span></div><div><strong>'+workspace.records.filter(r=>r.kind!=='organization-backup').length+'</strong><span>Company records</span></div></div><h2 class="section-title">Skill activity</h2><div class="run-list">'+(workspace.runs.length?workspace.runs.map(r=>'<button class="run-row" data-run="'+r.id+'"><span class="run-symbol">'+icon(r.status==='completed'?'check':'board')+'</span><span class="run-info"><strong>'+safe(workspace.skills.find(s=>s.id===r.skill_id)?.title||title(r.skill_id.replaceAll('-',' ')))+'</strong><small>'+safe(personName(r.person_id))+' · '+dateLabel(r.created_at)+'</small></span>'+pill(r.status)+'<span aria-hidden="true">→</span></button>').join(''):'<div class="panel muted">No runs yet. Open a skill to create your first result.</div>')+'</div><h2 class="section-title">Company register</h2>'+recordRows(workspace.records.filter(r=>r.kind!=='organization-backup'&&r.kind!=='knowledge-save'));
}
function recordRows(records){return records.length?'<div class="record-list">'+records.map(r=>'<article class="record-row"><div><strong>'+safe(r.title)+'</strong><small>'+safe(title(r.kind.replaceAll('-',' ')))+' · '+safe(r.payload.owner||r.payload.manager||'Workspace')+'</small></div><button class="text-link" data-record="'+r.id+'">Open →</button></article>').join('')+'</div>':'<div class="panel muted">Records from skills will appear here.</div>';}
function resultMarkup(value){
  if(value===null||value===undefined)return '<span class="muted">—</span>';
  if(Array.isArray(value)){
    if(!value.length)return '<span class="muted">No items</span>';
    if(value.every(v=>v&&typeof v==='object'&&!Array.isArray(v))){
      const cols=[...new Set(value.flatMap(Object.keys))];
      return '<div class="table-scroll"><table class="result-table"><thead><tr>'+cols.map(k=>'<th>'+safe(title(k))+'</th>').join('')+'</tr></thead><tbody>'+value.slice(0,100).map(row=>'<tr>'+cols.map(k=>'<td>'+resultMarkup(row[k])+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>'+(value.length>100?'<p class="muted">Showing 100 of '+value.length+' items. Full data is available through the API.</p>':'');
    }
    return '<ul>'+value.map(x=>'<li>'+resultMarkup(x)+'</li>').join('')+'</ul>';
  }
  if(typeof value==='object')return '<dl class="result-data">'+Object.entries(value).filter(([k])=>!['artifacts','summary'].includes(k)).map(([k,v])=>'<div><dt>'+safe(title(k))+'</dt><dd>'+resultMarkup(v)+'</dd></div>').join('')+'</dl>';
  return '<span>'+safe(value)+'</span>';
}
async function openRun(id){
  try{
    const r=await api('/api/runs/'+id);const s=workspace.skills.find(s=>s.id===r.skill_id);
    $('#run-dialog').innerHTML='<div class="dialog-heading"><div><span class="eyebrow">ACTIVITY DETAILS</span><h2>'+safe(s?.title||title(r.skill_id.replaceAll('-',' ')))+'</h2></div><button data-close="run-dialog" class="icon-btn" aria-label="Close">×</button></div><div class="run-meta">'+pill(r.status)+'<span>'+safe(personName(r.person_id))+' · '+dateLabel(r.created_at)+'</span></div>'+(r.status==='awaiting_approval'?'<div class="review-banner"><strong>Review this exact action</strong><p>'+(s?.effect==='reviewed_write'?'This will create a new reviewed local file and leave the original unchanged.':'This will act on a connected service. Check the recipient, destination and full content below.')+'</p></div>':'')+'<h3>Inputs</h3>'+resultMarkup(r.input)+(r.output?'<h3>Result</h3><p>'+safe(r.output.summary||r.output.error||'')+'</p>'+(r.output.artifacts||[]).map(fileLink).join('')+resultMarkup(r.output):'')+'<details class="raw-result"><summary>Full run record</summary><pre>'+safe(JSON.stringify(r,null,2))+'</pre></details><p class="form-error" id="run-error" role="alert"></p><div class="dialog-actions">'+(r.status==='awaiting_approval'?'<button class="secondary-btn" data-run-decision="reject" data-id="'+r.id+'">Cancel action</button><button class="primary-btn" data-run-decision="approve" data-id="'+r.id+'">Approve & execute</button>':'<button class="primary-btn" data-close="run-dialog">Done</button>')+'</div>';
    if(!$('#run-dialog').open)$('#run-dialog').showModal();
  }catch(error){notice(error.message,true);}
}
function renderFiles(){
  $('#view-files').innerHTML=pageHeading('A HOME FOR YOUR WORK','From a file to a finished result.','Upload source files, download completed work, and find shared company knowledge.','<label class="primary-btn upload-button">'+icon('plus')+' Upload files<input id="upload-files" type="file" multiple accept=".csv,.xlsx,.docx,.pptx,.pdf,.txt,.md,.json,.eml,.ics" hidden></label>')+
    '<p class="hint">Files stay in this workspace. Supports Excel, Word, PowerPoint, PDF, CSV, text, email and calendar files. Up to 15 MB each.</p><div class="file-list">'+(workspace.files.length?workspace.files.map(f=>'<article class="file-row"><span class="file-type">'+safe(f.name.split('.').at(-1).toUpperCase())+'</span><div><strong>'+safe(f.name)+'</strong><small>'+Math.max(1,Math.round(f.size/1024))+' KB · '+dateLabel(f.created_at)+'</small></div>'+fileLink(f)+'</article>').join(''):'<div class="empty-state"><h2>Your work will live here</h2><p>Upload a source file or run a skill to create a new one.</p><button class="secondary-btn" data-view="skills">Explore skills</button></div>')+'</div><div class="section-heading"><h2 class="section-title">Company knowledge</h2><button class="text-link" data-skill="knowledge-save">＋ Add a note</button></div><input class="search-input" id="knowledge-query" placeholder="Search source notes…" aria-label="Search knowledge"><div id="knowledge-results">'+recordRows(workspace.records.filter(r=>r.kind==='knowledge-save'))+'</div>';
}
function renderConnections(c){
  const google=c.google;
  $('#view-connections').innerHTML=pageHeading('YOUR TOOLS, TOGETHER','Connect the places you already work.','Start with local files. Add Google Workspace, then bring in more services through MCP.','<button data-refresh-workspace class="secondary-btn">Refresh status</button>')+
    '<section class="connection-feature"><div class="google-mark" aria-hidden="true">G</div><div><span class="eyebrow">FIRST ACCOUNT INTEGRATION</span><h2>Google Workspace</h2><p>Gmail · Drive · Calendar · Sheets · Docs · Slides</p><span class="tag '+(google.status==='credentials_saved'?'ok':'warn')+'">'+safe(title(google.status))+'</span><p class="hint">'+safe(google.message)+'</p>'+(google.services.length?'<p>Authorized services: '+safe(google.services.join(', '))+'</p>':'')+'</div></section><details class="connection-setup" '+(google.status!=='credentials_saved'?'open':'')+'><summary>Connect your Google account</summary><ol><li>In Google Cloud, enable the APIs you want to use and configure the OAuth consent screen.</li><li>Create a <strong>Desktop app</strong> OAuth client. Save its JSON file privately on this computer.</li><li>From the project folder, run the command below. Google will open its own sign-in and consent page.</li></ol><pre>python scripts/google_connect.py --credentials "path/to/client-secret.json" --services drive sheets docs slides gmail calendar</pre><p>Choose only the services you need. Refresh this page after connecting. Tokens stay in the server’s private data folder. External writes wait for review in Activity. Demo email and invite delivery is restricted to <code>amonsk007@gmail.com</code>.</p><a href="https://developers.google.com/workspace/drive/api/quickstart/python" target="_blank" rel="noopener">Google’s official setup guide ↗</a></details><section class="panel settings-section"><div class="panel-heading"><h3>Telegram boss updates</h3><span class="tag '+(c.telegram?.status==='configured'?'ok':'warn')+'">'+safe(title(c.telegram?.status||'not_connected'))+'</span></div><p class="hint">'+safe(c.telegram?.message||'Add bot credentials to .env.')+'</p></section><div class="section-heading"><h2 class="section-title">MCP connections</h2><span class="tag">'+c.mcp.length+' configurable connections</span></div><p class="hint">Configure a trusted server in <code>config/mcp-servers.json</code>, enable it, and list the tools it may use. A template is not an active account connection.</p><div class="connection-grid">'+c.mcp.map(s=>'<article class="connection-card"><div class="connector-icon">'+safe(s.name[0])+'</div><div><h3>'+safe(s.name)+'</h3><small>'+safe(s.transport==='stdio'?'Local process':'Remote MCP')+'</small></div><span class="tag '+(s.enabled?'ok':'')+'">'+(s.enabled?'Configured':'Not connected')+'</span>'+(s.enabled?'<button class="text-link" data-discover="'+safe(s.id)+'">Discover tools →</button>':'<small class="connection-footnote">Server URL, credentials and tool allowlist required</small>')+'</article>').join('')+'</div><div id="discovered-tools"></div>';
}

async function editRecord(id){
  const record=workspace.records.find(r=>r.id===id);
  if(!record)return;
  try{
    const s=await api('/api/skills/'+record.kind);
    workspace.recordEditing={record,schema:s.input_schema,data:record.payload};
    $('#record-dialog').innerHTML='<form id="record-edit-form"><div class="dialog-heading"><h2>'+safe(record.title)+'</h2><button type="button" data-close="record-dialog" class="icon-btn">×</button></div>'+fieldMarkup(s.input_schema,record.payload,'','Record')+'<p class="form-error" id="record-error"></p><div class="dialog-actions"><button class="primary-btn">Save record</button></div></form>';
    $('#record-dialog').showModal();
  }catch(error){notice(error.message,true);}
}

document.addEventListener('click',async event=>{
  const button=event.target.closest('button,a');if(!button)return;
  if(button.dataset.skill){openSkill(button.dataset.skill,button.dataset.person||'atlas');return;}
  if(button.dataset.run){openRun(button.dataset.run);return;}
  if(button.hasAttribute('data-refresh-workspace')){renderWorkspaceView(state.view);return;}
  if(button.dataset.record){editRecord(button.dataset.record);return;}
  if(button.dataset.addRow!==undefined||button.dataset.removeRow!==undefined){
    try{
      const isRecord=!!button.closest('#record-dialog');
      let base=isRecord?workspace.recordEditing.data:workspace.formData;
      const schema=isRecord?workspace.recordEditing.schema:workspace.activeSkill.input_schema;
      base=readForm(isRecord?$('#record-dialog'):$('#skill-fields'),base);
      const path=button.dataset.addRow??button.dataset.removeRow;
      const list=pathGet(base,path);const itemSchema=schemaAt(schema,path);
      if(button.dataset.addRow!==undefined){if(list.length>=(itemSchema.maxItems||500))throw Error('The item limit has been reached.');list.push(defaultValue(itemSchema.items));}
      else list.splice(Number(button.dataset.rowIndex),1);
      if(isRecord){workspace.recordEditing.data=base;const record=workspace.recordEditing.record;record.payload=base;editRecord(record.id);}
      else{workspace.formData=base;workspace.peoplePicker=$('#skill-person').value;renderSkillDialog();}
    }catch(error){notice(error.message,true);}return;
  }
  if(button.dataset.runDecision){
    button.disabled=true;
    try{await api('/api/runs/'+button.dataset.id+'/'+button.dataset.runDecision,{});await openRun(button.dataset.id);if(state.view==='activity')renderWorkspaceView('activity');}
    catch(error){$('#run-error').textContent=error.message;button.disabled=false;}return;
  }
  if(button.dataset.discover){
    button.disabled=true;button.textContent='Discovering…';
    try{const result=await api('/api/mcp/discover',{server_id:button.dataset.discover});$('#discovered-tools').innerHTML='<div class="panel discovered"><h3>Available tools</h3>'+result.tools.map(t=>'<div class="tool-discovery"><strong>'+safe(t.name)+'</strong><p>'+safe(t.description||'')+'</p><span class="tag">'+(result.allowed_tools.includes(t.name)?'Allowlisted':'Not allowlisted')+'</span></div>').join('')+'<button class="primary-btn" data-skill="mcp-tool">Prepare a tool call</button></div>';}
    catch(error){notice(error.message,true);}finally{button.disabled=false;button.textContent='Discover tools →';}return;
  }
  if(button.id==='apply-company-template'){
    const template=$('#company-template').value;
    button.disabled=true;
    try{state.company=await api('/api/company/template',{template});newConversation();renderShell();notice('Company template applied. The previous organization is saved in the local register.');}
    catch(error){notice(error.message,true);}finally{button.disabled=false;}
  }
});
document.addEventListener('submit',async event=>{
  if(event.target.id==='execute-skill-form'){
    event.preventDefault();const button=$('#execute-skill');button.disabled=true;button.textContent='Working…';
    try{const inputs=readForm($('#skill-fields'),workspace.formData);const r=await api('/api/skills/'+workspace.activeSkill.id+'/run',{inputs,person_id:$('#skill-person').value,idempotency_key:crypto.randomUUID()});$('#skill-dialog').close();await openRun(r.id);}
    catch(error){$('#skill-form-error').textContent=error.message;button.disabled=false;button.textContent=effectLabel(workspace.activeSkill.effect)==='Review before action'?'Prepare for review':'Run skill';}
  }
  if(event.target.id==='record-edit-form'){
    event.preventDefault();try{const p=workspace.recordEditing;await api('/api/records/'+p.record.id,readForm($('#record-dialog'),p.data));$('#record-dialog').close();renderWorkspaceView(state.view);notice('Record updated.');}catch(error){$('#record-error').textContent=error.message;}
  }
  if(event.target.id==='company-name-form'){
    event.preventDefault();try{state.company=await api('/api/company',{...state.company,company:$('#company-name').value.trim()});renderShell();notice('Company name updated.');}catch(error){notice(error.message,true);}
  }
});
document.addEventListener('input',event=>{
  if(event.target.id==='skill-search'){workspace.query=event.target.value;const pos=event.target.selectionStart;renderSkills();$('#skill-search').focus();if(pos!==null)$('#skill-search').setSelectionRange?.(pos,pos);}
  if(event.target.id==='knowledge-query')$('#knowledge-results').innerHTML=recordRows(workspace.records.filter(r=>r.kind==='knowledge-save'&&(r.title+JSON.stringify(r.payload)).toLowerCase().includes(event.target.value.toLowerCase())));
});
document.addEventListener('change',async event=>{
  if(event.target.id==='skill-category'){workspace.category=event.target.value;renderSkills();}
  if(event.target.id==='upload-files'){
    try{for(const file of event.target.files){if(file.size>15000000)throw Error(file.name+' exceeds the 15 MB limit.');const content=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file);});await api('/api/files',{name:file.name,content_base64:content});}notice('Files uploaded. They are ready for your team’s skills.');renderWorkspaceView('files');}catch(error){notice(error.message,true);}
  }
});

// Extend existing views while preserving the tourism workflow and saved conversations.
const originalWelcome=welcome;
welcome=function(){
  if(state.company?.template==='tourism')return originalWelcome();
  return '<div class="welcome company-welcome"><div class="welcome-emblem">'+icon('sparkle')+'</div><div class="eyebrow">A LITTLE LESS BUSYWORK. A LOT MORE POSSIBILITY.</div><h1>What can we take care of?</h1><p>Your people, your tools, one thoughtful workspace.<br>Bring a question. Leave with something done.</p><div class="suggestion-grid">'+[['spreadsheet-create','board','Make sense of the numbers','Build an Excel workbook'],['presentation-create','file','Give your next idea a voice','Create a PowerPoint deck'],['project-plan','people','Turn a plan into progress','Organize a project & its owners']].map(([id,i,title,sub])=>'<button class="suggestion" data-skill="'+id+'">'+icon(i)+'<strong>'+title+'</strong><small>'+sub+'</small></button>').join('')+'</div><div class="welcome-team"><div class="stacked-faces">'+state.company.people.slice(0,5).map(p=>'<button data-talk="'+p.id+'" aria-label="Talk to '+safe(p.name)+'">'+face(p)+'</button>').join('')+'</div><span>'+state.company.people.length+' AI colleagues, ready to help</span><button class="text-link" data-view="organization">Explore the org chart →</button></div><div class="welcome-bottom"><button class="text-link" data-view="skills">Explore the skills library</button><span>·</span><button class="text-link" data-view="connections">Connect Google Workspace</button></div></div>';
};
const originalCompanion=renderCompanion;
renderCompanion=function(){
  originalCompanion();
  if(!state.case){
    const footer=$('.rail-footer');if(footer)footer.innerHTML='Fictional AI colleagues · '+(state.config.ai_configured?'AI tools connected':'Local tools ready');
    const steps=$('.rail-steps');if(steps)steps.innerHTML=['Understand your request','Choose the right skill','Create & review','Keep a clear record'].map(x=>'<div class="rail-step">'+x+'</div>').join('');
    const p=person(state.personId);
    if(p.id!=='atlas')$('#companion-panel').insertAdjacentHTML('beforeend','<button class="secondary-btn rail-skill-link" data-person-skills="'+safe(p.id)+'">View my skills</button>');
  }
};
document.addEventListener('click',async event=>{const b=event.target.closest('[data-person-skills]');if(b){await loadCatalog();const p=person(b.dataset.personSkills);$('#run-dialog').innerHTML='<div class="dialog-heading"><h2>'+safe(p.name)+'’s skills</h2><button data-close="run-dialog" class="icon-btn">×</button></div>'+workspace.skills.filter(s=>p.skills.includes(s.id)).map(s=>'<button class="run-row" data-skill="'+s.id+'" data-person="'+p.id+'"><strong>'+safe(s.title)+'</strong><span>→</span></button>').join('');$('#run-dialog').showModal();}});
const originalSettings=renderSettings;
renderSettings=function(){
  originalSettings();
  $('#view-settings').insertAdjacentHTML('afterbegin','<section class="panel settings-section organization-settings"><span class="eyebrow">YOUR COMPANY</span><h2>Make this workspace yours.</h2><form id="company-name-form"><label>Company name<input id="company-name" value="'+safe(state.company.company)+'" maxlength="150" required></label><button class="secondary-btn">Save name</button></form><div class="template-controls"><label>Organization template<select id="company-template"><option value="general" '+(state.company.template==='general'?'selected':'')+'>General company</option><option value="tourism" '+(state.company.template==='tourism'?'selected':'')+'>Chengdu tourism</option></select></label><button class="secondary-btn" id="apply-company-template">Apply template</button></div><p class="hint">Applying a template replaces the current roster and saves a backup in the local register. Conversations and files remain available.</p><p class="hint">Skill actions use the review rules shown on each skill. The controls below apply to tourism proposals.</p></section>');
};
const originalStaffDialog=staffDialog;
staffDialog=function(p=null){
  originalStaffDialog(p);
  const grid=$('#staff-form .form-grid');
  $('#staff-extras')?.remove();
  const presets=['director','sales_manager','sales_exec','account_exec','product_manager','itinerary_specialist','supplier_manager','ops_manager','transport_coordinator','finance_manager'];
  grid.insertAdjacentHTML('beforeend','<div id="staff-extras" class="wide"><label>Portrait preset<select id="staff-portrait">'+presets.map(id=>'<option value="'+id+'" '+((p?.portrait||p?.id)===id?'selected':'')+'>'+safe(title(id))+'</option>').join('')+'</select></label><button type="button" class="text-link" id="pick-staff-skills">Choose from the skills library</button><div id="staff-skill-picker"></div></div>');
};
// Existing saveStaff reads the extra fields through this serializer hook.
document.addEventListener('click',async event=>{
  if(event.target.id==='pick-staff-skills'){
    await loadCatalog();const current=$('#staff-skills').value.split(',').map(x=>x.trim());
    $('#staff-skill-picker').innerHTML='<div class="skill-checkboxes">'+workspace.skills.map(s=>'<label><input type="checkbox" data-staff-skill="'+s.id+'" '+(current.includes(s.id)?'checked':'')+'>'+safe(s.title)+'</label>').join('')+'</div>';
  }
});
document.addEventListener('change',event=>{if(event.target.dataset.staffSkill){const selected=new Set($('#staff-skills').value.split(',').map(s=>s.trim()).filter(Boolean));event.target.checked?selected.add(event.target.dataset.staffSkill):selected.delete(event.target.dataset.staffSkill);$('#staff-skills').value=[...selected].join(', ');}});
loadCatalog().catch(()=>{});
