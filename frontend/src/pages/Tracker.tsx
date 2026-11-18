import { useEffect, useState } from "react";
import { api, STATUSES } from "../api";
import { Badge, Win } from "../components/ui";

export default function Tracker() {
  const [cols, setCols] = useState<Record<string, any[]>>({});
  const [err, setErr] = useState("");
  const [over, setOver] = useState("");
  const [detail, setDetail] = useState<{ app: any; history: any[] } | null>(null);
  const load = () => api("/tracker").then((d) => setCols(d.columns)).catch((e) => setErr(e.message));
  useEffect(() => { load(); }, []);

  const move = async (id: number, to: string) => {
    let app: any, from = "";
    for (const [s, l] of Object.entries(cols)) { const f = l.find((a) => a.id === id); if (f) { app = f; from = s; } }
    if (!app || from === to) return;
    setCols((c) => ({ ...c, [from]: c[from].filter((a) => a.id !== id), [to]: [{ ...app, status: to }, ...(c[to] || [])] }));
    try { await api(`/applications/${id}/status`, { method: "PUT", body: { status: to } }); }
    catch (x) { setErr((x as Error).message); load(); }
  };
  const open = async (a: any) => setDetail({ app: a, history: (await api(`/applications/${a.id}/history`)).history });

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-extrabold text-choc">Tracker</h1>
      <p className="text-sm">Seret kartu ke kolom lain, atau pakai menu status di kartu (untuk layar sentuh).</p>
      {err && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{err}</p>}
      <div className="flex gap-3 overflow-x-auto pb-3">
        {STATUSES.map((s) => (
          <div key={s} onDragOver={(e) => { e.preventDefault(); setOver(s); }} onDragLeave={() => setOver("")}
            onDrop={(e) => { e.preventDefault(); setOver(""); move(Number(e.dataTransfer.getData("text/plain")), s); }}
            className={`w-64 shrink-0 rounded-2xl border-2 p-2 transition ${over === s ? "border-sky bg-sky-soft/50" : "border-choc/30 bg-white/60"}`}>
            <h2 className="mb-2 flex items-center justify-between px-1 text-sm font-bold text-choc">{s}<span className="rounded-full bg-butter px-2 text-xs">{cols[s]?.length || 0}</span></h2>
            <div className="min-h-[80px] space-y-2">
              {(cols[s] || []).map((a) => (
                <div key={a.id} draggable onDragStart={(e) => e.dataTransfer.setData("text/plain", String(a.id))}
                  className="cursor-grab rounded-xl border border-choc/30 bg-white p-2 text-sm shadow-sm active:cursor-grabbing">
                  <button className="text-left" onClick={() => open(a)}><p className="font-semibold">{a.position}</p><p className="text-xs">{a.company_name}</p></button>
                  <select className="input mt-2 !py-1 text-xs" value={a.status} onChange={(e) => move(a.id, e.target.value)} aria-label={`Status ${a.position}`}>
                    {STATUSES.map((x) => <option key={x}>{x}</option>)}</select>
                </div>))}
            </div>
          </div>))}
      </div>
      {detail && (
        <div className="fixed inset-0 z-30 grid place-items-center bg-cocoa/40 p-4" role="dialog" aria-modal="true">
          <div className="w-full max-w-md"><Win title="riwayat_status.exe">
            <p className="font-semibold">{detail.app.position} · {detail.app.company_name}</p>
            <ol className="my-3 space-y-2 border-l-2 border-sky pl-4">{detail.history.map((h, i) => (
              <li key={i} className="text-sm"><Badge status={h.to} />{" "}<span className="text-xs">{new Date(h.changed_at + "Z").toLocaleString("id-ID", { dateStyle: "medium", timeStyle: "short" })}{h.from ? ` (dari ${h.from})` : " (dibuat)"}</span></li>))}</ol>
            <button className="btn-ghost" onClick={() => setDetail(null)}>Tutup</button></Win></div>
        </div>)}
    </div>
  );
}
