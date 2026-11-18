import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { Menu, X, LogOut, Send } from "lucide-react";
import { useAuth } from "../contexts/Auth";
import { api } from "../api";

const LINKS = [["/", "Overview"], ["/applications", "My Applications"], ["/tracker", "Tracker"],
  ["/calendar", "Calendar"], ["/companies", "Companies"], ["/notes", "Notes"]];

export default function Layout() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [open, setOpen] = useState(false);
  const [menu, setMenu] = useState(false);
  const [tg, setTg] = useState(false);
  useEffect(() => { api("/telegram/status").then((d) => setTg(d.connected)).catch(() => {}); }, []);
  const cls = ({ isActive }: { isActive: boolean }) =>
    `rounded-full px-4 py-1.5 text-sm font-semibold transition ${isActive ? "bg-sky-soft text-choc" : "hover:bg-white/70"}`;
  return (
    <div className="sky-bg min-h-screen">
      <div aria-hidden className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-[5%] top-24 h-24 w-56 animate-drift rounded-full bg-white/70 blur-xl" />
        <div className="absolute right-[8%] top-64 h-20 w-44 animate-drift rounded-full bg-white/60 blur-xl [animation-delay:-6s]" />
      </div>
      <nav className="sticky top-0 z-20 border-b-2 border-choc/20 bg-cream/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-2">
          <span className="font-brand text-2xl font-semibold text-choc">jobby<span className="text-sky">✦</span></span>
          <div className="ml-4 hidden gap-1 md:flex">{LINKS.map(([to, l]) => <NavLink key={to} to={to} end={to === "/"} className={cls}>{l}</NavLink>)}</div>
          <div className="ml-auto flex items-center gap-2">
            <Link to="/telegram" title={tg ? "Telegram terhubung" : "Telegram belum terhubung"}
              className={`hidden items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold sm:flex ${tg ? "bg-meadow/50" : "bg-gray-200"}`}>
              <Send size={14} />{tg ? "Terhubung" : "Belum terhubung"}</Link>
            <div className="relative">
              <button onClick={() => setMenu(!menu)} aria-label="Menu profil"
                className="grid h-9 w-9 place-items-center rounded-full bg-bubble font-bold text-choc">{user?.name[0]?.toUpperCase()}</button>
              {menu && (
                <div className="absolute right-0 mt-2 w-52 rounded-xl border-2 border-choc/30 bg-white p-3 shadow-lg">
                  <p className="truncate text-sm font-semibold">{user?.name}</p>
                  <p className="mb-2 truncate text-xs text-choc/70">{user?.email}</p>
                  <Link to="/profile" onClick={() => setMenu(false)} className="btn-ghost mb-2 w-full">Profil</Link>
                  <button onClick={() => { logout(); nav("/login"); }} className="btn-ghost w-full"><LogOut size={14} />Keluar</button>
                </div>
              )}
            </div>
            <button className="md:hidden" aria-label="Buka menu" onClick={() => setOpen(!open)}>{open ? <X /> : <Menu />}</button>
          </div>
        </div>
        {open && <div className="flex flex-col gap-1 px-4 pb-3 md:hidden">
          {LINKS.map(([to, l]) => <NavLink key={to} to={to} end={to === "/"} className={cls} onClick={() => setOpen(false)}>{l}</NavLink>)}</div>}
      </nav>
      <main className="relative mx-auto max-w-6xl px-4 py-6"><Outlet /></main>
    </div>
  );
}
