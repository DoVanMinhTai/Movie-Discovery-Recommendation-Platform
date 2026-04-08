import { BrowserRouter, Route, Routes } from 'react-router-dom'
import './App.css'
import HomePage from './pages/homepage/HomePage'
import MainLayout from './common/layouts/MainLayout'
import AdminLayout from './common/layouts/AdminLayout'
import Login from './pages/login/Login'
import Register from './pages/register/Register'
import MovieDetail from './pages/movie/Movie'
import SearchResult from './pages/search/SearchResult'
import Profile from './pages/profile/Profile'
import WatchList from './pages/watchlist/WatchList'
import MovieManage from './pages/admin/MovieManage'
import Category from './pages/category/Category'
import "./index.css";
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import ProtectedRoute from './common/auth/components/ProtectedRoute'
import OnBoarding from './pages/onboarding/OnBoarding'
import { Toaster } from 'react-hot-toast';
import AdminDashboard from './pages/admin/AdminDashboard'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Toaster position="top-center" reverseOrder={false} />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute allowedRoles={['USER', 'ADMIN']} />}>
            <Route path="/onboarding" element={<OnBoarding />} />
            <Route path='/' element={<MainLayout />}>
              <Route index element={<HomePage />} />
              <Route path="movie/:id" element={<MovieDetail />} />
              <Route path="search" element={<SearchResult />} />
              <Route path="category" element={<Category />} />
              <Route path="profile" element={<Profile />} />
              <Route path="watchlist" element={<WatchList />} />
            </Route>
          </Route>

          <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
            <Route path="/admin" element={<AdminLayout />}>
              <Route index element={<AdminDashboard />} />
              <Route path="movies" element={<MovieManage />} />
              <Route path="users" element={<div>Quản lý người dùng</div>} />
            </Route>
          </Route>
          <Route path="*" element={<h1>404 - Not Found</h1>} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
export default App