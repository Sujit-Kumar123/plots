"use client";

import { motion } from "motion/react";
import { Trophy, Star, Award, Medal, Zap, Globe } from "lucide-react";
import { cn } from "@/lib/utils";

const awards = [
  {
    icon: Trophy,
    year: "2024",
    title: "Agency of the Year",
    org: "Awwwards",
    category: "Digital Excellence",
    featured: true,
    color: "text-yellow-500",
    bg: "bg-yellow-500/10",
    border: "border-yellow-500/20",
  },
  {
    icon: Star,
    year: "2024",
    title: "Best UX Design",
    org: "CSS Design Awards",
    category: "User Experience",
    featured: false,
    color: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/20",
  },
  {
    icon: Award,
    year: "2023",
    title: "Site of the Day",
    org: "FWA",
    category: "Web Innovation",
    featured: false,
    color: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/20",
  },
  {
    icon: Medal,
    year: "2023",
    title: "Top Creative Studio",
    org: "Clutch",
    category: "B2B Services",
    featured: false,
    color: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/20",
  },
  {
    icon: Zap,
    year: "2023",
    title: "Innovation Award",
    org: "Webby Awards",
    category: "Technology",
    featured: false,
    color: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/20",
  },
  {
    icon: Globe,
    year: "2022",
    title: "Global Design Leader",
    org: "Red Dot",
    category: "Brand Identity",
    featured: false,
    color: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/20",
  },
];

const stats = [
  { value: "28+", label: "Awards Won" },
  { value: "6",   label: "Years Running" },
  { value: "12",  label: "Nominations" },
];

export default function AwardsSection() {
  return (
    <section id="awards" className="w-full py-16 md:py-24 bg-muted/40">
      <div className="container mx-auto px-4 max-w-6xl">

        {/* Label */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: "easeOut" }}
          className="flex justify-center mb-4"
        >
          <span className="text-xs font-semibold tracking-widest uppercase text-primary border border-primary/30 bg-primary/5 rounded-full px-4 py-1.5">
            Recognition
          </span>
        </motion.div>

        {/* Heading */}
        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.1, ease: "easeOut" }}
          className="text-4xl md:text-5xl lg:text-6xl font-medium text-center leading-tight mb-6"
        >
          Work that gets{" "}
          <span className="font-serif italic tracking-tight">
            recognised
          </span>
        </motion.h2>

        {/* Subtext */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
          className="text-base text-muted-foreground text-center max-w-2xl mx-auto mb-10"
        >
          Honoured by the world&apos;s most respected design and technology
          organisations for our craft, innovation, and impact.
        </motion.p>

        {/* Stats strip */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.25, ease: "easeOut" }}
          className="flex items-center justify-center gap-10 mb-16"
        >
          {stats.map((s, i) => (
            <div key={s.label} className="flex items-center gap-10">
              <div className="text-center">
                <p className="text-4xl font-bold text-foreground">{s.value}</p>
                <p className="text-sm text-muted-foreground">{s.label}</p>
              </div>
              {i < stats.length - 1 && (
                <div className="h-10 w-px bg-border" />
              )}
            </div>
          ))}
        </motion.div>

        {/* Awards grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {awards.map((award, index) => {
            const Icon = award.icon;
            return (
              <motion.div
                key={`${award.title}-${award.year}`}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.08, ease: "easeOut" }}
                className={cn(
                  "group relative flex flex-col gap-4 rounded-2xl border p-6 transition-all duration-300 hover:shadow-lg",
                  award.featured
                    ? "bg-foreground text-background border-foreground col-span-1 sm:col-span-2 lg:col-span-1 hover:shadow-foreground/10"
                    : "bg-card border-border hover:border-primary/40 hover:shadow-primary/5",
                )}
              >
                {/* Top row */}
                <div className="flex items-start justify-between">
                  <div
                    className={cn(
                      "w-11 h-11 rounded-xl flex items-center justify-center",
                      award.featured ? "bg-background/15" : award.bg,
                    )}
                  >
                    <Icon
                      className={cn(
                        "w-5 h-5",
                        award.featured ? "text-background" : award.color,
                      )}
                    />
                  </div>
                  <span
                    className={cn(
                      "text-xs font-semibold px-2.5 py-1 rounded-full border",
                      award.featured
                        ? "border-background/20 text-background/70 bg-background/10"
                        : "border-border text-muted-foreground bg-muted",
                    )}
                  >
                    {award.year}
                  </span>
                </div>

                {/* Category */}
                <p
                  className={cn(
                    "text-xs font-semibold uppercase tracking-widest",
                    award.featured ? "text-background/60" : "text-muted-foreground",
                  )}
                >
                  {award.category}
                </p>

                {/* Title */}
                <h3
                  className={cn(
                    "text-xl font-semibold leading-snug",
                    award.featured ? "text-background" : "text-foreground",
                  )}
                >
                  {award.title}
                </h3>

                {/* Org */}
                <div className="flex items-center gap-2 mt-auto">
                  <div
                    className={cn(
                      "h-px flex-1",
                      award.featured ? "bg-background/20" : "bg-border",
                    )}
                  />
                  <span
                    className={cn(
                      "text-sm font-medium",
                      award.featured ? "text-background/80" : "text-muted-foreground",
                    )}
                  >
                    {award.org}
                  </span>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
