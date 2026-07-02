import { Link } from "react-router-dom"
import { ImageIcon, FileTextIcon, ShieldIcon } from "lucide-react"

export default function HomePage() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-16 space-y-20">

      {/* Hero */}
      <section className="grid md:grid-cols-2 gap-12 items-center">
        <div>
          <p className="font-mono text-xs text-flag tracking-widest mb-4">
            MEDIA AUTHENTICITY TOOLKIT
          </p>
          <h1 className="text-5xl font-display font-bold leading-tight text-primary mb-5">
            Look closer before you believe it.
          </h1>
          <p className="text-secondary leading-relaxed mb-8">
            TruthLens examines images and articles for the small,
            machine-detectable signs of manipulation that the human eye
            misses — then explains exactly what it found, signal by signal.
          </p>
          <div className="flex gap-4">
            <Link
              to="/image"
              className="px-5 py-2.5 bg-accent text-white rounded-sm font-medium
                         hover:bg-accent/90 transition-colors text-sm"
            >
              Analyze an Image
            </Link>
            <Link
              to="/text"
              className="px-5 py-2.5 border border-border text-primary rounded-sm
                         font-medium hover:border-secondary transition-colors text-sm"
            >
              Check an Article
            </Link>
          </div>
        </div>

        {/* Specimen frame with animated scan indicator */}
        <div className="specimen-frame bg-surface border border-border p-8
                        flex flex-col items-center justify-center aspect-square gap-4">
          <ShieldIcon size={48} className="text-border" />
          <p className="font-mono text-xs text-muted text-center">
            AWAITING MEDIA INPUT
            <br />
            <span className="text-flag">■</span> READY TO SCAN
          </p>
        </div>
      </section>

      {/* How it works */}
      <section>
        <p className="font-mono text-xs text-secondary tracking-widest mb-6">HOW IT WORKS</p>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { step: "01", title: "Upload Media", desc: "Drop an image or paste article text into the scanner." },
            { step: "02", title: "Multi-Signal Analysis", desc: "Five forensic signals examine the media simultaneously." },
            { step: "03", title: "Read the Report", desc: "A trust score and signal-by-signal breakdown explains every finding." },
          ].map((item) => (
            <div key={item.step} className="bg-surface border border-border p-5">
              <p className="font-mono text-flag text-xs mb-3">{item.step}</p>
              <h3 className="font-display font-semibold text-primary mb-2">{item.title}</h3>
              <p className="text-secondary text-sm leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Module cards */}
      <section className="grid md:grid-cols-2 gap-4">
        <Link to="/image"
          className="bg-surface border border-border p-6 hover:border-accent
                     transition-colors group">
          <ImageIcon className="mb-4 text-secondary group-hover:text-accent transition-colors" size={22} />
          <h2 className="font-display font-semibold text-primary mb-2">Image Forensics</h2>
          <p className="text-secondary text-sm leading-relaxed">
            ELA heatmap, metadata inspection, noise consistency,
            and frequency analysis for spotting edited or AI-generated images.
          </p>
        </Link>
        <Link to="/text"
          className="bg-surface border border-border p-6 hover:border-accent
                     transition-colors group">
          <FileTextIcon className="mb-4 text-secondary group-hover:text-accent transition-colors" size={22} />
          <h2 className="font-display font-semibold text-primary mb-2">Text Credibility</h2>
          <p className="text-secondary text-sm leading-relaxed">
            Sensationalism detection, linguistic red flag analysis, and source
            verification against trusted news outlets.
          </p>
        </Link>
      </section>

    </div>
  )
}
