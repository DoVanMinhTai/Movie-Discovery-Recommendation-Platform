import type { Genre } from "../model/Genre";

type Props = {
    genres: Genre[];
    activeSort: string;
    activeGenre?: string;
    onSortChange: (sortBy: string) => void;
    onGenreChange: (genreId: string) => void;
}

export default function SideBar({ genres, activeSort, activeGenre, onSortChange, onGenreChange }: Props) {
     const sortOptions = [
        { id: 'POPULARITY', label: 'Phổ biến nhất' },
        { id: 'NEWEST', label: 'Mới nhất' },
        { id: 'OLDEST', label: 'Cũ nhất' },
        { id: 'RATING', label: 'Đánh giá cao' },
    ];

    return (
        <div className="flex flex-col gap-8 sticky top-24">
            <div>
                <h3 className="text-gray-400 uppercase text-xs font-bold tracking-widest mb-4">Sắp xếp theo</h3>
                <div className="flex flex-col gap-2">
                    {sortOptions.map((opt) => (
                        <button
                            key={opt.id}
                            onClick={() => onSortChange(opt.id)}
                            className={`text-left px-4 py-2 rounded-md transition-all duration-200 text-sm font-medium
                                ${activeSort === opt.id 
                                    ? 'bg-red-600 text-white shadow-lg shadow-red-600/20' 
                                    : 'text-gray-400 hover:bg-[#2f2f2f] hover:text-white'
                                }`}
                        >
                            {opt.label}
                        </button>
                    ))}
                </div>
            </div>

            {/* Divider */}
            <div className="h-[1px] bg-gray-800 w-full" />

            <div>
                <h3 className="text-gray-400 uppercase text-xs font-bold tracking-widest mb-4">Thể loại</h3>
                <div className="flex flex-wrap gap-2">
                    <button
                        onClick={() => onGenreChange('')}
                        className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all
                            ${activeGenre === '' 
                                ? 'border-red-600 bg-red-600 text-white' 
                                : 'border-gray-600 text-gray-400 hover:border-white hover:text-white'
                            }`}
                    >
                        Tất cả
                    </button>

                    {genres.map((genre) => (
                        <button
                            key={genre.id}
                            onClick={() => onGenreChange(genre.id.toString())}
                            className={`px-3 py-1.5 rounded-full text-xs font-semibold border transition-all
                                ${activeGenre === genre.id.toString() 
                                    ? 'border-red-600 bg-red-600 text-white' 
                                    : 'border-gray-600 text-gray-400 hover:border-white hover:text-white'
                                }`}
                        >
                            {genre.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}