import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getAllMovieByTitle } from "../../modules/search/service/SearchService";
import MovieGrid from "../../common/components/MovieGrid";
import { useState, useEffect } from "react";
import { Search, Film } from "lucide-react";

export default function SearchResult() {
    const [searchParams] = useSearchParams();
    const query = searchParams.get("s") || "";
    const [page, setPage] = useState(0);

    useEffect(() => {
        setPage(0);
    }, [query]);

    const searchResultsQuery = useQuery({
        queryKey: ["search-results", query, page],
        queryFn: () => getAllMovieByTitle(query),
        enabled: !!query,
        placeholderData: (prev) => prev,
    });

    const banner_search_image = "https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=1280";

    return (
        <div className="flex flex-col w-full bg-[#141414] min-h-screen text-white">
            {/* Header Banner Section */}
            <div className="relative w-full h-[40vh] overflow-hidden">
                <img
                    className="w-full h-full object-cover opacity-40"
                    src={banner_search_image}
                    alt="Search Banner"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-transparent to-black/60" />
                <div className="absolute bottom-10 left-4 md:left-12">
                    <div className="flex items-center gap-3 mb-2">
                        <Search className="text-red-600" size={32} />
                        <h1 className="text-4xl md:text-5xl font-bold">Kết quả tìm kiếm</h1>
                    </div>
                    <p className="text-gray-300 text-lg">
                        Tìm thấy {searchResultsQuery.data?.totalElements || 0} kết quả cho: 
                        <span className="text-white font-bold ml-2 italic">"{query}"</span>
                    </p>
                </div>
            </div>

            <div className="w-full max-w-[1600px] mx-auto px-4 md:px-12 py-12">
                {query ? (
                    <main className="w-full">
                        {searchResultsQuery.data?.content?.length > 0 ? (
                            <MovieGrid
                                data={searchResultsQuery.data}
                                loading={searchResultsQuery.isLoading}
                                onPageChange={setPage}
                            />
                        ) : (
                            !searchResultsQuery.isLoading && (
                                <div className="flex flex-col items-center justify-center py-20 text-center">
                                    <div className="p-6 bg-zinc-800/50 rounded-full mb-6">
                                        <Film size={64} className="text-zinc-600" />
                                    </div>
                                    <h2 className="text-2xl font-bold mb-2">Không tìm thấy phim nào</h2>
                                    <p className="text-zinc-500 max-w-md">
                                        Rất tiếc, chúng mình không tìm thấy bộ phim nào khớp với từ khóa của bạn. 
                                        Hãy thử tìm kiếm với tên phim hoặc thể loại khác nhé!
                                    </p>
                                </div>
                            )
                        )}
                        
                        {searchResultsQuery.isLoading && !searchResultsQuery.data && (
                             <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-y-10 gap-x-4">
                                {[...Array(12)].map((_, i) => (
                                    <div key={i} className="aspect-[2/3] w-full bg-[#2f2f2f] animate-pulse rounded-md" />
                                ))}
                             </div>
                        )}
                    </main>
                ) : (
                    <div className="text-center py-20">
                        <h2 className="text-2xl font-bold">Hãy nhập từ khóa để tìm kiếm</h2>
                    </div>
                )}
            </div>
        </div>
    );
}
