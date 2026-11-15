import React, { useState } from 'react';
import { Play, RotateCcw, AlertOctagon, CheckCircle, ArrowRight, Zap, Shield } from 'lucide-react';

export default function SimulatorView({ stages, onPredict, isPredicting, predictionResult }) {
  const [currentSequence, setCurrentSequence] = useState([
    'Solar_Exposed_Transit',
    'High_Heat_Liquefaction',
    'Cold_Storage_Holding',
    'Bulk_Export_Drumming'
  ]);

  const presets = [
    {
      title: 'Preset 1: Critical Thermal Failure Chain',
      desc: 'Initiated by Solar Transit followed by High Heat Liquefaction',
      seq: ['Solar_Exposed_Transit', 'High_Heat_Liquefaction', 'Cold_Storage_Holding', 'Bulk_Export_Drumming']
    },
    {
      title: 'Preset 2: Clean Traceable Pathway (Certified)',
      desc: 'Cold chain transit, vacuum dehydration, NMR testing passed',
      seq: ['Apiary_Harvest_Modern', 'Cold_Chain_Transit', 'Vacuum_Dehydration', 'NMR_Testing_Passed', 'Glass_Jar_Bottling']
    },
    {
      title: 'Preset 3: Testing Bypassed Risk',
      desc: 'Ambient warehouse with testing skipped prior to bottling',
      seq: ['Cooperative_Collection', 'Ambient_Trucking', 'Gentle_Centrifugation', 'Ambient_Warehouse', 'Testing_Bypassed', 'Glass_Jar_Bottling']
    }
  ];

  const handleAddStage = (stage) => {
    setCurrentSequence([...currentSequence, stage]);
  };

  const handleRemoveStage = (index) => {
    const updated = [...currentSequence];
    updated.splice(index, 1);
    setCurrentSequence(updated);
  };

  const handleClear = () => {
    setCurrentSequence([]);
  };

  const handleAnalyze = () => {
    if (currentSequence.length === 0) return;
    onPredict(currentSequence);
  };

  const earliestNode = predictionResult?.earliest_predictive_handoff;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 16 }}>
          <div>
            <span className="badge badge-info" style={{ marginBottom: 6 }}>Faculty Demonstration Tool</span>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>
              Interactive Supply Chain Pathway Simulator
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
              Click any stage below to construct a real-world handling sequence. Test how all 3 models react and observe whether the engine detects the <b>Earliest Predictive Handoff</b>.
            </p>
          </div>
        </div>

        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8 }}>
            ONE-CLICK FACULTY DEMO PRESETS:
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 10 }}>
            {presets.map((p, idx) => (
              <button
                key={idx}
                onClick={() => setCurrentSequence(p.seq)}
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 8,
                  padding: '10px 14px',
                  textAlign: 'left',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => e.currentTarget.style.borderColor = '#f59e0b'}
                onMouseLeave={(e) => e.currentTarget.style.borderColor = 'var(--border-subtle)'}
              >
                <div style={{ fontSize: 13, fontWeight: 600, color: '#f1f5f9' }}>{p.title}</div>
                <div style={{ fontSize: 11, color: 'var(--text-secondary)', marginTop: 2 }}>{p.desc}</div>
              </button>
            ))}
          </div>
        </div>

        <div style={{
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 10,
          padding: 16,
          marginBottom: 20
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: '#cbd5e1' }}>
              Constructed Handoff Sequence ({currentSequence.length} Steps):
            </span>
            {currentSequence.length > 0 && (
              <button onClick={handleClear} style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: '#f87171' }}>
                <RotateCcw size={12} /> Clear Sequence
              </button>
            )}
          </div>

          {currentSequence.length === 0 ? (
            <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: 13 }}>
              No stages selected. Click on the stages below or choose a preset above to begin.
            </div>
          ) : (
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8 }}>
              {currentSequence.map((stage, idx) => {
                const isEarliest = earliestNode && stage === earliestNode;
                return (
                  <React.Fragment key={idx}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      background: isEarliest ? 'rgba(239, 68, 68, 0.25)' : 'var(--bg-secondary)',
                      border: isEarliest ? '2px solid #ef4444' : '1px solid var(--border-subtle)',
                      padding: '6px 12px',
                      borderRadius: 8,
                      fontSize: 12,
                      fontWeight: isEarliest ? 700 : 500,
                      color: isEarliest ? '#fca5a5' : '#f8fafc',
                      boxShadow: isEarliest ? '0 0 15px rgba(239, 68, 68, 0.4)' : 'none'
                    }}
                    className={isEarliest ? 'pulse-red' : ''}
                    >
                      <span>{idx + 1}. {stage}</span>
                      {isEarliest && (
                        <span style={{
                          background: '#ef4444',
                          color: '#fff',
                          fontSize: 9,
                          fontWeight: 800,
                          padding: '1px 5px',
                          borderRadius: 4,
                          textTransform: 'uppercase'
                        }}>
                          ROOT TRIGGER
                        </span>
                      )}
                      <button
                        onClick={() => handleRemoveStage(idx)}
                        style={{ color: 'var(--text-muted)', fontSize: 14, marginLeft: 4, cursor: 'pointer' }}
                        title="Remove stage"
                      >
                        &times;
                      </button>
                    </div>
                    {idx < currentSequence.length - 1 && (
                      <ArrowRight size={14} color="var(--text-muted)" />
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          )}

          <div style={{ marginTop: 16, display: 'flex', gap: 10 }}>
            <button
              onClick={handleAnalyze}
              disabled={isPredicting || currentSequence.length === 0}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                background: currentSequence.length === 0 ? 'var(--bg-secondary)' : 'linear-gradient(135deg, #f59e0b, #d97706)',
                color: currentSequence.length === 0 ? 'var(--text-muted)' : '#000',
                fontWeight: 700,
                fontSize: 14,
                padding: '10px 20px',
                borderRadius: 8,
                boxShadow: currentSequence.length === 0 ? 'none' : '0 4px 15px rgba(245, 158, 11, 0.3)',
                cursor: currentSequence.length === 0 ? 'not-allowed' : 'pointer'
              }}
            >
              <Zap size={16} />
              {isPredicting ? 'Evaluating Across 3 Models...' : 'Analyze Sequence Across All Models'}
            </button>
          </div>
        </div>

        <div>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', marginBottom: 8 }}>
            AVAILABLE HANDOFF STAGES (CLICK TO APPEND TO CHAIN):
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {(stages || []).map((stage) => (
              <button
                key={stage}
                onClick={() => handleAddStage(stage)}
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 6,
                  padding: '6px 10px',
                  fontSize: 12,
                  color: 'var(--text-secondary)',
                  transition: 'all 0.15s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = '#38bdf8';
                  e.currentTarget.style.color = '#fff';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-subtle)';
                  e.currentTarget.style.color = 'var(--text-secondary)';
                }}
              >
                + {stage}
              </button>
            ))}
          </div>
        </div>
      </div>

      {predictionResult && (
        <div className="glass-card" style={{ border: '1px solid rgba(245, 158, 11, 0.4)' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 12,
            borderBottom: '1px solid var(--border-subtle)',
            paddingBottom: 16,
            marginBottom: 20
          }}>
            <div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Multi-Model Consensus Evaluation
              </div>
              <h3 style={{ fontSize: 20, fontWeight: 700, color: '#fff', marginTop: 2, display: 'flex', alignItems: 'center', gap: 8 }}>
                {predictionResult.consensus_risk === 'HIGH_RISK' ? (
                  <>
                    <AlertOctagon size={22} color="#ef4444" />
                    <span style={{ color: '#ef4444' }}>CRITICAL DOWNSTREAM FAILURE DETECTED</span>
                  </>
                ) : (
                  <>
                    <CheckCircle size={22} color="#10b981" />
                    <span style={{ color: '#10b981' }}>COMPLIANT TRACEABILITY SEQUENCE</span>
                  </>
                )}
              </h3>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Average Predicted Failure Probability</div>
              <div style={{
                fontSize: 22,
                fontWeight: 800,
                color: predictionResult.average_failure_probability >= 0.5 ? '#f87171' : '#34d399'
              }}>
                {(predictionResult.average_failure_probability * 100).toFixed(1)}%
              </div>
            </div>
          </div>

          {predictionResult.earliest_predictive_handoff && (
            <div style={{
              background: 'rgba(239, 68, 68, 0.1)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 8,
              padding: 14,
              marginBottom: 20,
              display: 'flex',
              alignItems: 'flex-start',
              gap: 12
            }}>
              <Shield size={20} color="#f87171" style={{ marginTop: 2, flexShrink: 0 }} />
              <div>
                <div style={{ fontWeight: 700, color: '#f87171', fontSize: 14 }}>
                  Earliest Predictive Handoff Identified: "{predictionResult.earliest_predictive_handoff}"
                </div>
                <div style={{ fontSize: 13, color: '#e2e8f0', marginTop: 4 }}>
                  {predictionResult.model_comparisons?.model_3_prefixspan?.explanation}
                </div>
                <div style={{
                  marginTop: 8,
                  paddingTop: 8,
                  borderTop: '1px solid rgba(239, 68, 68, 0.2)',
                  fontSize: 12,
                  color: '#fbbf24',
                  fontWeight: 600
                }}>
                  Automated Smart Contract Trigger: {predictionResult.smart_contract_recommendation}
                </div>
              </div>
            </div>
          )}

          <div style={{ fontSize: 13, fontWeight: 700, color: '#fff', marginBottom: 12 }}>
            Side-by-Side Model Diagnostics:
          </div>

          <div className="grid-3">
            <div style={{ background: 'var(--bg-secondary)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>MODEL 1 (UNORDERED BAG-OF-STAGES)</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6, marginBottom: 8 }}>
                <span className={`badge ${predictionResult.model_comparisons?.model_1_baseline?.risk_status === 'HIGH_RISK' ? 'badge-danger' : 'badge-success'}`}>
                  {predictionResult.model_comparisons?.model_1_baseline?.risk_status}
                </span>
                <span style={{ fontSize: 15, fontWeight: 700, color: '#cbd5e1' }}>
                  {(predictionResult.model_comparisons?.model_1_baseline?.failure_probability * 100).toFixed(1)}% Prob
                </span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                <b>Limitation:</b> {predictionResult.model_comparisons?.model_1_baseline?.limitation}
              </div>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: 16, borderRadius: 8, border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>MODEL 2 (SEQUENTIAL N-GRAM ML)</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6, marginBottom: 8 }}>
                <span className={`badge ${predictionResult.model_comparisons?.model_2_ngram?.risk_status === 'HIGH_RISK' ? 'badge-danger' : 'badge-success'}`}>
                  {predictionResult.model_comparisons?.model_2_ngram?.risk_status}
                </span>
                <span style={{ fontSize: 15, fontWeight: 700, color: '#cbd5e1' }}>
                  {(predictionResult.model_comparisons?.model_2_ngram?.failure_probability * 100).toFixed(1)}% Prob
                </span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', lineHeight: 1.4 }}>
                <b>Sequential Detection:</b> {predictionResult.model_comparisons?.model_2_ngram?.strength}
              </div>
            </div>

            <div style={{ background: 'var(--bg-secondary)', padding: 16, borderRadius: 8, border: '1px solid rgba(245, 158, 11, 0.4)' }}>
              <div style={{ fontSize: 11, color: '#f59e0b', fontWeight: 700 }}>MODEL 3 (PREFIXSPAN DISCOVERY)</div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6, marginBottom: 8 }}>
                <span className={`badge ${predictionResult.model_comparisons?.model_3_prefixspan?.risk_status === 'CRITICAL_RISK' ? 'badge-danger' : 'badge-success'}`}>
                  {predictionResult.model_comparisons?.model_3_prefixspan?.risk_status}
                </span>
                <span style={{ fontSize: 15, fontWeight: 700, color: '#f59e0b' }}>
                  {(predictionResult.model_comparisons?.model_3_prefixspan?.failure_probability * 100).toFixed(1)}% Prob
                </span>
              </div>
              <div style={{ fontSize: 11, color: '#94a3b8', lineHeight: 1.4 }}>
                <b>White-Box Lift:</b> {predictionResult.model_comparisons?.model_3_prefixspan?.worst_rule?.lift ? `${predictionResult.model_comparisons?.model_3_prefixspan?.worst_rule?.lift}x Baseline Risk` : 'Within safe tolerance'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

