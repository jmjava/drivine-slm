"use client";

import { useMemo, useState } from "react";
import type { AmdProfile } from "@/lib/data";

export function AmdTrainer({ profiles }: { profiles: AmdProfile[] }) {
  const [id, setId] = useState(profiles[0]?.id ?? "");
  const profile = useMemo(
    () => profiles.find((p) => p.id === id) ?? profiles[0],
    [id, profiles],
  );

  if (!profile) return null;

  const train = profile.defaultTrain;
  const command = [
    "cd python && source .venv/bin/activate",
    `drivine-check-amd`,
    `drivine-train-lora --profile ${profile.id}`,
    `drivine-infer --adapter ../outputs/drivine-lora --prompt "What is Drivine?"`,
  ].join("\n");

  return (
    <div className="grid gap-8 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
      <div className="space-y-3">
        {profiles.map((p) => {
          const selected = p.id === profile.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => setId(p.id)}
              className={`w-full border px-4 py-4 text-left transition ${
                selected
                  ? "border-[var(--ember)] bg-[color-mix(in_oklab,var(--ember)_12%,transparent)]"
                  : "border-[var(--edge)] hover:border-[var(--ink)]/30"
              }`}
            >
              <div className="font-[family-name:var(--font-display)] text-xl tracking-tight">
                {p.name}
              </div>
              <p className="mt-1 font-mono text-xs text-[var(--muted)]">
                {p.chip} · {p.gpu} · {p.gfx}
              </p>
            </button>
          );
        })}
      </div>

      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {[
            ["gfx", profile.gfx],
            ["unified", `${profile.unifiedMemoryGb} GB`],
            ["target VRAM", `${profile.recommendedVramGb} GB`],
            ["method", train.method.toUpperCase()],
          ].map(([label, value]) => (
            <div key={label} className="border border-[var(--edge)] bg-[var(--panel)] px-3 py-3">
              <p className="font-mono text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]">
                {label}
              </p>
              <p className="mt-1 font-mono text-sm text-[var(--ink)]">{value}</p>
            </div>
          ))}
        </div>

        <div className="border border-[var(--edge)] bg-[var(--panel)] p-5">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[var(--ember)]">
            default LoRA recipe
          </p>
          <dl className="mt-4 grid gap-2 font-mono text-sm sm:grid-cols-2">
            <div>
              <dt className="text-[var(--muted)]">model</dt>
              <dd>{train.model}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">rank / alpha</dt>
              <dd>
                r={train.loraR} · α={train.loraAlpha}
              </dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">seq / steps</dt>
              <dd>
                {train.maxSeqLen} tok · {train.maxSteps} steps
              </dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">batch</dt>
              <dd>
                {train.batchSize} × accum {train.gradAccum} · lr {train.lr}
              </dd>
            </div>
          </dl>
        </div>

        <div>
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-[var(--muted)]">
            run on your GEEKOM
          </p>
          <pre className="mt-3 overflow-x-auto border border-[var(--edge)] bg-[var(--code)] p-4 font-mono text-[12.5px] leading-relaxed text-[var(--code-ink)]">
            {command}
          </pre>
        </div>

        <ul className="space-y-2 text-sm text-[var(--muted)]">
          {profile.notes.map((note) => (
            <li key={note} className="flex gap-2">
              <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-[var(--ember)]" />
              <span>{note}</span>
            </li>
          ))}
          <li className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 bg-[var(--ember)]" />
            <span>
              Torch index: <span className="font-mono text-[var(--ink)]">{profile.torchPackage}</span>
            </span>
          </li>
        </ul>
      </div>
    </div>
  );
}
