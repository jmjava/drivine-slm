"use client";

import { useMemo, useState } from "react";
import { Input } from "@/components/ui/input";
import type { InstructRow } from "@/lib/data";

export function DatasetBrowser({ rows }: { rows: InstructRow[] }) {
  const [q, setQ] = useState("");
  const [topic, setTopic] = useState("all");
  const [activeId, setActiveId] = useState(rows[0]?.id ?? "");

  const topics = useMemo(() => {
    const set = new Set(rows.map((r) => r.topic));
    return ["all", ...Array.from(set).sort()];
  }, [rows]);

  const filtered = useMemo(() => {
    const query = q.trim().toLowerCase();
    return rows.filter((row) => {
      if (topic !== "all" && row.topic !== topic) return false;
      if (!query) return true;
      return `${row.instruction} ${row.response} ${row.topic}`.toLowerCase().includes(query);
    });
  }, [q, rows, topic]);

  const active = filtered.find((r) => r.id === activeId) ?? filtered[0];

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <Input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search instructions…"
          className="h-11 rounded-none border-[var(--edge)] bg-[var(--panel)] font-mono text-sm"
        />
        <div className="flex flex-wrap gap-2">
          {topics.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTopic(t)}
              className={`px-3 py-2 font-mono text-[11px] uppercase tracking-[0.14em] transition ${
                topic === t
                  ? "bg-[var(--ink)] text-[var(--paper)]"
                  : "border border-[var(--edge)] text-[var(--muted)] hover:text-[var(--ink)]"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <p className="font-mono text-xs text-[var(--muted)]">
        showing {filtered.length} / {rows.length} pairs · sample data for local LoRA SFT
      </p>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,0.95fr)_minmax(0,1.05fr)]">
        <div className="max-h-[420px] overflow-y-auto border border-[var(--edge)]">
          {filtered.map((row) => {
            const selected = active?.id === row.id;
            return (
              <button
                key={row.id}
                type="button"
                onClick={() => setActiveId(row.id)}
                className={`block w-full border-b border-[var(--edge)] px-4 py-3 text-left transition ${
                  selected ? "bg-[color-mix(in_oklab,var(--ember)_14%,transparent)]" : "hover:bg-[var(--panel)]"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]">
                    {row.id} · {row.topic}
                  </span>
                </div>
                <p className="mt-1 text-sm text-[var(--ink)]">{row.instruction}</p>
              </button>
            );
          })}
          {filtered.length === 0 ? (
            <p className="p-6 text-sm text-[var(--muted)]">No rows match that filter.</p>
          ) : null}
        </div>

        {active ? (
          <div className="border border-[var(--edge)] bg-[var(--panel)] p-5 md:p-6">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[var(--ember)]">
              assistant target
            </p>
            <h3 className="mt-2 font-[family-name:var(--font-display)] text-2xl tracking-tight">
              {active.instruction}
            </h3>
            <pre className="mt-5 max-h-[320px] overflow-auto whitespace-pre-wrap border border-[var(--edge)] bg-[var(--code)] p-4 font-mono text-[12.5px] leading-relaxed text-[var(--code-ink)]">
              {active.response}
            </pre>
          </div>
        ) : null}
      </div>
    </div>
  );
}
