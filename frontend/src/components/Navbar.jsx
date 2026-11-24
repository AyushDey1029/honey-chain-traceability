import React from 'react';
import { Database, Activity, GitFork, RefreshCw, Layers } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onRetrain, isRetraining }) {
  const tabs = [
    { id: 'benchmark', label: 'Model Benchmark & Story', icon: Layers },
    { id: 'simulator', label: 'Interactive Pathway Simulator', icon: GitFork },
    { id: 'baselines', label: 'Per-Stage Baselines', icon: Activity },
    { id: 'rules', label: 'Mined Risk Sequences', icon: Database },
  ];

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(10, 15, 29, 0.95)',
      backdropFilter: 'blur(8px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '14px 24px'
    }}>
      <div style={{
        maxWidth: 1300,
        margin: '0 auto',
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{
            background: 'linear-gradient(135deg, #f59e0b, #ef4444)',
            width: 36,
            height: 36,
            borderRadius: 8,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            fontWeight: 800,
            fontSize: 18,
            boxShadow: '0 2px 10px rgba(245, 158, 11, 0.4)'
          }}>
            H
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: '0.3px', color: '#fff' }}>
                Honey Chain Sequence Discovery
              </span>
              <span className="badge badge-honey">SIH 2026 // SIH26021</span>
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
              Supply Chain Quality Failure Mining | Ministry of MSME
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
          <nav style={{
            display: 'flex',
            background: 'var(--bg-secondary)',
            padding: 4,
            borderRadius: 8,
            border: '1px solid var(--border-subtle)'
          }}>
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '8px 14px',
                    borderRadius: 6,
                    fontSize: 13,
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? '#fff' : 'var(--text-secondary)',
                    background: isActive ? 'var(--bg-card)' : 'transparent',
                    border: isActive ? '1px solid var(--border-subtle)' : '1px solid transparent',
                    boxShadow: isActive ? '0 2px 8px rgba(0,0,0,0.2)' : 'none',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <Icon size={14} color={isActive ? '#f59e0b' : 'currentColor'} />
                  {tab.label}
                </button>
              );
            })}
          </nav>

          <button
            onClick={onRetrain}
            disabled={isRetraining}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              padding: '8px 12px',
              borderRadius: 8,
              color: 'var(--text-primary)',
              fontSize: 12,
              fontWeight: 600,
              cursor: isRetraining ? 'not-allowed' : 'pointer',
              opacity: isRetraining ? 0.6 : 1
            }}
            title="Retrain all 3 models & recompute metrics"
          >
            <RefreshCw size={13} style={{ animation: isRetraining ? 'spin 1s linear infinite' : 'none' }} />
            {isRetraining ? 'Retraining...' : 'Retrain Pipeline'}
          </button>
        </div>
      </div>
    </header>
  );
}
