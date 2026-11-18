import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/Auth";
import { Win } from "../components/ui";

export default function AuthPage({ mode }: { mode: "login" | "register" }) {
  const { user, login, register } = useAuth();
  const nav = useNavigate();
  const [f, setF] = useState({ name: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/" replace />;
  const reg = mode === "register";
  const submit = async (e: FormEvent) => {
    e.preventDefault(); setError(""); setBusy(true);
    try { reg ? await register(f.name, f.email, f.password) : await login(f.email, f.password); nav("/"); }
    catch (err) { setError((err as Error).message); } finally { setBusy(false); }
  };
  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) => setF({ ...f, [k]: e.target.value });
  return (
    <div className="sky-bg grid min-h-screen place-items-center p-4">
      <div className="w-full max-w-sm">
        <h1 className="mb-1 text-center font-brand text-5xl font-semibold text-choc">jobby<span className="text-sky">✦</span></h1>
        <p className="mb-5 text-center text-sm text-choc">Your Career Journey, Organized.</p>
        <Win title={reg ? "buat_akun.exe" : "masuk.exe"}>
          <form onSubmit={submit} className="space-y-3">
            {reg && <input className="input" placeholder="Nama" required value={f.name} onChange={set("name")} aria-label="Nama" />}
            <input className="input" type="email" placeholder="Email" required value={f.email} onChange={set("email")} aria-label="Email" />
            <input className="input" type="password" placeholder="Password (min. 8 karakter)" required minLength={8} value={f.password} onChange={set("password")} aria-label="Password" />
            {error && <p role="alert" className="rounded-lg bg-bubble/40 px-3 py-2 text-sm">{error}</p>}
            <button className="btn-primary w-full" disabled={busy}>{busy ? "Memproses…" : reg ? "Buat akun" : "Masuk"}</button>
          </form>
          {!reg && <p className="mt-3 text-center text-sm"><Link className="underline" to="/forgot-password">Lupa password?</Link></p>}
          <p className="mt-3 text-center text-sm">{reg ? "Sudah punya akun?" : "Belum punya akun?"}{" "}
            <Link className="font-semibold underline" to={reg ? "/login" : "/register"}>{reg ? "Masuk" : "Daftar"}</Link></p>
        </Win>
      </div>
    </div>
  );
}
