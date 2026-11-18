import { FormEvent, useCallback, useEffect, useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { api } from "../api";
import { Win } from "../components/ui";

const TYPES = ["Interview", "Assessment Test", "Application Deadline", "Document Submission", "Follow-up", "Other"];
const pad = (n: number) => String(n).padStart(2, "0");
const iso = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export default function CalendarPage() {
  const [cur, setCur] = useState(new Date());
  const [view, setView] = useState<"month" | "week">("month");
  const [events, setEvents] = useState<any[]>([]);
  const [form, setForm] = useState<any | null>(null);
  const [err, setErr] = useState("");
  const y = cur.getFullYear(), m = cur.getMonth();
  const ws = new Date(y, m, cur.getDate() - cur.getDay());
  const range = view === "month" ? [new Date(y, m, 1), new Date(y, m + 1, 0)] : [ws, new Date(ws.getFullYear(), ws.getMonth(), ws.getDate() + 6)];
  const from = iso(range[0]), to = iso(range[1]);
  const cells: (Date | null)[] = view === "month"
    ? [...Array(range[0].getDay()).fill(null), ...Array.from({ length: range[1].getDate() }, (_, i) => new Date(y, m, i + 1))]
    : Array.from({ length: 7 }, (_, i) => new Date(ws.getFullYear(), ws.getMonth(), ws.getDate() + i));
  const title = view === "month" ? cur.toLocaleDateString("id-ID", { month: "long", year: "numeric" })
    : `${range[0].toLocaleDateString("id-ID", { day: "numeric", month: "short" })} – ${range[1].toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}`;

  const load = useCallback(() => {
    api(`/events?from=${from}T00:00&to=${to}T23:59`).then((d) => setEvents(d.events)).catch((e) => setErr(e.message));
  }, [from, to]);
  useEffect(() => { load(); }, [load]);
  useEffect(() => { if (new URLSearchParams(window.location.search).has("new")) setForm(blank(new Date())); }, []); // eslint-disable-line

  const shift = (n: number) => setCur(view === "month" ? new Date(y, m + n, 1) : new Date(y, m, cur.getDate() + 7 * n));
  function blank(d: Date) { return { title: "", event_type: "Interview", date: iso(d), time: "09:00", location: "", description: "" }; }
  const edit = (e: any) => setForm({ id: e.id, title: e.title, event_type: e.event_type, date: e.starts_at.slice(0, 10), time: e.starts_at.slice(11, 16), location: e.location || "", description: e.description || "" });
  const save = async (ev: FormEvent) => {
    ev.preventDefault(); setErr("");
    const { id, date, time, ...rest } = form;
    try { await api(id ? `/events/${id}` : "/events", { method: id ? "PUT" : "POST", body: { ...rest, starts_at: `${date}T${time || "09:00"}` } }); setForm(null); load(); }
    catch (x) { setErr((x as Error).message); }
  };
  const del = async () => { if (window.confirm("Hapus jadwal ini?")) { await api(`/events/${form.id}`, { method: "DELETE" }); setForm(null); load(); } };
  const f = (k: string) => ({ value: form?.[k] ?? "", onChange: (e: React.ChangeEvent<any>) => setForm({ ...form, [k]: e.target.value }) });
  const todayKey = iso(new Date());

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-3xl font-extrabold text-choc">Calendar</h1>
        <div className="flex gap-1" role="group" aria-label="Tampilan">
          {(["month", "week"] as const).map((v) => <button key={v} onClick={() => setView(v)} className={view === v ? "btn-primary" : "btn-ghost"}>{v === "month" ? "Bulanan" : "Mingguan"}</button>)}</div>
        <button className="btn-ghost !px-3" aria-label="Sebelumnya" onClick={() => shift(-1)}><ChevronLeft size={16} /></button>
        <span className="min-w-[10rem] text-center font-head font-bold">{title}</span>
        <button className="btn-ghost !px-3" aria-label="Berikutnya" onClick={() => shift(1)}><ChevronRight size={16} /></button>
        <button className="btn-primary" onClick={() => setForm(blank(new Date()))}>Tambah jadwal</button>
      </div>
      {err && !form && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{err}</p>}
      <Win title="kalender.exe">
        <div className="overflow-x-auto"><div className="min-w-[640px]">
          <div className="grid grid-cols-7 gap-1 text-center text-xs font-bold">{["Min", "Sen", "Sel", "Rab", "Kam", "Jum", "Sab"].map((d) => <div key={d}>{d}</div>)}</div>
          <div className="mt-1 grid grid-cols-7 gap-1">
            {cells.map((d, i) => {
              if (!d) return <div key={"b" + i} />;
              const key = iso(d);
              return (
                <div key={key} onClick={() => setForm(blank(d))} className={`cursor-pointer rounded-lg border p-1 text-xs hover:bg-sky-soft/40 ${view === "week" ? "min-h-[220px]" : "min-h-[84px]"} ${key === todayKey ? "border-sky bg-butter/40" : "border-choc/15"}`}>
                  <span className="font-bold">{d.getDate()}</span>
                  {events.filter((e) => e.starts_at.startsWith(key)).map((e) => (
                    <button key={e.id} onClick={(ev) => { ev.stopPropagation(); edit(e); }} className={`mt-0.5 block w-full rounded bg-lav px-1 text-left ${view === "week" ? "whitespace-normal py-1" : "truncate"}`}>{e.starts_at.slice(11, 16)} {e.title}</button>))}
                </div>);
            })}
          </div>
        </div></div>
      </Win>
      {form && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-cocoa/40 p-4" role="dialog" aria-modal="true">
          <form onSubmit={save} className="w-full max-w-md"><Win title={form.id ? "edit_jadwal.exe" : "jadwal_baru.exe"}>
            <div className="grid gap-3">
              <input className="input" placeholder="Judul *" required {...f("title")} aria-label="Judul" />
              <select className="input" {...f("event_type")} aria-label="Jenis">{TYPES.map((t) => <option key={t}>{t}</option>)}</select>
              <div className="grid grid-cols-2 gap-2"><input type="date" required className="input" {...f("date")} aria-label="Tanggal" /><input type="time" className="input" {...f("time")} aria-label="Jam" /></div>
              <input className="input" placeholder="Lokasi atau link meeting" {...f("location")} aria-label="Lokasi" />
              <textarea className="input" rows={3} placeholder="Deskripsi" {...f("description")} aria-label="Deskripsi" />
            </div>
            {err && <p role="alert" className="mt-3 rounded-lg bg-bubble/40 p-2 text-sm">{err}</p>}
            <div className="mt-4 flex justify-between gap-2">
              {form.id ? <button type="button" className="btn-ghost" onClick={del}>Hapus</button> : <span />}
              <span className="flex gap-2"><button type="button" className="btn-ghost" onClick={() => { setForm(null); setErr(""); }}>Batal</button><button className="btn-primary">Simpan</button></span>
            </div></Win></form>
        </div>)}
    </div>
  );
}
