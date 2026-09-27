/* The conversation's persisted execution record is the source of every metric. */
window.AtlasAgentRun = (() => {
  const completed = new Set(['completed', 'complete', 'succeeded', 'executed']);
  const active = new Set(['planning', 'running', 'executing', 'queued', 'in_progress', 'awaiting_approval', 'pending_approval', 'pending']);
  const labels = {planning:'Planning',running:'Working',executing:'Working',in_progress:'Working',queued:'Queued',pending:'Pending',completed:'Completed',complete:'Completed',succeeded:'Completed',executed:'Completed',failed:'Failed',error:'Failed',blocked:'Blocked',awaiting_approval:'Awaiting approval',pending_approval:'Awaiting approval',skipped:'Skipped',cancelled:'Cancelled',partial:'Partially completed'};
  const number = value => typeof value === 'number' && Number.isFinite(value) ? value.toLocaleString() : '—';
  const duration = value => {
    if(typeof value !== 'number' || !Number.isFinite(value))return '—';
    const seconds = Math.max(0, Math.floor(value / 1000));
    return seconds < 60 ? seconds + 's' : Math.floor(seconds / 60) + 'm ' + String(seconds % 60).padStart(2,'0') + 's';
  };
  const statusClass = status => completed.has(status) ? 'done' : /failed|error|blocked/.test(status) ? 'failed' : /approval/.test(status) ? 'review' : /running|executing|in_progress/.test(status) ? 'working' : 'pending';
  const status = value => '<span class="agent-run-status '+statusClass(value)+'">'+safe(labels[value] || title(value || 'pending'))+'</span>';
  const skillName = id => title(String(id || '').replaceAll('-', ' '));
  const staffName = id => id ? personName(id) : 'Assignment pending';
  const time = value => {
    const date = new Date(value);
    return Number.isNaN(date.getTime()) ? '' : date.toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit'});
  };
  let scrollSnapshot = null;

  function captureScroll(){
    const list = document.querySelector('[data-agent-call-list]');
    scrollSnapshot = list ? {id:list.dataset.agentCallList,top:list.scrollTop,following:list.scrollHeight-list.clientHeight-list.scrollTop<30} : null;
  }
  function restoreScroll(){
    const list = document.querySelector('[data-agent-call-list]');
    if(list && scrollSnapshot?.id === list.dataset.agentCallList)list.scrollTop = scrollSnapshot.following ? list.scrollHeight : scrollSnapshot.top;
    else if(list)list.scrollTop = list.scrollHeight;
  }
  function markup(run, {busy=false,offline=false}={}){
    if(!run){
      return busy ? '<section class="agent-run-card agent-run-preparing" aria-label="Agent execution"><span class="agent-run-symbol">'+icon('sparkle')+'</span><div><span class="eyebrow">AGENT EXECUTION</span><h3>Understanding your request</h3><p>Atlas is choosing the work and bringing the right skills together.</p>'+(offline?'<p class="agent-run-offline">Live updates are temporarily unavailable. Reconnecting…</p>':'')+'</div><span class="agent-live-label"><i></i> Starting</span></section>' : '';
    }
    const steps = Array.isArray(run.steps) ? run.steps : [];
    const calls = Array.isArray(run.calls) ? run.calls : [];
    const stats = run.statistics || {};
    const done = steps.filter(step => completed.has(step.status)).length;
    const pending = steps.filter(step => /planned|pending|queued|approval|blocked/.test(step.status)).length;
    const people = [...new Set(steps.map(step=>step.person_id).filter(Boolean))];
    const isWorking = active.has(run.status) && !/approval/.test(run.status);
    const progress = steps.length ? Math.min(completed.has(run.status)?100:99,Math.round(done/steps.length*100)) : 0;
    const metrics = [['skills_executed','Skills called'],['skills_completed','Completed'],['artifacts','Files created'],['delegated_people','People involved']];
    const headline = completed.has(run.status) ? 'Your team has finished' : /approval/.test(run.status) ? 'Ready for your review' : /failed|error|blocked|needs_attention|budget_exhausted/.test(run.status) ? 'Your team needs attention' : run.status === 'needs_input' ? 'Your team needs more information' : run.status === 'partial' ? 'Work completed with open items' : 'Your team is on it';
    return '<section class="agent-run-card" aria-label="Agent execution" data-agent-run-id="'+safe(run.id)+'">'+
      '<header class="agent-run-header"><span class="agent-run-symbol">'+icon(completed.has(run.status)?'check':'sparkle')+'</span><div><span class="eyebrow">AGENT EXECUTION</span><h3>'+headline+'</h3></div><div class="agent-run-heading-status">'+(isWorking?'<span class="agent-live-label"><i></i> Live</span>':'')+status(run.status)+'</div></header>'+
      (offline?'<p class="agent-run-offline" role="status">Live updates interrupted. Showing the last recorded state; reconnecting…</p>':'')+
      '<div class="agent-run-metrics">'+metrics.map(([key,label])=>'<div><strong>'+number(stats[key])+'</strong><span>'+label+'</span></div>').join('')+'</div>'+
      '<div class="agent-run-meter"><div><strong>'+ (steps.length ? done+' of '+steps.length+' plan steps completed' : 'Building the team plan')+'</strong><span>'+ (pending ? pending+' pending or awaiting review' : steps.length ? (completed.has(run.status)?'All recorded steps complete':'Execution in progress') : 'Steps appear as Atlas delegates')+'</span></div><div class="agent-run-track" role="progressbar" aria-label="Completed plan steps" aria-valuemin="0" aria-valuemax="'+Math.max(1,steps.length)+'" aria-valuenow="'+done+'"><span style="width:'+progress+'%"></span></div></div>'+
      (steps.length?'<section class="agent-run-plan"><div class="agent-run-section-title"><h4>Team plan</h4><span>'+people.length+' assigned '+(people.length===1?'colleague':'colleagues')+'</span></div><ol>'+steps.map((step,index)=>{
        const dependencies = (step.depends_on || []).map(id=>steps.find(s=>s.id===id)?.title||id);
        return '<li class="agent-plan-step '+statusClass(step.status)+'"><span class="agent-plan-number">'+(completed.has(step.status)?icon('check'):index+1)+'</span><div class="agent-plan-copy"><strong>'+safe(step.title||skillName(step.skill_id)||'Plan step')+'</strong><div><span>'+safe(staffName(step.person_id))+'</span>'+(step.skill_id?'<span class="agent-skill-name">'+safe(skillName(step.skill_id))+'</span>':'')+'</div>'+(dependencies.length?'<small>After '+dependencies.map(safe).join(' · ')+'</small>':'')+(step.error?'<p class="agent-run-error">'+safe(step.error)+'</p>':'')+'</div><div class="agent-plan-outcome">'+status(step.status)+(step.run_id?'<button class="text-link" data-run="'+safe(step.run_id)+'">Open result ↗</button>':'')+'</div></li>';
      }).join('')+'</ol></section>':'')+
      '<section class="agent-run-calls"><div class="agent-run-section-title"><h4>Live tool calls</h4><span>'+calls.length+' recorded</span></div>'+(calls.length?'<ol data-agent-call-list="'+safe(run.id)+'">'+calls.map(call=>{
        const label = call.skill_id ? skillName(call.skill_id) : title(String(call.tool||'Tool call').replaceAll('_',' '));
        return '<li><span class="agent-call-dot '+statusClass(call.status)+'"></span><div class="agent-call-copy"><strong>'+safe(label)+'</strong><small>'+safe(call.person_id?staffName(call.person_id):'Atlas')+' · <code>'+safe(call.tool||'skill')+'</code>'+(call.started_at?' · '+safe(time(call.started_at)):'')+'</small>'+(call.error?'<p class="agent-run-error">'+safe(call.error)+'</p>':'')+'</div><div class="agent-call-result">'+status(call.status)+'<small>'+duration(call.duration_ms)+'</small></div></li>';
      }).join('')+'</ol>':'<p class="agent-run-empty">Actual tool calls will appear here as they begin.</p>')+'</section>'+
      '<footer class="agent-run-footer"><span><strong>'+duration(stats.elapsed_ms ?? run.elapsed_ms)+'</strong> elapsed</span><span><strong>'+number(stats.tool_calls)+'</strong> tool calls</span><span><strong>'+number(stats.model_requests)+'</strong> model requests</span><span title="Input: '+number(stats.input_tokens)+' · Output: '+number(stats.output_tokens)+'"><strong>'+number(stats.total_tokens)+'</strong> tokens</span>'+(run.model?'<span class="agent-run-model">'+safe(run.model)+'</span>':'')+'</footer>'+
      (stats.skills_failed?'<p class="agent-run-footnote">'+number(stats.skills_failed)+' skill '+(stats.skills_failed===1?'call needs':'calls need')+' attention. Open the result above for details.</p>':'')+
      (/approval/.test(run.status)?'<p class="agent-run-footnote">Actions awaiting approval have not executed. Open the recorded result to review the exact action.</p>':'')+'</section>';
  }
  return {markup,captureScroll,restoreScroll,isActive:run=>!!run&&active.has(run.status)};
})();
