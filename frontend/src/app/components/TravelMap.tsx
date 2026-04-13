import { useState, useEffect, useRef } from 'react';
import { MapPin } from 'lucide-react';

export interface Location {
  name: string;
  lat: number;
  lng: number;
  time: string;
  description: string;
}

interface TravelMapProps {
  locations: Location[];
}

export function TravelMap({ locations }: TravelMapProps) {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<any>(null);
  const markersRef = useRef<any[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<number | null>(null);

  // 初始化高德地图
  useEffect(() => {
    if (!mapContainerRef.current || locations.length === 0) return;

    // 检查 AMap 是否已加载
    if (typeof window.AMap === 'undefined') {
      console.error('高德地图 API 未加载');
      return;
    }

    // 计算中心点
    const centerLat = locations.reduce((sum, loc) => sum + loc.lat, 0) / locations.length;
    const centerLng = locations.reduce((sum, loc) => sum + loc.lng, 0) / locations.length;

    // 创建地图实例
    const map = new window.AMap.Map(mapContainerRef.current, {
      zoom: 13,
      center: [centerLng, centerLat], // 高德地图使用 [lng, lat]
      viewMode: '2D',
    });

    mapInstanceRef.current = map;

    // 添加标记
    const markers: any[] = [];
    locations.forEach((loc, index) => {
      const marker = new window.AMap.Marker({
        position: [loc.lng, loc.lat],
        title: loc.name,
        label: {
          content: `<div style="background: white; padding: 2px 6px; border-radius: 4px; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">${index + 1}. ${loc.name}</div>`,
          direction: 'top',
        },
        extData: { index },
      });

      marker.on('click', () => {
        setSelectedLocation(index);
      });

      marker.setMap(map);
      markers.push(marker);
    });

    markersRef.current = markers;

    // 自动调整视野以显示所有标记
    if (markers.length > 0) {
      map.setFitView(markers);
    }

    // 清理函数
    return () => {
      if (map) {
        markers.forEach(marker => marker.setMap(null));
        map.destroy();
      }
    };
  }, [locations]);

  // 当选中地点变化时，更新信息窗口
  useEffect(() => {
    if (!mapInstanceRef.current || selectedLocation === null) return;

    const loc = locations[selectedLocation];
    const map = mapInstanceRef.current;

    // 移除旧的信息窗口
    if ((map as any).infoWindow) {
      (map as any).infoWindow.close();
    }

    // 创建新的信息窗口
    const infoWindow = new window.AMap.InfoWindow({
      content: `
        <div style="padding: 12px; max-width: 280px;">
          <h3 style="margin: 0 0 8px 0; font-size: 16px; color: #333;">${selectedLocation + 1}. ${loc.name}</h3>
          <p style="margin: 0 0 8px 0; font-size: 13px; color: #666;">${loc.time}</p>
          <p style="margin: 0; font-size: 13px; color: #555; line-height: 1.5;">${loc.description}</p>
        </div>
      `,
      offset: new window.AMap.Pixel(0, -30),
    });

    infoWindow.open(map, [loc.lng, loc.lat]);
    (map as any).infoWindow = infoWindow;
  }, [selectedLocation, locations]);

  if (locations.length === 0) {
    return null;
  }

  return (
    <div className="w-full rounded-lg overflow-hidden border border-gray-200 bg-white shadow-sm">
      {/* 地图容器 */}
      <div ref={mapContainerRef} style={{ height: '500px', width: '100%' }} />

      {/* 地点列表 */}
      <div className="p-4 border-t border-gray-200 bg-gray-50">
        <h3 className="font-semibold text-sm text-gray-900 mb-3 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-blue-600" />
          行程景点
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {locations.map((location, index) => (
            <div
              key={index}
              className={`flex items-center gap-3 p-3 rounded-lg transition-all cursor-pointer ${
                selectedLocation === index
                  ? 'bg-blue-50 border border-blue-200'
                  : 'bg-white hover:bg-gray-50 border border-gray-200'
              }`}
              onClick={() => setSelectedLocation(selectedLocation === index ? null : index)}
            >
              <div className="flex-shrink-0 w-7 h-7 bg-red-600 text-white rounded-full flex items-center justify-center text-xs font-bold">
                {index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {location.name}
                </p>
                <p className="text-xs text-gray-500">{location.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
