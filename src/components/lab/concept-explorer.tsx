"use client";

import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import type { Concept } from "@/lib/data";

export function ConceptExplorer({ concepts }: { concepts: Concept[] }) {
  const [activeId, setActiveId] = useState(concepts[0]?.id ?? "");
  const active = useMemo(
    () => concepts.find((c) => c.id === activeId) ?? concepts[0],
    [activeId, concepts],
  );
  const related = useMemo(() => {
    if (!active) return [];
    const map = new Map(concepts.map((c) => [c.id, c]));
    return active.related.map((id) => map.get(id)).filter(Boolean) as Concept[];
  }, [active, concepts]);

  if (!active) return null;

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)]">
      <div className="flex flex-col gap-2">
        {concepts.map((concept) => {
          const selected = concept.id === active.id;
          return (
            <button
              key={concept.id}
              type="button"
              onClick={() => setActiveId(concept.id)}
              className={`group rounded-none border-l-2 px-4 py-3 text-left transition-colors ${
                selected
                  ? "border-l-[var(--signal)] bg-[color-mix(in_oklab,var(--signal)_12%,transparent)]"
                  : "border-l-transparent hover:border-l-[var(--edge)] hover:bg-[color-mix(in_oklab,var(--ink)_4%,transparent)]"
              }`}
            >
              <div className="flex items-center gap-2">
                <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-[var(--muted)]">
                  {concept.category}
                </span>
                {concept.id === "lora-goal" ? (
                  <Badge variant="secondary" className="rounded-none font-mono text-[10px]">
                    start here
                  </Badge>
                ) : null}
              </div>
              <div className="mt-1 font-[family-name:var(--font-display)] text-lg tracking-tight text-[var(--ink)]">
                {concept.title}
              </div>
              <p className="mt-1 line-clamp-2 text-sm text-[var(--muted)]">{concept.summary}</p>
            </button>
          );
        })}
      </div>

      <div className="relative min-h-[320px] border border-[var(--edge)] bg-[color-mix(in_oklab,var(--panel)_88%,transparent)] p-6 backdrop-blur-sm md:p-8">
        <div className="absolute right-0 top-0 h-16 w-16 border-b border-l border-[var(--signal)]/40" />
        <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-[var(--signal)]">
          concept / {active.id}
        </p>
        <h3 className="mt-3 font-[family-name:var(--font-display)] text-3xl tracking-tight text-[var(--ink)] md:text-4xl">
          {active.title}
        </h3>
        <p className="mt-4 max-w-2xl text-base leading-relaxed text-[var(--muted)]">{active.detail}</p>
        {related.length > 0 ? (
          <div className="mt-8">
            <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
              related hops
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              {related.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => setActiveId(item.id)}
                  className="border border-[var(--edge)] bg-transparent px-3 py-1.5 font-mono text-xs text-[var(--ink)] transition hover:border-[var(--signal)] hover:text-[var(--signal)]"
                >
                  {item.title}
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
