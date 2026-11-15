import React, { useState, useEffect } from 'react';
import { Blocks, ShieldCheck, Lock, Link as LinkIcon, PlusCircle, RefreshCw } from 'lucide-react';

export default function BlockchainView({ stages }) {
  const [ledger, setLedger] = useState([]);
  const [totalBlocks, setTotalBlocks] = useState(0);
  const [batchId, setBatchId] = useState('HONEY-EXP-2026-01');
  const [selectedStage, setSelectedStage] = useState(stages[0] || 'Solar_Exposed_Transit');
  const [isMining, setIsMining] = useState(false);
  const [miningResult, setMiningResult] = useState(null);

  const fetchLedger = async () => {
    try {
      const res = await fetch('/api/blockchain');
      const data = await res.json();
      setLedger(data.ledger || []);
      setTotalBlocks(data.total_blocks || 0);
    } catch (err) {
      console.error('Failed to load ledger', err);
    }
  };

  useEffect(() => {
    fetchLedger();
  }, []);

  const handleRecordHandoff = async () => {
    setIsMining(true);
    try {
      const res = await fetch('/api/blockchain/record', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch_id: batchId, stage: selectedStage })
      });
      const data = await res.json();
      setMiningResult(data);
      await fetchLedger();
    } catch (err) {
      alert('Mining error: ' + err.message);
    } finally {
      setIsMining(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
          <div>
            <span className="badge badge-purple" style={{ marginBottom: 6 }}>
              Honey Chain Smart Contract Layer
            </span>
            <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>
              Immutable Blockchain Ledger & Automated Regulatory Enforcement
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
              Demonstrates how the SIH Sequence Mining Engine acts as an automated Oracle for Honey Chain. If an incoming handoff creates a critical failure sequence, the smart contract automatically locks escrow funds and halts packaging.
            </p>
          </div>
          <button
            onClick={fetchLedger}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              padding: '8px 12px',
              borderRadius: 8,
              color: 'var(--text-secondary)',
              fontSize: 12,
              fontWeight: 600
            }}
          >
            <RefreshCw size={13} /> Refresh Ledger ({totalBlocks} Blocks)
          </button>
        </div>

        <div style={{
          marginTop: 20,
          background: 'rgba(15, 23, 42, 0.7)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 10,
          padding: 16
        }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: '#cbd5e1', marginBottom: 12 }}>
            Mine New Traceability Handoff on Honey Chain:
          </div>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>
            <div>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Batch ID</label>
              <input
                type="text"
                value={batchId}
                onChange={(e) => setBatchId(e.target.value)}
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#fff',
                  fontSize: 13,
                  outline: 'none',
                  minWidth: 200
                }}
              />
            </div>

            <div>
              <label style={{ fontSize: 11, color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>Handoff Stage Event</label>
              <select
                value={selectedStage}
                onChange={(e) => setSelectedStage(e.target.value)}
                style={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 6,
                  padding: '8px 12px',
                  color: '#fff',
                  fontSize: 13,
                  outline: 'none',
                  minWidth: 240
                }}
              >
                {(stages || []).map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            <div style={{ alignSelf: 'flex-end' }}>
              <button
                onClick={handleRecordHandoff}
                disabled={isMining}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 6,
                  background: 'linear-gradient(135deg, #a855f7, #7c3aed)',
                  color: '#fff',
                  fontWeight: 600,
                  fontSize: 13,
                  padding: '9px 18px',
                  borderRadius: 6,
                  cursor: isMining ? 'not-allowed' : 'pointer',
                  boxShadow: '0 4px 12px rgba(168, 85, 247, 0.3)'
                }}
              >
                <PlusCircle size={15} />
                {isMining ? 'Mining Block...' : 'Commit Block to Honey Chain'}
              </button>
            </div>
          </div>

          {miningResult && (
            <div style={{
              marginTop: 14,
              padding: 12,
              borderRadius: 6,
              background: miningResult.block?.status === 'FLAGGED_HIGH_RISK' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(16, 185, 129, 0.15)',
              border: miningResult.block?.status === 'FLAGGED_HIGH_RISK' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(16, 185, 129, 0.3)',
              fontSize: 13,
              color: miningResult.block?.status === 'FLAGGED_HIGH_RISK' ? '#fca5a5' : '#6ee7b7'
            }}>
              <b>Block #{miningResult.block?.index} Mined:</b> {miningResult.block?.smart_contract_action}
            </div>
          )}
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
        <h4 style={{ fontSize: 16, fontWeight: 700, color: '#fff' }}>
          Cryptographic Honey Chain Ledger ({ledger.length} Verified Blocks):
        </h4>

        {ledger.slice().reverse().map((block) => {
          const isGenesis = block.index === 0;
          const isFlagged = block.status === 'FLAGGED_HIGH_RISK';
          return (
            <div
              key={block.index}
              className="glass-card"
              style={{
                border: isGenesis ? '1px solid rgba(59, 130, 246, 0.4)' : isFlagged ? '1px solid rgba(239, 68, 68, 0.5)' : '1px solid rgba(16, 185, 129, 0.4)',
                background: 'var(--bg-secondary)',
                padding: 16
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Blocks size={18} color={isGenesis ? '#60a5fa' : isFlagged ? '#f87171' : '#34d399'} />
                  <span style={{ fontWeight: 800, fontSize: 14, color: '#fff' }}>
                    Block #{block.index} &bull; Batch: {block.batch_id}
                  </span>
                </div>

                <div>
                  <span className={`badge ${isGenesis ? 'badge-info' : isFlagged ? 'badge-danger' : 'badge-success'}`}>
                    {isFlagged ? <Lock size={11} /> : <ShieldCheck size={11} />}
                    {block.status || 'VERIFIED'}
                  </span>
                </div>
              </div>

              <div style={{ fontSize: 13, color: '#e2e8f0', marginBottom: 10 }}>
                <b>Handoff Event:</b> <span className="seq-code">{block.stage}</span>
                <span style={{ marginLeft: 16, color: 'var(--text-muted)', fontSize: 12 }}>
                  {new Date(block.timestamp * 1000).toLocaleTimeString()}
                </span>
              </div>

              <div style={{
                background: 'rgba(15, 23, 42, 0.8)',
                borderRadius: 6,
                padding: '8px 12px',
                fontSize: 11,
                fontFamily: 'var(--font-mono)',
                color: 'var(--text-secondary)',
                wordBreak: 'break-all',
                marginBottom: 8
              }}>
                <div><b>Current Hash:</b> {block.hash}</div>
                <div style={{ marginTop: 2 }}><b>Previous Hash:</b> {block.previous_hash}</div>
              </div>

              <div style={{ fontSize: 12, color: isFlagged ? '#fbbf24' : '#94a3b8' }}>
                <b>Smart Contract Rule Enforcement:</b> {block.smart_contract_action}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

