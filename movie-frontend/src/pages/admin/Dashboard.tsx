import { useQuery } from '@tanstack/react-query';
import { API_ENDPOINTS } from '../../constants/ApiEndpoints';

export default function Dashboard() {
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['admin-stats'],
    queryFn: async () => {
      const res = await fetch(API_ENDPOINTS.ADMIN.DASHBOARD, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem("token")}`
        }
      });

      if (!res.ok) {
        throw new Error(`Dashboard request failed: ${res.status}`);
      }
      return res.json();
    }
  });

  if (isLoading) return <div className="p-6 text-white animate-pulse">Đang tải dữ liệu...</div>;
  if (error) return <div className="p-6 text-red-500">Lỗi kết nối server!</div>;

  const cards = [
    { title: 'Tổng người dùng', value: stats?.totalUsers || 0, icon: '', color: 'bg-blue-600' },
    { title: 'Phim & Series', value: stats?.totalMedia || 0, icon: '', color: 'bg-red-600' },
    { title: 'Lượt đánh giá', value: stats?.totalRatings || 0, icon: '', color: 'bg-yellow-600' },
    { title: 'Lượt xem hôm nay', value: stats?.viewsToday || 0, icon: '', color: 'bg-green-600' },
  ];

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold text-white">Bảng điều khiển Admin</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {cards.map((card, i) => (
          <div key={i} className={`${card.color} p-6 rounded-xl shadow-lg flex items-center justify-between`}>
            <div>
              <p className="text-white/80 text-sm font-medium">{card.title}</p>
              <p className="text-white text-3xl font-bold mt-1">{card.value.toLocaleString()}</p>
            </div>
            <span className="text-4xl">{card.icon}</span>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
          <h2 className="text-white font-bold mb-4">Phim mới thêm gần đây</h2>
          <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
            <h2 className="text-white font-bold mb-4">Phim mới thêm gần đây</h2>
            <div className="space-y-4">
              {stats?.recentMovies?.length > 0 ? (
                stats.recentMovies.map((movie: any) => (
                  <div key={movie.id} className="flex justify-between items-center border-b border-zinc-800 pb-2">
                    <span className="text-zinc-300">{movie.title}</span>
                    <span className="text-zinc-500 text-xs">{movie.releaseDate}</span>
                  </div>
                ))
              ) : (
                <div className="text-zinc-500 text-sm italic">Chưa có dữ liệu mới.</div>
              )}
            </div>
          </div>
        </div>
        <div className="bg-zinc-900 p-6 rounded-xl border border-zinc-800">
          <h2 className="text-white font-bold mb-4">Hoạt động người dùng</h2>
          {/* List log hoạt động... */}
          <div className="text-zinc-500 text-sm italic">Chưa có hoạt động.</div>
        </div>
      </div>
    </div>
  );
}