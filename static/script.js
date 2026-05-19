// ─── DOM Elements ───
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const analyzeBtn = document.getElementById('analyze-btn');
const roleInput = document.getElementById('role-input');
const progressContainer = document.getElementById('progress-container');
const progressFill = document.getElementById('progress-fill');
const progressLabel = document.getElementById('progress-label');
const skillsSection = document.getElementById('skills-section');
const tabsContainer = document.getElementById('tabs-container');

// Session state
let currentFile = null;
let cachedResumeText = '';

// ─── File Upload Handlers ───
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('dragover'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
dropZone.addEventListener('drop', e => {
    e.preventDefault();
    dropZone.classList.remove('dragover');
    if (e.dataTransfer.files.length) selectFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', e => { if (e.target.files.length) selectFile(e.target.files[0]); });

function selectFile(file) {
    if (file.type !== 'application/pdf') { alert('Please upload a PDF file.'); return; }
    currentFile = file;
    analyzeBtn.disabled = false;
    dropZone.querySelector('p').textContent = `Selected: ${file.name}`;
}

// ─── Tab System ───
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    });
});

// ─── Progress Helpers ───
function setProgress(pct, label) {
    progressFill.style.width = pct + '%';
    progressLabel.textContent = label;
}

function showProgress() {
    progressContainer.classList.remove('hidden');
    analyzeBtn.disabled = true;
    dropZone.style.opacity = '0.5';
    dropZone.style.pointerEvents = 'none';
}

function hideProgress() {
    progressContainer.classList.add('hidden');
    analyzeBtn.disabled = false;
    dropZone.style.opacity = '1';
    dropZone.style.pointerEvents = 'auto';
}

// ─── Main Analyze Flow ───
analyzeBtn.addEventListener('click', async () => {
    if (!currentFile) return;
    showProgress();

    const formData = new FormData();
    formData.append('file', currentFile);
    formData.append('target_role', roleInput.value.trim());
    formData.append('experience_level', document.getElementById('experience-select').value);
    formData.append('location', document.getElementById('location-input').value.trim());

    try {
        // Stage 1: Analyze
        setProgress(15, '📄 Parsing your resume...');
        const analyzeRes = await fetch('/analyze', { method: 'POST', body: formData });
        const analyzeData = await analyzeRes.json();
        if (analyzeData.error) { alert(analyzeData.error); hideProgress(); return; }
        cachedResumeText = analyzeData.resume_text || '';
        renderSkills(analyzeData.skills);
        renderJobsTab(analyzeData);
        setProgress(40, '🔎 Finding job matches... Done!');

        // Stage 2: Roast
        setProgress(55, '🔥 Roasting your resume...');
        const roastForm = new FormData();
        roastForm.append('file', currentFile);
        roastForm.append('target_role', roleInput.value.trim());
        roastForm.append('experience_level', document.getElementById('experience-select').value);
        const roastRes = await fetch('/roast', { method: 'POST', body: roastForm });
        const roastData = await roastRes.json();
        renderRoastTab(roastData);
        setProgress(75, '🔥 Resume roast complete!');

        // Stage 3: Interview Prep
        setProgress(85, '🎯 Preparing interview questions...');
        const interviewForm = new FormData();
        interviewForm.append('file', currentFile);
        interviewForm.append('target_role', roleInput.value.trim());
        interviewForm.append('experience_level', document.getElementById('experience-select').value);
        const interviewRes = await fetch('/interview-prep', { method: 'POST', body: interviewForm });
        const interviewData = await interviewRes.json();
        cachedResumeText = interviewData.resume_text || cachedResumeText;
        renderInterviewTab(interviewData);
        setProgress(100, '✅ All analysis complete!');

        // Show results
        skillsSection.classList.remove('hidden');
        tabsContainer.classList.remove('hidden');
        setTimeout(() => { tabsContainer.scrollIntoView({ behavior: 'smooth' }); }, 300);
    } catch (err) {
        alert('Connection failed. Is the server running?');
        console.error(err);
    } finally {
        setTimeout(hideProgress, 1500);
    }
});

// ─── Render: Skills ───
function renderSkills(skills) {
    const el = document.getElementById('skills-list');
    el.innerHTML = skills.map(s => `<span class="tag">${s}</span>`).join('');
}

// ─── Render: Jobs Tab ───
function renderJobsTab(data) {
    document.getElementById('ai-feedback').innerHTML = marked.parse(data.feedback || '');
    const jobsList = document.getElementById('jobs-list');
    jobsList.innerHTML = '';
    if (!data.jobs || !data.jobs.length) {
        jobsList.innerHTML = '<p style="color:#94a3b8">No jobs found. Try a different role or location.</p>';
        return;
    }
    data.jobs.forEach(job => {
        const score = job.score || 0;
        const scoreColor = score >= 75 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444';
        const srcColors = { adzuna:'#2563eb', remotive:'#7c3aed', remoteok:'#0891b2', jsearch:'#6366f1' };
        const srcBg = srcColors[job.source] || '#6366f1';
        const srcLabel = (job.source||'').charAt(0).toUpperCase() + (job.source||'').slice(1);
        const reasons = (job.match_reasons||[]).map(r => `<li>${r}</li>`).join('');
        const gaps = (job.gaps||[]).map(g => `<li>${g}</li>`).join('');
        const div = document.createElement('div');
        div.className = 'job-card';
        div.innerHTML = `
            <div class="job-card-header">
                <div><h4 class="job-title">${job.title}</h4><p class="job-meta">🏢 ${job.company} • 📍 ${job.location}</p></div>
                <span class="source-badge" style="background:${srcBg}">${srcLabel}</span>
            </div>
            <div class="score-section">
                <div class="score-label"><span>Match Score</span><span class="score-value" style="color:${scoreColor}">${score}%</span></div>
                <div class="score-bar-track"><div class="score-bar-fill" style="width:${score}%;background:${scoreColor}"></div></div>
            </div>
            ${reasons ? `<div class="match-section"><p class="section-label">✅ Why you fit</p><ul class="match-list">${reasons}</ul></div>` : ''}
            ${gaps ? `<div class="gaps-section"><p class="section-label">⚠️ Skill gaps</p><ul class="gaps-list">${gaps}</ul></div>` : ''}
            <a href="${job.url}" target="_blank" rel="noopener noreferrer" class="apply-btn">Apply Now →</a>`;
        jobsList.appendChild(div);
    });
}

// ─── Render: Roast Tab ───
function renderRoastTab(data) {
    document.getElementById('roast-loading').classList.add('hidden');
    const el = document.getElementById('roast-results');
    el.classList.remove('hidden');

    const os = data.overall_score || 0;
    const osColor = os >= 75 ? 'var(--green)' : os >= 50 ? 'var(--yellow)' : 'var(--red)';
    const ds = data.dimension_scores || {};

    let dimBars = '';
    for (const [key, val] of Object.entries(ds)) {
        const c = val >= 75 ? 'var(--green)' : val >= 50 ? 'var(--yellow)' : 'var(--red)';
        dimBars += `<div class="dim-bar"><label>${key.replace(/_/g,' ')} — ${val}%</label><div class="score-bar-track"><div class="score-bar-fill" style="width:${val}%;background:${c}"></div></div></div>`;
    }

    const strengths = (data.strengths||[]).map(s => `<span class="tag tag-green">${s}</span>`).join('');
    const bullets = (data.weak_bullets||[]).map(b => `
        <div class="bullet-comparison">
            <p class="bullet-original">❌ ${b.original}</p>
            <p class="bullet-rewritten">✅ ${b.rewritten}</p>
        </div>`).join('');
    const missing = (data.missing_sections||[]).map(s => `<span class="tag tag-yellow">${s}</span>`).join('');
    const cliches = (data.cliches_found||[]).map(c => `<span class="cliche-item">${c}</span>`).join('');

    el.innerHTML = `
        <div class="card">
            <div class="score-circle" style="border-color:${osColor};color:${osColor}">${os}</div>
            <div class="dimension-bars">${dimBars}</div>
        </div>
        <div class="roast-callout"><p>🔥 ${data.roast || ''}</p></div>
        ${strengths ? `<div class="card"><h3>💪 Strengths</h3><div class="tags" style="margin-top:0.75rem">${strengths}</div></div>` : ''}
        ${bullets ? `<div class="card"><h3>📝 Weak Bullets → Rewritten</h3>${bullets}</div>` : ''}
        ${missing ? `<div class="card"><h3>⚠️ Missing Sections</h3><div class="tags" style="margin-top:0.75rem">${missing}</div></div>` : ''}
        ${cliches ? `<div class="card"><h3>🚫 Clichés Found</h3><div style="margin-top:0.75rem">${cliches}</div></div>` : ''}
        <div class="card">
            <h3>✉️ Tailored Cover Letter</h3>
            <div class="cover-letter-box">
                <button class="copy-btn" onclick="copyText(this)">Copy</button>
                <pre>${data.cover_letter || 'N/A'}</pre>
            </div>
        </div>`;
}

// ─── Render: Interview Tab ───
let allQuestions = [];

function renderInterviewTab(data) {
    document.getElementById('interview-loading').classList.add('hidden');
    const el = document.getElementById('interview-results');
    el.classList.remove('hidden');

    const bq = data.behavioral_questions || [];
    const tq = data.technical_questions || [];
    allQuestions = [...bq.map(q=>q.question), ...tq.map(q=>q.question)];

    const bqCards = bq.map(q => `
        <div class="q-card">
            <h4>${q.question}</h4>
            <p class="q-sub">${q.why_asked}</p>
            <div class="q-hint" onclick="this.classList.toggle('open')">💡 Show hint
                <div class="q-hint-text">${q.answer_hint}</div>
            </div>
        </div>`).join('');

    const diffColors = { Easy:'var(--green)', Medium:'var(--yellow)', Hard:'var(--red)' };
    const tqCards = tq.map(q => `
        <div class="q-card">
            <h4>${q.question} <span class="difficulty-badge" style="background:${diffColors[q.difficulty]||'var(--primary)'}">${q.difficulty}</span></h4>
            <span class="tag" style="margin-top:0.3rem;display:inline-block">${q.topic}</span>
        </div>`).join('');

    const roadmap = (data.study_roadmap||[]).map(r => `
        <div class="roadmap-card">
            <h4>${r.topic}</h4>
            <p class="why">${r.why}</p>
            <p class="resource">📚 ${r.free_resource}</p>
        </div>`).join('');

    const qOptions = allQuestions.map((q,i) => `<option value="${i}">${q.substring(0,80)}...</option>`).join('');

    el.innerHTML = `
        <div class="card">
            <h3>❓ Question Bank</h3>
            <div class="toggle-group">
                <button class="toggle-btn active" onclick="showQType(this,'behavioral')">Behavioral</button>
                <button class="toggle-btn" onclick="showQType(this,'technical')">Technical</button>
            </div>
            <div id="q-behavioral">${bqCards || '<p class="q-sub">No questions generated.</p>'}</div>
            <div id="q-technical" class="hidden">${tqCards || '<p class="q-sub">No questions generated.</p>'}</div>
        </div>

        <div class="card evaluator-section">
            <h3>🎤 Answer Evaluator</h3>
            <div class="form-group">
                <label>Select a question or type your own</label>
                <select id="eval-question-select" class="text-input" onchange="document.getElementById('eval-custom-q').value=allQuestions[this.value]||''">
                    <option value="">-- Select --</option>
                    ${qOptions}
                </select>
            </div>
            <div class="form-group" style="margin-top:0.5rem">
                <input type="text" id="eval-custom-q" class="text-input" placeholder="Or type a custom question here">
            </div>
            <div class="form-group">
                <label>Your Answer</label>
                <textarea id="eval-answer" class="text-input" placeholder="Type your answer here..."></textarea>
            </div>
            <button class="btn btn-primary" onclick="evaluateAnswer()">Evaluate My Answer</button>
            <div id="eval-result"></div>
        </div>

        <div class="card">
            <h3>📚 Study Roadmap</h3>
            <div class="roadmap-grid">${roadmap}</div>
        </div>`;
}

function showQType(btn, type) {
    btn.parentElement.querySelectorAll('.toggle-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('q-behavioral').classList.toggle('hidden', type !== 'behavioral');
    document.getElementById('q-technical').classList.toggle('hidden', type !== 'technical');
}

async function evaluateAnswer() {
    const question = document.getElementById('eval-custom-q').value.trim();
    const answer = document.getElementById('eval-answer').value.trim();
    if (!question || !answer) { alert('Please provide both a question and an answer.'); return; }

    const resultEl = document.getElementById('eval-result');
    resultEl.innerHTML = '<p class="q-sub" style="margin-top:1rem">Evaluating...</p>';

    const fd = new FormData();
    fd.append('question', question);
    fd.append('user_answer', answer);
    fd.append('resume_text', cachedResumeText);

    try {
        const res = await fetch('/evaluate-answer', { method: 'POST', body: fd });
        const data = await res.json();
        const scoreColor = data.score >= 7 ? 'var(--green)' : data.score >= 4 ? 'var(--yellow)' : 'var(--red)';
        resultEl.innerHTML = `
            <div class="eval-result">
                <p class="eval-score" style="color:${scoreColor};margin-top:1rem">${data.score}/10</p>
                <p style="color:var(--text-muted);margin:0.5rem 0">${data.feedback}</p>
                ${data.better_answer ? `<div class="better-answer-box"><p><strong>Stronger answer:</strong> ${data.better_answer}</p></div>` : ''}
            </div>`;
    } catch (err) {
        resultEl.innerHTML = '<p style="color:#f87171;margin-top:1rem">Failed to evaluate. Is the server running?</p>';
    }
}

// ─── Utilities ───
function copyText(btn) {
    const text = btn.parentElement.querySelector('pre').textContent;
    navigator.clipboard.writeText(text).then(() => { btn.textContent = 'Copied!'; setTimeout(() => { btn.textContent = 'Copy'; }, 2000); });
}
