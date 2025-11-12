import React from 'react';
import './SiteFooter.css';

function SiteFooter() {
  const year = new Date().getFullYear();
  return (
    <footer className="site-footer">
      <div className="site-footer__divider" />
      <div className="site-footer__content">
        <span className="site-footer__copy">&copy; {year} Cerevyn Solutions Pvt Ltd. All rights reserved.</span>
        <span className="site-footer__brand">Cerevyn</span>
        <p className="site-footer__tagline">
          Global AI company transforming healthcare, education, and business operations with intelligent solutions for a
          smarter tomorrow.
        </p>
        <div className="site-footer__contact">
          <a href="mailto:info@cerevyn.com">info@cerevyn.com</a>
          <span className="site-footer__dot">•</span>
          <a href="tel:+917893525665">+91 78935 25665</a>
        </div>
        <address className="site-footer__address">
          T Hub, Hyderabad Knowledge City, Serilingampally, Hyderabad, Telangana 500081, India
        </address>
      </div>
    </footer>
  );
}

export default SiteFooter;


