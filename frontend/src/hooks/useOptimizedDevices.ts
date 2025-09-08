/**
 * 最適化されたデバイス管理フック
 * - メモ化
 * - 仮想スクロール対応
 * - デバウンス処理
 */

import { useState, useEffect, useMemo, useCallback, useRef } from 'react';

interface Device {
  name: string;
  attribute?: string;
  selected?: boolean;
}

interface UseOptimizedDevicesProps {
  initialDevices?: Device[];
  onUpdate?: (devices: Device[]) => void;
  virtualScrollEnabled?: boolean;
  itemHeight?: number;
}

// 簡易デバウンス実装
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): T & { cancel: () => void } {
  let timeout: ReturnType<typeof setTimeout> | null = null;
  
  const debounced = ((...args: Parameters<T>) => {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  }) as T;
  
  (debounced as any).cancel = () => {
    if (timeout) clearTimeout(timeout);
  };
  
  return debounced as T & { cancel: () => void };
}

export const useOptimizedDevices = ({
  initialDevices = [],
  onUpdate,
  virtualScrollEnabled = true,
  itemHeight = 48
}: UseOptimizedDevicesProps) => {
  const [devices, setDevices] = useState<Device[]>(initialDevices);
  const [filter, setFilter] = useState('');
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 50 });
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // デバウンス処理されたフィルタ更新
  const debouncedSetFilter = useMemo(
    () => debounce((value: string) => setFilter(value), 300),
    []
  );

  // フィルタリングされたデバイス（メモ化）
  const filteredDevices = useMemo(() => {
    if (!filter) return devices;
    
    const lowerFilter = filter.toLowerCase();
    return devices.filter(device => 
      device.name.toLowerCase().includes(lowerFilter) ||
      device.attribute?.toLowerCase().includes(lowerFilter)
    );
  }, [devices, filter]);

  // 仮想スクロール用の可視デバイス
  const visibleDevices = useMemo(() => {
    if (!virtualScrollEnabled) return filteredDevices;
    
    return filteredDevices.slice(visibleRange.start, visibleRange.end);
  }, [filteredDevices, visibleRange, virtualScrollEnabled]);

  // 選択状態の一括変更（最適化）
  const toggleSelection = useCallback((deviceName: string) => {
    setDevices(prev => {
      const newDevices = [...prev];
      const index = newDevices.findIndex(d => d.name === deviceName);
      if (index !== -1) {
        newDevices[index] = {
          ...newDevices[index],
          selected: !newDevices[index].selected
        };
      }
      return newDevices;
    });
  }, []);

  // 全選択/全解除（最適化）
  const toggleAll = useCallback((selected: boolean) => {
    setDevices(prev => prev.map(device => ({ ...device, selected })));
  }, []);

  // バッチ更新
  const batchUpdate = useCallback((updates: Map<string, Partial<Device>>) => {
    setDevices(prev => {
      const newDevices = [...prev];
      updates.forEach((update, deviceName) => {
        const index = newDevices.findIndex(d => d.name === deviceName);
        if (index !== -1) {
          newDevices[index] = { ...newDevices[index], ...update };
        }
      });
      return newDevices;
    });
  }, []);

  // スクロールハンドラー（仮想スクロール用）
  const handleScroll = useCallback(() => {
    if (!scrollContainerRef.current || !virtualScrollEnabled) return;

    const container = scrollContainerRef.current;
    const scrollTop = container.scrollTop;
    const containerHeight = container.clientHeight;

    const start = Math.floor(scrollTop / itemHeight);
    const visibleCount = Math.ceil(containerHeight / itemHeight);
    const end = Math.min(start + visibleCount + 10, filteredDevices.length);

    setVisibleRange({ start: Math.max(0, start - 5), end });
  }, [itemHeight, filteredDevices.length, virtualScrollEnabled]);

  // スクロールイベントのデバウンス
  const debouncedHandleScroll = useMemo(
    () => debounce(handleScroll, 50),
    [handleScroll]
  );

  // 更新通知（デバウンス）
  const debouncedOnUpdate = useMemo(
    () => onUpdate ? debounce(onUpdate, 500) : undefined,
    [onUpdate]
  );

  useEffect(() => {
    if (debouncedOnUpdate) {
      debouncedOnUpdate(devices);
    }
  }, [devices, debouncedOnUpdate]);

  // メモリクリーンアップ
  useEffect(() => {
    return () => {
      debouncedSetFilter.cancel();
      if (debouncedOnUpdate) {
        debouncedOnUpdate.cancel();
      }
      debouncedHandleScroll.cancel();
    };
  }, [debouncedSetFilter, debouncedOnUpdate, debouncedHandleScroll]);

  return {
    devices: visibleDevices,
    allDevices: devices,
    filteredDevices,
    filter,
    setFilter: debouncedSetFilter,
    toggleSelection,
    toggleAll,
    batchUpdate,
    scrollContainerRef,
    handleScroll: debouncedHandleScroll,
    totalCount: filteredDevices.length,
    selectedCount: devices.filter(d => d.selected).length,
    containerStyle: virtualScrollEnabled ? {
      height: `${filteredDevices.length * itemHeight}px`,
      position: 'relative' as const
    } : {},
    itemStyle: virtualScrollEnabled ? {
      position: 'absolute' as const,
      height: `${itemHeight}px`,
      width: '100%'
    } : {}
  };
};