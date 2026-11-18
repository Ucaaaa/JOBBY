import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../api";
import { Win } from "../components/ui";

export default function Recovery({ mode }: { mode: "forgot" | "reset" }) {
  const [sp] = useSearchParams();
  const nav = useNavigate();
  const [v, setV] = useState("");
  const [msg, setMsg] = useState("");
  const [link, setLink] = useState("");
  const [err, setErr] = useState("");
  const submit = async (e: FormEvent) => {
    e.preventDefault(); setErr(""); setMsg("");
    try {
      if (mode === "forgot") {
        const d = await api("/auth/forgot-password", { method: "POST", body: { email: v } });
        setMsg(d.message); if (d.dev_reset_link) setLink(d.dev_reset_link);
      } else {
        await api("/auth/reset-password", { method: "POST", body: { token: sp.get("token"), new_password: v } });
        nav("/login");
      }
    } catch (x) { setErr((x as Error).message); }
  };
  return (
    <div className="sky-bg grid min-h-screen place-items-center p-4"><div className="w-full max-w-sm">
      <Win title={mode === "forgot" ? "lupa_password.exe" : "password_baru.exe"}>
        <form onSubmit={submit} className="space-y-3">
          <input className="input" required value={v} onChange={(e) => setV(e.target.value)} aria-label={mode === "forgot" ? "Email" : "Password baru"}
            type={mode === "forgot" ? "email" : "password"} minLength={mode === "forgot" ? undefined : 8} placeholder={mode === "forgot" ? "Email akun" : "Password baru (min. 8 karakter)"} />
          {err && <p role="alert" className="rounded-lg bg-bubble/40 px-3 py-2 text-sm">{err}</p>}
          {msg && <p className="rounded-lg bg-meadow/40 px-3 py-2 text-sm">{msg}</p>}
          {link && <p className="break-all rounded-lg bg-butter/50 p-2 text-xs">Mode development (belum ada layanan email): <a className="underline" href={link.replace(/^https?:\/\/[^/]+/, "")}>buka link reset</a></p>}
          <button className="btn-primary w-full">{mode === "forgot" ? "Kirim instruksi reset" : "Simpan password"}</button>
        </form>
        <p className="mt-3 text-center text-sm"><Link className="underline" to="/login">Kembali ke login</Link></p>
      </Win></div></div>
  );
}
