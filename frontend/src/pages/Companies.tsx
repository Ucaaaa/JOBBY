import { FormEvent, useEffect, useState } from "react";
import { Pencil, Trash2 } from "lucide-react";
import { api } from "../api";
import { Empty, Win } from "../components/ui";

export default function Companies() {
  const [rows, setRows] = useState<any[]>([]);
  const [q, setQ] = useState("");
  const [form, setForm] = useState<any | null>(null);
  const [err, setErr] = useState("");
  const load = () => api("/companies").then((d) => setRows(d.companies)).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);
  const shown = rows.filter((c) => (c.name + (c.industry || "")).toLowerCase().includes(q.toLowerCase()));
  useEffect(() => { if (new URLSearchParams(window.location.search).has("new")) setForm({ name: "", industry: "", location: "", website: "", logo_url: "", career_page: "", description: "", research_notes: "" }); }, []);
  const save = async (e: FormEvent) => {
    e.preventDefault(); setErr("");
    const { id, ...body } = form;
    try { await api(id ? `/companies/${id}` : "/companies", { method: id ? "PUT" : "POST", body }); setForm(null); load(); }
    catch (x) { setErr((x as Error).message); }
  };
  const del = async (c: any) => { if (window.confirm(`Hapus ${c.name}? Lamaran terkait tidak ikut terhapus.`)) { await api(`/companies/${c.id}`, { method: "DELETE" }); load(); } };
  const f = (k: string) => ({ value: form?.[k] ?? "", onChange: (e: React.ChangeEvent<any>) => setForm({ ...form, [k]: e.target.value }) });
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-3xl font-extrabold text-choc">Companies</h1>
        <input className="input w-56" placeholder="Cari perusahaan" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Cari" />
        <button className="btn-primary" onClick={() => setForm({ name: "", industry: "", location: "", website: "", logo_url: "", career_page: "", description: "", research_notes: "" })}>Tambah perusahaan</button>
      </div>
      {err && !form && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{err}</p>}
      {shown.length === 0 ? <Win title="perusahaan.exe"><Empty text={q ? "Tidak ada perusahaan yang cocok." : "Belum ada perusahaan. Simpan riset tentang perusahaan incaranmu di sini."} /></Win> :
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">{shown.map((c) => (
          <Win key={c.id} title={c.name}>
            {c.logo_url && <img src={c.logo_url} alt="" className="mb-2 h-10 rounded" />}
            <p className="text-sm">{[c.industry, c.location].filter(Boolean).join(" · ") || "Detail belum diisi"}</p>
            {c.website && <a className="text-sm underline" href={c.website} target="_blank" rel="noreferrer">{c.website}</a>}
            {c.description && <p className="mt-1 text-sm">{c.description}</p>}
            {c.career_page && <a className="block text-sm underline" href={c.career_page} target="_blank" rel="noreferrer">Halaman karier</a>}
            {c.research_notes && <p className="mt-2 whitespace-pre-wrap rounded-lg bg-butter/40 p-2 text-sm">{c.research_notes}</p>}
            <div className="mt-3 flex gap-2"><button className="btn-ghost !px-3" aria-label="Edit" onClick={() => setForm({ ...c })}><Pencil size={14} /></button>
              <button className="btn-ghost !px-3" aria-label="Hapus" onClick={() => del(c)}><Trash2 size={14} /></button></div>
          </Win>))}</div>}
      {form && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-cocoa/40 p-4" role="dialog" aria-modal="true">
          <form onSubmit={save} className="w-full max-w-md"><Win title={form.id ? "edit_perusahaan.exe" : "perusahaan_baru.exe"}>
            <div className="grid gap-3">
              <input className="input" placeholder="Nama *" required {...f("name")} aria-label="Nama" />
              <input className="input" placeholder="Industri" {...f("industry")} aria-label="Industri" />
              <input className="input" placeholder="Lokasi" {...f("location")} aria-label="Lokasi" />
              <input className="input" placeholder="Website (https://…)" {...f("website")} aria-label="Website" />
              <input className="input" placeholder="Career page (https://…)" {...f("career_page")} aria-label="Career page" />
              <input className="input" placeholder="URL logo" {...f("logo_url")} aria-label="URL logo" />
              <textarea className="input" rows={2} placeholder="Deskripsi perusahaan" {...f("description")} aria-label="Deskripsi" />
              <textarea className="input" rows={4} placeholder="Catatan riset" {...f("research_notes")} aria-label="Catatan riset" />
            </div>
            {err && <p role="alert" className="mt-3 rounded-lg bg-bubble/40 p-2 text-sm">{err}</p>}
            <div className="mt-4 flex justify-end gap-2"><button type="button" className="btn-ghost" onClick={() => { setForm(null); setErr(""); }}>Batal</button><button className="btn-primary">Simpan</button></div>
          </Win></form>
        </div>)}
    </div>
  );
}
