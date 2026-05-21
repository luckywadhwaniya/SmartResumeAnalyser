import React, { useState, useRef } from 'react';
import { Upload, ChevronDown } from 'lucide-react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';

function App() {
  // --- Form & File State ---
  const [file, setFile] = useState(null);
  const [role, setRole] = useState('');
  const [location, setLocation] = useState('India');
  const [experience, setExperience] = useState('Auto-Detect');
  
  // --- UI State ---
  const [isDragOver, setIsDragOver] = useState(false);
  const [isExpMenuOpen, setIsExpMenuOpen] = useState(false);
  const [progress, setProgress] = useState({ active: false, pct: 0, label: '' });
  const [activeTab, setActiveTab] = useState('jobs');
  const fileInputRef = useRef(null);

  // --- Data State ---
  const [cachedResumeText, setCachedResumeText] = useState('');
  const [results, setResults] = useState({
    skills: null,
    jobsData: null,
    roastData: null,
    interviewData: null,
    jdData: null
  });

  // --- JD Matcher State ---
  const [jdText, setJdText] = useState('');
  const [isMatchingJd, setIsMatchingJd] = useState(false);

  // --- Interview Evaluator State ---
  const [evalQ, setEvalQ] = useState('');
  const [evalA, setEvalA] = useState('');
  const [evalResult, setEvalResult] = useState(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [activeInterviewCategory, setActiveInterviewCategory] = useState('behavioral');

  // --- Handlers ---
  const handleFileSelect = (selectedFile) => {
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
    } else {
      alert('Please upload a PDF file.');
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    
    setProgress({ active: true, pct: 10, label: 'Starting analysis...' });
    let currentResumeText = cachedResumeText;

    try {
      // Stage 1: Analyze & Jobs
      setProgress({ active: true, pct: 15, label: '📄 Parsing your resume & extracting skills...' });
      const analyzeFd = new FormData();
      analyzeFd.append('file', file);
      analyzeFd.append('target_role', role);
      analyzeFd.append('experience_level', experience);
      analyzeFd.append('location', location);

      const analyzeRes = await fetch('/analyze', { method: 'POST', body: analyzeFd });
      const analyzeData = await analyzeRes.json();
      if (analyzeData.error) throw new Error(analyzeData.error);
      
      currentResumeText = analyzeData.resume_text;
      setCachedResumeText(currentResumeText);
      setResults(prev => ({ ...prev, skills: analyzeData.skills, jobsData: analyzeData }));

      // Stage 2: Roast
      setProgress({ active: true, pct: 55, label: '🔥 Roasting your resume...' });
      const roastFd = new FormData();
      roastFd.append('file', file);
      roastFd.append('target_role', role);
      roastFd.append('experience_level', experience);
      const roastRes = await fetch('/roast', { method: 'POST', body: roastFd });
      const roastData = await roastRes.json();
      setResults(prev => ({ ...prev, roastData }));

      // Stage 3: Interview Prep
      setProgress({ active: true, pct: 85, label: '🎯 Preparing interview questions...' });
      const interviewFd = new FormData();
      interviewFd.append('file', file);
      interviewFd.append('target_role', role);
      interviewFd.append('experience_level', experience);
      const interviewRes = await fetch('/interview-prep', { method: 'POST', body: interviewFd });
      const interviewData = await interviewRes.json();
      setResults(prev => ({ ...prev, interviewData }));

      setProgress({ active: true, pct: 100, label: '✅ All analysis complete!' });
      setTimeout(() => setProgress(p => ({ ...p, active: false })), 1500);

    } catch (err) {
      alert(`Analysis failed: ${err.message}`);
      setProgress({ active: false, pct: 0, label: '' });
    }
  };

  const handleJdMatch = async () => {
    if (!cachedResumeText) return alert("Please upload and analyze a resume first!");
    if (!jdText.trim()) return alert("Please paste a Job Description!");

    setIsMatchingJd(true);
    const fd = new FormData();
    fd.append('resume_text', cachedResumeText);
    fd.append('jd_text', jdText);

    try {
      const res = await fetch('/match-jd', { method: 'POST', body: fd });
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setResults(prev => ({ ...prev, jdData: data }));
    } catch (err) {
      alert("Match analysis failed.");
    } finally {
      setIsMatchingJd(false);
    }
  };

  const handleEvaluateAnswer = async () => {
    if (!evalQ || !evalA) return alert('Please provide both a question and an answer.');
    
    setIsEvaluating(true);
    const fd = new FormData();
    fd.append('question', evalQ);
    fd.append('user_answer', evalA);
    fd.append('resume_text', cachedResumeText);

    try {
      const res = await fetch('/evaluate-answer', { method: 'POST', body: fd });
      const data = await res.json();
      setEvalResult(data);
    } catch (err) {
      alert("Failed to evaluate answer.");
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="container" onClick={() => setIsExpMenuOpen(false)}>
      <header>
        <h1 id="main-title">Smart Resume <span>Analyzer</span></h1>
        <p className="subtitle">AI-powered skill extraction, job matching & interview prep</p>
      </header>

      <main>
        {/* --- UPLOAD SECTION --- */}
        <section className="upload-section card">
          <div 
            className={`upload-box ${isDragOver ? 'dragover' : ''}`}
            style={{ opacity: progress.active ? 0.5 : 1, pointerEvents: progress.active ? 'none' : 'auto' }}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => { e.preventDefault(); setIsDragOver(false); handleFileSelect(e.dataTransfer.files[0]); }}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="upload-icon mx-auto" />
            <p>{file ? `Selected: ${file.name}` : 'Drag & drop your PDF resume or click to upload'}</p>
            <input type="file" accept=".pdf" hidden ref={fileInputRef} onChange={(e) => handleFileSelect(e.target.files[0])} />
            <button className="btn btn-primary">Choose File</button>
          </div>

          <div className="form-row">
            {/* Custom Experience Dropdown */}
            <div className="form-group" onClick={(e) => e.stopPropagation()}>
              <label>Experience Level</label>
              <div className={`custom-select-wrapper ${isExpMenuOpen ? 'open' : ''}`}>
                <div className="custom-select-trigger" onClick={() => setIsExpMenuOpen(!isExpMenuOpen)}>
                  <span>{experience}</span>
                  <ChevronDown size={18} className="text-primary transition-transform duration-300" style={{ transform: isExpMenuOpen ? 'rotate(180deg)' : 'rotate(0)' }}/>
                </div>
                <div className="custom-options">
                  {['Auto-Detect', 'Internship', 'Entry Level / Junior', 'Mid-Level', 'Senior / Lead'].map(level => (
                    <span 
                      key={level} 
                      className={`custom-option ${experience === level ? 'selected' : ''}`} 
                      onClick={() => { setExperience(level); setIsExpMenuOpen(false); }}
                    >
                      {level}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="form-group">
              <label>Target Role (Optional)</label>
              <input type="text" className="text-input" placeholder="e.g. Data Scientist" value={role} onChange={e => setRole(e.target.value)} />
            </div>
            <div className="form-group">
              <label>Location</label>
              <input type="text" className="text-input" placeholder="e.g. India, Remote" value={location} onChange={e => setLocation(e.target.value)} />
            </div>
          </div>

          <button className="btn btn-primary btn-analyze w-full" disabled={!file || progress.active} onClick={handleAnalyze}>
            <span>🚀 Analyze My Resume</span>
          </button>

          {progress.active && (
            <div id="progress-container">
              <div className="progress-track">
                <div className="progress-fill" style={{ width: `${progress.pct}%` }}></div>
              </div>
              <p className="progress-label">{progress.label}</p>
            </div>
          )}
        </section>

        {/* --- RESULTS SECTION --- */}
        {results.skills && (
          <section id="skills-section">
            <div className="card">
              <h3>🛠️ Extracted Skills</h3>
              <div className="tags">
                {results.skills.map((s, i) => <span key={i} className="tag">{s}</span>)}
              </div>
            </div>
          </section>
        )}

        {results.jobsData && (
          <div id="tabs-container">
            <div className="tabs">
              {['jobs', 'roast', 'jd-match', 'interview'].map(tab => (
                <button key={tab} className={`tab ${activeTab === tab ? 'active' : ''}`} onClick={() => setActiveTab(tab)}>
                  {tab === 'jobs' ? '💼 Job Matches' : tab === 'roast' ? '📝 Analysis' : tab === 'jd-match' ? '🎯 JD Matcher' : '🎯 Interview'}
                </button>
              ))}
            </div>

            {/* TAB: JOBS */}
            {activeTab === 'jobs' && (
              <div className="tab-panel active">
                <div className="card">
                  <h3>💼 AI-Matched Job Listings</h3>
                  <p className="subtitle mb-4">Real jobs scored against your resume.</p>
                  <div className="jobs-grid">
                    {results.jobsData.jobs?.map((job, i) => (
                      <div key={i} className="job-card">
                        <div className="job-card-header">
                          <div>
                            <h4 className="job-title">{job.title}</h4>
                            <p className="job-meta">🏢 {job.company} • 📍 {job.location}</p>
                          </div>
                          <span className="source-badge" style={{background: '#6366f1'}}>{job.source}</span>
                        </div>
                        <div className="score-section">
                          <div className="score-label"><span>Match Score</span><span className="score-value" style={{color: job.score >= 75 ? '#10b981' : '#f59e0b'}}>{job.score}%</span></div>
                          <div className="score-bar-track"><div className="score-bar-fill" style={{width: `${job.score}%`, background: job.score >= 75 ? '#10b981' : '#f59e0b'}}></div></div>
                        </div>
                        <a href={job.link || job.url} target="_blank" rel="noreferrer" className="apply-btn">Apply Now →</a>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB: ROAST (WITH RADAR CHART) */}
            {/* TAB: ROAST (WITH RADAR CHART) */}
            {activeTab === 'roast' && results.roastData && (
              <div className="tab-panel active">
                
                <div className="card">
                  <h3 className="text-center mb-4">Resume Dimension Analysis</h3>
                  
                  {/* --- Radar Chart --- */}
                  <div style={{ width: '100%', height: 320 }} className="mb-6">
                    <ResponsiveContainer>
                      <RadarChart 
                        cx="50%" cy="50%" outerRadius="70%" 
                        data={Object.entries(results.roastData.dimension_scores || {}).map(([key, val]) => ({
                          subject: key.replace(/_/g, ' ').toUpperCase(),
                          A: val,
                          fullMark: 100
                        }))}
                      >
                        <PolarGrid stroke="rgba(255,255,255,0.1)" />
                        <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                        <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                        <Radar name="Score" dataKey="A" stroke="#a855f7" fill="#a855f7" fillOpacity={0.4} />
                        <Tooltip contentStyle={{ backgroundColor: '#12121c', borderColor: '#a855f7', borderRadius: '8px' }} itemStyle={{ color: '#ec4899' }}/>
                      </RadarChart>
                    </ResponsiveContainer>
                  </div>

                  <div className="score-circle-wrap mt-2">
                    <h3 className="mb-2">Overall Score</h3>
                    <div className="score-circle mx-auto" style={{borderColor: '#10b981', color: '#10b981'}}>{results.roastData.overall_score}</div>
                  </div>
                  
                  <div className="roast-callout mt-6"><p>🔥 {results.roastData.roast}</p></div>
                </div>

                {/* --- RESTORED: Strengths --- */}
                {results.roastData.strengths?.length > 0 && (
                  <div className="card mt-4">
                    <h3>💪 Strengths</h3>
                    <div className="tags mt-3">
                      {results.roastData.strengths.map((s, i) => <span key={i} className="tag tag-green">{s}</span>)}
                    </div>
                  </div>
                )}
                
                {/* --- Weak Bullets --- */}
                {results.roastData.weak_bullets?.length > 0 && (
                  <div className="card mt-4">
                    <h3 className="mb-2">📝 Weak Bullets Rewritten</h3>
                    {results.roastData.weak_bullets.map((b, i) => (
                      <div key={i} className="bullet-comparison">
                        <p className="bullet-original">❌ {b.original}</p>
                        <p className="bullet-rewritten">✅ {b.rewritten}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* --- RESTORED: Missing Sections --- */}
                {results.roastData.missing_sections?.length > 0 && (
                  <div className="card mt-4">
                    <h3>⚠️ Missing Sections</h3>
                    <div className="tags mt-3">
                      {results.roastData.missing_sections.map((s, i) => <span key={i} className="tag tag-yellow">{s}</span>)}
                    </div>
                  </div>
                )}

                {/* --- RESTORED: Cliches Found --- */}
                {results.roastData.cliches_found?.length > 0 && (
                  <div className="card mt-4">
                    <h3>🚫 Clichés Found</h3>
                    <div className="mt-3">
                      {results.roastData.cliches_found.map((c, i) => <span key={i} className="cliche-item">{c}</span>)}
                    </div>
                  </div>
                )}

                {/* --- RESTORED: Tailored Cover Letter --- */}
                {results.roastData.cover_letter && (
                  <div className="card mt-4">
                    <h3>✉️ Tailored Cover Letter</h3>
                    <div className="cover-letter-box">
                      <button 
                        className="copy-btn" 
                        onClick={(e) => {
                          navigator.clipboard.writeText(results.roastData.cover_letter);
                          e.target.textContent = 'Copied!';
                          setTimeout(() => e.target.textContent = 'Copy', 2000);
                        }}
                      >
                        Copy
                      </button>
                      <pre>{results.roastData.cover_letter}</pre>
                    </div>
                  </div>
                )}
                
              </div>
            )}

            {/* TAB: JD MATCH (WITH DONUT CHART) */}
            {activeTab === 'jd-match' && (
              <div className="tab-panel active">
                <div className="card">
                  <h3>🎯 Resume vs. Job Description</h3>
                  <textarea className="text-input mt-2" style={{minHeight: '150px'}} placeholder="Paste JD here..." value={jdText} onChange={e => setJdText(e.target.value)}></textarea>
                  <button className="btn btn-primary mt-4" onClick={handleJdMatch} disabled={isMatchingJd}>{isMatchingJd ? 'Analyzing...' : 'Analyze Match'}</button>
                </div>
                
                {results.jdData && (
                  <>
                    <div className="card mt-4">
                      
                      {/* --- NEW: Donut Chart --- */}
                      <div className="flex flex-col items-center justify-center mt-4" style={{ position: 'relative' }}>
                        <h3 className="mb-0">ATS Match Score</h3>
                        <div style={{ width: '100%', height: 250 }}>
                          <ResponsiveContainer>
                            <PieChart>
                              <Pie
                                data={[
                                  { name: 'Match', value: results.jdData.ats_score || 0 },
                                  { name: 'Gap', value: 100 - (results.jdData.ats_score || 0) }
                                ]}
                                cx="50%" cy="50%" innerRadius={75} outerRadius={95}
                                stroke="none" dataKey="value" startAngle={90} endAngle={-270}
                                animationDuration={1500}
                              >
                                <Cell fill="#a855f7" style={{ filter: 'drop-shadow(0px 0px 8px rgba(168,85,247,0.6))' }} />
                                <Cell fill="rgba(255,255,255,0.05)" />
                              </Pie>
                              <Tooltip contentStyle={{ backgroundColor: '#12121c', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }} itemStyle={{ color: '#f1f5f9' }} />
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                        {/* Center Number Overlay */}
                        <div style={{ position: 'absolute', top: '55%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: '2.5rem', fontWeight: 'bold', color: '#10b981', fontFamily: 'Outfit, sans-serif' }}>
                          {results.jdData.ats_score}%
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6 border-t border-white/10 pt-6">
                         <div>
                           <h3 className="mb-2">✅ Matched Keywords</h3>
                           <div className="tags">{results.jdData.matched_skills?.map((s,i) => <span key={i} className="tag tag-green">{s}</span>)}</div>
                         </div>
                         <div>
                           <h3 className="mb-2">⚠️ Missing Keywords</h3>
                           <div className="tags">{results.jdData.missing_skills?.map((s,i) => <span key={i} className="tag tag-red">{s}</span>)}</div>
                         </div>
                      </div>
                    </div>
                    
                    {/* --- RESTORED: Culture Fit --- */}
                    {results.jdData.culture_fit_analysis && (
                      <div className="card mt-4">
                        <h3>🏢 Culture & Experience Fit</h3>
                        <p className="markdown-content mt-2">{results.jdData.culture_fit_analysis}</p>
                      </div>
                    )}

                    {/* --- RESTORED: Bullet Suggestions --- */}
                    {results.jdData.bullet_suggestions?.length > 0 && (
                      <div className="card mt-4">
                        <h3>📝 Resume Tailoring Suggestions</h3>
                        <p className="subtitle mb-2">Update these bullets on your resume to increase your ATS score for this specific job.</p>
                        {results.jdData.bullet_suggestions.map((b, i) => (
                          <div key={i} className="bullet-comparison mt-2">
                            <p className="bullet-original">❌ {b.current_bullet}</p>
                            <p className="bullet-rewritten">✅ <strong>Tailored:</strong> {b.tailored_bullet}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {/* TAB: INTERVIEW */}
            {activeTab === 'interview' && results.interviewData && (
              <div className="tab-panel active">
                <div className="card">
                   <h3>❓ Question Bank</h3>
                   <div className="toggle-group mt-2">
                     <button className={`toggle-btn ${activeInterviewCategory === 'behavioral' ? 'active' : ''}`} onClick={() => setActiveInterviewCategory('behavioral')}>Behavioral</button>
                     <button className={`toggle-btn ${activeInterviewCategory === 'technical' ? 'active' : ''}`} onClick={() => setActiveInterviewCategory('technical')}>Technical</button>
                   </div>
                   
                   <div className="mt-4">
                     {activeInterviewCategory === 'behavioral' 
                       ? results.interviewData.behavioral_questions?.map((q, i) => (
                           <div key={i} className="q-card"><h4>{q.question}</h4><p className="q-sub">{q.why_asked}</p></div>
                         ))
                       : results.interviewData.technical_questions?.map((q, i) => (
                           <div key={i} className="q-card"><h4>{q.question}</h4><span className="tag mt-2 inline-block">{q.topic}</span></div>
                         ))
                     }
                   </div>
                </div>

                <div className="card mt-4">
                  <h3>🎤 Answer Evaluator</h3>
                  <input type="text" className="text-input mt-2" placeholder="Type a question to answer..." value={evalQ} onChange={e => setEvalQ(e.target.value)} />
                  <textarea className="text-input mt-2" style={{minHeight:'100px'}} placeholder="Your answer..." value={evalA} onChange={e => setEvalA(e.target.value)}></textarea>
                  <button className="btn btn-primary mt-4" onClick={handleEvaluateAnswer} disabled={isEvaluating}>Evaluate</button>
                  
                  {evalResult && (
                    <div className="mt-4">
                      <p className="eval-score" style={{color: '#10b981'}}>{evalResult.score}/10</p>
                      <p className="mt-2 text-muted">{evalResult.feedback}</p>
                      <div className="better-answer-box mt-2"><p><strong>Stronger answer:</strong> {evalResult.better_answer}</p></div>
                    </div>
                  )}
                </div>
              </div>
            )}

          </div>
        )}
      </main>
    </div>
  );
}

export default App;