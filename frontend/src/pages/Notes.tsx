import { FormEvent, useCallback, useEffect, useState } from "react";
import { Pencil, Trash2, X } from "lucide-react";
import { api } from "../api";
import { Empty, Win } from "../components/ui";

const CATS = ["Interview Preparation", "Interview Questions", "Interview Answers", "Assessment Preparation", "Company Research", "General Notes"];

function NoteCard({ n, onChange, onEdit }: { n: any; onChange: () => void; onEdit: () => void }) {
  const [text, setText] = useState("");
  const pct = n.progress.total ? Math.round((n.progress.done / n.progress.total) * 100) : 0;
  const add = async (e: FormEvent) => { e.preventDefault(); if (!text.trim()) return; await api("/checklists", { method: "POST", body: { text, note_id: n.id } }); setText(""); onChange(); };
  const toggle = async (i: any) => { await api(`/checklists/${i.id}`, { method: "PUT", body: { done: !i.done } }); onChange(); };
  const rm = async (i: any) => { await api(`/checklists/${i.id}`, { method: "DELETE" }); onChange(); };
  const delNote = async () => { if (window.confirm(`Hapus catatan “${n.title}” beserta checklist-nya?`)) { await api(`/notes/${n.id}`, { method: "DELETE" }); onChange(); } };
  return (
    <Win title={n.category}>
      <h3 className="font-bold">{n.title}</h3>
      {n.application_id && <p className="text-xs">Terkait lamaran #{n.application_id}</p>}
      {n.content && <p className="mt-1 whitespace-pre-wrap text-sm">{n.content}</p>}
      <div className="mt-3" aria-label={`Progres ${pct}%`}>
        <div className="h-2 overflow-hidden rounded-full bg-gray-200"><div className="h-full bg-meadow transition-all" style={{ width: `${pct}%` }} /></div>
        <p className="mt-1 text-xs">{n.progress.done}/{n.progress.total} selesai</p>
      </div>
      <ul className="mt-2 space-y-1">{n.items.map((i: any) => (
        <li key={i.id} className="flex items-center gap-2 text-sm">
          <input type="checkbox" className="h-4 w-4 accent-sky" checked={i.done} onChange={() => toggle(i)} id={`c${i.id}`} />
          <label htmlFor={`c${i.id}`} className={`flex-1 ${i.done ? "line-through opacity-60" : ""}`}>{i.text}</label>
          <button aria-label="Hapus item" onClick={() => rm(i)}><X size={14} /></button></li>))}</ul>
      <form onSubmit={add} className="mt-2 flex gap-2"><input className="input" placeholder="Tambah item checklist" value={text} onChange={(e) => setText(e.target.value)} aria-label="Item baru" /><button className="btn-ghost">Tambah</button></form>
      <div className="mt-3 flex gap-2"><button className="btn-ghost !px-3" aria-label="Edit" onClick={onEdit}><Pencil size={14} /></button><button className="btn-ghost !px-3" aria-label="Hapus" onClick={delNote}><Trash2 size={14} /></button></div>
    </Win>
  );
}

export default function Notes() {
  const [notes, setNotes] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [cat, setCat] = useState("");
  const [form, setForm] = useState<any | null>(null);
  const [err, setErr] = useState("");
  const [apps, setApps] = useState<any[]>([]);
  useEffect(() => { api("/applications").then((d) => setApps(d.applications)).catch(() => {}); }, []);
  const load = useCallback(() => {
    const q = new URLSearchParams({ ...(search && { search }), ...(cat && { category: cat }) });
    api("/notes?" + q).then((d) => setNotes(d.notes)).catch((e) => setErr(e.message));
  }, [search, cat]);
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [load]);
  useEffect(() => { if (new URLSearchParams(window.location.search).has("new")) setForm({ title: "", content: "", category: "Interview Preparation" }); }, []);
  const save = async (e: FormEvent) => {
    e.preventDefault(); setErr("");
    try { await api(form.id ? `/notes/${form.id}` : "/notes", { method: form.id ? "PUT" : "POST", body: { title: form.title, content: form.content, category: form.category, application_id: form.application_id ? Number(form.application_id) : null } }); setForm(null); load(); }
    catch (x) { setErr((x as Error).message); }
  };
  const f = (k: string) => ({ value: form?.[k] ?? "", onChange: (e: React.ChangeEvent<any>) => setForm({ ...form, [k]: e.target.value }) });
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-3xl font-extrabold text-choc">Notes</h1>
        <input className="input w-52" placeholder="Cari catatan" value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Cari" />
        <select className="input w-auto" value={cat} onChange={(e) => setCat(e.target.value)} aria-label="Kategori"><option value="">Semua kategori</option>{CATS.map((c) => <option key={c}>{c}</option>)}</select>
        <button className="btn-primary" onClick={() => setForm({ title: "", content: "", category: "Interview Preparation" })}>Buat catatan</button>
      </div>
      {err && !form && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{err}</p>}
      {notes.length === 0 ? <Win title="catatan.exe"><Empty text={search || cat ? "Tidak ada catatan yang cocok." : "Belum ada catatan. Buat daftar persiapan interview pertamamu."} /></Win> :
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">{notes.map((n) => <NoteCard key={n.id} n={n} onChange={load} onEdit={() => setForm({ ...n })} />)}</div>}
      {form && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-cocoa/40 p-4" role="dialog" aria-modal="true">
          <form onSubmit={save} className="w-full max-w-md"><Win title={form.id ? "edit_catatan.exe" : "catatan_baru.exe"}>
            <div className="grid gap-3">
              <input className="input" placeholder="Judul *" required {...f("title")} aria-label="Judul" />
              <select className="input" {...f("category")} aria-label="Kategori">{CATS.map((c) => <option key={c}>{c}</option>)}</select>
              <select className="input" {...f("application_id")} aria-label="Lamaran terkait"><option value="">Tidak terkait lamaran</option>{apps.map((a) => <option key={a.id} value={a.id}>{a.position} @ {a.company_name}</option>)}</select>
              <textarea className="input" rows={5} placeholder="Isi catatan" {...f("content")} aria-label="Isi" />
            </div>
            {err && <p role="alert" className="mt-3 rounded-lg bg-bubble/40 p-2 text-sm">{err}</p>}
            <div className="mt-4 flex justify-end gap-2"><button type="button" className="btn-ghost" onClick={() => { setForm(null); setErr(""); }}>Batal</button><button className="btn-primary">Simpan</button></div>
          </Win></form>
        </div>)}
    </div>
  );
}
