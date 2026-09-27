const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const safe = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const money = value => "CNY " + Number(value || 0).toLocaleString("en-SG");
const title = value => String(value || "").replaceAll("_"," ").replace(/\b\w/g,c=>c.toUpperCase());
const ATLAS = {id:"atlas",name:"Atlas",role:"Your company assistant",voice:"en-US",avatar_color:"#668d7b",skills:["Task understanding","Team coordination","Outcome delivery"]};
const state = {company:null,config:{},settings:{autonomy_mode:"proposal_first"},history:[],conversation:null,events:[],case:null,personId:"atlas",view:"assistant",workTab:"overview",peopleTab:"directory",peopleQuery:"",orgSelectedId:null,orgQuery:"",orgZoom:1,busy:false,pendingMessage:"",reviewAction:null,voiceEnabled:localStorage.getItem("atlasVoice")==="true",network:{reports_to:true,collaborates:true,follows:false}};
const ICONS = {
  chat:'<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z"/>',
  people:'<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 5a3 3 0 0 1 0 6M21 21v-3a6 6 0 0 0-4-5.7"/>',
  board:'<rect x="3" y="4" width="18" height="17" rx="3"/><path d="M3 10h18M10 10v11M7 2v4M17 2v4"/>',
  file:'<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h5"/>',
  settings:'<path d="m9 3-1 3-3 1 1 3-2 2 2 2-1 3 3 1 1 3h6l1-3 3-1-1-3 2-2-2-2 1-3-3-1-1-3z"/><circle cx="12" cy="12" r="3"/>',
  search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 5 5"/>',
  mic:'<rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10v2a7 7 0 0 0 14 0v-2M12 19v3M8 22h8"/>',
  volume:'<path d="m11 5-6 4H2v6h3l6 4zM15 8a6 6 0 0 1 0 8M18 5a10 10 0 0 1 0 14"/>',
  "arrow-up":'<path d="M12 19V5m-6 6 6-6 6 6"/>',
  arrow:'<path d="M4 12h16m-6-6 6 6-6 6"/>',
  sparkle:'<path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5zM20 2v4M18 4h4"/>',
  globe:'<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18M5 6h14M5 18h14"/>',
  check:'<path d="m5 12 4 4L19 6"/>',
  play:'<path d="m8 4 12 8-12 8z"/>',
  copy:'<rect x="8" y="8" width="12" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
  menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
  shield:'<path d="m12 2 9 4v6c0 5-9 10-9 10S3 17 3 12V6z"/><path d="m8 12 3 3 5-6"/>',
  edit:'<path d="m15 4 5 5M4 20l5-1L21 7l-5-5L4 14z"/>',
  flag:'<path d="M5 22V3m0 1c5-5 9 5 15 0v11c-6 5-10-5-15 0"/>',
  download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',
  mail:'<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 6 9 7 9-7"/>'
};
const icon = name => '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">'+(ICONS[name]||ICONS.sparkle)+'</svg>';
const face = (person,size="small") => window.AtlasAvatar ? AtlasAvatar.markup(person,{size}) : '<span class="account-avatar">'+safe(person.name?.[0]||"A")+'</span>';
const person = id => id==="atlas" ? ATLAS : (state.company?.people||[]).find(p=>p.id===id) || (state.case?.people_snapshot||[]).find(p=>p.id===id) || ATLAS;
const personName = id => person(id).name;
const pill = status => '<span class="pill '+(/ok|approved|complete|ready|executed|resolved/.test(status)?"ok":/block|error|escalat/.test(status)?"bad":"warn")+'">'+safe(title(status||"Pending"))+'</span>';
function formatText(text){
  const inline=value=>safe(value).replace(/\[([^\]]{1,120})\]\((https?:\/\/[^\s)]+|\/api\/files\/file_[A-Za-z0-9_-]+\/download)\)/g,'<a href="$2" target="_blank" rel="noopener noreferrer">$1 ↗</a>').replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>");
  const lines=String(text??"").split(/\r?\n/),out=[];
  const cells=line=>line.trim().replace(/^\||\|$/g,"").split("|").map(cell=>inline(cell.trim()));
  const tableAt=i=>i+1<lines.length&&lines[i].includes("|")&&/^\s*\|?[\s:|-]+\|?\s*$/.test(lines[i+1])&&lines[i+1].includes("-");
  for(let i=0;i<lines.length;){
    if(!lines[i].trim()){i++;continue;}
    if(tableAt(i)){
      const head=cells(lines[i]);i+=2;const rows=[];
      while(i<lines.length&&lines[i].trim().startsWith("|")){rows.push(cells(lines[i++]));}
      out.push('<div class="message-table-wrap"><table><thead><tr>'+head.map(cell=>'<th>'+cell+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(cell=>'<td>'+cell+'</td>').join('')+'</tr>').join('')+'</tbody></table></div>');continue;
    }
    if(/^\s*[-*] /.test(lines[i])){
      const items=[];while(i<lines.length&&/^\s*[-*] /.test(lines[i]))items.push('<li>'+inline(lines[i++].replace(/^\s*[-*] /,""))+'</li>');
      out.push('<ul>'+items.join('')+'</ul>');continue;
    }
    const paragraph=[];while(i<lines.length&&lines[i].trim()&&!tableAt(i)&&!/^\s*[-*] /.test(lines[i]))paragraph.push(inline(lines[i++]));
    out.push('<p>'+paragraph.join('<br>')+'</p>');
  }
  return out.join('');
}
const views = {assistant:"Assistant",people:"Your people",organization:"Org chart",work:"Tourism workflow",reports:"Tourism reports",settings:"Workspace settings",skills:"Skills library",activity:"Activity & approvals",files:"Files & knowledge",connections:"Connections"};
function hydrateIcons(){ $$("[data-icon]").forEach(el=>el.innerHTML=icon(el.dataset.icon)); }
async function api(path,body){
  const response=await fetch(path,body===undefined?{}:{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
  const data=await response.json();
  if(!response.ok)throw new Error(data.error||"The request could not be completed.");
  return data;
}
function notice(message,error=false){const node=$("#notice");node.textContent=message||"";node.classList.toggle("hidden",!message);node.classList.toggle("error",error);}
function setView(view){
  if(!views[view])view="assistant";
  state.view=view;history.replaceState(null,"","#"+view);
  $$(".view").forEach(node=>node.classList.toggle("hidden",node.id!=="view-"+view));
  $$("[data-view]").forEach(node=>node.classList.toggle("active",node.dataset.view===view));
  $("#page-title").textContent=views[view];$("#sidebar").classList.remove("open");
  renderView();renderCompanion();hydrateIcons();
  document.body.dataset.view=view;
}
function renderView(){
  if(state.view==="assistant")renderConversation();
  if(state.view==="people")renderPeople();
  if(state.view==="organization")renderOrganization();
  if(state.view==="work")renderWork();
  if(state.view==="reports")renderReports();
  if(state.view==="settings")renderSettings();
  if(window.renderWorkspaceView)renderWorkspaceView(state.view);
  if(state.view==="organization"||(state.view==="people"&&state.peopleTab==="network"))requestAnimationFrame(()=>{
    const canvas=document.querySelector("#view-"+state.view+" .network-canvas");
    if(canvas){const focusY=Number(canvas.dataset.focusY||0);canvas.scrollTop=Math.max(0,focusY-canvas.clientHeight/2);}
  });
}
function renderShell(){
  $("#staff-count").textContent=state.company?.people.length||0;
  $("#company-label").textContent=state.company?.company||"Atlas Company";
  $$('.main-nav [data-view="work"],.main-nav [data-view="reports"]').forEach(n=>n.hidden=state.company?.template!=="tourism");
  $("#connection-chip").innerHTML='<span class="status-dot"></span> '+(state.config.ai_configured?"OpenAI connected":"Local assistant");
  $("#chat-target").innerHTML=[ATLAS,...(state.company?.people||[])].map(p=>'<option value="'+safe(p.id)+'">'+safe(p.name)+(p.id==="atlas"?" · company assistant":"")+'</option>').join("");
  $("#chat-target").value=state.personId;
  const captions={proposal_first:"Proposal first · Review before execution",approval_required:"Approval gates · Plan and delivery",autonomous:"Autonomous · Within your saved rules"};
  $("#autonomy-caption").textContent=captions[state.settings.autonomy_mode]||captions.proposal_first;
  renderHistory();renderView();renderCompanion();hydrateIcons();
}
function renderHistory(){
  const query=$("#history-search").value.toLowerCase().trim();
  const items=state.history.filter(c=>(c.title+" "+c.preview).toLowerCase().includes(query));
  let group="";
  $("#history-list").innerHTML=items.length?items.map(c=>{
    const date=new Date(c.updated_at),today=new Date(),label=date.toDateString()===today.toDateString()?"Today":date.toLocaleDateString(undefined,{month:"short",day:"numeric"});
    const heading=label!==group?'<div class="history-date">'+safe(label)+'</div>':"";group=label;
    return heading+'<button class="history-item '+(c.id===state.conversation?.id?"active":"")+'" data-conversation="'+safe(c.id)+'" title="'+safe(c.title)+'"><strong>'+safe(c.title)+'</strong><small>'+safe(c.person_id&&c.person_id!=="atlas"?personName(c.person_id):c.preview||"Company conversation")+'</small></button>';
  }).join(""):'<p class="sidebar-hint">'+(query?"No matching conversations.":"Your conversations and proposals will appear here.")+'</p>';
}
async function refreshHistory(){state.history=await api("/api/conversations");renderHistory();}
async function refreshEvents(){if(!state.conversation?.id)return;state.events=await api('/api/conversation/'+encodeURIComponent(state.conversation.id)+'/events');if(state.view==='assistant')renderConversation();}
async function openConversation(id){
  try{stopSpeech();state.conversation=await api("/api/conversation/"+encodeURIComponent(id));state.personId=state.conversation.person_id||"atlas";state.case=null;state.events=[];await refreshEvents();
    if(state.conversation.request_id)try{state.case=await api("/api/case/"+encodeURIComponent(state.conversation.request_id));}catch{}
    localStorage.setItem("atlasConversation",id);$("#chat-target").value=state.personId;setView("assistant");renderHistory();scrollChat();
  }catch(error){notice(error.message,true);}
}
function newConversation(){
  if(state.busy)return;stopSpeech();state.conversation=null;state.case=null;state.events=[];state.personId="atlas";localStorage.removeItem("atlasConversation");$("#chat-input").value="";$("#chat-target").value="atlas";notice("");setView("assistant");renderHistory();$("#chat-input").focus();
}
function welcome(){
  const colleagues=(state.company?.people||[]).filter(p=>["sales_manager","product_manager","ops_manager","finance_manager"].includes(p.id));
  return '<div class="welcome"><div class="welcome-emblem">'+icon("sparkle")+'</div><div class="eyebrow">A WHOLE TEAM, ONE CONVERSATION</div><h1>What can we take care of?</h1><p>From the first idea to the final delivery, your company assistant brings the right people together.</p><div class="suggestion-grid">'+[
    ["globe","Plan a group journey","Compare options. Build a complete proposal.","RFQ: 30 travelers for a 3 day Chengdu food, tea and heritage tour from 2026-10-25, budget CNY 200000.","delegate"],
    ["people","Meet your company","Find the right person for the job.","Who is on my team and how do they work together?","ask"],
    ["shield","Choose how we work","Set approvals and autonomy.","settings","settings"]
  ].map(x=>'<button class="suggestion" data-prompt="'+safe(x[3])+'" data-intent="'+x[4]+'">'+icon(x[0])+'<strong>'+x[1]+'</strong><small>'+x[2]+'</small></button>').join("")+'</div><div class="welcome-team"><div class="stacked-faces">'+colleagues.map(p=>'<button data-talk="'+safe(p.id)+'" title="'+safe(p.name)+'">'+face(p)+'</button>').join("")+'</div><span>'+(state.company?.people.length||10)+' colleagues, ready to help</span><button class="text-link" data-view="people">Meet the team →</button></div></div>';
}
function renderConversation(){
  const messages=state.conversation?.messages||[];
  let content=messages.length?messages.map((m,index)=>{
    const agent=person(m.person_id||"atlas");
    return '<article class="message '+safe(m.role)+'">'+(m.role==="user"?"":'<button class="avatar-button" data-talk="'+safe(agent.id)+'" title="'+safe(agent.name)+'">'+face(agent)+'</button>')+'<div class="message-body"><div class="message-heading"><strong>'+safe(m.name||agent.name)+'</strong><span>'+safe(m.mode==="openai"?"OpenAI":m.mode==="error"?"Needs attention":"Company assistant")+'</span></div><div class="message-text">'+formatText(m.content)+'</div>'+(m.role==="assistant"?'<div class="message-actions"><button class="icon-btn" data-speak-index="'+index+'" title="Read aloud" aria-label="Read aloud">'+icon("volume")+'</button><button class="icon-btn" data-copy-index="'+index+'" title="Copy answer" aria-label="Copy answer">'+icon("copy")+'</button></div>':"")+'</div></article>';
  }).join(""):welcome();
  if(state.pendingMessage)content+='<article class="message user"><div class="message-body"><div class="message-text">'+formatText(state.pendingMessage)+'</div></div></article>';
  if(state.busy)content+='<article class="message"><button class="avatar-button">'+face(person(state.personId))+'</button><div class="message-body"><div class="message-heading"><strong>'+safe(personName(state.personId))+'</strong></div><div class="thinking"><i></i><i></i><i></i><span>Working with your company…</span></div></div></article>';
  if(state.events.length)content+='<section class="agent-progress" aria-label="Agent activity"><div class="agent-progress-title">Agent activity <span>'+state.events.length+' updates</span></div>'+state.events.slice(-10).map(e=>'<div class="agent-progress-row"><span class="agent-progress-dot '+safe(e.stage)+'"></span><strong>'+safe(personName(e.person_id))+'</strong><span>'+safe(e.detail)+'</span><small>'+safe(new Date(e.created_at).toLocaleTimeString())+'</small></div>').join('')+'</section>';
  if(state.case&&!state.busy)content+=caseSummary();
  if(state.conversation?.proposal&&!state.busy)content+=proposalCard();
  $("#conversation-content").innerHTML=content;
  $("#send-message").disabled=state.busy;$("#chat-input").disabled=state.busy;
}
function caseSummary(){
  const c=state.case,q=c.selected_option||c.comparison?.data?.recommended,tasks=c.workload?.data?.tasks||[],done=Object.keys(c.execution?.data?.completed||{}).length;
  return '<div class="case-card"><div class="case-card-heading">'+icon("board")+'<strong>Your company work plan</strong>'+pill(c.outcome?.data?.decision||"planning")+'</div><div class="metric-grid"><div class="metric"><strong>'+money(q?.quote_cny)+'</strong><small>Indicative group quote</small></div><div class="metric"><strong>'+tasks.length+' tasks</strong><small>'+done+' completed</small></div><div class="metric"><strong>'+safe(c.inquiry?.data?.duration_days||"—")+' days</strong><small>'+safe(c.inquiry?.data?.group_size||"—")+' travelers</small></div></div><div class="card-actions"><button class="secondary-btn" data-work="options">'+icon("globe")+' Compare options</button><button class="secondary-btn" data-work="tasks">'+icon("board")+' View work plan</button><button class="secondary-btn" data-view="reports">'+icon("file")+' Documents</button></div>'+(c.assumptions?.length?'<details class="hint" style="margin-top:12px;font-size:10px"><summary>Review planning assumptions</summary><p>'+c.assumptions.map(safe).join("<br>")+'</p></details>':"")+'</div>';
}
function proposalCard(){
  const p=state.conversation.proposal,blocked=["blocked","escalated"].includes(p.status),comments=p.comments||[],manager=typeof p.manager==="object"?(p.manager?.name||p.manager?.id):personName(p.manager);
  let actions="";
  if(["pending_review","proposed","pending_approval","awaiting_approval"].includes(p.status))actions+='<button class="primary-btn" data-review="approve">'+icon("check")+' Approve & execute</button><button class="secondary-btn" data-review="request_changes">Return with comments</button>';
  if(["changes_requested","revision_requested","resolved","ready_to_resubmit","draft"].includes(p.status))actions+='<button class="primary-btn" data-review="resubmit">Submit revised proposal</button><button class="secondary-btn" id="revise-in-chat">Revise in chat</button>';
  if(blocked)actions+='<button class="primary-btn" data-review="resolve">Resolve with guidance</button>';
  if(["approved","completed"].includes(p.status))actions+='<button class="secondary-btn" data-review="request_changes">Request a revision</button>';
  if(!blocked)actions+='<button class="secondary-btn" data-review="escalate">'+icon("flag")+' Ask manager</button>';
  if(p.delivery?.status==="awaiting_approval")actions+='<button class="primary-btn" data-review="approve_email">'+icon("mail")+' Approve email delivery</button>';
  const issues=(p.issues||[]).map(x=>typeof x==="string"?x:x.message||x.reason||JSON.stringify(x));
  return '<div class="proposal-card"><div class="panel-heading"><h3>'+safe(blocked?"Manager attention needed":p.status==="changes_requested"?"Revision requested":"Proposal & decisions")+'</h3>'+pill(p.status)+'</div><p>Revision '+safe(p.revision||1)+' · '+safe(title(p.policy_snapshot?.autonomy_mode||"proposal_first"))+'</p>'+(blocked?'<div class="manager-note">'+icon("flag")+'<div><strong>Escalated to '+safe(manager||"your manager")+'</strong><p>'+safe(p.manager_message||issues.join(" ")||"This plan needs management guidance before it can continue.")+'</p><p>'+safe(p.suggested_resolution||"Provide guidance below so the team can prepare a revised plan.")+'</p></div></div>':"")+issues.map(x=>'<p>'+safe(x)+'</p>').join("")+'<div class="card-actions">'+actions+'</div>'+(comments.length?'<details open><summary>Review comments ('+comments.length+')</summary><ul class="audit">'+comments.map(c=>'<li>'+safe(typeof c==="string"?c:c.comment||c.text||c.message||"")+'</li>').join("")+'</ul></details>':"")+'<details><summary>Decision history</summary><ul class="audit">'+(p.audit||[]).map(a=>'<li>'+safe(title(a.action||a.event||a.status))+(a.comment?': '+safe(a.comment):"")+'</li>').join("")+'</ul></details></div>';
}
function scrollChat(){requestAnimationFrame(()=>{$("#conversation-scroll").scrollTop=$("#conversation-scroll").scrollHeight;});}
async function sendChat(event){
  event?.preventDefault();if(state.busy)return;
  const input=$("#chat-input"),message=input.value.trim();if(!message)return;
  const mode=$("#chat-mode").value;
  const revision=!!state.case&&/^(please\s+)?(revise|change|update|reduce|increase|adjust)\b/i.test(message)&&/\b(budget|cny|days|travelers|travellers|guests|date|tour|itinerary)\b/i.test(message);
  const runWorkflow=state.company?.template==="tourism"&&(mode==="delegate"||(mode==="auto"&&(/\b(rfq|quotation|travelers|travellers|guests|group trip|tour for|plan.*(?:tour|trip|journey))\b/i.test(message)||revision)));
  state.busy=true;state.pendingMessage=message;state.events=[];input.value="";notice("");setView("assistant");scrollChat();
  AtlasAvatar?.setState(state.personId,"thinking");
  let progressTimer;
  try{
    if(!state.conversation){state.conversation=await api('/api/conversations/new',{title:message,person_id:state.personId});localStorage.setItem('atlasConversation',state.conversation.id);renderConversation();}
    progressTimer=setInterval(()=>refreshEvents().catch(()=>{}),1100);
    const result=await api("/api/chat",{message,conversation_id:state.conversation?.id,person_id:state.personId,request_id:state.case?.request?.request_id,run_workflow:runWorkflow});
    state.conversation=result.conversation;state.case=result.case||null;
    if(!state.case&&state.conversation.request_id)try{state.case=await api("/api/case/"+state.conversation.request_id);}catch{}
    localStorage.setItem("atlasConversation",state.conversation.id);await Promise.all([refreshHistory(),refreshEvents()]);
    state.busy=false;state.pendingMessage="";renderConversation();renderCompanion();scrollChat();
    const last=state.conversation.messages.at(-1);
    if(state.voiceEnabled&&last?.role==="assistant"&&last.mode!=="error")speak(last.content,last.person_id||state.personId);
  }catch(error){input.value=message;notice(error.message,true);}
  finally{clearInterval(progressTimer);state.busy=false;state.pendingMessage="";$("#send-message").disabled=false;input.disabled=false;renderConversation();if(!window.speechSynthesis?.speaking)AtlasAvatar?.stop();scrollChat();}
}
function renderCompanion(){
  const p=person(state.personId),c=state.case,assignments=c?.hierarchy?.data?.assignments||{},lead=c?.hierarchy?.data?.task_lead;
  const colleagues=[...new Set([lead,...Object.values(assignments)].filter(Boolean))].slice(0,4);
  $("#companion-panel").innerHTML='<div class="companion-heading">YOUR ASSISTANT <span class="presence"><span class="status-dot"></span> Available</span></div><div class="companion-portrait">'+face(p,"large")+'</div><h2 class="companion-name">'+safe(p.name)+'</h2><p class="companion-role">'+safe(p.role)+'</p><div class="companion-status" id="speech-status"><span class="status-dot"></span> Ready when you are</div><div class="voice-controls"><span>Spoken replies</span><label class="switch-label"><input id="voice-enabled" type="checkbox" '+(state.voiceEnabled?"checked":"")+' aria-label="Enable spoken replies"></label></div><button class="companion-intro" id="hear-intro">'+icon("play")+' Hear my introduction</button><div class="rail-divider"></div><div class="rail-label">'+(c?"WORKING ON THIS REQUEST":"WHAT I CAN HELP WITH")+'</div>'+(colleagues.length?colleagues.map(id=>{const member=person(id);return '<div class="rail-person"><button class="avatar-button" data-talk="'+safe(id)+'">'+face(member)+'</button><div><strong>'+safe(member.name)+'</strong><small>'+safe(member.role)+'</small></div>'+(id===lead?'<span class="tag">Lead</span>':"")+'</div>';}).join(""):'<p class="rail-note">'+(p.id==="atlas"?"Describe what you need. I’ll help your team understand it, compare options, and deliver a clear outcome.":safe(p.agent_instructions||"I can help with "+p.skills.join(", ")+".") )+'</p><div class="skill-tags">'+p.skills.slice(0,4).map(s=>'<span class="skill-tag">'+safe(title(s))+'</span>').join("")+'</div>' )+'<div class="rail-label">FROM REQUEST TO RESULT</div><div class="rail-steps">'+[["inquiry","Understand the request"],["hierarchy","Bring the team together"],["comparison","Compare & propose"],["execution","Execute & report"]].map(([key,label])=>'<div class="rail-step '+(c?.[key]?.status==="ok"?"done":"")+'">'+label+'</div>').join("")+'</div><div class="rail-footer">AI staff avatars · '+(state.config.ai_configured?"OpenAI conversation":"Local demonstration")+'<br>Travel offers in this workspace are sample estimates.</div>';
  if(state.busy)AtlasAvatar?.setState(p.id,"thinking");
}
let speechGeneration=0;
function stopSpeech(){speechGeneration++;window.speechSynthesis?.cancel();AtlasAvatar?.stop();const label=$("#speech-status");if(label)label.innerHTML='<span class="status-dot"></span> Ready when you are';}
function speak(text,id="atlas"){
  if(!("speechSynthesis" in window)){notice("This browser does not support voice playback. The full answer is available in the conversation.",true);return;}
  stopSpeech();const generation=speechGeneration,p=person(id),utterance=new SpeechSynthesisUtterance(String(text).replace(/[*#]/g,"").slice(0,8000));
  utterance.lang=p.voice||"en-US";utterance.rate=.98;
  const voices=window.speechSynthesis.getVoices(),voice=voices.find(v=>v.lang===utterance.lang&&/natural|online|samantha|aria/i.test(v.name))||voices.find(v=>v.lang===utterance.lang);
  if(voice)utterance.voice=voice;
  utterance.onstart=()=>{if(generation!==speechGeneration)return;AtlasAvatar.setState(id,"speaking");const label=$("#speech-status");if(label)label.textContent="Speaking · press the speaker to stop";};
  const finish=()=>{if(generation!==speechGeneration)return;AtlasAvatar.stop();const label=$("#speech-status");if(label)label.innerHTML='<span class="status-dot"></span> Ready when you are';};
  utterance.onend=finish;utterance.onerror=finish;window.speechSynthesis.speak(utterance);
}
function talkTo(id){state.personId=id;$("#chat-target").value=id;setView("assistant");$("#chat-input").placeholder="Ask "+personName(id)+" about this request…";$("#chat-input").focus();}
function pageHeading(eyebrow,heading,detail,action=""){return '<div class="page-heading"><div><span class="eyebrow">'+eyebrow+'</span><h1>'+heading+'</h1><p>'+detail+'</p></div>'+action+'</div>';}
function renderPeople(){
  const people=state.company?.people||[],query=state.peopleQuery.toLowerCase(),filtered=people.filter(p=>(p.name+" "+p.role+" "+p.skills.join(" ")).toLowerCase().includes(query));
  $("#view-people").innerHTML=pageHeading("YOUR ORGANIZATION","Good work starts with the right people.","Each colleague has a clear role, a set of skills, and a place in your company.",'<button class="primary-btn" id="add-staff">＋ Add colleague</button>')+'<div class="filter-row"><div class="segmented"><button data-people-tab="directory" class="'+(state.peopleTab==="directory"?"active":"")+'">People directory</button><button data-people-tab="network" class="'+(state.peopleTab==="network"?"active":"")+'">Relationship map</button></div><input id="people-search" class="search-input" type="search" value="'+safe(state.peopleQuery)+'" placeholder="Find a person or skill…" aria-label="Search staff"></div>'+(state.peopleTab==="network"?networkView():'<div class="people-grid">'+filtered.map(p=>{
    const free=p.capacity_hours-p.assigned_hours,percent=Math.round(p.assigned_hours/p.capacity_hours*100);
    return '<article class="staff-card"><div class="staff-card-top"><button class="avatar-button" data-talk="'+safe(p.id)+'" aria-label="Talk to '+safe(p.name)+'">'+face(p,"medium")+'</button><div><h3>'+safe(p.name)+'</h3><p class="staff-role">'+safe(p.role)+'</p><span class="tag '+(p.available?"ok":"warn")+'">'+(p.available?"Available":"Away")+'</span></div><button class="icon-btn" data-edit="'+safe(p.id)+'" aria-label="Edit '+safe(p.name)+'">'+icon("edit")+'</button></div><div class="staff-meta"><span>Workload</span><span>'+p.assigned_hours+' / '+p.capacity_hours+' hours</span></div><div class="capacity-track"><span style="width:'+percent+'%"></span></div><div class="skill-tags">'+p.skills.map(s=>'<span class="skill-tag">'+safe(title(s))+'</span>').join("")+'</div><div class="staff-card-footer"><small>Reports to '+safe(p.reports_to?personName(p.reports_to):"Company board")+'<br>'+free+' hours available</small><button class="text-link" data-talk="'+safe(p.id)+'">Talk to '+safe(p.name.split(" ").at(-1))+' →</button></div></article>';
  }).join("")+'</div>');
}
function networkView(){
  const people=state.company.people,byId=Object.fromEntries(people.map(p=>[p.id,p])),children=Object.fromEntries(people.map(p=>[p.id,[]]));
  people.forEach(p=>{if(children[p.reports_to])children[p.reports_to].push(p);});
  const roots=people.filter(p=>!byId[p.reports_to]);
  const pos={},visited=new Set();let leaf=0,maxDepth=0;
  function place(p,depth){
    if(visited.has(p.id))return;visited.add(p.id);maxDepth=Math.max(maxDepth,depth);
    const kids=children[p.id].filter(x=>!visited.has(x.id));
    kids.forEach(x=>place(x,depth+1));
    pos[p.id]={x:145+depth*270,y:kids.length?kids.reduce((n,x)=>n+pos[x.id].y,0)/kids.length:110+leaf++*140};
  }
  roots.forEach(p=>place(p,0));people.filter(p=>!visited.has(p.id)).forEach(p=>place(p,0));
  const width=Math.max(900,290+maxDepth*270),height=Math.max(450,190+leaf*140),zoom=state.orgZoom||1,scope=state.view==="organization"?"organization":"people";
  const selected=byId[state.orgSelectedId]||byId[state.case?.hierarchy?.data?.task_lead]||roots[0]||people[0];
  if(selected)state.orgSelectedId=selected.id;
  const edges=[...people.filter(p=>p.reports_to).map(p=>({from:p.reports_to,to:p.id,kind:"reports_to"})),...people.flatMap(p=>(p.follows||[]).map(to=>({from:p.id,to,kind:"follows"}))),...(state.case?.hierarchy?.data?.relationships||[]).filter(e=>e.kind==="collaborates")];
  const matches=p=>!state.orgQuery||(p.name+" "+p.role+" "+(p.department||"")+" "+p.skills.join(" ")).toLowerCase().includes(state.orgQuery.toLowerCase());
  const direct=selected?children[selected.id]:[];
  const usage=selected?Math.min(100,Math.round(100*selected.assigned_hours/selected.capacity_hours)):0;
  return '<div class="org-overview"><div><strong>'+people.length+'</strong><span>Colleagues</span></div><div><strong>'+(maxDepth+1)+'</strong><span>Reporting levels</span></div><div><strong>'+new Set(people.map(p=>p.department||p.role)).size+'</strong><span>Teams and roles</span></div><div><strong>'+people.filter(p=>!p.available||p.assigned_hours>=p.capacity_hours).length+'</strong><span>At capacity or away</span></div></div>'+
    '<div class="org-toolbar"><div class="network-filters">'+[["reports_to","Reporting lines"],["collaborates","Current task"],["follows","Follows"]].map(([key,label])=>'<button class="network-filter '+(state.network[key]?"active":"")+'" data-network="'+key+'" aria-pressed="'+state.network[key]+'">'+label+'</button>').join("")+'</div><label class="org-search-label">Find colleague<input id="org-search-'+scope+'" data-org-search type="search" value="'+safe(state.orgQuery)+'" placeholder="Name, role or skill"></label><label class="org-zoom-label">Zoom<input id="org-zoom-'+scope+'" data-org-zoom type="range" min="0.7" max="1.4" step="0.1" value="'+zoom+'"></label></div>'+
    '<div class="org-layout"><div class="network-canvas" data-focus-y="'+(selected?pos[selected.id].y*zoom:0)+'" role="region" aria-label="Scrollable company relationship graph"><div class="org-graph-surface" style="width:'+(width*zoom)+'px;height:'+(height*zoom)+'px"><svg width="'+width+'" height="'+height+'" viewBox="0 0 '+width+' '+height+'" style="transform:scale('+zoom+')" aria-label="Company hierarchy graph"><defs><marker id="org-arrow-'+scope+'" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0 10 5 0 10z" fill="#9bb6a1"/></marker></defs>'+edges.filter(e=>state.network[e.kind]&&pos[e.from]&&pos[e.to]).map(e=>'<line class="network-edge '+e.kind+' '+(e.from===selected?.id||e.to===selected?.id?'related':'')+'" x1="'+(pos[e.from].x+96)+'" y1="'+pos[e.from].y+'" x2="'+(pos[e.to].x-96)+'" y2="'+pos[e.to].y+'" '+(e.kind==="reports_to"?'marker-end="url(#org-arrow-'+scope+')"':'')+'/>').join("")+people.map(p=>'<g class="network-node '+(p.id===selected?.id?'selected ':'')+(matches(p)?'':'dimmed')+'"><foreignObject x="'+(pos[p.id].x-96)+'" y="'+(pos[p.id].y-53)+'" width="192" height="106"><button class="org-node-card" data-org-node="'+safe(p.id)+'" aria-label="View '+safe(p.name)+' in the organization">'+face(p,"small")+'<span><strong>'+safe(p.name)+'</strong><small>'+safe(p.role)+'</small><em>'+safe(p.department||"Team")+'</em></span></button></foreignObject></g>').join("")+'</svg></div></div>'+
    (selected?'<aside class="org-inspector"><div class="org-inspector-head">'+face(selected,"medium")+'<div><span class="eyebrow">SELECTED COLLEAGUE</span><h3>'+safe(selected.name)+'</h3><p>'+safe(selected.role)+'</p></div></div><div class="org-inspector-grid"><div><span>Department</span><strong>'+safe(selected.department||"Company")+'</strong></div><div><span>Reports to</span><strong>'+safe(selected.reports_to?personName(selected.reports_to):"Company board")+'</strong></div><div><span>Direct reports</span><strong>'+direct.length+'</strong></div><div><span>Availability</span><strong>'+safe(selected.available?"Available":"Away")+'</strong></div></div><div class="staff-meta"><span>Weekly workload</span><strong>'+selected.assigned_hours+' / '+selected.capacity_hours+' hours</strong></div><div class="capacity-track"><span style="width:'+usage+'%"></span></div><p class="hint">'+safe(Math.max(0,selected.capacity_hours-selected.assigned_hours))+' hours free · '+safe(selected.decision_style||"balanced")+' decision style</p><h4>Assigned skills</h4><div class="skill-tags">'+selected.skills.map(s=>'<span class="skill-tag">'+safe(title(s))+'</span>').join("")+'</div>'+(direct.length?'<h4>Direct reports</h4><div class="org-report-list">'+direct.map(p=>'<button data-org-node="'+safe(p.id)+'">'+face(p,"small")+'<span>'+safe(p.name)+'<small>'+safe(p.role)+'</small></span></button>').join("")+'</div>':"")+'<div class="card-actions"><button class="primary-btn" data-talk="'+safe(selected.id)+'">Talk to '+safe(selected.name)+'</button><button class="secondary-btn" data-edit="'+safe(selected.id)+'">Edit colleague</button></div></aside>':'')+'</div><p class="hint org-legend"><span class="org-line-key reporting"></span> Reporting <span class="org-line-key collaboration"></span> Task collaboration <span class="org-line-key follows"></span> Follows · Select a person to inspect or speak with them.</p>';
}
function renderOrganization(){
  $("#view-organization").innerHTML=pageHeading("COMPANY RELATIONSHIPS","See how your team fits together.","Explore reporting, workload, skills and live task relationships in one place.",'<button class="secondary-btn" data-view="people">Open people directory</button>')+networkView();
}
function noCase(){return '<div class="empty-state">'+icon("board")+'<h2>Your next plan starts with a conversation</h2><p>Give the company a task, or reopen a previous request from the history.</p><button class="primary-btn" data-view="assistant">Go to assistant</button></div>';}
function renderWork(){
  let html=pageHeading("WORK & DECISIONS","A clear path from request to result.","Compare the choices, review the plan, and see who is responsible for every step.");
  if(!state.case){$("#view-work").innerHTML=html+noCase();return;}
  html+='<div class="filter-row"><div class="segmented">'+[["overview","Overview"],["options","Options"],["schedule","Schedule"],["tasks","Tasks"]].map(([key,label])=>'<button data-work="'+key+'" class="'+(state.workTab===key?"active":"")+'">'+label+'</button>').join("")+'</div><span class="tag">'+safe(state.case.request.request_id)+'</span></div>';
  if(state.workTab==="overview")html+=caseSummary()+(state.conversation?.proposal?proposalCard():"")+'<div class="panel" style="margin-top:18px"><h3>Your request</h3><p class="hint">'+safe(state.case.request.message)+'</p><p class="hint">'+safe(state.case.outcome?.data?.management_summary||"The team is preparing the proposal.")+'</p></div>';
  if(state.workTab==="options")html+=optionsView();
  if(state.workTab==="schedule")html+=scheduleView();
  if(state.workTab==="tasks")html+=tasksView();
  $("#view-work").innerHTML=html;
}
function optionsView(){
  const c=state.case,comparison=c.comparison?.data;if(!comparison)return '<div class="panel"><p class="hint">No feasible comparison is available. Check the manager escalation for missing information.</p></div>';
  const options=[comparison.recommended,...(comparison.alternatives||[])].filter(Boolean);
  return '<div class="panel"><div class="panel-heading"><h3>Complete package options</h3><span class="tag">Sample prices</span></div>'+options.map(o=>'<div class="option-card '+(o.id===c.selected_option?.id?"selected":"")+'"><div class="option-top"><h3>'+safe(title(o.id))+' '+(o.id===c.selected_option?.id?'<span class="tag ok">Selected</span>':"")+'</h3><div class="option-price">'+money(o.quote_cny)+'<small>'+money(o.quote_per_person_cny)+' / person</small></div></div><p class="hint" style="margin:8px 0">'+safe((o.included||[]).join(" · "))+'</p><div class="breakdown"><span>Land '+money(o.land_quote_cny)+'</span><span>Flights '+money(o.flight_estimate_cny)+'</span><span>Activities '+money(o.activity_estimate_cny)+'</span><span>Score '+o.score+'</span></div>'+(o.id!==c.selected_option?.id?'<button class="secondary-btn" data-option="'+safe(o.id)+'">Choose this option</button>':"")+'</div>').join("")+(comparison.rejected||[]).map(o=>'<div class="reason">'+safe(title(o.id))+': '+safe(o.reasons.join(", "))+'</div>').join("")+'</div><div class="two-col"><div class="panel"><h3>Flight comparison</h3>'+[c.flights?.data?.recommended,...(c.flights?.data?.alternatives||[])].filter(Boolean).map(f=>'<div class="option-card"><div class="option-top"><h3>'+safe(f.carrier)+'</h3><strong>'+money(f.group_total_cny)+'</strong></div><p class="hint" style="margin:8px 0 0">'+safe(f.origin)+' → '+safe(f.destination)+' · '+f.stops+' stops · '+f.duration_minutes+' min</p></div>').join("")+'</div><div class="panel"><h3>Tour choices</h3>'+(c.tours?.data?.matches||[]).map(t=>'<div class="option-card"><h3>'+safe(t.name)+'</h3><p class="hint">'+money(t.group_total_cny)+' · up to '+t.max_group+' guests</p></div>').join("")+'</div></div>';
}
function scheduleView(){
  const s=state.case.schedule?.data;if(!s)return noCase();
  return '<div class="panel"><div class="panel-heading"><h3>Your day-by-day journey</h3><span class="tag">'+safe(s.travel_days||s.days?.length)+' calendar days</span></div>'+(s.days||[]).map(d=>'<div class="day-card"><h3>Day '+d.day_number+' · '+safe(d.date)+'</h3>'+(d.activities||[]).map(a=>'<div class="slot-row"><span>'+safe(a.slot)+'</span><span>'+safe(a.title)+'</span></div>').join("")+'</div>').join("")+'</div>'+((s.unscheduled||[]).length?'<div class="panel"><h3>Needs scheduling</h3>'+s.unscheduled.map(a=>'<p class="hint">'+safe(a.id)+': '+safe(a.reason)+'</p>').join("")+'</div>':"");
}
const dutySkills={intake:"intake",itinerary:"itinerary",supplier:"supplier",pricing:"pricing",safety:"safety",finance:"financial_approval",response:"client_email",report:"reporting",executive:"executive_approval"};
function tasksView(){
  const c=state.case,tasks=c.workload?.data?.tasks||[],done=c.execution?.data?.completed||{},ready=new Set(c.execution?.data?.ready_tasks||[]),staff=c.people_snapshot||state.company.people;
  const proposal=state.conversation?.proposal;
  const canExecute=!proposal||(["approved","completed"].includes(proposal.status)&&proposal.policy_snapshot?.execute_plan!==false&&!(proposal.issues||[]).length);
  return (!canExecute?'<div class="notice">Execution is paused. Review the proposal, resolve any open issues, and approve the plan before completing tasks.</div>':"")+'<div class="task-grid">'+tasks.map(t=>{
    const p=person(t.owner_id),eligible=staff.filter(x=>x.available&&x.skills.includes(dutySkills[t.duty])&&x.assigned_hours<x.capacity_hours);
    return '<article class="task-card '+(done[t.id]?"done":"")+'"><div class="task-header"><h3>'+safe(t.title)+'</h3>'+pill(done[t.id]?"complete":ready.has(t.id)?"ready":"waiting")+'</div><div class="task-owner"><button class="avatar-button" data-talk="'+safe(p.id)+'">'+face(p)+'</button><span>'+safe(p.name)+'</span></div><div class="task-meta">Due '+safe(t.due_date)+' · '+t.effort_hours+' hours<br>Depends on '+safe(t.depends_on.join(", ")||"no prior work")+(t.gate?'<br>Approval: '+safe(title(t.gate)):"")+'</div><div class="task-actions"><button data-complete="'+safe(t.id)+'" '+(!canExecute||!ready.has(t.id)||done[t.id]?"disabled":"")+'>Mark complete</button><button data-incident="'+safe(t.id)+'">Report issue</button><select data-reassign="'+safe(t.duty)+'" aria-label="Reassign '+safe(t.title)+'"><option value="">Reassign…</option>'+eligible.map(x=>'<option value="'+safe(x.id)+'">'+safe(x.name)+'</option>').join("")+'</select></div></article>';
  }).join("")+'</div>'+(c.execution?.data?.incidents||[]).map(i=>'<div class="notice error">Issue: '+safe(i.reason)+' <button class="secondary-btn" data-resolve="'+safe(i.task_id)+'">Resolve issue</button></div>').join("");
}
function renderReports(){
  let html=pageHeading("DOCUMENTS & DELIVERY","The outcome, ready to share.","Your proposals, management reports, and customer communications in one place.");
  const c=state.case,r=c?.outcome?.data;
  if(r){
    const id=c.request.request_id,draft=r.customer_email_draft;
    html+='<div class="panel"><div class="panel-heading"><h3>Current request</h3>'+pill(c.outcome.status)+'</div><p class="hint">'+safe(r.management_summary)+'</p>'+(c.reports_generated===false?'<p class="hint">Document generation is disabled in workspace settings.</p>':'<div class="download-grid">'+[["decision-brief.docx","Word proposal","DOCX"],["management-deck.pptx","Management deck","PPTX"],["trace.json","Decision record","JSON"]].map(([suffix,label,format])=>'<a class="download-card" href="/download/'+safe(id)+'-'+suffix+'">'+icon("file")+'<span><strong>'+label+'</strong><small>'+format+' · Download</small></span></a>').join("")+'</div>')+'</div>';
    if(draft)html+='<div class="panel"><div class="panel-heading"><h3>Customer email</h3>'+pill(state.conversation?.proposal?.delivery?.status||"draft")+'</div><div class="email-preview">To: '+safe(draft.to||"Recipient to be supplied")+'\nSubject: '+safe(draft.subject)+'\n\n'+safe(draft.body)+'</div></div>';
  }else html+=noCase();
  html+='<div class="panel"><h3>Search saved work</h3><div class="search-row"><input id="case-search" class="search-input" placeholder="Search trips, activities, or requests…"><button class="primary-btn" id="search-cases">Search</button></div><div id="case-search-results"></div></div>';
  $("#view-reports").innerHTML=html;
}
function renderSettings(){
  const s=state.settings;
  $("#view-settings").innerHTML=pageHeading("WORKSPACE SETTINGS","Your company. Your level of control.","Choose how much the team can do on its own, and when it should come back to you.")+
  '<form id="settings-form"><section class="settings-section"><h2>How should the team work?</h2><p>These controls apply to tourism proposals and their SMTP delivery. Each proposal keeps a record of its rules. External write actions through connected accounts or MCP skills always require a separate review in Activity.</p><div class="mode-grid">'+[
    ["proposal_first","file","Proposal first","Prepare a plan, compare options, and wait for your approval to execute."],
    ["approval_required","shield","Approval checkpoints","Approve the plan, then review again before customer email delivery."],
    ["autonomous","sparkle","Autonomous","Execute and deliver within the action permissions and limits you set."]
  ].map(([value,symbol,label,description])=>'<label class="mode-card"><input type="radio" name="autonomy_mode" value="'+value+'" '+(s.autonomy_mode===value?"checked":"")+'>'+icon(symbol)+'<strong>'+label+'</strong><small>'+description+'</small></label>').join("")+'</div></section><section class="settings-section panel"><h2>Action permissions</h2>'+[
    ["execute_plan","Execute the agreed plan","Allow the team to progress tasks after the required approval or under autonomous rules."],
    ["generate_reports","Generate documents","Create the Word proposal and PowerPoint management report."],
    ["send_email","Send customer emails","Allow delivery to the recipients below when SMTP is configured and the plan is eligible."]
  ].map(([key,label,detail])=>'<div class="setting-row"><div><strong>'+label+'</strong><p>'+detail+'</p></div><label class="switch-label"><input type="checkbox" name="'+key+'" '+(s[key]?"checked":"")+' aria-label="'+label+'"></label></div>').join("")+'<div class="form-grid" style="margin-top:20px"><label>Autonomous quotation limit (CNY)<input name="max_auto_quote_cny" type="number" min="1" step="1" value="'+safe(s.max_auto_quote_cny||200000)+'" required></label><label>Allowed email recipients<small>Separate addresses with commas</small><input name="allowed_recipients" type="text" value="'+safe((s.allowed_recipients||[]).join(", "))+'" placeholder="client@example.com"></label></div></section><section class="settings-section panel"><h2>When something cannot proceed</h2><p class="hint">The assistant records the blocker, routes it to the lead’s manager, and suggests a resolution. Use “Resolve with guidance” to provide a decision, then submit the revised proposal. Review comments and decisions stay in the conversation.</p><div class="settings-footer"><small>Current mode: '+safe(title(s.autonomy_mode))+'</small><button class="primary-btn" type="submit">Save workspace controls</button></div></section></form>'+
  '<section class="settings-section panel"><div class="panel-heading"><h3>OpenAI connection</h3><span class="tag '+(state.config.ai_configured?"ok":"warn")+'">'+(state.config.ai_configured?"Key configured":"Key not configured")+'</span></div><p class="hint">Create a new key in the <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener">OpenAI dashboard ↗</a>. If an earlier key was shared in chat, revoke it there first. This local setup form saves your replacement in the server’s ignored <code>.env</code> file beside <code>app.py</code>.</p>'+(state.config.key_source==="environment"?'<p class="hint">A server environment variable currently supplies the key. Update <code>OPENAI_API_KEY</code> in that environment to change it.</p>':'<form id="api-key-form" autocomplete="off" class="api-key-form"><label for="api-key-input">New OpenAI API key</label><div><input id="api-key-input" type="password" name="api_key" required minlength="23" maxlength="303" autocomplete="new-password" placeholder="Paste a newly generated key"><button class="primary-btn" type="submit">Save key</button></div><small>The key is sent only to this local server. It is never shown again or stored in the browser.</small></form>')+'<details class="manual-key-setup"><summary>Prefer to edit the server file yourself?</summary><ol class="setup-steps"><li>Copy <code>.env.example</code> to <code>.env</code> beside <code>app.py</code>.</li><li>Add <code>OPENAI_API_KEY</code> and your new key, then save the file.</li><li>Refresh the connection status below. A restart is not required for the file method.</li></ol><pre class="setup-code">OPENAI_API_KEY=your_new_key_here\nOPENAI_MODEL='+safe(state.config.model||"gpt-6-astra")+'</pre></details><div class="settings-footer"><small>'+(state.config.ai_configured?"OpenAI is configured for staff conversations and assigned skills.":"Local skills and tourism simulations are available while no key is configured.")+'</small><button class="secondary-btn" id="refresh-connection">Refresh status</button></div></section>'+
  '<section class="settings-section panel"><h3>Voice & appearance</h3><div class="setting-row"><div><strong>Read replies aloud</strong><p>Your colleague’s portrait highlights while your browser speaks. You can stop playback at any time.</p></div><label class="switch-label"><input type="checkbox" id="settings-voice" '+(state.voiceEnabled?"checked":"")+' aria-label="Read replies aloud"></label></div><p class="hint">Each colleague’s voice language, avatar accent, and instructions can be changed from the people directory.</p></section>';
}
function staffDialog(p=null){
  $("#staff-modal-title").textContent=p?"Configure "+p.name:"Add a colleague";$("#staff-id").value=p?.id||"";
  for(const [selector,value] of Object.entries({"#staff-name":p?.name||"","#staff-role":p?.role||"","#staff-skills":p?.skills?.join(", ")||"","#staff-capacity":p?.capacity_hours??30,"#staff-assigned":p?.assigned_hours??0,"#staff-color":p?.avatar_color||"#668d7b","#staff-voice":p?.voice||"en-US","#staff-style":p?.decision_style||"balanced","#staff-guidance":p?.agent_instructions||""}))$(selector).value=value;
  $("#staff-available").checked=p?.available??true;
  $("#staff-manager").innerHTML='<option value="">Company board / top-level</option>'+state.company.people.filter(x=>x.id!==p?.id).map(x=>'<option value="'+safe(x.id)+'">'+safe(x.name)+'</option>').join("");
  $("#staff-manager").value=p?(p.reports_to||""):(state.company.people.find(x=>x.reports_to===null)?.id||"");
  $("#staff-follows").innerHTML=state.company.people.filter(x=>x.id!==p?.id).map(x=>'<option value="'+safe(x.id)+'" '+(p?.follows?.includes(x.id)?"selected":"")+'>'+safe(x.name)+'</option>').join("");
  $("#delete-staff").classList.toggle("hidden",!p);$("#staff-error").textContent="";$("#staff-dialog").showModal();
}
async function saveStaff(event){
  event.preventDefault();
  const previous=$("#staff-id").value;
  const p={...(state.company.people.find(x=>x.id===previous)||{}),portrait:$("#staff-portrait")?.value||"director",id:previous||"staff_"+Date.now().toString(36),name:$("#staff-name").value.trim(),role:$("#staff-role").value.trim(),skills:$("#staff-skills").value.split(",").map(x=>x.trim()).filter(Boolean),capacity_hours:Number($("#staff-capacity").value),assigned_hours:Number($("#staff-assigned").value),avatar_color:$("#staff-color").value,voice:$("#staff-voice").value.trim(),decision_style:$("#staff-style").value,agent_instructions:$("#staff-guidance").value.trim(),available:$("#staff-available").checked,reports_to:$("#staff-manager").value||null,follows:[...$("#staff-follows").selectedOptions].map(o=>o.value)};
  try{state.company=await api("/api/company",{...state.company,people:[...state.company.people.filter(x=>x.id!==previous),p]});$("#staff-dialog").close();renderShell();notice("Colleague saved. New requests use the updated organization.");}catch(error){$("#staff-error").textContent=error.message;}
}
async function updateCase(endpoint,body){
  try{state.case=await api(endpoint,{request_id:state.case.request.request_id,...body});if(state.conversation)state.conversation=await api("/api/conversation/"+state.conversation.id);renderView();renderCompanion();notice(endpoint==="/api/option"?"Option updated. The team needs fresh pricing approval.":"Work plan updated.");}catch(error){notice(error.message,true);}
}
function openReview(action){
  state.reviewAction=action;
  const config={request_changes:["Return with comments","Tell the team what to improve. The proposal pauses until a revised plan is submitted.","Send comments"],escalate:["Ask the manager","Describe what cannot proceed. The lead’s manager will receive an issue record in this conversation.","Escalate issue"],resolve:["Resolve with guidance","Record the manager’s decision or the information that removes the blocker. The team will then need to resubmit the plan.","Record resolution"],resubmit:["Submit the revised proposal","Describe how you addressed the comments. Change the option or send an updated task request first if the plan itself needs to change.","Submit for review"]};
  if(config[action]){
    const [heading,description,label]=config[action];$("#review-title").textContent=heading;$("#review-description").textContent=description;$("#review-submit").textContent=label;$("#review-comment").value="";$("#review-error").textContent="";$("#review-dialog").showModal();
  }else runReview(action,"");
}
async function runReview(action,comment){
  try{
    const result=await api("/api/review",{conversation_id:state.conversation.id,action,comment});
    state.conversation=result.conversation;state.case=result.case||state.case;$("#review-dialog").close();renderView();renderCompanion();refreshHistory();notice(action==="request_changes"?"Comments sent. Revise the request or option, then submit it again.":action==="escalate"?"Issue recorded for the responsible manager.":action==="resolve"?"Resolution recorded. Review and resubmit the updated plan.":"Decision recorded.");scrollChat();
  }catch(error){if($("#review-dialog").open)$("#review-error").textContent=error.message;else notice(error.message,true);}
}
async function searchCases(){
  try{const rows=await api("/api/search?q="+encodeURIComponent($("#case-search").value));$("#case-search-results").innerHTML=rows.length?rows.map(r=>'<div class="search-result"><button data-case="'+safe(r.request_id)+'"><strong>'+safe(r.request_id)+'</strong><small>'+safe(r.snippet)+'</small></button></div>').join(""):'<p class="hint" style="margin:14px 0 0">No matching saved work.</p>';}catch(error){notice(error.message,true);}
}
async function saveSettings(event){
  event.preventDefault();const f=new FormData(event.target);
  try{state.settings=await api("/api/settings",{autonomy_mode:f.get("autonomy_mode"),execute_plan:f.has("execute_plan"),generate_reports:f.has("generate_reports"),send_email:f.has("send_email"),allowed_recipients:String(f.get("allowed_recipients")||"").split(",").map(x=>x.trim()).filter(Boolean),max_auto_quote_cny:Number(f.get("max_auto_quote_cny"))});renderShell();notice("Workspace controls saved. New proposals will use these rules.");}catch(error){notice(error.message,true);}
}
let recognition=null;
function dictate(){
  if(recognition){recognition.stop();return;}
  const Recognition=window.SpeechRecognition||window.webkitSpeechRecognition;
  if(!Recognition){notice("Dictation is unavailable in this browser. Type your message or use your device’s keyboard dictation.",true);return;}
  recognition=new Recognition();recognition.lang=person(state.personId).voice||"en-US";recognition.interimResults=false;
  recognition.onstart=()=>{AtlasAvatar.setState(state.personId,"listening");notice("Listening. Review the transcript before sending. Your browser may use its speech service.");};
  recognition.onresult=e=>{$("#chat-input").value=e.results[0][0].transcript;$("#chat-input").focus();};
  recognition.onerror=e=>notice("Dictation stopped: "+e.error+". You can type your message.",true);
  recognition.onend=()=>{recognition=null;AtlasAvatar.stop();};recognition.start();
}
document.addEventListener("click",async event=>{
  const button=event.target.closest("button,a,[data-talk]");if(!button)return;
  if(button.dataset.view){event.preventDefault();setView(button.dataset.view);return;}
  if(button.dataset.conversation){openConversation(button.dataset.conversation);return;}
  if(button.dataset.talk){talkTo(button.dataset.talk);return;}
  if(button.dataset.close){$("#"+button.dataset.close).close();return;}
  if(button.dataset.prompt){if(button.dataset.intent==="settings"){setView("settings");return;}$("#chat-input").value=button.dataset.prompt;$("#chat-mode").value=button.dataset.intent;$("#chat-input").focus();return;}
  if(button.dataset.work){state.workTab=button.dataset.work;setView("work");return;}
  if(button.dataset.peopleTab){state.peopleTab=button.dataset.peopleTab;renderPeople();return;}
  if(button.dataset.orgNode){state.orgSelectedId=button.dataset.orgNode;renderView();return;}
  if(button.dataset.network){state.network[button.dataset.network]=!state.network[button.dataset.network];renderView();return;}
  if(button.dataset.edit){staffDialog(state.company.people.find(p=>p.id===button.dataset.edit));return;}
  if(button.dataset.review){openReview(button.dataset.review);return;}
  if(button.dataset.option){updateCase("/api/option",{option_id:button.dataset.option});return;}
  if(button.dataset.complete){updateCase("/api/event",{task_id:button.dataset.complete,action:"complete"});return;}
  if(button.dataset.incident){if(state.conversation?.proposal){openReview("escalate");}else updateCase("/api/event",{task_id:button.dataset.incident,action:"incident"});return;}
  if(button.dataset.resolve){updateCase("/api/event",{task_id:button.dataset.resolve,action:"resolve_incident"});return;}
  if(button.dataset.speakIndex!==undefined){const m=state.conversation.messages[Number(button.dataset.speakIndex)];speak(m.content,m.person_id||"atlas");return;}
  if(button.dataset.copyIndex!==undefined){try{await navigator.clipboard.writeText(state.conversation.messages[Number(button.dataset.copyIndex)].content);notice("Answer copied.");}catch{notice("Your browser could not copy this answer.",true);}return;}
  if(button.dataset.case){try{state.case=await api("/api/case/"+button.dataset.case);const linked=state.history.find(c=>c.request_id===button.dataset.case);if(linked){await openConversation(linked.id);setView("reports");}else renderReports();}catch(error){notice(error.message,true);}return;}
  if(button.id==="add-staff"){staffDialog();return;}
  if(button.id==="revise-in-chat"){setView("assistant");$("#chat-mode").value="delegate";$("#chat-input").placeholder="Describe the changes, for example: Revise the budget to CNY 180000…";$("#chat-input").focus();return;}
  if(button.id==="search-cases"){searchCases();return;}
  if(button.id==="hear-intro"){const p=person(state.personId);speak(p.id==="atlas"?"Hello, I’m Atlas, your company assistant. Tell me what you need, and I’ll bring the right people together. We can prepare a proposal, compare options, and work through delivery at the level of control you choose.":"Hello, I’m "+p.name+", your "+p.role+". "+(p.agent_instructions||"I’m ready to help with "+p.skills.join(", ")+"."),p.id);return;}
  if(button.id==="refresh-connection"){try{state.config=await api("/api/config");renderShell();notice(state.config.ai_configured?"OpenAI key is configured.":"No key is configured yet. Add it to .env and restart the app.");}catch(error){notice(error.message,true);}return;}
});
document.addEventListener("change",event=>{
  const target=event.target;
  if(target.id==="chat-target"){state.personId=target.value;stopSpeech();renderCompanion();}
  if(target.dataset.reassign&&target.value)updateCase("/api/reassign",{duty:target.dataset.reassign,person_id:target.value});
  if(["voice-enabled","settings-voice"].includes(target.id)){state.voiceEnabled=target.checked;localStorage.setItem("atlasVoice",String(state.voiceEnabled));if(!state.voiceEnabled)stopSpeech();renderCompanion();}
});
document.addEventListener("input",event=>{
  if(event.target.id==="people-search"){state.peopleQuery=event.target.value;const selection=event.target.selectionStart;renderPeople();$("#people-search").focus();if(selection!==null)$("#people-search").setSelectionRange(selection,selection);}
  if(event.target.matches("[data-org-search]")){state.orgQuery=event.target.value;const selection=event.target.selectionStart,id=event.target.id;const query=state.orgQuery.toLowerCase().trim();if(query){const found=state.company.people.find(p=>(p.name+" "+p.role+" "+(p.department||"")+" "+p.skills.join(" ")).toLowerCase().includes(query));if(found)state.orgSelectedId=found.id;}renderView();document.getElementById(id).focus();if(selection!==null)document.getElementById(id).setSelectionRange(selection,selection);}
  if(event.target.matches("[data-org-zoom]")){state.orgZoom=Number(event.target.value);renderView();}
});
document.addEventListener("submit",async event=>{
  if(event.target.id==="settings-form")saveSettings(event);
  if(event.target.id==="api-key-form"){
    event.preventDefault();const input=$("#api-key-input"),button=event.target.querySelector("button[type=submit]");button.disabled=true;
    try{state.config=await api("/api/config/key",{api_key:input.value.trim()});renderShell();notice("OpenAI key saved on this computer. The assistant can use it now.");}
    catch(error){input.value="";notice(error.message,true);button.disabled=false;}
  }
});
document.addEventListener("keydown",event=>{
  if(event.target.closest(".network-node")&&["Enter"," "].includes(event.key)){event.preventDefault();talkTo(event.target.closest(".network-node").dataset.talk);}
  if(event.key==="n"&&!event.ctrlKey&&!event.metaKey&&!event.altKey&&!["INPUT","TEXTAREA","SELECT"].includes(document.activeElement.tagName)){newConversation();}
});
$("#chat-form").addEventListener("submit",sendChat);
$("#chat-input").addEventListener("keydown",event=>{if(event.key==="Enter"&&!event.shiftKey&&!event.isComposing){event.preventDefault();sendChat();}});
$("#new-chat").addEventListener("click",newConversation);
$("#voice-stop").addEventListener("click",stopSpeech);
$("#dictate").addEventListener("click",dictate);
$("#menu-toggle").addEventListener("click",()=>$("#sidebar").classList.toggle("open"));
$("#toggle-history-search").addEventListener("click",()=>{$("#history-search").classList.toggle("hidden");if(!$("#history-search").classList.contains("hidden"))$("#history-search").focus();});
$("#history-search").addEventListener("input",renderHistory);
$("#staff-form").addEventListener("submit",saveStaff);
$("#review-form").addEventListener("submit",event=>{event.preventDefault();runReview(state.reviewAction,$("#review-comment").value.trim());});
$("#delete-staff").addEventListener("click",async()=>{
  const id=$("#staff-id").value;if(state.company.people.some(p=>p.reports_to===id)){$("#staff-error").textContent="Reassign this manager’s direct reports before removing them.";return;}
  try{state.company=await api("/api/company",{...state.company,people:state.company.people.filter(p=>p.id!==id).map(p=>({...p,follows:(p.follows||[]).filter(x=>x!==id)}))});$("#staff-dialog").close();renderShell();notice("Colleague removed from the current organization. Saved case history is retained.");}catch(error){$("#staff-error").textContent=error.message;}
});
async function boot(){
  hydrateIcons();
  const shell=$(".app-shell");shell.inert=true;shell.setAttribute("aria-busy","true");
  try{
    const results=await Promise.allSettled([api("/api/company"),api("/api/config"),api("/api/settings"),api("/api/conversations")]);
    if(results[0].status==="rejected")throw results[0].reason;
    state.company=results[0].value;
    if(results[1].status==="fulfilled")state.config=results[1].value;
    if(results[2].status==="fulfilled")state.settings=results[2].value;
    if(results[3].status==="fulfilled")state.history=results[3].value;
    const last=localStorage.getItem("atlasConversation");
    if(last&&state.history.some(c=>c.id===last)){
      state.conversation=await api("/api/conversation/"+last);state.personId=state.conversation.person_id||"atlas";
      if(state.conversation.request_id)try{state.case=await api("/api/case/"+state.conversation.request_id);}catch{}
    }
    renderShell();setView(location.hash.slice(1)||"assistant");if(state.conversation)scrollChat();
  }catch(error){notice("The workspace could not load: "+error.message,true);}
  finally{shell.inert=false;shell.setAttribute("aria-busy","false");document.body.dataset.ready="true";}
}
boot();
