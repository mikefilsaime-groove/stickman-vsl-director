"use client";

import { useEffect, useRef, useState } from "react";

const GITHUB_URL =
  "https://github.com/mikefilsaime-groove/stickman-vsl-director";
const HUB_URL =
  "https://github.com/mikefilsaime-groove/mikefilsaime-skills";
const VIDEO_URL = "https://www.youtube.com/watch?v=nv7HuwnofW0";

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "styles", label: "Compare Styles" },
  { id: "workflow", label: "Workflow" },
  { id: "visual-system", label: "Visual System" },
  { id: "metrics", label: "Metrics" },
  { id: "example", label: "Example" },
  { id: "installation", label: "Installation" },
] as const;

type TabId = (typeof tabs)[number]["id"];

const metrics = [
  ["3,125", "spoken words"],
  ["240", "sentences"],
  ["233", "visual slides"],
  ["11.45", "images / minute"],
  ["13.41", "words / image"],
  ["5.24s", "average hold"],
];

const workflow = [
  {
    number: "01",
    title: "Choose the visual direction",
    copy: "Review both complete example boards and select Simple & Cute or Full-Color & Expressive before art direction begins.",
  },
  {
    number: "02",
    title: "Analyze the voiceover",
    copy: "Count every word and sentence, then preserve the exact wording as the timeline source of truth.",
  },
  {
    number: "03",
    title: "Find the visual beats",
    copy: "Split on meaning, emotion, contrast, proof, and pacing—not on arbitrary word counts.",
  },
  {
    number: "04",
    title: "Choose the concept",
    copy: "Turn each beat into one readable metaphor, expression, grid, diagram, or miniature scene.",
  },
  {
    number: "05",
    title: "Direct GPT Image 2",
    copy: "Generate through the Codex subscription by default, keeping character, line, palette, and composition consistent.",
  },
  {
    number: "06",
    title: "Hand off the timeline",
    copy: "Deliver numbered slides with the precise words read over each image, plus timing and production notes.",
  },
];

const layoutCards = [
  {
    title: "Single scene",
    copy: "One dominant idea and one unmistakable emotion.",
    visual: "single",
  },
  {
    title: "Contrast split",
    copy: "Before and after, problem and solution, old and new.",
    visual: "split",
  },
  {
    title: "Expression grid",
    copy: "A 2×2 contact sheet for rapid emotional progression.",
    visual: "grid",
  },
  {
    title: "Process diagram",
    copy: "A compact flow when sequence matters more than setting.",
    visual: "process",
  },
];

function StickFigure({ mood = "neutral" }: { mood?: string }) {
  return (
    <span className={`stick-figure mood-${mood}`} aria-hidden="true">
      <span className="stick-head">
        <i className="eye eye-left" />
        <i className="eye eye-right" />
        <i className="mouth" />
      </span>
      <span className="stick-body" />
      <span className="stick-arm arm-left" />
      <span className="stick-arm arm-right" />
      <span className="stick-leg leg-left" />
      <span className="stick-leg leg-right" />
    </span>
  );
}

function HeroStoryboard() {
  return (
    <div className="hero-board" aria-label="A sample visual storyboard">
      <div className="board-topline">
        <span>SLIDE 042</span>
        <span>00:03.8</span>
      </div>
      <div className="board-stage">
        <span className="idea-burst">IDEA</span>
        <StickFigure mood="delighted" />
        <span className="arrow-path" aria-hidden="true">↗</span>
        <div className="board-grid" aria-hidden="true">
          <span /><span /><span /><span />
        </div>
      </div>
      <div className="board-voiceover">
        <span>VOICEOVER READS</span>
        <strong>“...and suddenly, the whole idea becomes visible.”</strong>
      </div>
    </div>
  );
}

function LayoutVisual({ type }: { type: string }) {
  if (type === "grid") {
    return (
      <div className="layout-visual grid-visual" aria-hidden="true">
        <StickFigure mood="worried" />
        <StickFigure mood="surprised" />
        <StickFigure mood="thinking" />
        <StickFigure mood="delighted" />
      </div>
    );
  }
  if (type === "split") {
    return (
      <div className="layout-visual split-visual" aria-hidden="true">
        <span><StickFigure mood="worried" /></span>
        <span><StickFigure mood="delighted" /></span>
      </div>
    );
  }
  if (type === "process") {
    return (
      <div className="layout-visual process-visual" aria-hidden="true">
        <span>A</span><i>→</i><span>B</span><i>→</i><span>C</span>
      </div>
    );
  }
  return (
    <div className="layout-visual single-visual" aria-hidden="true">
      <StickFigure mood="delighted" />
      <span className="idea-burst">AHA</span>
    </div>
  );
}

function CopyCode({ children }: { children: string }) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(children);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
  }

  return (
    <div className="code-block">
      <code>{children}</code>
      <button type="button" onClick={copy} aria-label="Copy command">
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const tabRefs = useRef<Array<HTMLButtonElement | null>>([]);

  useEffect(() => {
    const hash = window.location.hash.slice(1);
    const match = tabs.find((tab) => tab.id === hash);
    if (match) setActiveTab(match.id);
  }, []);

  function chooseTab(id: TabId) {
    setActiveTab(id);
    window.history.replaceState(null, "", `#${id}`);
  }

  function onTabKeyDown(
    event: React.KeyboardEvent<HTMLButtonElement>,
    index: number,
  ) {
    if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
    if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === "Home") next = 0;
    if (event.key === "End") next = tabs.length - 1;
    chooseTab(tabs[next].id);
    tabRefs.current[next]?.focus();
  }

  return (
    <main>
      <div className="announcement">
        <span>OPEN-SOURCE CODEX SKILL</span>
        <span>GPT IMAGE 2 INCLUDED WITH YOUR CODEX SUBSCRIPTION</span>
      </div>

      <header className="site-header">
        <a className="brand" href="#overview" onClick={() => chooseTab("overview")}>
          <span className="brand-mark" aria-hidden="true">SV</span>
          <span>
            <strong>Stickman VSL</strong>
            <small>Director</small>
          </span>
        </a>
        <a className="header-github" href={GITHUB_URL} target="_blank" rel="noreferrer">
          View on GitHub <span aria-hidden="true">↗</span>
        </a>
      </header>

      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow"><span>Visual direction</span> for every spoken beat.</p>
          <h1>Turn any script into a <em>timed visual storyboard.</em></h1>
          <p className="hero-lede">
            A production-ready Codex skill that decides what every image should mean,
            how it should look, and the exact voiceover it owns.
          </p>
          <div className="hero-actions">
            <button type="button" className="button button-primary" onClick={() => chooseTab("styles")}>
              Compare the two styles <span aria-hidden="true">→</span>
            </button>
            <button type="button" className="button button-secondary" onClick={() => chooseTab("installation")}>
              Install the skill
            </button>
          </div>
          <ul className="hero-proof" aria-label="Key capabilities">
            <li><span>✓</span> Scene-by-scene prompts</li>
            <li><span>✓</span> Exact voiceover mapping</li>
            <li><span>✓</span> Editable slide timeline</li>
            <li><span>✓</span> Two complete art workflows</li>
          </ul>
        </div>
        <HeroStoryboard />
      </section>

      <section className="portal" aria-labelledby="portal-title">
        <div className="portal-heading">
          <div>
            <p className="eyebrow">EXPLORE THE SYSTEM</p>
            <h2 id="portal-title">One skill. The complete visual plan.</h2>
          </div>
          <p>Move from analysis to finished, numbered slides without losing the rhythm of the original voiceover.</p>
        </div>

        <div className="tab-shell">
          <div className="tab-list" role="tablist" aria-label="Skill guide">
            {tabs.map((tab, index) => (
              <button
                key={tab.id}
                ref={(node) => { tabRefs.current[index] = node; }}
                id={`tab-${tab.id}`}
                type="button"
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls={`panel-${tab.id}`}
                tabIndex={activeTab === tab.id ? 0 : -1}
                onClick={() => chooseTab(tab.id)}
                onKeyDown={(event) => onTabKeyDown(event, index)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div
            className="tab-panel"
            id={`panel-${activeTab}`}
            role="tabpanel"
            aria-labelledby={`tab-${activeTab}`}
            tabIndex={0}
          >
            {activeTab === "overview" && (
              <div className="panel-grid overview-panel">
                <div>
                  <p className="panel-kicker">THE CORE PROMISE</p>
                  <h3>Every image earns its place on the timeline.</h3>
                  <p>
                    Paste in a video sales letter. The skill reads the persuasion,
                    emotion, cadence, and concepts—then creates a slide manifest that
                    an image model and video editor can execute.
                  </p>
                  <div className="quote-card">
                    <span>SLIDE 018 · 00:42.1–00:46.7</span>
                    <strong>Voiceover reads:</strong>
                    <q>Most people keep adding tools when what they need is a system.</q>
                  </div>
                </div>
                <div className="feature-stack">
                  <article>
                    <span>01</span>
                    <div><h4>Semantic concept selection</h4><p>Images are chosen for what the line means and how it should feel.</p></div>
                  </article>
                  <article>
                    <span>02</span>
                    <div><h4>Visual continuity</h4><p>Character, expression language, stroke, palette, and layout stay coherent.</p></div>
                  </article>
                  <article>
                    <span>03</span>
                    <div><h4>Production ownership</h4><p>Each numbered slide carries its voiceover, prompt, duration, and QA notes.</p></div>
                  </article>
                </div>
              </div>
            )}

            {activeTab === "workflow" && (
              <div className="workflow-panel">
                <div className="panel-intro">
                  <p className="panel-kicker">THE SIX-PASS PIPELINE</p>
                  <h3>From spoken copy to visual direction.</h3>
                </div>
                <ol className="workflow-list">
                  {workflow.map((item) => (
                    <li key={item.number}>
                      <span>{item.number}</span>
                      <div><h4>{item.title}</h4><p>{item.copy}</p></div>
                    </li>
                  ))}
                </ol>
              </div>
            )}

            {activeTab === "styles" && (
              <div className="styles-panel">
                <div className="styles-intro">
                  <div>
                    <p className="panel-kicker">CHOOSE BEFORE GENERATION</p>
                    <h3>Same script. Two proven visual personalities.</h3>
                  </div>
                  <p>
                    The skill now pauses before art direction and asks which world you want.
                    Both examples below use the same two-minute voiceover and the same 23-slide timing plan.
                  </p>
                </div>

                <div className="style-choice-grid">
                  <article className="style-choice simple-choice">
                    <div className="style-choice-heading">
                      <span className="option-number">OPTION 1</span>
                      <div><h4>Simple &amp; Cute</h4><span className="style-alias">Warm · minimal · charming</span></div>
                    </div>
                    <p>
                      A warm storybook treatment with cream backgrounds, generous open space,
                      restrained accent colors, a compact blue-body character, and softer rounded
                      expressions. It feels friendly, clear, and charming, with fewer environmental
                      details competing with the message.
                    </p>
                    <ul className="style-traits">
                      <li>Cream stage-like backgrounds</li>
                      <li>Blue rectangular torso</li>
                      <li>Cleaner, quieter compositions</li>
                      <li>Cute and gently humorous faces</li>
                    </ul>
                    <div className="storyboard-pages">
                      <img src="/storyboards/simple-cute-01.webp" alt="Simple and Cute storyboard, slides 1 through 12" loading="lazy" />
                      <img src="/storyboards/simple-cute-02.webp" alt="Simple and Cute storyboard, slides 13 through 23" loading="lazy" />
                    </div>
                  </article>

                  <article className="style-choice expressive-choice">
                    <div className="style-choice-heading">
                      <span className="option-number">OPTION 2</span>
                      <div><h4>Full-Color &amp; Expressive</h4><span className="style-alias">Energetic · vivid · humorous</span></div>
                    </div>
                    <p>
                      A saturated explainer-cartoon treatment with full cyan, blue, green, and brown
                      environments; true stick-figure bodies; larger emotional reactions; more physical
                      comedy; and denser visual storytelling. It feels energetic, humorous, and closer
                      to the source-video world.
                    </p>
                    <ul className="style-traits">
                      <li>Full-color environmental backgrounds</li>
                      <li>Thin true stick-figure bodies</li>
                      <li>Richer metaphors and visual detail</li>
                      <li>Bigger reactions and more comedy</li>
                    </ul>
                    <div className="storyboard-pages">
                      <img src="/storyboards/full-color-expressive-01.webp" alt="Full-Color and Expressive storyboard, slides 1 through 12" loading="lazy" />
                      <img src="/storyboards/full-color-expressive-02.webp" alt="Full-Color and Expressive storyboard, slides 13 through 23" loading="lazy" />
                    </div>
                  </article>
                </div>

                <div className="choice-rule">
                  <span>THE SKILL WILL ASK</span>
                  <strong>“Do you prefer Option 1 — Simple &amp; Cute, or Option 2 — Full-Color &amp; Expressive?”</strong>
                  <p>No hidden default. Your answer locks the character sheet, palette, prompt system, and reference pack for the entire project.</p>
                </div>
              </div>
            )}

            {activeTab === "visual-system" && (
              <div className="visual-panel">
                <div className="panel-intro">
                  <p className="panel-kicker">THE ART DIRECTION ENGINE</p>
                  <h3>Choose a composition that makes the idea instant.</h3>
                  <p>The skill uses a controlled visual grammar—not a random stream of illustrations.</p>
                </div>
                <div className="layout-grid">
                  {layoutCards.map((card) => (
                    <article key={card.title}>
                      <LayoutVisual type={card.visual} />
                      <h4>{card.title}</h4>
                      <p>{card.copy}</p>
                    </article>
                  ))}
                </div>
                <div className="expression-strip">
                  <div><span>EXPRESSION ARC</span><strong>Worry → surprise → thought → relief</strong></div>
                  <div className="faces" aria-label="Four-expression progression">
                    <StickFigure mood="worried" />
                    <span>→</span>
                    <StickFigure mood="surprised" />
                    <span>→</span>
                    <StickFigure mood="thinking" />
                    <span>→</span>
                    <StickFigure mood="delighted" />
                  </div>
                </div>
              </div>
            )}

            {activeTab === "metrics" && (
              <div className="metrics-panel">
                <div className="panel-intro">
                  <p className="panel-kicker">REFERENCE CALIBRATION</p>
                  <h3>Measured from the example—not guessed.</h3>
                  <p>These figures calibrate pacing. The skill still changes images at conceptual beats rather than forcing a fixed interval.</p>
                </div>
                <div className="metric-grid">
                  {metrics.map(([value, label]) => (
                    <article key={label}><strong>{value}</strong><span>{label}</span></article>
                  ))}
                </div>
                <div className="metric-notes">
                  <p><strong>0.0746</strong> images per spoken word</p>
                  <p><strong>0.971</strong> structural images per sentence</p>
                  <p><strong>1.03</strong> structural sentences per image</p>
                  <p><strong>4.80s</strong> median image hold</p>
                </div>
              </div>
            )}

            {activeTab === "example" && (
              <div className="example-panel">
                <div className="video-wrap">
                  <iframe
                    src="https://www.youtube-nocookie.com/embed/nv7HuwnofW0?rel=0"
                    title="Reference video used to calibrate Stickman VSL Director"
                    loading="lazy"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                  />
                </div>
                <div className="example-copy">
                  <p className="panel-kicker">THE REFERENCE STUDY</p>
                  <h3>A frame-by-frame model of visual rhythm.</h3>
                  <p>
                    This YouTube video was analyzed for transcript density, sentence
                    boundaries, shot changes, hold duration, recurring compositions,
                    facial-expression patterns, and concept-to-image decisions.
                  </p>
                  <ul>
                    <li>233 visual slides across 20.34 minutes</li>
                    <li>232 detected transitions</li>
                    <li>Single scenes, contrasts, grids, and simple diagrams</li>
                    <li>Expressions used as narrative punctuation</li>
                  </ul>
                  <a href={VIDEO_URL} target="_blank" rel="noreferrer">Watch on YouTube <span aria-hidden="true">↗</span></a>
                </div>
              </div>
            )}

            {activeTab === "installation" && (
              <div className="install-panel">
                <div className="panel-intro">
                  <p className="panel-kicker">READY TO USE</p>
                  <h3>Install once. Direct any VSL.</h3>
                  <p>GPT Image 2 through Codex is the default renderer. Optional Gen Media routes can be selected when you specifically want another model.</p>
                </div>
                <div className="install-grid">
                  <section>
                    <span className="step-label">1 · CLONE</span>
                    <CopyCode>{`git clone ${GITHUB_URL}.git`}</CopyCode>
                  </section>
                  <section>
                    <span className="step-label">2 · INSTALL GLOBALLY</span>
                    <CopyCode>{`cp -R stickman-vsl-director ~/.codex/skills/`}</CopyCode>
                  </section>
                  <section className="prompt-example">
                    <span className="step-label">3 · RUN THE SKILL</span>
                    <blockquote>
                      Use $stickman-vsl-director on this script. Create a timed slide
                      manifest, quote the exact voiceover for every image, and render
                      with GPT Image 2 through my Codex subscription.
                    </blockquote>
                  </section>
                </div>
                <div className="model-route">
                  <span className="default-badge">DEFAULT</span>
                  <strong>Codex subscription → GPT Image 2</strong>
                  <span>Optional: Nano Banana 2, SeedDream 5.0, and other Gen Media models</span>
                </div>
                <div className="repo-links">
                  <a href={GITHUB_URL} target="_blank" rel="noreferrer">Dedicated repository <span>↗</span></a>
                  <a href={HUB_URL} target="_blank" rel="noreferrer">Mike Filsaime Skills hub <span>↗</span></a>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="closing-cta">
        <div>
          <p className="eyebrow">THE SCRIPT IS ALREADY THE TIMELINE</p>
          <h2>Give every sentence a <em>visual job.</em></h2>
        </div>
        <button type="button" className="button button-light" onClick={() => chooseTab("installation")}>
          Get the open-source skill <span aria-hidden="true">→</span>
        </button>
      </section>

      <footer>
        <div className="footer-brand">
          <span className="brand-mark" aria-hidden="true">SV</span>
          <p><strong>Stickman VSL Director</strong><br />A public Codex skill by Mike Filsaime.</p>
        </div>
        <nav aria-label="Footer links">
          <a href={GITHUB_URL} target="_blank" rel="noreferrer">GitHub</a>
          <a href={HUB_URL} target="_blank" rel="noreferrer">Skills Hub</a>
          <a href={VIDEO_URL} target="_blank" rel="noreferrer">Reference Video</a>
        </nav>
      </footer>
    </main>
  );
}
