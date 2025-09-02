import React, { useState } from 'react';

const TestMultipleDevices: React.FC = () => {
  const [devicesToAdd, setDevicesToAdd] = useState<string[]>([]);
  const [newDevice, setNewDevice] = useState('');
  const [debugInfo, setDebugInfo] = useState<any>({});

  const handleAddDevice = () => {
    if (newDevice.trim()) {
      // カンマ区切りで複数機種を処理（全角カンマ、全角スペースにも対応）
      const normalizedInput = newDevice
        .replace(/，/g, ',')  // 全角カンマを半角に
        .replace(/　/g, ' '); // 全角スペースを半角に
      
      const devices = normalizedInput.split(',').map(d => d.trim()).filter(d => d);
      
      const debug = {
        originalInput: newDevice,
        normalizedInput: normalizedInput,
        devices: devices,
        devicesLength: devices.length
      };
      setDebugInfo(debug);
      console.log('[DEBUG] handleAddDevice:', debug);
      
      // 単一デバイスの場合
      if (devices.length === 1) {
        console.log('[DEBUG] Single device - would show database dialog');
      } else {
        // 複数デバイスの場合は直接追加
        console.log('[DEBUG] Multiple devices - adding directly');
        const uniqueNewDevices = devices.filter(d => !devicesToAdd.includes(d));
        console.log('[DEBUG] uniqueNewDevices:', uniqueNewDevices);
        if (uniqueNewDevices.length > 0) {
          setDevicesToAdd(prev => {
            const updated = [...prev, ...uniqueNewDevices];
            console.log('[DEBUG] Updated devicesToAdd:', updated);
            return updated;
          });
          setNewDevice('');
        }
      }
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>複数機種追加テスト</h2>
      
      <div>
        <input
          type="text"
          value={newDevice}
          onChange={(e) => setNewDevice(e.target.value)}
          placeholder="例: test1, test2, test3"
          style={{ width: '300px', padding: '8px' }}
        />
        <button onClick={handleAddDevice} style={{ marginLeft: '10px', padding: '8px 16px' }}>
          追加
        </button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <h3>追加予定の機種: ({devicesToAdd.length}個)</h3>
        {devicesToAdd.length === 0 ? (
          <p>まだ追加する機種がありません</p>
        ) : (
          <ul>
            {devicesToAdd.map(device => (
              <li key={device}>{device}</li>
            ))}
          </ul>
        )}
      </div>

      <div style={{ marginTop: '20px', background: '#f0f0f0', padding: '10px' }}>
        <h3>デバッグ情報:</h3>
        <pre>{JSON.stringify(debugInfo, null, 2)}</pre>
      </div>
    </div>
  );
};

export default TestMultipleDevices;