import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { api } from "../api";
import { useAuth } from "../contexts/Auth";
import { Badge, Empty, Win } from "../components/ui";

export default function Overview() {
  const { user } = useAuth();
  const [s, setS] = useState<any>(null);
  const [recent, setRecent] = useState<any[]>([]);
  const [events, setEvents] = useState<any[]>([]);
  const [error, setError] = useState("");
  const [tg, setTg] = useState(false);
  const [todo, setTodo] = useState<any[]>([]);
  useEffect(() => {
    Promise.all([api("/dashboard/summary"), api("/dashboard/recent-applications"), api("/dashboard/upcoming-events"), api("/telegram/status"), api("/checklists?pending=1")])
      .then(([a, b, c, t, k]) => { setS(a); setRecent(b.applications); setEvents(c.events); setTg(t.connected); setTodo(k.items.slice(0, 5)); })
      .catch((e) => setError(e.message));
  }, []);
  const h = new Date().getHours();
  const greet = h < 11 ? "Selamat pagi" : h < 15 ? "Selamat siang" : h < 19 ? "Selamat sore" : "Selamat malam";
  const cards = s ? [["Total", s.total, "bg-sky-soft"], ["In Progress", s.in_progress, "bg-butter"], ["Interviews", s.interviews, "bg-lav"],
    ["Accepted", s.accepted, "bg-meadow/60"], ["Rejected", s.rejected, "bg-bubble/70"]] : [];
  const chart = s ? Object.entries(s.by_status).map(([status, count]) => ({ status: status.split(" ")[0], count })) : [];
  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-3xl font-extrabold text-choc">{greet}, {user?.name.split(" ")[0]}!</h1>
        <p className="text-sm">{new Date().toLocaleDateString("id-ID", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}</p>
      </div>
      {error && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{error}</p>}
      {!s && !error && <Empty text="Memuat data…" />}
      {s && <>
        <div className="grid grid-cols-2 gap-3 md:grid-cols-5">
          {cards.map(([l, n, bg]) => (
            <div key={l as string} className={`rounded-2xl border-2 border-choc/60 p-3 ${bg}`}>
              <p className="text-xs font-semibold">{l}</p><p className="font-head text-3xl font-extrabold text-choc">{n as number}</p></div>))}
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          <Win title="statistik.exe" className="lg:col-span-2">
            <div className="h-60" role="img" aria-label="Jumlah lamaran per status">
              <ResponsiveContainer><BarChart data={chart}><XAxis dataKey="status" fontSize={11} /><YAxis allowDecimals={false} fontSize={11} width={24} />
                <Tooltip /><Bar dataKey="count" fill="#76B9EF" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div>
          </Win>
          <Win title="jadwal.exe">
            {events.length === 0 ? <Empty text="Belum ada jadwal. Tambahkan interview atau deadline di Calendar." /> :
              <ul className="space-y-2">{events.map((e) => (
                <li key={e.id} className="rounded-xl bg-butter/50 p-2 text-sm"><p className="font-semibold">{e.title}</p>
                  <p className="text-xs">{new Date(e.starts_at).toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" })} · {e.event_type}</p></li>))}</ul>}
          </Win>
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          <Win title="aksi_cepat.exe"><div className="flex flex-wrap gap-2">
            <Link className="btn-primary" to="/applications?new=1">Tambah lamaran</Link><Link className="btn-ghost" to="/calendar?new=1">Tambah jadwal</Link>
            <Link className="btn-ghost" to="/companies?new=1">Tambah perusahaan</Link><Link className="btn-ghost" to="/notes?new=1">Buat catatan</Link></div></Win>
          <Win title="telegram.exe"><p className="text-sm">{tg ? "Terhubung. Pengingat dan briefing dikirim ke Telegram." : "Belum terhubung. Hubungkan untuk menerima pengingat deadline dan interview."}</p>
            <Link className="btn-ghost mt-3" to="/telegram">{tg ? "Atur notifikasi" : "Hubungkan Telegram"}</Link></Win>
          <Win title="checklist_persiapan.exe">{todo.length === 0 ? <Empty text="Semua persiapan selesai, atau belum ada checklist." /> :
            <ul className="list-disc space-y-1 pl-5 text-sm">{todo.map((i) => <li key={i.id}>{i.text}</li>)}</ul>}<Link className="btn-ghost mt-3" to="/notes">Buka Notes</Link></Win>
        </div>
        <Win title="lamaran_terbaru.exe">
          {recent.length === 0 ? <Empty text="Belum ada lamaran. Mulai dari My Applications." /> :
            <ul className="divide-y divide-choc/10">{recent.map((a) => (
              <li key={a.id} className="flex flex-wrap items-center justify-between gap-2 py-2">
                <div><p className="font-semibold">{a.position}</p><p className="text-sm">{a.company_name} · {a.applied_date || "tanggal belum diisi"}</p></div>
                <Badge status={a.status} /></li>))}</ul>}
          <Link to="/applications" className="btn-ghost mt-3">Lihat semua lamaran</Link>
        </Win>
      </>}
    </div>
  );
}
