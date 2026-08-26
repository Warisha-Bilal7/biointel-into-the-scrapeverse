'use client';

import { useState } from 'react';
import { Search, Bell, User, Menu } from 'lucide-react';

export default function Header() {
  const [searchQuery, setSearchQuery] = useState('');
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);

  return (
    <header className="flex h-14 items-center justify-between gap-4 border-b border-border/30 bg-background px-6">
      {/* Left: Menu + Search */}
      <div className="flex min-w-0 flex-1 items-center gap-3">
        <button
          type="button"
          className="rounded-md p-1.5 text-foreground hover:bg-accent/20"
          aria-label="Toggle navigation"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="relative w-full max-w-md">
          <Search className="absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />

          <input
            type="search"
            placeholder="Search research..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full rounded-md bg-slate-900/50 py-1.5 pl-9 pr-3 text-sm text-foreground placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-primary"
            aria-label="Search research papers"
          />
        </div>
      </div>

      {/* Right: Notifications + User */}
      <div className="flex items-center gap-3">
        {/* Notifications */}
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setNotificationsOpen((open) => !open);
              setUserMenuOpen(false);
            }}
            className="relative rounded-md p-2 text-foreground hover:bg-accent/20"
            aria-label="Notifications"
            aria-expanded={notificationsOpen}
          >
            <Bell className="h-5 w-5" />

            <span className="absolute right-1 top-1 h-2.5 w-2.5 rounded-full bg-rose-500" />
          </button>

          {notificationsOpen && (
            <div
              className="absolute right-0 z-50 mt-2 w-72 rounded-md border border-border/30 bg-background p-4 shadow-lg"
              role="menu"
            >
              <p className="mb-3 font-medium">Notifications</p>

              <ul className="space-y-3 text-sm">
                <li className="flex gap-2">
                  <span className="text-emerald-400">•</span>
                  <span>New scrape completed - Clinical Data source</span>
                </li>

                <li className="flex gap-2">
                  <span className="text-rose-400">•</span>
                  <span>Structural drift detected - Research Source</span>
                </li>

                <li className="flex gap-2">
                  <span className="text-emerald-400">•</span>
                  <span>Self-healing review triggered</span>
                </li>
              </ul>

              <button
                type="button"
                className="mt-3 text-xs text-slate-500 hover:text-foreground"
              >
                See all notifications
              </button>
            </div>
          )}
        </div>

        {/* User */}
        <div className="relative">
          <button
            type="button"
            onClick={() => {
              setUserMenuOpen((open) => !open);
              setNotificationsOpen(false);
            }}
            className="rounded-md p-2 text-foreground hover:bg-accent/20"
            aria-label="User menu"
            aria-expanded={userMenuOpen}
          >
            <User className="h-5 w-5" />
          </button>

          {userMenuOpen && (
            <div
              className="absolute right-0 z-50 mt-2 w-40 rounded-md border border-border/30 bg-background p-3 shadow-lg"
              role="menu"
            >
              <p className="mb-2 text-sm font-medium">User</p>

              <div className="space-y-1 text-sm">
                <button
                  type="button"
                  className="w-full rounded-md px-2 py-1.5 text-left hover:bg-accent/20"
                >
                  Profile
                </button>

                <button
                  type="button"
                  className="w-full rounded-md px-2 py-1.5 text-left hover:bg-accent/20"
                >
                  Settings
                </button>

                <button
                  type="button"
                  onClick={() => alert('Logout')}
                  className="w-full rounded-md px-2 py-1.5 text-left text-destructive hover:bg-accent/20"
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}