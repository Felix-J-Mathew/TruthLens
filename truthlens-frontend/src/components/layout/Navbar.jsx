import { NavLink } from "react-router-dom"

const links = [
  { to: "/",      label: "Home" },
  { to: "/image", label: "Image Forensics" },
  { to: "/text",  label: "Text Checker" },
]

export default function Navbar() {
  return (
    <header className="border-b border-border bg-surface sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
        <span className="font-display text-xl font-bold tracking-tight text-primary">
          Truth<span className="text-flag">Lens</span>
        </span>
        <nav className="flex gap-6">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.to === "/"}
              className={({ isActive }) =>
                `text-sm font-medium transition-colors ${
                  isActive
                    ? "text-primary border-b border-flag pb-0.5"
                    : "text-secondary hover:text-primary"
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}
