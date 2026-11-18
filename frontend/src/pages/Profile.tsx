import { FormEvent, useState } from "react";
import { api } from "../api";
import { useAuth } from "../contexts/Auth";
import { Win } from "../components/ui";

export default function Profile() {
  const { user, setUser } = useAuth();
  const [p, setP] = useState({ name: user?.name || "", email: user?.email || "" });
  const [pw, setPw] = useState({ old_password: "", new_password: "" });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");
  const run = (fn: () => Promise<void>) => async (e: FormEvent) => {
    e.preventDefault(); setErr(""); setMsg("");
    try { await fn(); } catch (x) { setErr((x as Error).message); }
  };
  return (
    <div className="mx-auto max-w-md space-y-4">
      <h1 className="text-3xl font-extrabold text-choc">Profil</h1>
      {err && <p role="alert" className="rounded-lg bg-bubble/40 p-3 text-sm">{err}</p>}
      {msg && <p className="rounded-lg bg-meadow/40 p-3 text-sm">{msg}</p>}
      <Win title="profil.exe">
        <form className="space-y-3" onSubmit={run(async () => { const d = await api("/auth/profile", { method: "PUT", body: p }); setUser(d.user); setMsg("Profil diperbarui."); })}>
          <input className="input" required value={p.name} onChange={(e) => setP({ ...p, name: e.target.value })} aria-label="Nama" />
          <input className="input" type="email" required value={p.email} onChange={(e) => setP({ ...p, email: e.target.value })} aria-label="Email" />
          <button className="btn-primary">Simpan profil</button>
        </form>
      </Win>
      <Win title="ubah_password.exe">
        <form className="space-y-3" onSubmit={run(async () => { await api("/auth/change-password", { method: "PUT", body: pw }); setPw({ old_password: "", new_password: "" }); setMsg("Password diperbarui."); })}>
          <input className="input" type="password" required placeholder="Password lama" value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} aria-label="Password lama" />
          <input className="input" type="password" required minLength={8} placeholder="Password baru (min. 8 karakter)" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} aria-label="Password baru" />
          <button className="btn-primary">Ubah password</button>
        </form>
      </Win>
    </div>
  );
}
