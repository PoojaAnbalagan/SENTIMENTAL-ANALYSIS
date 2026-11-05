import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Zap, 
  BarChart3, 
  Database, 
  Cpu, 
  FileText, 
  UploadCloud,
  ChevronLeft,
  ChevronRight,
  MessageSquareHeart,
  X,
  Sun,
  Moon
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

export function Sidebar({ currentTab, setTab, mobileMenuOpen = false, setMobileMenuOpen = () => {} }) {
  const { theme, setTheme } = useTheme();
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { id: 'Overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'Live Predictor', label: 'Live Predictor', icon: Zap },
    { id: 'Batch Upload', label: 'Batch Upload', icon: UploadCloud },
    { id: 'Sentiment Analytics', label: 'Sentiment Analytics', icon: BarChart3 },
    { id: 'Review Explorer', label: 'Review Explorer', icon: Database },
    { id: 'Model Performance', label: 'Model Performance', icon: Cpu },
    { id: 'Reports', label: 'Reports', icon: FileText },
  ];

  const handleSelectTab = (tabId) => {
    setTab(tabId);
    setMobileMenuOpen(false);
  };

  const toggleTheme = () => {
    setTheme(theme === 'Light' ? 'Dark' : 'Light');
  };

  return (
    <>
      {/* ── MOBILE BACKDROP OVERLAY ── */}
      {mobileMenuOpen && (
        <div 
          onClick={() => setMobileMenuOpen(false)}
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden transition-opacity duration-300"
          aria-label="Close navigation drawer"
        />
      )}

      {/* ── MOBILE SLIDE-OUT DRAWER ── */}
      <aside 
        className={`fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-[var(--surface)] border-r border-[var(--border)] p-4 flex flex-col justify-between shadow-2xl transition-transform duration-300 ease-out md:hidden ${
          mobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div>
          {/* Mobile Drawer Header */}
          <div className="flex items-center justify-between pb-3.5 mb-4 border-b border-[var(--border)]">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-md flex items-center justify-center shrink-0">
                <MessageSquareHeart className="w-5 h-5" />
              </div>
              <div>
                <span className="font-extrabold text-xs tracking-wider uppercase text-[var(--accent)] block">
                  Review Analytics
                </span>
                <span className="text-[10px] text-[var(--text-muted)] font-semibold">
                  AI Intelligence Platform
                </span>
              </div>
            </div>
            <button
              onClick={() => setMobileMenuOpen(false)}
              className="p-2 rounded-xl text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg)] border border-[var(--border)] transition-all touch-manipulation"
              aria-label="Close menu"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Navigation Menu */}
          <nav className="space-y-1.5">
            <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] mb-2 px-1">
              Navigation Menu
            </p>
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleSelectTab(item.id)}
                  className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-xs font-bold transition-all touch-manipulation ${
                    isActive
                      ? 'bg-[var(--accent-bg)] text-[var(--accent)] border-l-4 border-l-[var(--accent)] border border-[var(--border)] shadow-sm'
                      : 'text-[var(--text-secondary)] hover:bg-[var(--bg)] hover:text-[var(--text-primary)] border border-transparent active:bg-[var(--bg)]'
                  }`}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'}`} />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Mobile Drawer Footer with Theme Toggle */}
        <div className="pt-3 border-t border-[var(--border)] space-y-3">
          <button
            onClick={toggleTheme}
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-[var(--bg)] border border-[var(--border)] text-xs font-bold text-[var(--text-primary)] touch-manipulation"
          >
            <span className="flex items-center gap-2">
              {theme === 'Light' ? <Moon className="w-4 h-4 text-indigo-500" /> : <Sun className="w-4 h-4 text-amber-400" />}
              <span>{theme === 'Light' ? 'Dark Mode' : 'Light Mode'}</span>
            </span>
            <span className="text-[10px] px-2 py-0.5 rounded bg-[var(--surface)] text-[var(--text-muted)] border border-[var(--border)]">
              {theme}
            </span>
          </button>
          <div className="flex items-center justify-between text-[11px] text-[var(--text-muted)] px-1">
            <span className="font-extrabold text-[var(--text-primary)]">v2026.1</span>
            <span>Mobile Ready</span>
          </div>
        </div>
      </aside>

      {/* ── DESKTOP SIDEBAR ── */}
      <aside className={`hidden md:flex border-r border-[var(--border)] bg-[var(--surface)] p-3.5 flex-col justify-between min-h-screen transition-all duration-300 shrink-0 ${
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

        {/* Desktop Footer - Theme Toggle + Version */}
        <div className={`pt-3 border-t border-[var(--border)] text-[11px] text-[var(--text-muted)] ${collapsed ? 'text-center' : ''}`}>
          <div className="mb-2">
            {!collapsed ? (
              <button
                onClick={toggleTheme}
                className="w-full flex items-center justify-between px-2.5 py-1.5 rounded-xl bg-[var(--bg)] border border-[var(--border)] text-xs font-bold text-[var(--text-primary)] hover:border-[var(--border-hover)] transition-all touch-manipulation"
                title={`Switch to ${theme === 'Light' ? 'Dark' : 'Light'} Mode`}
              >
                <span className="flex items-center gap-2">
                  {theme === 'Light' ? <Moon className="w-3.5 h-3.5 text-indigo-500" /> : <Sun className="w-3.5 h-3.5 text-amber-400" />}
                  <span>{theme === 'Light' ? 'Dark Mode' : 'Light Mode'}</span>
                </span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--surface)] text-[var(--text-muted)] border border-[var(--border)] font-semibold">
                  {theme}
                </span>
              </button>
            ) : (
              <button
                onClick={toggleTheme}
                className="w-full flex justify-center p-2 rounded-xl bg-[var(--bg)] border border-[var(--border)] hover:border-[var(--border-hover)] text-[var(--text-primary)] transition-all"
                title={`Switch to ${theme === 'Light' ? 'Dark' : 'Light'} Mode`}
              >
                {theme === 'Light' ? <Moon className="w-4 h-4 text-indigo-500" /> : <Sun className="w-4 h-4 text-amber-400" />}
              </button>
            )}
          </div>
          {!collapsed && (
            <div className="flex items-center justify-between px-1 text-[10px] text-[var(--text-muted)]">
              <span className="font-extrabold text-[var(--text-primary)]">v2026.1</span>
              <span>McDonald's Analytics</span>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
