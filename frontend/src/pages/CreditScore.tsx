import { useState } from 'react';
import { submitApplication, getApplications } from '../services/api';
import type { CreditApplication, ApplicationResponse } from '../types';

const ALTERNATIVE_PARAMS = [
  { key: 'gig_platform_rating', label: 'Gig Platform Rating', hint: '0 – 5', type: 'number', step: '0.1', min: 0, max: 5 },
  { key: 'upi_transaction_frequency', label: 'UPI Transactions per Month', hint: 'count', type: 'number', min: 0 },
  { key: 'savings_account_balance', label: 'Savings Account Balance', hint: '₹', type: 'number', min: 0 },
  { key: 'remittance_frequency', label: 'Remittances Sent per Year', hint: 'count', type: 'number', min: 0 },
  { key: 'community_verification_score', label: 'Community Verification Score', hint: '0 – 10', type: 'number', step: '0.1', min: 0, max: 10 },
  { key: 'microfinance_repayment_count', label: 'Microfinance Repayments Done', hint: 'count', type: 'number', min: 0 },
  { key: 'utility_payment_history', label: 'Utility Payment History', hint: '', type: 'select', options: ['good', 'average', 'poor'] },
  { key: 'employment_type', label: 'Employment Type', hint: '', type: 'select', options: ['salaried', 'self_employed', 'gig_worker', 'daily_wage', 'unemployed'] },
];

function getRiskColor(risk: string) {
  if (risk === 'low') return '#1a6e40';
  if (risk === 'medium') return '#b85c00';
  return '#c62828';
}

function getRiskBg(risk: string) {
  if (risk === 'low') return '#e6f4ec';
  if (risk === 'medium') return '#fff3e0';
  return '#fdecea';
}

function ScoreDisplay({ result, onBack }: { result: ApplicationResponse; onBack: () => void }) {
  const score = Math.round(result.credit_score || 0);
  const risk = result.risk_category || 'medium';
  const color = getRiskColor(risk);
  const bg = getRiskBg(risk);

  return (
    <div className="cs-page">
      <div className="cs-result-card">
        <div className="cs-result-header">
          <div className="cs-brand-mark">◈</div>
          <h2>Your Alternate Credit Score</h2>
          <p>Based on your alternative financial data</p>
        </div>

        <div className="cs-score-ring" style={{ borderColor: color }}>
          <span className="cs-score-num" style={{ color }}>{score}</span>
          <span className="cs-score-sub">out of 850</span>
        </div>

        <div className="cs-risk-badge" style={{ background: bg, color }}>
          {risk === 'low' ? '✓ LOW RISK' : risk === 'medium' ? '◷ MEDIUM RISK' : '✗ HIGH RISK'}
        </div>

        <div className="cs-result-meta">
          <div className="cs-meta-row">
            <span>Application ID</span>
            <b>#{result.application_id}</b>
          </div>
          <div className="cs-meta-row">
            <span>Status</span>
            <b style={{ textTransform: 'capitalize' }}>{result.status.replace('_', ' ')}</b>
          </div>
          <div className="cs-meta-row">
            <span>Applicant type</span>
            <b style={{ textTransform: 'capitalize' }}>{result.applicant_type}</b>
          </div>
          <div className="cs-meta-row">
            <span>Requested amount</span>
            <b>₹{Number(result.requested_amount).toLocaleString('en-IN')}</b>
          </div>
        </div>

        <div className="cs-pending-note">
          <span>⏳</span>
          <div>
            <b>Pending Bank Review</b>
            <p>Your application has been scored by AI. A bank officer will review it and make the final lending decision.</p>
          </div>
        </div>

        <div className="cs-scale-row">
          <div className="cs-scale-item" style={{ background: '#e6f4ec', color: '#1a6e40' }}>
            <b>700 – 850</b><small>Low risk</small>
          </div>
          <div className="cs-scale-item" style={{ background: '#fff3e0', color: '#b85c00' }}>
            <b>600 – 699</b><small>Medium risk</small>
          </div>
          <div className="cs-scale-item" style={{ background: '#fdecea', color: '#c62828' }}>
            <b>300 – 599</b><small>High risk</small>
          </div>
        </div>

        <button className="cs-btn-primary" onClick={onBack}>← Back to Credit Score</button>
        <p className="cs-disclaimer">
          This is an alternate credit score based on non-traditional data. It is not an official CIBIL or bureau score.
          Final lending decisions are made by banks or lenders.
        </p>
      </div>
    </div>
  );
}

export default function CreditScore() {
  const [view, setView] = useState<'list' | 'form' | 'result'>('list');
  const [applications, setApplications] = useState<ApplicationResponse[]>([]);
  const [loadingApps, setLoadingApps] = useState(true);
  const [result, setResult] = useState<ApplicationResponse | null>(null);

  // Form state
  const [applicantType, setApplicantType] = useState<'underbanked' | 'unbanked'>('underbanked');
  const [fullName, setFullName] = useState('');
  const [age, setAge] = useState(25);
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');
  const [amount, setAmount] = useState(50000);
  const [purpose, setPurpose] = useState('');
  const [income, setIncome] = useState(25000);
  const [selectedParams, setSelectedParams] = useState<string[]>([]);
  const [altValues, setAltValues] = useState<Record<string, any>>({});
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Load applications on mount
  useState(() => {
    getApplications()
      .then(setApplications)
      .catch(() => setApplications([]))
      .finally(() => setLoadingApps(false));
  });

  const toggleParam = (key: string) => {
    setSelectedParams(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
    if (selectedParams.includes(key)) {
      setAltValues(prev => { const n = { ...prev }; delete n[key]; return n; });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (selectedParams.length < 4) {
      setError('Please select at least 4 alternative data parameters.');
      return;
    }
    for (const key of selectedParams) {
      if (altValues[key] === undefined || altValues[key] === '') {
        setError(`Please fill in: ${ALTERNATIVE_PARAMS.find(p => p.key === key)?.label}`);
        return;
      }
    }

    setSubmitting(true);
    const application: CreditApplication = {
      applicant_type: applicantType,
      full_name: fullName,
      age,
      phone_number: phone,
      address,
      requested_amount: amount,
      loan_purpose: purpose,
      monthly_income: income,
      alternative_data: altValues,
    };

    try {
      const response = await submitApplication(application);
      setResult(response);
      // Refresh list
      getApplications().then(setApplications).catch(() => {});
      setView('result');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Submission failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const statusColor = (s: string) =>
    s === 'approved' ? '#1a6e40' : s === 'rejected' ? '#c62828' : '#b85c00';

  // ── Result view ──────────────────────────────────────────────────────────
  if (view === 'result' && result) {
    return <ScoreDisplay result={result} onBack={() => setView('list')} />;
  }

  // ── Application form ─────────────────────────────────────────────────────
  if (view === 'form') {
    return (
      <div className="cs-page">
        <div className="cs-form-card">
          <div className="cs-form-header">
            <div className="cs-brand-mark">◈</div>
            <h2>Apply for Alternate Credit Score</h2>
            <p>No CIBIL history needed. We use your real financial activity to assess creditworthiness.</p>
          </div>

          <form onSubmit={handleSubmit} className="cs-form">
            {/* Applicant type */}
            <div className="cs-section-label">About you</div>
            <div className="cs-two-col">
              <div className="cs-field">
                <label>Applicant Type</label>
                <select value={applicantType} onChange={e => setApplicantType(e.target.value as any)}>
                  <option value="underbanked">Underbanked (has some bank access)</option>
                  <option value="unbanked">Unbanked (no formal bank history)</option>
                </select>
              </div>
              <div className="cs-field">
                <label>Requested Loan Amount (₹)</label>
                <input type="number" min={1000} required value={amount}
                  onChange={e => setAmount(Number(e.target.value))} />
              </div>
            </div>

            <div className="cs-two-col">
              <div className="cs-field">
                <label>Full Name</label>
                <input type="text" required maxLength={120} value={fullName}
                  onChange={e => setFullName(e.target.value)} placeholder="As per documents" />
              </div>
              <div className="cs-field">
                <label>Age</label>
                <input type="number" min={18} max={100} required value={age}
                  onChange={e => setAge(Number(e.target.value))} />
              </div>
            </div>

            <div className="cs-two-col">
              <div className="cs-field">
                <label>Phone Number</label>
                <input type="tel" required value={phone}
                  onChange={e => setPhone(e.target.value)} />
              </div>
              <div className="cs-field">
                <label>Monthly Income (₹)</label>
                <input type="number" min={1} required value={income}
                  onChange={e => setIncome(Number(e.target.value))} />
              </div>
            </div>

            <div className="cs-field">
              <label>Address</label>
              <input type="text" required maxLength={240} value={address}
                onChange={e => setAddress(e.target.value)} placeholder="Current residential address" />
            </div>

            <div className="cs-field">
              <label>Loan Purpose</label>
              <input type="text" required maxLength={160} value={purpose}
                onChange={e => setPurpose(e.target.value)}
                placeholder="e.g. Working capital, home repair, education" />
            </div>

            {/* Alternative data */}
            <div className="cs-section-label" style={{ marginTop: 24 }}>
              Alternative Data
              <span className="cs-section-hint">Select at least 4 that apply to you ({selectedParams.length} selected)</span>
            </div>

            <div className="cs-param-grid">
              {ALTERNATIVE_PARAMS.map(param => (
                <label key={param.key} className={`cs-param-chip ${selectedParams.includes(param.key) ? 'selected' : ''}`}>
                  <input type="checkbox" checked={selectedParams.includes(param.key)}
                    onChange={() => toggleParam(param.key)} />
                  <div>
                    <span>{param.label}</span>
                    {param.hint && <small>{param.hint}</small>}
                  </div>
                </label>
              ))}
            </div>

            {selectedParams.length > 0 && (
              <div className="cs-param-inputs">
                <div className="cs-section-label">Fill in your selected parameters</div>
                <div className="cs-two-col">
                  {ALTERNATIVE_PARAMS.filter(p => selectedParams.includes(p.key)).map(param => (
                    <div className="cs-field" key={param.key}>
                      <label>{param.label}{param.hint ? ` (${param.hint})` : ''}</label>
                      {param.type === 'select' ? (
                        <select value={altValues[param.key] || ''}
                          onChange={e => setAltValues({ ...altValues, [param.key]: e.target.value })}>
                          <option value="">Select…</option>
                          {param.options?.map(opt => (
                            <option key={opt} value={opt}>{opt.replace(/_/g, ' ')}</option>
                          ))}
                        </select>
                      ) : (
                        <input type="number" step={(param as any).step || '1'}
                          min={param.min} max={(param as any).max}
                          value={altValues[param.key] ?? ''}
                          onChange={e => setAltValues({ ...altValues, [param.key]: Number(e.target.value) })} />
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {error && <div className="cs-error">{error}</div>}

            <div className="cs-form-actions">
              <button type="button" className="cs-btn-secondary" onClick={() => { setView('list'); setError(''); }}>
                Cancel
              </button>
              <button type="submit" className="cs-btn-primary" disabled={submitting}>
                {submitting ? 'Scoring your profile…' : 'Get My Credit Score'}
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // ── List / landing view ──────────────────────────────────────────────────
  return (
    <div className="cs-page">
      {/* Hero */}
      <div className="cs-hero">
        <div>
          <div className="cs-hero-eyebrow">◈ ALTERNATE CREDIT SCORE</div>
          <h1 className="cs-hero-title">Your creditworthiness,<br />your way.</h1>
          <p className="cs-hero-desc">
            No CIBIL history? No problem. ArthSaathi uses your real financial activity —
            gig ratings, UPI usage, savings, community scores — to generate an alternate credit score.
          </p>
          <button className="cs-btn-primary large" onClick={() => setView('form')}>
            ＋ Apply for Credit Score
          </button>
        </div>
        <div className="cs-hero-visual">
          <div className="cs-hero-ring">
            <span>◈</span>
          </div>
        </div>
      </div>

      {/* How it works */}
      <div className="cs-how-grid">
        <div className="cs-how-card">
          <div className="cs-how-num">1</div>
          <b>Share alternative data</b>
          <p>Gig ratings, UPI usage, savings, community scores — information that reflects how you actually manage money.</p>
        </div>
        <div className="cs-how-card">
          <div className="cs-how-num">2</div>
          <b>AI scores your profile</b>
          <p>An XGBoost model trained on 1,50,000 records maps your data to a credit score between 300 and 850.</p>
        </div>
        <div className="cs-how-card">
          <div className="cs-how-num">3</div>
          <b>Instant result</b>
          <p>See your score and risk category immediately. Submit for bank review — no waiting days for a bureau report.</p>
        </div>
      </div>

      {/* Score scale */}
      <div className="cs-scale-row">
        <div className="cs-scale-item" style={{ background: '#e6f4ec', color: '#1a6e40' }}>
          <b>700 – 850</b><small>Low risk</small>
        </div>
        <div className="cs-scale-item" style={{ background: '#fff3e0', color: '#b85c00' }}>
          <b>600 – 699</b><small>Medium risk</small>
        </div>
        <div className="cs-scale-item" style={{ background: '#fdecea', color: '#c62828' }}>
          <b>300 – 599</b><small>High risk</small>
        </div>
      </div>

      {/* Application history */}
      <div className="cs-history-card">
        <div className="cs-history-header">
          <div>
            <h3>Your Applications</h3>
            <p>All credit score applications you have submitted</p>
          </div>
          <button className="cs-btn-primary" onClick={() => setView('form')}>＋ New Application</button>
        </div>

        {loadingApps ? (
          <div className="cs-loading">Loading your applications…</div>
        ) : applications.length === 0 ? (
          <div className="cs-empty">
            <span>◌</span>
            <b>No applications yet</b>
            <small>Click "Apply for Credit Score" to get started without needing a CIBIL history.</small>
          </div>
        ) : (
          <div className="cs-table-wrap">
            <table className="cs-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Amount</th>
                  <th>Credit Score</th>
                  <th>Risk</th>
                  <th>Status</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {applications.map(app => (
                  <tr key={app.application_id}>
                    <td>#{app.application_id}</td>
                    <td style={{ textTransform: 'capitalize' }}>{app.applicant_type}</td>
                    <td>₹{Number(app.requested_amount).toLocaleString('en-IN')}</td>
                    <td>
                      {app.credit_score
                        ? <b style={{ color: getRiskColor(app.risk_category || 'medium'), fontSize: '1.1rem' }}>{Math.round(app.credit_score)}</b>
                        : '—'}
                    </td>
                    <td>
                      {app.risk_category
                        ? <span className={`cs-risk-pill ${app.risk_category}`}>{app.risk_category}</span>
                        : '—'}
                    </td>
                    <td>
                      <span style={{ color: statusColor(app.status), fontWeight: 600, textTransform: 'capitalize' }}>
                        {app.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>{new Date(app.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: '2-digit' })}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <p className="cs-disclaimer">
        ArthSaathi's alternate credit score is powered by machine learning and is not an official CIBIL or bureau score.
        It is designed to help people without traditional credit history. Final lending decisions are made by banks or lenders.
      </p>
    </div>
  );
}
