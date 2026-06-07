import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Trash2, Play, Plus, Search, Info, Sparkles } from 'lucide-react';
import { getWatchList, removeFromWatchList } from '../../modules/watchlist/service/WatchListService';
import { getCollaborativeFiltering } from '../../modules/movie/service/MovieService';
import { getMyProfile } from '../../modules/auth/service/AuthService';
import ImageFallback from '../../common/components/ImageFallback';
import { toast } from 'react-hot-toast';

interface Movie {
    id: number;
    title: string;
    backdropPath: string;
    releaseDate: string;
}

import type { MovieThumbnailGetVm } from '../../modules/movie/model/MovieThumbnailGetVm';

export default function WatchList() {
    const queryClient = useQueryClient();

    const { data: myList = [], isLoading: isListLoading } = useQuery<MovieThumbnailGetVm[]>({
        queryKey: ['watchlist'],
        queryFn: async () => {
            return getWatchList();
        }
    });

    const { data: recommendedMovies = [], isLoading: isRecoLoading } = useQuery<MovieThumbnailGetVm[]>({
        queryKey: ['recommendations-cf'],
        queryFn: async () => {
            try {
                const profile = await getMyProfile();
                if (profile && profile.id) {
                    return getCollaborativeFiltering(profile.id);
                }
                return [];
            } catch (error) {
                console.error("Lỗi lấy gợi ý CF:", error);
                return [];
            }
        },
        staleTime: 1000 * 60 * 10,
    });

    const deleteMutation = useMutation({
        mutationFn: async (movieId: number) => {
            return removeFromWatchList(movieId);
        },
        onMutate: () => {
            return toast.loading("Đang xóa khỏi danh sách...");
        },
        onSuccess: (_data, _variables, context) => {
            toast.success("Đã xóa bộ phim thành công!", { id: context });

            queryClient.invalidateQueries({ queryKey: ['watchlist'] });
        },
        onError: (error: any, _variables, context) => {
            toast.error(error.message || "Không thể xóa phim này", { id: context });
        }
    });

    const removeFromList = (id: number) => {
        deleteMutation.mutate(id);
    };

    if (isListLoading) return (
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
                                    <ImageFallback
                                        src={movie.backdropPath ? `https://image.tmdb.org/t/p/w500${movie.backdropPath}` : "https://via.placeholder.com/500x750?text=No+Poster"}
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
                    <div className="flex items-center gap-2">
                        <Sparkles size={24} className="text-red-600 fill-red-600" />
                        <h2 className="text-2xl font-bold">Có thể bạn sẽ thích</h2>
                    </div>
                    <Link to="/" className="text-zinc-400 text-sm font-bold hover:text-white transition-colors">Xem thêm</Link>
                </div>

                {isRecoLoading ? (
                    <div className="flex gap-4 overflow-x-auto pb-4 no-scrollbar">
                        {[...Array(6)].map((_, i) => (
                            <div key={i} className="min-w-[240px] aspect-video bg-zinc-800/50 rounded-md animate-pulse"></div>
                        ))}
                    </div>
                ) : recommendedMovies.length > 0 ? (
                    <div className="flex gap-6 overflow-x-auto pb-10 no-scrollbar">
                        {recommendedMovies.map((movie: any) => (
                            <div key={movie.id} className="min-w-[240px] group cursor-pointer relative">
                                <Link to={`/movie/${movie.id}`}>
                                    <div className="relative aspect-video rounded-lg overflow-hidden border border-white/5 transition-transform duration-300 group-hover:scale-105">
                                        <ImageFallback
                                            src={movie.backdropPath ? `https://image.tmdb.org/t/p/w500${movie.backdropPath}` : "https://via.placeholder.com/500x750?text=No+Poster"}
                                            alt={movie.title}
                                            className="w-full h-full object-cover"
                                        />
                                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end p-4">
                                            <div className="flex items-center gap-2 text-white">
                                                <Play size={16} fill="currentColor" />
                                                <span className="text-xs font-bold uppercase">Xem ngay</span>
                                            </div>
                                        </div>
                                    </div>
                                    <h3 className="mt-3 text-sm font-semibold text-zinc-300 group-hover:text-white transition-colors truncate">
                                        {movie.title}
                                    </h3>
                                </Link>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="py-10 bg-zinc-900/40 rounded-xl border border-zinc-800/50 flex flex-col items-center justify-center text-center">
                        <p className="text-zinc-500 text-sm italic mb-2">Đánh giá thêm nhiều phim để nhận gợi ý cá nhân hóa!</p>
                        <p className="text-zinc-600 text-[11px]">Hệ thống AI đang học hỏi sở thích của bạn...</p>
                    </div>
                )}
            </div>
        </div>
    );
}