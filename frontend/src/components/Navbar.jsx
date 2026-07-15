import { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar({ onOpenLogin, onOpenSignup }) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 30);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const links = [
    { to: "/", label: "Search" },
    { to: "/analytics", label: "Analytics" },
    { to: "/dashboard", label: "Dashboard" },
  ];

  return (
    <nav className={`navbar ${scrolled ? "scrolled" : ""}`}>
      <div className="nav-inner">
        <NavLink to="/" className="nav-logo">
          <span className="logo-icon">✈</span>
          <span className="logo-text">Price<span className="logo-accent">Lens</span></span>
        </NavLink>

        <ul className="nav-links" style={{ display: menuOpen ? "flex" : undefined }}>
          {links.map((l) => (
            <li key={l.label}>
              <NavLink
                to={l.to}
                end
                className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}
                onClick={() => setMenuOpen(false)}
              >
                {l.label}
              </NavLink>
            </li>
          ))}
        </ul>

        <div className="nav-actions" style={{ display: menuOpen ? "flex" : undefined }}>
          {user ? (
            <>
              <span className="user-pill">👤 {user.full_name?.split(" ")[0]}</span>
              <button className="btn-ghost" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <button className="btn-ghost" onClick={onOpenLogin}>Login</button>
              <button className="btn-primary" onClick={onOpenSignup}>Sign Up</button>
            </>
          )}
        </div>

        <button className="hamburger" onClick={() => setMenuOpen((m) => !m)}>
          <span></span><span></span><span></span>
        </button>
      </div>
    </nav>
  );
}
