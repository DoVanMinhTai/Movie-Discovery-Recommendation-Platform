import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import logo from "../../../../public/logo.png";
import { getMovieSuggestionByTitle } from "../../../modules/search/service/SearchService";
import { getAuthData } from "../../auth/AuthUtils";

const Header = () => {
	const [searchValue, setSearchValue] = useState("");
	const [searchResults, setSearchResults] = useState<Array<{ id: number; title: string; releaseDate: number; backdropPath: string }>>([]);
	const [showDropdown, setShowDropdown] = useState(false);
	const navigate = useNavigate();

	useEffect(() => {
		if (!searchValue.trim()) {
			return;
		}

		const delayDebounceFn = setTimeout(() => {
			if (searchValue.trim().length > 0) {
				try {
					getMovieSuggestionByTitle(searchValue).then((data) => {
						setSearchResults(data);
						setShowDropdown(true);
					});
				} catch (error) {
					console.error("Error fetching search results:", error);
				}
			} else {
				setSearchResults([]);
				setShowDropdown(false);
			}
		}, 300);
		return () => clearTimeout(delayDebounceFn);
	}, [searchValue]);

	const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
		const value = e.target.value;
		setSearchValue(value);

		if (value.trim().length === 0) {
			setSearchResults([]);
			setShowDropdown(false);
		}
	}

	const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		if (searchValue.trim()) {
			setShowDropdown(false);
			navigate(`/search?s=${encodeURIComponent(searchValue)}`);
		}
	}
	const handleLogout = () => {
		localStorage.clear();
		navigate('/login');
	};
	const auth = getAuthData();
    const role = auth?.role;

	return (<>
		<header className="flex items-center w-full m-5">
			<div className="flex gap-3 w-2/4" >
				<Link to="/"><img src={logo} className="w-20 h-10 object-cover " /></Link>
				<ul className="flex items-center justify-center gap-3 font-bold">
					<li><Link to="/">Home</Link></li>
					<li><Link to="/category">Danh mục</Link></li>
					<li><Link to="/watchlist">Danh sách của tôi</Link></li>
				</ul>
			</div>
			<div className="flex items-center justify-center gap-3 w-2/4 border-l-2 pl-4">
				<form onSubmit={handleSubmit} className="flex justify-between w-1/2 items-center gap-2">
					<input type="text"
						placeholder="Phim, thể loại,..."
						className="
						bg-transparent outline-none text-white w-full focus:w-full transition-all duration-300
						border-b-2 border-white pb-1 
						"
						onChange={handleSearch}
					/>
				</form>

				<div className="group relative">
					<img
						src="https://upload.wikimedia.org/wikipedia/commons/0/0b/Netflix-avatar.png"
						alt="Profile"
						className="cursor-pointer rounded w-8 h-8 object-cover"
					/>
					<div className="absolute right-0 top-full hidden w-40 flex-col bg-black border border-gray-700 py-2 group-hover:flex pt-2 z-50">
						<Link to="/profile" className="px-4 py-2 hover:bg-gray-800">Hồ sơ</Link>
						{role === 'ADMIN' && <Link to="/admin" className="px-4 py-2 text-sm text-nfRed font-bold hover:bg-nfGrey-800">Trang quản trị</Link>}
						<hr className="border-gray-700 my-1" />
						<button onClick={handleLogout} className="text-left px-4 py-2 text-sm hover:bg-nfGrey-800">Đăng xuất</button>
					</div>
				</div>
			</div>
			{showDropdown && searchResults.length > 0 && (
				<div className="absolute top-15 right-60 w-1/4 bg-[#141414] border border-gray-700 mt-2 rounded-md shadow-2xl z-[100]">
					{searchResults.map((movie) => (
						<Link
							key={movie.id}
							to={`/movie/${movie.id}`}
							className="flex flex-col px-4 py-3 hover:bg-gray-800 border-b border-gray-800 last:border-none"
							onClick={() => setSearchValue("")}
						>
							<div className="flex flex-1 items-center gap-3">
								{movie.backdropPath && (
									<img src={`https://image.tmdb.org/t/p/w500${movie.backdropPath}`} alt={movie.title}
										className="w-12 h-12 object-cover rounded mb-2" />
								)}
								<span className="font-bold text-sm">{movie.title}</span>
								<span className="text-xs text-gray-400">{movie.releaseDate}</span>
							</div>
						</Link>
					))}
					<Link
						to={`/search?s=${searchValue}`}
						className="block text-center py-2 text-xs text-blue-400 hover:bg-gray-800">
						Xem tất cả kết quả
					</Link>
				</div>
			)}
		</header>
	</>
	)
}

export default Header;