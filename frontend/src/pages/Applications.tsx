import { FormEvent, useCallback, useEffect, useState } from "react";
import { Plus, Pencil, Trash2, Search } from "lucide-react";
import { api, STATUSES } from "../api";
import { Badge, Empty, Win } from "../components/ui";

const EMPTY = { company_name: "", position: "", location: "", employment_type: "Full-time", work_arrangement: "On-site",
  status: "Applied", applied_date: "", deadline: "", job_url: "" };

export default function Applications() {
  const [rows, setRows] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("desc");
  const [form, setForm] = useState<any | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    const q = new URLSearchParams({ sort, ...(search && { search }), ...(status && { status }) });
    api("/applications?" + q).then((d) => setRows(d.applications)).catch((e) => setError(e.message)).finally(() => setLoading(false));
  }, [search, status, sort]);
  useEffect(() => { const t = setTimeout(load, 250); return () => clearTimeout(t); }, [load]);

  useEffect(() => { if (new URLSearchParams(window.location.search).has("new")) setForm({ ...EMPTY }); }, []);
  const save = async (e: FormEvent) => {
    e.preventDefault(); setError("");
    try {
      const { id, ...body } = form;
      await api(id ? `/applications/${id}` : "/applications", { method: id ? "PUT" : "POST", body });
      setForm(null); load();
    } catch (err) { setError((err as Error).message); }
  };
  const remove = async (a: any) => {
    if (!window.confirm(`Hapus lamaran ${a.position} di ${a.company_name}? Riwayat statusnya ikut terhapus.`)) return;
    await api(`/applications/${a.id}`, { method: "DELETE" }); load();
  };
  const changeStatus = async (a: any, s: string) => { await api(`/applications/${a.id}/status`, { method: "PUT", body: { status: s } }); load(); };
  const f = (k: string) => ({ value: form?.[k] ?? "", onChange: (e: React.ChangeEvent<any>) => setForm({ ...form, [k]: e.target.value }) });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2">
        <h1 className="mr-auto text-3xl font-extrabold text-choc">My Applications</h1>
        <button className="btn-primary" onClick={() => setForm({ ...EMPTY })}><Plus size={16} />Tambah lamaran</button>
      </div>
      <div className="flex flex-wrap gap-2">
        <label className="relative min-w-[200px] flex-1"><Search size={16} className="absolute left-3 top-2.5 text-choc/60" />
          <input className="input pl-9" placeholder="Cari perusahaan atau posisi" value={search} onChange={(e) => setSearch(e.target.value)} aria-label="Cari" /></label>
        <select className="input w-auto" value={status} onChange={(e) => setStatus(e.target.value)} aria-label="Filter status">
          <option value="">Semua status</option>{STATUSES.map((s) => <option key={s}>{s}</option>)}</select>
        <select className="input w-auto" value={sort} onChange={(e) => setSort(e.target.value)} aria-label="Urutkan">
          <option value="desc">Terbaru</option><option value="asc">Terlama</option></select>
      </div>
      {error && !form && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{error}</p>}
      <Win title="daftar_lamaran.exe">
        {loading ? <Empty text="Memuat…" /> : rows.length === 0 ? <Empty text={search || status ? "Tidak ada lamaran yang cocok dengan filter." : "Belum ada lamaran. Klik “Tambah lamaran” untuk memulai."} /> :
          <ul className="divide-y divide-choc/10">{rows.map((a) => (
            <li key={a.id} className="flex flex-wrap items-center gap-3 py-3">
              <div className="min-w-[200px] flex-1"><p className="font-semibold">{a.position}</p>
                <p className="text-sm">{a.company_name}{a.location ? ` · ${a.location}` : ""} · {a.applied_date || "tanggal belum diisi"}</p></div>
              <Badge status={a.status} />
              <select className="input w-auto" value={a.status} onChange={(e) => changeStatus(a, e.target.value)} aria-label={`Ubah status ${a.position}`}>
                {STATUSES.map((s) => <option key={s}>{s}</option>)}</select>
              <button className="btn-ghost !px-3" aria-label="Edit" onClick={() => setForm({ ...EMPTY, ...a })}><Pencil size={14} /></button>
              <button className="btn-ghost !px-3" aria-label="Hapus" onClick={() => remove(a)}><Trash2 size={14} /></button>
            </li>))}</ul>}
      </Win>
      {form && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-cocoa/40 p-4" role="dialog" aria-modal="true">
          <form onSubmit={save} className="max-h-[90vh] w-full max-w-lg overflow-auto">
            <Win title={form.id ? "edit_lamaran.exe" : "lamaran_baru.exe"}>
              <div className="grid gap-3 sm:grid-cols-2">
                <input className="input" placeholder="Perusahaan *" required {...f("company_name")} aria-label="Perusahaan" />
                <input className="input" placeholder="Posisi *" required {...f("position")} aria-label="Posisi" />
                <input className="input" placeholder="Lokasi" {...f("location")} aria-label="Lokasi" />
                <select className="input" {...f("employment_type")} aria-label="Tipe">{["Full-time", "Part-time", "Internship", "Contract", "Freelance"].map((x) => <option key={x}>{x}</option>)}</select>
                <select className="input" {...f("work_arrangement")} aria-label="Sistem kerja">{["On-site", "Hybrid", "Remote"].map((x) => <option key={x}>{x}</option>)}</select>
                <select className="input" {...f("status")} aria-label="Status">{STATUSES.map((x) => <option key={x}>{x}</option>)}</select>
                <label className="text-xs">Tanggal melamar<input type="date" className="input" {...f("applied_date")} /></label>
                <label className="text-xs">Deadline<input type="date" className="input" {...f("deadline")} /></label>
                <input className="input sm:col-span-2" placeholder="URL lowongan" {...f("job_url")} aria-label="URL lowongan" />
              </div>
              {error && <p role="alert" className="mt-3 rounded-lg bg-bubble/40 p-2 text-sm">{error}</p>}
              <div className="mt-4 flex justify-end gap-2">
                <button type="button" className="btn-ghost" onClick={() => { setForm(null); setError(""); }}>Batal</button>
                <button className="btn-primary">Simpan</button></div>
            </Win>
          </form>
        </div>)}
    </div>
  );
}
