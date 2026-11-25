import { AmdTrainer } from "@/components/lab/amd-trainer";
import { ConceptExplorer } from "@/components/lab/concept-explorer";
import { DatasetBrowser } from "@/components/lab/dataset-browser";
import { GraphField } from "@/components/lab/graph-field";
import { getConcepts, getInstruct, getProfiles } from "@/lib/data";

export default function Home() {
  const concepts = getConcepts();
  const rows = getInstruct();
  const profiles = getProfiles();

  return (
    <main className="relative flex-1">
      <section className="relative isolate min-h-[100svh] overflow-hidden px-5 pb-16 pt-8 md:px-10 md:pb-24 md:pt-10">
        <GraphField />
        <div className="relative mx-auto flex min-h-[calc(100svh-4rem)] max-w-6xl flex-col justify-between">
          <header className="flex items-center justify-between gap-4">
            <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-[var(--muted)]">
              drivine.org × local LoRA
            </p>
            <a
              href="https://drivine.org/"
              target="_blank"
              rel="noreferrer"
              className="font-mono text-[11px] uppercase tracking-[0.16em] text-[var(--signal)] underline-offset-4 hover:underline"
            >
              docs
            </a>
          </header>

          <div className="max-w-4xl py-16 md:py-20">
            <p className="rise-in font-mono text-[11px] uppercase tracking-[0.24em] text-[var(--signal)]">
              slm family · drivine track
            </p>
            <h1 className="rise-in rise-delay-1 mt-4 font-[family-name:var(--font-display)] text-[clamp(2.8rem,9vw,6.4rem)] leading-[0.92] tracking-[-0.04em] text-[var(--ink)]">
              drivine
              <span className="block text-[var(--signal)]">-slm</span>
            </h1>
            <p className="rise-in rise-delay-2 mt-6 max-w-xl text-lg leading-relaxed text-[var(--muted)] md:text-xl">
              Sibling of embabel-slm: map drivine.org into a corpus, then train a
              LoRA on the Halo AMD host when the clean baseline is scored.
            </p>
            <div className="rise-in rise-delay-3 mt-8 flex flex-wrap gap-3">
              <a
                href="#concepts"
                className="bg-[var(--ink)] px-5 py-3 font-mono text-xs uppercase tracking-[0.16em] text-[var(--paper)] transition hover:bg-[var(--signal)]"
              >
                Explore concepts
              </a>
              <a
                href="#train"
                className="border border-[var(--ink)]/25 px-5 py-3 font-mono text-xs uppercase tracking-[0.16em] text-[var(--ink)] transition hover:border-[var(--ember)] hover:text-[var(--ember)]"
              >
                AMD train recipe
              </a>
            </div>
          </div>

          <div className="grid gap-4 border-t border-[var(--edge)] pt-6 font-mono text-[11px] uppercase tracking-[0.14em] text-[var(--muted)] sm:grid-cols-3">
            <p>{concepts.length} graph concepts</p>
            <p>{rows.length} instruction pairs</p>
            <p>{profiles.length} GEEKOM / RDNA profiles</p>
          </div>
        </div>
      </section>

      <section id="concepts" className="px-5 py-20 md:px-10 md:py-28">
        <div className="mx-auto max-w-6xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-[var(--signal)]">
            01 · drivine map
          </p>
          <h2 className="mt-3 max-w-2xl font-[family-name:var(--font-display)] text-4xl tracking-tight text-[var(--ink)] md:text-5xl">
            Compose views. Retrieve with vectors. Train the assistant.
          </h2>
          <p className="mt-4 max-w-2xl text-[var(--muted)]">
            Browse the core ideas from drivine.org — object manager, Cypher on
            SQL stores, graph RAG — then hop related concepts like a tiny knowledge graph.
          </p>
          <div className="section-rule my-10" />
          <ConceptExplorer concepts={concepts} />
        </div>
      </section>

      <section id="dataset" className="px-5 py-20 md:px-10 md:py-28">
        <div className="mx-auto max-w-6xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-[var(--ember)]">
            02 · instruction set
          </p>
          <h2 className="mt-3 max-w-2xl font-[family-name:var(--font-display)] text-4xl tracking-tight md:text-5xl">
            What the LoRA learns
          </h2>
          <p className="mt-4 max-w-2xl text-[var(--muted)]">
            Sample Q&amp;A distilled for supervised fine-tuning: APIs, fragments,
            loadNearest, engine notes, and GEEKOM training tips. Extend{" "}
            <code className="font-mono text-[var(--ink)]">data/drivine_instruct.json</code>{" "}
            with your own schemas before a long run.
          </p>
          <div className="section-rule my-10" />
          <DatasetBrowser rows={rows} />
        </div>
      </section>

      <section id="train" className="px-5 py-20 md:px-10 md:py-28">
        <div className="mx-auto max-w-6xl">
          <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-[var(--ember)]">
            03 · GEEKOM AMD
          </p>
          <h2 className="mt-3 max-w-2xl font-[family-name:var(--font-display)] text-4xl tracking-tight md:text-5xl">
            LoRA on Ryzen AI silicon
          </h2>
          <p className="mt-4 max-w-2xl text-[var(--muted)]">
            Profiles for A9 Mega/Max+ (<span className="font-mono">gfx1151</span>) and
            A9 Max (<span className="font-mono">gfx1150</span>). Training runs on your
            machine via the Python lab — this page is the briefing room.
          </p>
          <div className="section-rule my-10" />
          <AmdTrainer profiles={profiles} />
        </div>
      </section>

      <footer className="border-t border-[var(--edge)] px-5 py-10 md:px-10">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 text-sm text-[var(--muted)] md:flex-row md:items-center md:justify-between">
          <p className="font-[family-name:var(--font-display)] text-lg tracking-tight text-[var(--ink)]">
            drivine-slm
          </p>
          <p className="font-mono text-xs">
            Concepts are sample study notes — verify against{" "}
            <a className="text-[var(--signal)] underline-offset-2 hover:underline" href="https://drivine.org/" target="_blank" rel="noreferrer">
              drivine.org
            </a>{" "}
            before production use.
          </p>
        </div>
      </footer>
    </main>
  );
}
