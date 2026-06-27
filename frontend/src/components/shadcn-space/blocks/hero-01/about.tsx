"use client";

import { motion } from "motion/react";
import { CheckCircle } from "lucide-react";

const stats = [
  { value: "500+", label: "Projects Delivered" },
  { value: "10+",  label: "Years of Experience" },
  { value: "1k+",  label: "Happy Clients" },
  { value: "98%",  label: "Satisfaction Rate" },
];

const highlights = [
  "User-centered design philosophy",
  "Agile & transparent process",
  "Cross-functional expert team",
  "End-to-end product delivery",
  "Scalable, maintainable code",
  "Dedicated post-launch support",
];

export default function AboutSection() {
  return (
    <section id="about" className="w-full py-16 md:py-24">
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
            About Us
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
          We craft experiences that{" "}
          <span className="font-serif italic tracking-tight">
            people remember
          </span>
        </motion.h2>

        {/* Subtext */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
          className="text-base text-muted-foreground text-center max-w-2xl mx-auto mb-16"
        >
          We are a multidisciplinary studio blending strategy, design, and technology
          to help ambitious companies build products that stand out and scale up.
        </motion.p>

        {/* Stats */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, delay: 0.3, ease: "easeOut" }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20"
        >
          {stats.map((stat) => (
            <div
              key={stat.label}
              className="flex flex-col items-center justify-center text-center p-6 rounded-2xl border border-border bg-card"
            >
              <span className="text-4xl md:text-5xl font-bold text-foreground mb-1">
                {stat.value}
              </span>
              <span className="text-sm text-muted-foreground">{stat.label}</span>
            </div>
          ))}
        </motion.div>

        {/* Two-column content */}
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left — visual */}
          <motion.div
            initial={{ opacity: 0, x: -32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2, ease: "easeOut" }}
            className="relative rounded-3xl overflow-hidden bg-muted aspect-[4/3] flex items-center justify-center"
          >
            <div className="absolute inset-0 bg-linear-to-br from-primary/20 via-transparent to-primary/5" />
            <div className="grid grid-cols-2 gap-3 p-8 w-full h-full">
              {["Strategy", "Design", "Development", "Growth"].map((label, i) => (
                <div
                  key={label}
                  className="rounded-2xl border border-border bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center gap-2 p-4"
                >
                  <span className="text-2xl font-bold text-primary">{`0${i + 1}`}</span>
                  <span className="text-sm font-medium text-foreground">{label}</span>
                </div>
              ))}
            </div>
          </motion.div>

          {/* Right — text */}
          <motion.div
            initial={{ opacity: 0, x: 32 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.3, ease: "easeOut" }}
            className="flex flex-col gap-6"
          >
            <h3 className="text-2xl md:text-3xl font-semibold text-foreground leading-snug">
              A studio built on curiosity,{" "}
              <span className="font-serif italic">craft & care</span>
            </h3>
            <p className="text-muted-foreground text-base leading-relaxed">
              From scrappy startups to established enterprises, we partner with
              clients who share our belief that great design is great business.
              Our team brings together researchers, designers, engineers, and
              strategists to deliver work that truly moves the needle.
            </p>
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {highlights.map((item) => (
                <li key={item} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <CheckCircle className="w-4 h-4 text-primary mt-0.5 shrink-0" />
                  {item}
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
