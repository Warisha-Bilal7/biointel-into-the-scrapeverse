'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import {
  Home,
  Settings,
  LogOut,
  Microscope,
  ChartBar,
  Folder,
  Network,
  LucideIcon,
} from 'lucide-react';

interface NavLink {
  href: string;
  icon: LucideIcon;
  label: string;
}

const navLinks: NavLink[] = [
  {
    href: '/',
    icon: Home,
    label: 'Dashboard',
  },
  {
    href: '/explorer',
    icon: Microscope,
    label: 'Explorer',
  },
  {
    href: '/ingestion',
    icon: Folder,
    label: 'Ingestion',
  },
  {
    href: '/knowledge-graph',
    icon: Network,
    label: 'Knowledge Graph',
  },
  {
    href: '/system-status',
    icon: ChartBar,
    label: 'System Status',
  },
  {
    href: '/settings',
    icon: Settings,
    label: 'Settings',
  },
];

export default function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setCollapsed(window.innerWidth <= 768);
    };

    handleResize();

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  return (
    <aside
      className={`flex h-full shrink-0 flex-col border-r border-border/30 bg-background transition-all duration-200 ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      {/* Logo */}
      <div
        className={`flex h-16 items-center border-b border-border/20 px-4 ${
          collapsed ? 'justify-center' : 'gap-3'
        }`}
      >
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-primary text-sm font-medium text-white">
          BI
        </div>

        {!collapsed && (
          <span className="font-medium text-white">
            BioIntel
          </span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-2 py-4">
        <ul className="space-y-1">
          {navLinks.map(({ href, icon: Icon, label }) => (
            <li key={href}>
              <Link
                href={href}
                title={collapsed ? label : undefined}
                className={`group flex items-center rounded-md p-2 text-sm font-medium text-foreground transition-colors hover:bg-accent/20 hover:text-primary ${
                  collapsed
                    ? 'justify-center'
                    : 'gap-3'
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />

                {!collapsed && (
                  <span>{label}</span>
                )}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Logout */}
      <div className="border-t border-border/20 p-3">
        <button
          type="button"
          onClick={() => alert('Logout clicked')}
          title={collapsed ? 'Logout' : undefined}
          className={`flex w-full items-center rounded-md p-2 text-sm font-medium text-destructive transition-colors hover:bg-accent/20 ${
            collapsed
              ? 'justify-center'
              : 'gap-3'
          }`}
        >
          <LogOut className="h-4 w-4 shrink-0" />

          {!collapsed && (
            <span>Logout</span>
          )}
        </button>
      </div>
    </aside>
  );
}