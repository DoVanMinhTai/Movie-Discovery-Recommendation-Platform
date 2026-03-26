import { useState } from 'react';
import Dashboard from './Dashboard';
import MovieManage from './MovieManage';
import AIRetraining from './AIRetraining';

type TabType = 'statistics' | 'movies' | 'users' | 'ai-system';

export default function AdminDashboard() {
    const [activeTab, setActiveTab] = useState<TabType>('statistics');

    return (
        <div className="min-h-screen bg-[#141414] text-white">
            <div className="p-6 border-b border-zinc-800 bg-zinc-900/50 sticky top-0 z-20 backdrop-blur-md">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <h1 className="text-2xl font-black tracking-wider text-red-600">ADMIN</h1>
                    
                    <nav className="flex bg-black rounded-lg p-1 border border-zinc-800 overflow-x-auto">
                        <button
                            onClick={() => setActiveTab('statistics')}
                            className={`px-4 py-2 rounded-md text-sm font-bold whitespace-nowrap transition-all ${
                                activeTab === 'statistics' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                        >
                            Thống kê
                        </button>
                        <button
                            onClick={() => setActiveTab('movies')}
                            className={`px-4 py-2 rounded-md text-sm font-bold whitespace-nowrap transition-all ${
                                activeTab === 'movies' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                        >
                            Quản lý phim
                        </button>
                        <button
                            onClick={() => setActiveTab('ai-system')}
                            className={`px-4 py-2 rounded-md text-sm font-bold whitespace-nowrap transition-all ${
                                activeTab === 'ai-system' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                        >
                            Hệ thống AI
                        </button>
                        <button
                            onClick={() => setActiveTab('users')}
                            className={`px-4 py-2 rounded-md text-sm font-bold whitespace-nowrap transition-all ${
                                activeTab === 'users' ? 'bg-zinc-800 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                        >
                            Người dùng
                        </button>
                    </nav>
                </div>
            </div>

            <main className="p-6 animate-fadeIn">
                {activeTab === 'statistics' && <Dashboard />}
                {activeTab === 'movies' && <MovieManage />}
                {activeTab === 'ai-system' && <AIRetraining />}
                {activeTab === 'users' && (
                    <div className="p-20 text-center text-zinc-500 border-2 border-dashed border-zinc-800 rounded-xl">
                        Chức năng quản lý người dùng đang được phát triển...
                    </div>
                )}
            </main>
        </div>
    );
}