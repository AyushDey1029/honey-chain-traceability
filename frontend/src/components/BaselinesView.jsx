import React from 'react';
import { Activity, AlertTriangle, CheckCircle } from 'lucide-react';

export default function BaselinesView({ baselinesData }) {
  if (!baselinesData) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-secondary)' }}>Loading stage baselines...</div>;
  }

  const { overall_baseline_failure_rate, stage_baselines } = baselinesData;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <span className="badge badge-honey" style={{ marginBottom: 6 }}>SIH Mandatory Requirement</span>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>
              Unconditional Per-Stage Baseline Failure Rates
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
              Formula: P(Quality_Failure = 1 | Stage &isin; Sequence). Calculates isolated failure likelihood when each handoff event occurs anywhere in a batch's journey.
            </p>
          </div>
          <div style={{
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 8,
            padding: '10px 16px',
            textAlign: 'right'
          }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>Dataset Baseline (Threshold)</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#f87171' }}>
              {(overall_baseline_failure_rate * 100).toFixed(2)}%
            </div>
          </div>
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Handoff Stage</th>
              <th>Total Batches</th>
              <th>Failed Batches</th>
              <th>Baseline Failure Rate</th>
              <th>Failure Probability vs Benchmark</th>
              <th>Risk Assessment</th>
            </tr>
          </thead>
          <tbody>
            {(stage_baselines || []).map((row) => {
              const ratePct = (row.Baseline_Failure_Rate * 100).toFixed(2);
              const isHigh = row.Elevated_Risk;
              const barWidth = Math.min(100, (row.Baseline_Failure_Rate / 0.6) * 100);
              return (
                <tr key={row.Stage}>
                  <td>
                    <span style={{ fontWeight: 600, color: '#f8fafc' }}>{row.Stage}</span>
                  </td>
                  <td>{row.Total_Batches}</td>
                  <td>{row.Failed_Batches}</td>
                  <td>
                    <span style={{
                      fontWeight: 700,
                      color: isHigh ? '#f87171' : '#34d399'
                    }}>
                      {ratePct}%
                    </span>
                  </td>
                  <td style={{ minWidth: 200 }}>
                    <div style={{
                      background: 'rgba(15, 23, 42, 0.8)',
                      borderRadius: 999,
                      height: 8,
                      width: '100%',
                      overflow: 'hidden',
                      position: 'relative'
                    }}>
                      <div style={{
                        background: isHigh ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : '#3b82f6',
                        height: '100%',
                        width: `${barWidth}%`,
                        borderRadius: 999
                      }} />
                    </div>
                  </td>
                  <td>
                    {isHigh ? (
                      <span className="badge badge-danger">
                        <AlertTriangle size={10} /> Above Baseline
                      </span>
                    ) : (
                      <span className="badge badge-success">
                        <CheckCircle size={10} /> Below Baseline
                      </span>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

