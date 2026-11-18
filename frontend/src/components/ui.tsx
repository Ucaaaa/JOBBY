import { ReactNode } from "react";
import { STATUS_COLOR } from "../api";

export function Win({ title, children, className = "" }: { title: string; children: ReactNode; className?: string }) {
  return (
    <section className={`overflow-hidden rounded-2xl border-2 border-choc/70 bg-white shadow-[4px_4px_0_#B8DDF8] ${className}`}>
      <header className="flex items-center gap-2 border-b-2 border-choc/70 bg-gradient-to-r from-sky-soft to-lav px-3 py-1.5">
        <span className="h-3 w-3 rounded-full bg-bubble" /><span className="h-3 w-3 rounded-full bg-butter" /><span className="h-3 w-3 rounded-full bg-meadow" />
        <h2 className="ml-2 font-head text-sm font-bold text-choc">{title}</h2>
      </header>
      <div className="p-4">{children}</div>
    </section>
  );
}
export const Badge = ({ status }: { status: string }) => (
  <span className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_COLOR[status] || "bg-gray-200"}`}>{status}</span>
);
export const Empty = ({ text }: { text: string }) => <p className="py-6 text-center text-sm text-choc/70">{text}</p>;
