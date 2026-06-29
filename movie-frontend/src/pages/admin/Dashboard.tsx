import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminService } from '../../modules/admin/service/AdminService';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';
import { unparse } from 'papaparse';
import {
  Users,
  Film,
  Star,
  Eye,
  Download,
  Calendar,
  Clock,
  TrendingUp
} from 'lucide-react';

const formatDate = (date: Date) => {
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, '0');
  const dd = String(date.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
};

const getDateRange = (preset: "7d" | "30d" | "year" | "custom") => {
  const today = new Date();
  let fromDate = new Date();
  if (preset === '7d') {
    fromDate.setDate(today.getDate() - 6);
  } else if (preset === '30d') {
    fromDate.setDate(today.getDate() - 29);
  } else if (preset === 'year') {
    fromDate = new Date(today.getFullYear(), 0, 1);
  }
  return {
    from: formatDate(fromDate),
    to: formatDate(today)
  };
};

export default function Dashboard() {
  const [activePreset, setActivePreset] = useState<"7d" | "30d" | "year" | "custom">("30d");
  const [dateRange, setDateRange] = useState(() => getDateRange("30d"));

  // Sync date inputs when preset changes
  useEffect(() => {
    if (activePreset !== "custom") {
      setDateRange(getDateRange(activePreset));
    }
  }, [activePreset]);

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['admin-stats', dateRange.from, dateRange.to],
    queryFn: async () => {
      const response = await adminService.getStats(dateRange.from, dateRange.to);
      return response;
    }
  });

  const handleExport = () => {
    if (!stats?.dailyViews || stats.dailyViews.length === 0) return;
    const csvData = stats.dailyViews.map((item: any) => ({
      'Ngày': item.date,
      'Lượt Xem': item.views
    }));
    const csv = unparse(csvData);
    
    // Add BOM for Vietnamese characters Excel support
    const blob = new Blob([new Uint8Array([0xEF, 0xBB, 0xBF]), csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `thong_ke_luot_xem_${dateRange.from}_den_${dateRange.to}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePresetChange = (preset: "7d" | "30d" | "year") => {
    setActivePreset(preset);
  };

  const handleCustomDateChange = (type: "from" | "to", value: string) => {
    setActivePreset("custom");
    setDateRange(prev => ({
      ...prev,
      [type]: value
    }));
  };

  if (isLoading) {
    return (
      <div className="p-6 space-y-8 animate-pulse">
        <div className="h-10 w-64 bg-zinc-800 rounded-lg"></div>
        <div className="h-14 w-full bg-zinc-800 rounded-xl"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-28 bg-zinc-800 rounded-2xl"></div>
          ))}
        </div>
        <div className="h-80 bg-zinc-800 rounded-2xl"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 text-center text-red-500 space-y-4">
        <p className="text-xl font-bold">Lỗi kết nối máy chủ!</p>
        <p className="text-sm text-zinc-400">Vui lòng kiểm tra lại backend và thử lại sau.</p>
      </div>
    );
  }

  const cards = [
    { 
      title: 'Tổng người dùng', 
      value: stats?.totalUsers || 0, 
      icon: <Users className="w-8 h-8 text-blue-400" />, 
      color: 'from-blue-600/20 to-blue-900/5 border-blue-900/30' 
    },
    { 
      title: 'Phim & Series', 
      value: stats?.totalMedia || 0, 
      icon: <Film className="w-8 h-8 text-red-400" />, 
      color: 'from-red-600/20 to-red-900/5 border-red-900/30' 
    },
    { 
      title: 'Lượt đánh giá (Khoảng)', 
      value: stats?.totalRatings || 0, 
      icon: <Star className="w-8 h-8 text-yellow-400" />, 
      color: 'from-yellow-600/20 to-yellow-900/5 border-yellow-900/30' 
    },
    { 
      title: 'Lượt xem hôm nay', 
      value: stats?.viewsToday || 0, 
      icon: <Eye className="w-8 h-8 text-green-400" />, 
      color: 'from-green-600/20 to-green-900/5 border-green-900/30' 
    },
  ];

  return (
    <div className="p-6 space-y-8 min-h-screen text-white bg-[#0a0a0a]">
      {/* Header Row */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
            Bảng điều khiển Admin
          </h1>
          <p className="text-zinc-400 text-sm mt-1">
            Theo dõi hiệu suất và số liệu hoạt động của hệ thống
          </p>
        </div>

        <button
          onClick={handleExport}
          disabled={!stats?.dailyViews || stats.dailyViews.length === 0}
          className="flex items-center gap-2 px-5 py-2.5 bg-red-600 hover:bg-red-700 disabled:bg-zinc-800 disabled:text-zinc-500 disabled:cursor-not-allowed transition-all duration-300 font-semibold rounded-xl text-sm shadow-lg shadow-red-600/20"
        >
          <Download className="w-4 h-4" />
          Xuất báo cáo CSV
        </button>
      </div>

      {/* Filter Row */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 bg-zinc-900/50 border border-zinc-800 rounded-2xl backdrop-blur-xl">
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-zinc-400" />
          <span className="text-sm font-medium text-zinc-300 mr-2">Bộ lọc nhanh:</span>
          <div className="flex bg-zinc-950 p-1 rounded-xl border border-zinc-800">
            <button
              onClick={() => handlePresetChange("7d")}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-200 ${
                activePreset === "7d"
                  ? "bg-red-600 text-white shadow-md"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              7 Ngày
            </button>
            <button
              onClick={() => handlePresetChange("30d")}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-200 ${
                activePreset === "30d"
                  ? "bg-red-600 text-white shadow-md"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              30 Ngày
            </button>
            <button
              onClick={() => handlePresetChange("year")}
              className={`px-4 py-1.5 text-xs font-semibold rounded-lg transition-all duration-200 ${
                activePreset === "year"
                  ? "bg-red-600 text-white shadow-md"
                  : "text-zinc-400 hover:text-white"
              }`}
            >
              Năm Nay
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2 text-zinc-300 text-sm">
          <span>Từ</span>
          <input
            type="date"
            value={dateRange.from}
            onChange={(e) => handleCustomDateChange("from", e.target.value)}
            className="bg-zinc-950 border border-zinc-800 text-white rounded-xl px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-red-600 transition-all duration-200"
          />
          <span>Đến</span>
          <input
            type="date"
            value={dateRange.to}
            onChange={(e) => handleCustomDateChange("to", e.target.value)}
            className="bg-zinc-950 border border-zinc-800 text-white rounded-xl px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-red-600 transition-all duration-200"
          />
        </div>
      </div>

      {/* Stats Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, i) => (
          <div
            key={i}
            className={`bg-gradient-to-br ${card.color} p-6 rounded-2xl border flex items-center justify-between shadow-xl transition-all duration-300 hover:scale-[1.02] hover:-translate-y-0.5`}
          >
            <div>
              <p className="text-zinc-400 text-xs font-semibold uppercase tracking-wider">
                {card.title}
              </p>
              <p className="text-white text-3xl font-extrabold mt-2">
                {card.value.toLocaleString()}
              </p>
            </div>
            <div className="p-3 bg-zinc-950/40 border border-zinc-800/50 rounded-xl">
              {card.icon}
            </div>
          </div>
        ))}
      </div>

      {/* Chart and Recent Movies Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chart Column (2/3 width) */}
        <div className="lg:col-span-2 bg-zinc-900/30 border border-zinc-800 p-6 rounded-2xl flex flex-col justify-between shadow-xl backdrop-blur-xl">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-red-500" />
              <h2 className="text-lg font-bold text-white">Xu hướng lượt xem</h2>
            </div>
            <span className="text-xs text-zinc-500">
              {dateRange.from} đến {dateRange.to}
            </span>
          </div>

          <div className="h-80 w-full">
            {stats?.dailyViews && stats.dailyViews.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats.dailyViews} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4} />
                      <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis
                    dataKey="date"
                    stroke="#71717a"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                  />
                  <YAxis
                    stroke="#71717a"
                    fontSize={11}
                    tickLine={false}
                    axisLine={false}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#18181b',
                      borderColor: '#27272a',
                      borderRadius: '12px',
                      color: '#ffffff'
                    }}
                    labelStyle={{ color: '#a1a1aa', fontWeight: 'bold' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="views"
                    name="Lượt xem"
                    stroke="#ef4444"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorViews)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 italic text-sm border border-dashed border-zinc-800 rounded-xl">
                Không có dữ liệu lượt xem trong khoảng thời gian này.
              </div>
            )}
          </div>
        </div>

        {/* Recent Movies Column (1/3 width) */}
        <div className="bg-zinc-900/30 border border-zinc-800 p-6 rounded-2xl flex flex-col shadow-xl backdrop-blur-xl">
          <div className="flex items-center gap-2 mb-6">
            <Clock className="w-5 h-5 text-red-500" />
            <h2 className="text-lg font-bold text-white">Phim mới thêm gần đây</h2>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto max-h-[320px] pr-2 scrollbar-thin">
            {stats?.recentMovies && stats.recentMovies.length > 0 ? (
              stats.recentMovies.map((movie: any) => (
                <div
                  key={movie.id}
                  className="flex justify-between items-center p-3 bg-zinc-950/40 border border-zinc-800/30 hover:border-zinc-800/80 rounded-xl transition-all duration-200"
                >
                  <div className="truncate pr-4">
                    <p className="text-sm font-semibold text-zinc-200 truncate">{movie.title}</p>
                    <p className="text-xs text-zinc-500 mt-0.5">ID: {movie.id}</p>
                  </div>
                  <span className="flex-shrink-0 text-xs px-2.5 py-1 bg-zinc-800/60 text-zinc-400 border border-zinc-700/30 rounded-lg">
                    {movie.releaseDate}
                  </span>
                </div>
              ))
            ) : (
              <div className="h-full flex items-center justify-center text-zinc-500 italic text-sm">
                Chưa có phim mới được thêm.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}