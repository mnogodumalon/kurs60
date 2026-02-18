import { NavLink, Outlet } from 'react-router-dom';
import { BookOpen, ClipboardList, DoorOpen, GraduationCap, LayoutDashboard, Menu, Users, X } from 'lucide-react';
import { useState } from 'react';

// ⚡ Customize these for your app
const APP_TITLE = 'KursManager';
const APP_SUBTITLE = 'Kursverwaltung';

const navigation = [
  { name: 'Übersicht', href: '/', icon: LayoutDashboard },
  { name: 'Dozenten', href: '/dozenten', icon: GraduationCap },
  { name: 'Teilnehmer', href: '/teilnehmer', icon: Users },
  { name: 'Räume', href: '/raeume', icon: DoorOpen },
  { name: 'Kurse', href: '/kurse', icon: BookOpen },
  { name: 'Anmeldungen', href: '/anmeldungen', icon: ClipboardList },
];

export function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background">
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64 bg-sidebar border-r border-sidebar-border
          transform transition-transform duration-200 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
      >
        <div className="flex items-center justify-between px-5 py-6 border-b border-sidebar-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-sidebar-primary flex items-center justify-center shadow-sm">
              <GraduationCap size={16} className="text-sidebar-primary-foreground" />
            </div>
            <div>
              <h1 className="text-sm font-bold tracking-tight text-sidebar-foreground">{APP_TITLE}</h1>
              <p className="text-xs text-sidebar-foreground/60">{APP_SUBTITLE}</p>
            </div>
          </div>
          <button
            className="lg:hidden p-1.5 rounded-lg text-sidebar-foreground/60 hover:text-sidebar-foreground transition-colors"
            onClick={() => setSidebarOpen(false)}
          >
            <X size={16} />
          </button>
        </div>
        <nav className="px-3 pt-4 space-y-0.5">
          <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-widest text-sidebar-foreground/40">
            Navigation
          </p>
          {navigation.map(item => (
            <NavLink
              key={item.href}
              to={item.href}
              end={item.href === '/'}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }: { isActive: boolean }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-sidebar-primary text-sidebar-primary-foreground shadow-sm'
                    : 'text-sidebar-foreground/70 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground'
                }`
              }
            >
              <item.icon size={16} className="shrink-0" />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="lg:hidden flex items-center gap-4 px-4 py-3 border-b bg-card sticky top-0 z-30">
          <button
            className="p-2 rounded-lg hover:bg-accent transition-colors"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={18} />
          </button>
          <span className="font-semibold text-sm">{APP_TITLE}</span>
        </header>
        <main className="p-6 lg:p-8 max-w-screen-2xl">
          <Outlet />
        </main>
      </div>
    </div>
  );
}