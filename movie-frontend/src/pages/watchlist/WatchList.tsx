import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Trash2, Play, Plus, Search, Info } from 'lucide-react'; 

interface Movie {
    id: number;
    title: string;
    backdropPath: string;
    releaseDate: string;
}

export default function WatchList() {
    const queryClient = useQueryClient();

    // 1. Fetch Danh sách yêu thích
    const { data: myList = [], isLoading, isError } = useQuery<Movie[]>({
        queryKey: ['watchlist'],
        queryFn: async () => {
            const response = await fetch("http://localhost:8080/user/api/getAllFavorites", {
                headers: { 'Authorization': `Bearer ${localStorage.getItem("token")}` }
            });
            if (!response.ok) throw new Error("Không thể tải danh sách");
            return response.json();
        }
    });

    // 2. Xóa phim khỏi danh sách
    const deleteMutation = useMutation({
        mutationFn: async (movieId: number) => {
            const response = await fetch(`http://localhost:8080/user/api/favorites/${movieId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem("token")}` }
            });
            if (!response.ok) throw new Error("Không thể xóa phim");
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['watchlist'] });
        }
    });

    const removeFromList = (id: number) => {
        if (window.confirm("Xóa bộ phim này khỏi danh sách yêu thích của bạn?")) {
            deleteMutation.mutate(id);
        }
    };

    if (isLoading) return (
        <div className="bg-[#141414] min-h-screen pt-32 px-12">
            <div className="h-10 w-64 bg-zinc-800 animate-pulse mb-8 rounded"></div>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {[...Array(12)].map((_, i) => (
                    <div key={i} className="aspect-video bg-zinc-800 animate-pulse rounded-md"></div>
                ))}
            </div>
        </div>
    );

    return (
        <div className="bg-[#141414] min-h-screen pt-32 pb-20 px-4 md:px-12 text-white">
            <header className="mb-10 flex items-end gap-4">
                <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Danh sách của tôi</h1>
                <span className="text-zinc-500 font-medium mb-1">{myList.length} phim</span>
            </header>

            {myList.length > 0 ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-x-4 gap-y-10">
                    {myList.map((movie) => (
                        <div key={movie.id} className="relative group">
                            <div className="relative aspect-video rounded-md overflow-hidden bg-zinc-900 border border-white/5 transition-all duration-300 group-hover:scale-110 group-hover:z-30 group-hover:shadow-[0_0_20px_rgba(0,0,0,0.5)]">
                                <Link to={`/movie/${movie.id}`}>
                                    <img 
                                        src={`https://image.tmdb.org/p/w500${movie.backdropPath}`} 
                                        alt={movie.title}
                                        className="w-full h-full object-cover"
                                    />
                                    <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
                                        <div className="p-2 bg-white rounded-full text-black hover:scale-110 transition">
                                            <Play size={20} fill="currentColor" />
                                        </div>
                                        <div className="p-2 bg-[#2a2a2a] rounded-full text-white border border-gray-500 hover:border-white transition">
                                            <Info size={20} />
                                        </div>
                                    </div>
                                </Link>

                                <button 
                                    onClick={() => removeFromList(movie.id)}
                                    className="absolute top-2 right-2 p-1.5 bg-black/60 rounded-full opacity-0 group-hover:opacity-100 hover:bg-red-600 transition-all z-40"
                                    title="Xóa khỏi danh sách"
                                >
                                    <Trash2 size={14} />
                                </button>
                            </div>
                            
                            <p className="mt-2 text-xs font-semibold text-zinc-300 truncate group-hover:opacity-0 transition-opacity">
                                {movie.title}
                            </p>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-20 text-center border border-dashed border-zinc-800 rounded-2xl bg-zinc-900/20">
                    <div className="p-6 bg-zinc-800/50 rounded-full mb-6">
                        <Plus size={48} className="text-zinc-600" />
                    </div>
                    <h2 className="text-xl font-bold mb-2">Danh sách của bạn đang trống</h2>
                    <p className="text-zinc-500 max-w-xs mb-8">
                        Hãy thêm những bộ phim bạn yêu thích vào đây để xem lại bất cứ lúc nào.
                    </p>
                    <Link 
                        to="/" 
                        className="flex items-center gap-2 bg-white text-black px-8 py-3 rounded font-bold hover:bg-red-600 hover:text-white transition-all duration-300 shadow-lg"
                    >
                        <Search size={18} /> KHÁM PHÁ NGAY
                    </Link>
                </div>
            )}

            <div className="mt-32">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-bold">Có thể bạn sẽ thích</h2>
                    <Link to="/category" className="text-red-500 text-sm font-bold hover:underline">Xem tất cả</Link>
                </div>
                <div className="flex gap-4 overflow-x-auto pb-4 no-scrollbar">
                    {[...Array(6)].map((_, i) => (
                        <div key={i} className="min-w-[200px] aspect-video bg-zinc-800 rounded-md animate-pulse"></div>
                    ))}
                </div>
            </div>
        </div>
    );
}