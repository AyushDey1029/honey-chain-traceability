import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import BenchmarkView from './components/BenchmarkView';
import SimulatorView from './components/SimulatorView';
import BaselinesView from './components/BaselinesView';
import MinedRulesView from './components/MinedRulesView';
import BlockchainView from './components/BlockchainView';

export default function App() {
  const [activeTab, setActiveTab] = useState('benchmark');
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [baselinesData, setBaselinesData] = useState(null);
  const [rulesData, setRulesData] = useState(null);
  const [stages, setStages] = useState([]);
  const [isRetraining, setIsRetraining] = useState(false);
  const [isPredicting, setIsPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);
  const [error, setError] = useState(null);

  const fetchAllData = async () => {
    try {
      const [resBench, resBase, resRules, resStages] = await Promise.all([
        fetch('/api/benchmark').then(r => r.json()),
        fetch('/api/baselines').then(r => r.json()),
        fetch('/api/mined-rules').then(r => r.json()),
        fetch('/api/stages').then(r => r.json()),
      ]);
      setBenchmarkData(resBench);
      setBaselinesData(resBase);
      setRulesData(resRules);
      setStages(resStages.stages || []);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch data from API:', err);
      setError('Could not connect to FastAPI backend on port 8000. Please ensure the backend server is running.');
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      await fetch('/api/retrain', { method: 'POST' });
      await fetchAllData();
      alert('Pipeline successfully retrained! Optimal metrics re-computed.');
    } catch (err) {
      alert('Retrain failed: ' + err.message);
    } finally {
      setIsRetraining(false);
    }
  };

  const handlePredict = async (sequence) => {
    setIsPredicting(true);
    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sequence })
      });
      const data = await res.json();
      setPredictionResult(data);
    } catch (err) {
      alert('Prediction failed: ' + err.message);
    } finally {
      setIsPredicting(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onRetrain={handleRetrain}
        isRetraining={isRetraining}
      />

      <main className="container" style={{ flex: 1, paddingBottom: 48 }}>
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.15)',
            border: '1px solid rgba(239, 68, 68, 0.4)',
            borderRadius: 8,
            padding: 16,
            marginBottom: 20,
            color: '#fca5a5',
            fontSize: 14
          }}>
            <b>Backend Connection Notice:</b> {error}
          </div>
        )}

        {activeTab === 'benchmark' && (
          <BenchmarkView benchmarkData={benchmarkData} />
        )}

        {activeTab === 'simulator' && (
          <SimulatorView
            stages={stages}
            onPredict={handlePredict}
            isPredicting={isPredicting}
            predictionResult={predictionResult}
          />
        )}

        {activeTab === 'baselines' && (
          <BaselinesView baselinesData={baselinesData} />
        )}

        {activeTab === 'rules' && (
          <MinedRulesView rulesData={rulesData} />
        )}

        {activeTab === 'blockchain' && (
          <BlockchainView stages={stages} />
        )}
      </main>

      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        padding: '16px 24px',
        textAlign: 'center',
        fontSize: 12,
        color: 'var(--text-muted)'
      }}>
        Smart India Hackathon 2026 &bull; PS ID: SIH26021 &bull; Honey Chain Traceability & Smart Beekeeping Management &bull; Ministry of MSME
      </footer>
    </div>
  );
}
