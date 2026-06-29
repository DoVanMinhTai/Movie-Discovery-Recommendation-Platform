import { useSearchParams, useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query";
import { getAllGenre, getMoviesFilter } from "../../modules/category/service/CategoryService";
import MovieGrid from "../../common/components/MovieGrid";
import SideBar from "../../modules/category/components/SideBar";
import { useState } from "react";
export default function Movies() {

    const [searchParams, setSearchParams] = useSearchParams();
    const navigate = useNavigate();
    const genreId = searchParams.get('genre') || '';
    const sortByParam = searchParams.get('sortBy') || 'POPULARITY';
    const dtypeParam = 'MOVIE';
    const [page, setPage] = useState(0);
    const genresQuery = useQuery({

        queryKey: ['genres'],
        queryFn: getAllGenre,
        staleTime: Infinity,
    });
    const movieQuery = useQuery(
        {
            queryKey: ['movies-only', sortByParam, genreId, page],
            queryFn: () => getMoviesFilter({ sortBy: sortByParam, genre: genreId, dtype: dtypeParam, page }),
            placeholderData: (pre) => pre,
        });

    const handleSortChange = (newSortBy: string) => { setPage(0); setSearchParams({ sortBy: newSortBy, genre: genreId }); }

    const handleGenreChange = (newGenreId: string) => { setPage(0); setSearchParams({ sortBy: sortByParam, genre: newGenreId }); }
    const handleDtypeChange = (newDtype: string) => { if (newDtype === 'SERIES') { navigate('/series'); } else if (newDtype === '') { navigate('/category'); } }
    const banner_image = "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?q=80&w=1280";


    return (<div className="flex flex-col w-full bg-[#141414] min-h-screen text-white">
        <div className="relative w-full h-[50vh] overflow-hidden">
            <img className="w-full h-full object-cover opacity-50" src={banner_image} alt="Banner" />
            <div className="absolute inset-0 bg-gradient-to-t from-[#141414] via-transparent to-black/60" />
            <div className="absolute bottom-10 left-12">                    <h1 className="text-5xl font-bold mb-2">Phim lẻ</h1>
                < p className="text-gray-300 text-lg">Khám phá các bộ phim lẻ bom tấn và đặc sắc</p>
            </div >
        </div >
        <div className="flex w-full max-w-[1600px] mx-auto px-4 md:px-12 py-8 gap-8">
            < aside className="w-64 flex-shrink-0 hidden md:block">
                < SideBar genres={genresQuery.data || []} activeSort={sortByParam} activeGenre={genreId} activeDtype={dtypeParam} onSortChange={handleSortChange} onGenreChange={handleGenreChange} onDtypeChange={handleDtypeChange} />
            </aside >
            <main className="flex-1">                    <MovieGrid data={movieQuery.data || []} loading={movieQuery.isLoading} onPageChange={setPage} />                </main>            </div>        </div>);

}