"use client";

import { motion } from "motion/react";
import { Icon } from "@iconify/react";
import Logo from "@/assets/logo/logo";

const footerLinks = [
  {
    heading: "Company",
    links: [
      { label: "About Us",  href: "#about"    },
      { label: "Services",  href: "#services"  },
      { label: "Pricing",   href: "#pricing"   },
      { label: "Careers",   href: "#"          },
      { label: "Blog",      href: "#"          },
    ],
  },
  {
    heading: "Product",
    links: [
      { label: "Features",     href: "#" },
      { label: "Integrations", href: "#" },
      { label: "Changelog",    href: "#" },
      { label: "Roadmap",      href: "#" },
      { label: "Status",       href: "#" },
    ],
  },
  {
    heading: "Resources",
    links: [
      { label: "Documentation", href: "#" },
      { label: "API Reference",  href: "#" },
      { label: "Support",        href: "#" },
      { label: "Community",      href: "#" },
      { label: "Contact",        href: "#" },
    ],
  },
  {
    heading: "Legal",
    links: [
      { label: "Privacy Policy",   href: "#" },
      { label: "Terms of Service", href: "#" },
      { label: "Cookie Policy",    href: "#" },
      { label: "Security",         href: "#" },
    ],
  },
];

const socialLinks = [
  { icon: "lucide:twitter",   href: "#", label: "Twitter"   },
  { icon: "lucide:linkedin",  href: "#", label: "LinkedIn"  },
  { icon: "lucide:github",    href: "#", label: "GitHub"    },
  { icon: "lucide:instagram", href: "#", label: "Instagram" },
  { icon: "lucide:dribbble",  href: "#", label: "Dribbble"  },
];

export default function Footer() {
  return (
    <footer className="w-full border-t border-border bg-card">
      <div className="container mx-auto px-4 max-w-6xl">

        {/* Top — logo + columns */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="grid grid-cols-2 md:grid-cols-6 gap-10 py-14"
        >
          {/* Brand column */}
          <div className="col-span-2 flex flex-col gap-5">
            <Logo />
            <p className="text-sm text-muted-foreground leading-relaxed max-w-xs">
              Building bold brands and thoughtful digital products for ambitious
              companies around the world.
            </p>
            {/* Social icons */}
            <div className="flex items-center gap-2 mt-1">
              {socialLinks.map(({ icon, href, label }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  className="flex items-center justify-center w-8 h-8 rounded-full border border-border text-muted-foreground hover:text-foreground hover:bg-muted transition-colors duration-200"
                >
                  <Icon icon={icon} width={15} height={15} />
                </a>
              ))}
            </div>
          </div>

          {/* Link columns */}
          {footerLinks.map((group) => (
            <div key={group.heading} className="flex flex-col gap-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-foreground">
                {group.heading}
              </p>
              <ul className="flex flex-col gap-2.5">
                {group.links.map(({ label, href }) => (
                  <li key={label}>
                    <a
                      href={href}
                      className="text-sm text-muted-foreground hover:text-foreground transition-colors duration-200"
                    >
                      {label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </motion.div>

        {/* Divider */}
        <div className="border-t border-border" />

        {/* Bottom bar */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 py-6 text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} ShadcnSpace. All rights reserved.</p>
          <div className="flex items-center gap-5">
            <a href="#" className="hover:text-foreground transition-colors duration-200">Privacy</a>
            <a href="#" className="hover:text-foreground transition-colors duration-200">Terms</a>
            <a href="#" className="hover:text-foreground transition-colors duration-200">Cookies</a>
          </div>
        </div>

      </div>
    </footer>
  );
}
