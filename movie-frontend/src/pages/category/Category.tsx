import { useSearchParams, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query";
import { getAllGenre, getMoviesFilter } from "../../modules/category/service/CategoryService";
import MovieGrid from "../../common/components/MovieGrid";
import SideBar from "../../modules/category/components/SideBar";
import { useState } from "react";

export default function Category() {
    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    const genreId = searchParams.get('genre') || '';
    const sortByParam = searchParams.get('sortBy') || 'POPULARITY';
    const dtypeParam = searchParams.get('dtype') || '';
    const [page, setPage] = useState(0);

    const genresQuery = useQuery({
        queryKey: ['genres'],
        queryFn: getAllGenre,
        staleTime: Infinity,
    });

    const movieQuery = useQuery({
        queryKey: ['movies', sortByParam, genreId, dtypeParam, page],
        queryFn: () => getMoviesFilter({ sortBy: sortByParam, genre: genreId, dtype: dtypeParam, page }),
        placeholderData: (pre) => pre,
    });

    const handleSortChange = (newSortBy: string) => {
        setPage(0);
        setSearchParams({ sortBy: newSortBy, genre: genreId, dtype: dtypeParam });
    }

    const handleGenreChange = (newGenreId: string) => {
        setPage(0);
        setSearchParams({ sortBy: sortByParam, genre: newGenreId, dtype: dtypeParam });
    }

    const handleDtypeChange = (newDtype: string) => {
        if (newDtype === 'MOVIE') {
            navigate('/movies');
        } else if (newDtype === 'SERIES') {
            navigate('/series');
        } else {
            setPage(0);
            setSearchParams({ sortBy: sortByParam, genre: genreId, dtype: '' });
        }
    }

    const banner_category_image = "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=1280";

    return (
        <div className="flex flex-col w-full bg-[#141414] min-h-screen text-white">
            <div className="relative w-full h-[50vh] overflow-hidden">
                <img
                    className="w-full h-full object-cover opacity-50"
                    src={banner_category_image}
                    alt="Banner"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-transparent to-black/60" />
                <div className="absolute bottom-10 left-12">
                    <h1 className="text-5xl font-bold mb-2">Khám phá</h1>
                    <p className="text-gray-300 text-lg">Tìm kiếm những bộ phim tuyệt vời nhất dành cho bạn</p>
                </div>
            </div>

            <div className="flex w-full max-w-[1600px] mx-auto px-4 md:px-12 py-8 gap-8">
                <aside className="w-64 flex-shrink-0 hidden md:block">
                    <SideBar
                        genres={genresQuery.data || []}
                        activeSort={sortByParam}
                        activeGenre={genreId}
                        activeDtype={dtypeParam}
                        onSortChange={handleSortChange}
                        onGenreChange={handleGenreChange}
                        onDtypeChange={handleDtypeChange}
                    />
                </aside>

                {/* Movie Grid bên phải */}
                <main className="flex-1">
                    <MovieGrid
                        data={movieQuery.data || []}
                        loading={movieQuery.isLoading}
                        onPageChange={setPage}
                    />
                </main>
            </div>
        </div>
    );
}