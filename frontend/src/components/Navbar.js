import React, { useState, useEffect } from 'react';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { Navbar as BsNavbar, Nav, Container } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const [scrolled, setScrolled] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setExpanded(false);
  }, [location]);

  return (
    <BsNavbar
      expand="lg"
      fixed="top"
      expanded={expanded}
      onToggle={setExpanded}
      className={`navbar-glass ${scrolled ? 'scrolled' : ''}`}
    >
      <Container>
        <BsNavbar.Brand as={Link} to="/" className="d-flex align-items-center">
          <span className="navbar-brand-icon">🛡️</span>
          <span className="navbar-brand-text">FactLens AI</span>
        </BsNavbar.Brand>

        <BsNavbar.Toggle aria-controls="main-nav" />
        <BsNavbar.Collapse id="main-nav">
          <Nav className="mx-auto">
            <Nav.Link
              as={NavLink}
              to="/"
              end
              className={({ isActive }) =>
                `nav-link-custom ${isActive ? 'active' : ''}`
              }
            >
              Home
            </Nav.Link>
            <Nav.Link
              as={NavLink}
              to="/analyze"
              className={({ isActive }) =>
                `nav-link-custom ${isActive ? 'active' : ''}`
              }
            >
              Analyze
            </Nav.Link>
            {isAuthenticated && (
              <>
                <Nav.Link
                  as={NavLink}
                  to="/history"
                  className={({ isActive }) =>
                    `nav-link-custom ${isActive ? 'active' : ''}`
                  }
                >
                  History
                </Nav.Link>
                <Nav.Link
                  as={NavLink}
                  to="/reports"
                  className={({ isActive }) =>
                    `nav-link-custom ${isActive ? 'active' : ''}`
                  }
                >
                  Reports
                </Nav.Link>
              </>
            )}
            {isAdmin && (
              <Nav.Link
                as={NavLink}
                to="/admin"
                className={({ isActive }) =>
                  `nav-link-custom ${isActive ? 'active' : ''}`
                }
              >
                Admin
              </Nav.Link>
            )}
          </Nav>

          <Nav className="d-flex align-items-center gap-2">
            {isAuthenticated ? (
              <>
                <span
                  style={{
                    color: 'var(--text-secondary)',
                    fontSize: 'var(--font-size-sm)',
                    fontWeight: 500,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                  }}
                >
                  <span
                    style={{
                      width: 28,
                      height: 28,
                      borderRadius: '50%',
                      background: 'var(--gradient-primary)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      color: 'white',
                    }}
                  >
                    {(user?.username || user?.email || 'U').charAt(0).toUpperCase()}
                  </span>
                  {user?.username || user?.email}
                </span>
                <button className="btn-glass" onClick={logout}>
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/?login=true" className="btn-glass">
                  Sign In
                </Link>
                <Link to="/?register=true" className="btn-primary-glow" style={{ fontSize: '0.875rem', padding: '8px 20px' }}>
                  Get Started
                </Link>
              </>
            )}
          </Nav>
        </BsNavbar.Collapse>
      </Container>
    </BsNavbar>
  );
};

export default Navbar;
