import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Zap, 
  BarChart3, 
  Database, 
  Cpu, 
  FileText, 
  Info,
  Sun,
  Moon,
  ChevronLeft,
  ChevronRight,
  MessageSquareHeart
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export function Sidebar({ currentTab, setTab }) {
  const { theme, setTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { id: 'Overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'Live Predictor', label: 'Live Predictor', icon: Zap },
    { id: 'Sentiment Analytics', label: 'Sentiment Analytics', icon: BarChart3 },
    { id: 'Review Explorer', label: 'Review Explorer', icon: Database },
    { id: 'Model Performance', label: 'Model Performance', icon: Cpu },
    { id: 'Reports', label: 'Reports', icon: FileText },
    { id: 'Project Information', label: 'Project Info', icon: Info },
  ];

  return (
    <aside className={`border-r border-[var(--border)] bg-[var(--surface)] p-3.5 flex flex-col justify-between min-h-screen transition-all duration-300 ${
      collapsed ? 'w-16' : 'w-60'
    }`}>
      <div>
        {/* Sentiment Brand Header & Collapse Toggle */}
        <div className="flex items-center justify-between pb-3.5 mb-4 border-b border-[var(--border)]">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-md flex items-center justify-center shrink-0">
              <MessageSquareHeart className="w-5 h-5" />
            </div>
            {!collapsed && (
              <span className="font-extrabold text-xs tracking-wider uppercase text-[var(--accent)]">
                Review Analytics
              </span>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            title={collapsed ? "Expand Sidebar" : "Collapse Sidebar"}
            className="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg)] border border-transparent hover:border-[var(--border)] transition-all shrink-0"
          >
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="space-y-1">
          {!collapsed && (
            <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-2">Navigation Menu</p>
          )}
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setTab(item.id)}
                title={collapsed ? item.label : undefined}
                className={`w-full flex items-center gap-3 ${collapsed ? 'justify-center px-2 py-2.5' : 'px-3 py-2.5'} rounded-xl text-xs font-bold transition-all ${
                  isActive
                    ? 'bg-[var(--accent-bg)] text-[var(--accent)] border-l-4 border-l-[var(--accent)] border border-[var(--border)] shadow-sm'
                    : 'text-[var(--text-secondary)] hover:bg-[var(--bg)] hover:text-[var(--text-primary)] border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'}`} />
                {!collapsed && <span className="truncate">{item.label}</span>}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Minimal Footer Info */}
      <div className={`pt-3 border-t border-[var(--border)] text-[11px] text-[var(--text-muted)] ${collapsed ? 'text-center' : ''}`}>
        <p className="font-extrabold text-[var(--text-primary)]">v2026.1</p>
      </div>
    </aside>
  );
}
