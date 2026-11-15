import React, { useState } from 'react';
import { Search, Flame, ShieldAlert } from 'lucide-react';

export default function MinedRulesView({ rulesData }) {
  const [searchTerm, setSearchTerm] = useState('');

  if (!rulesData) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-secondary)' }}>Loading mined rules...</div>;
  }

  const { mined_rules, earliest_predictive_handoff, highest_risk_sequence } = rulesData;

  const filteredRules = (mined_rules || []).filter(r =>
    r.sequence.toLowerCase().includes(searchTerm.toLowerCase()) ||
    r.earliest_predictive_handoff.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <span className="badge badge-danger" style={{ marginBottom: 6 }}>PrefixSpan Sequential Mining Output</span>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>
              Ranked Critical Handling Risk Sequences (Lift &gt; 1.4)
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
              Discovered chronological subsequences associated with downstream quality problems. Ranked strictly by Lift and Support.
            </p>
          </div>

          <div style={{ display: 'flex', gap: 12 }}>
            <div style={{
              background: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: 8,
              padding: '10px 14px'
            }}>
              <div style={{ fontSize: 11, color: '#fca5a5' }}>Global Earliest Predictive Handoff</div>
              <div style={{ fontSize: 14, fontWeight: 700, color: '#f87171' }}>{earliest_predictive_handoff}</div>
            </div>
          </div>
        </div>

        <div style={{ marginTop: 16, position: 'relative' }}>
          <Search size={16} color="var(--text-muted)" style={{ position: 'absolute', left: 12, top: 12 }} />
          <input
            type="text"
            placeholder="Search by stage name (e.g. Solar, Liquefaction, Warehouse)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 8,
              padding: '10px 12px 10px 36px',
              color: '#fff',
              fontSize: 13,
              outline: 'none'
            }}
          />
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Handling Sequence Pathway</th>
              <th>Earliest Predictive Handoff</th>
              <th>Length</th>
              <th>Support (Batches)</th>
              <th>Confidence P(Fail|Seq)</th>
              <th>Lift Multiplier</th>
            </tr>
          </thead>
          <tbody>
            {filteredRules.map((rule, idx) => {
              const isTop = idx < 3;
              return (
                <tr key={idx} style={{ background: isTop ? 'rgba(245, 158, 11, 0.04)' : 'transparent' }}>
                  <td>
                    <span style={{ fontWeight: 700, color: isTop ? '#f59e0b' : 'var(--text-muted)' }}>
                      #{idx + 1}
                    </span>
                  </td>
                  <td>
                    <span className="seq-code" style={{ color: isTop ? '#fbbf24' : '#e2e8f0' }}>
                      {rule.sequence}
                    </span>
                  </td>
                  <td>
                    <span className="badge badge-danger">
                      <ShieldAlert size={11} /> {rule.earliest_predictive_handoff}
                    </span>
                  </td>
                  <td>{rule.sequence_length} nodes</td>
                  <td>
                    <span style={{ color: '#cbd5e1' }}>
                      {(rule.support * 100).toFixed(2)}% ({rule.support_count})
                    </span>
                  </td>
                  <td>
                    <span style={{ fontWeight: 700, color: '#38bdf8' }}>
                      {(rule.confidence * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                      <span style={{
                        fontWeight: 800,
                        fontSize: 14,
                        color: rule.lift >= 2.5 ? '#ef4444' : rule.lift >= 1.8 ? '#f59e0b' : '#38bdf8'
                      }}>
                        {rule.lift.toFixed(2)}x
                      </span>
                      {rule.lift >= 2.5 && <Flame size={14} color="#ef4444" />}
                    </div>
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

