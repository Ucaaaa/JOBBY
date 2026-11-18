export async function api<T = any>(path: string, opts: { method?: string; body?: unknown } = {}): Promise<T> {
  const token = localStorage.getItem("jobby_token");
  const r = await fetch("/api" + path, {
    method: opts.method || "GET",
    headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  if (r.status === 204) return null as T;
  const d = await r.json().catch(() => ({}));
  if (!r.ok) {
    if (r.status === 401 && token) { localStorage.removeItem("jobby_token"); window.location.href = "/login"; }
    throw new Error(d.error || "Terjadi kesalahan, coba lagi");
  }
  return d as T;
}
export const STATUSES = ["Wishlist", "Applied", "Document Screening", "Assessment Test", "Interview", "Offering", "Accepted", "Rejected", "Withdrawn"];
export const STATUS_COLOR: Record<string, string> = {
  Wishlist: "bg-lav", Applied: "bg-sky-soft", "Document Screening": "bg-sky-soft", "Assessment Test": "bg-butter",
  Interview: "bg-butter", Offering: "bg-meadow/60", Accepted: "bg-meadow", Rejected: "bg-bubble", Withdrawn: "bg-gray-200" };
