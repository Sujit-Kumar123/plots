"use client";

import { motion } from "motion/react";
import { Icon } from "@iconify/react";

const team = [
  {
    name: "Alex Morrison",
    role: "Co-founder & CEO",
    image: "https://images.shadcnspace.com/assets/profiles/user-1.jpg",
    bio: "Visionary leader with 12+ years shaping digital products for Fortune 500s and fast-growing startups.",
    socials: { twitter: "#", linkedin: "#" },
  },
  {
    name: "Priya Sharma",
    role: "Head of Design",
    image: "https://images.shadcnspace.com/assets/profiles/user-2.jpg",
    bio: "Award-winning designer obsessed with the space between beautiful interfaces and meaningful experiences.",
    socials: { twitter: "#", linkedin: "#", dribbble: "#" },
  },
  {
    name: "James Okafor",
    role: "Lead Engineer",
    image: "https://images.shadcnspace.com/assets/profiles/user-3.jpg",
    bio: "Full-stack architect who turns complex requirements into elegant, scalable systems.",
    socials: { twitter: "#", linkedin: "#", github: "#" },
  },
  {
    name: "Sofia Reyes",
    role: "Head of Strategy",
    image: "https://images.shadcnspace.com/assets/profiles/user-5.jpg",
    bio: "Growth strategist who connects data, market insight, and creativity to help brands reach new heights.",
    socials: { twitter: "#", linkedin: "#" },
  },
  {
    name: "Marcus Lin",
    role: "Senior Developer",
    image: "https://images.shadcnspace.com/assets/profiles/user-1.jpg",
    bio: "Performance-focused engineer with a deep love for open source and cutting-edge frontend tooling.",
    socials: { linkedin: "#", github: "#" },
  },
  {
    name: "Nina Patel",
    role: "UX Researcher",
    image: "https://images.shadcnspace.com/assets/profiles/user-2.jpg",
    bio: "Brings the user's voice into every decision through rigorous research and human-centered thinking.",
    socials: { twitter: "#", linkedin: "#" },
  },
];

const socialIcons: Record<string, string> = {
  twitter:  "lucide:twitter",
  linkedin: "lucide:linkedin",
  github:   "lucide:github",
  dribbble: "lucide:dribbble",
};

export default function TeamSection() {
  return (
    <section id="team" className="w-full py-16 md:py-24">
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
            Our Team
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
          The people behind{" "}
          <span className="font-serif italic tracking-tight">
            the craft
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
          A tight-knit group of designers, engineers, and strategists united by
          a shared obsession with quality and impact.
        </motion.p>

        {/* Team grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {team.map((member, index) => (
            <motion.div
              key={member.name}
              initial={{ opacity: 0, y: 32 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: index * 0.08, ease: "easeOut" }}
              className="group flex flex-col rounded-2xl border border-border bg-card overflow-hidden hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
            >
              {/* Photo */}
              <div className="relative overflow-hidden bg-muted aspect-[4/3]">
                <img
                  src={member.image}
                  alt={member.name}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-linear-to-t from-black/40 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

                {/* Social links — slide up on hover */}
                <div className="absolute bottom-0 left-0 right-0 flex items-center justify-center gap-2 p-4 translate-y-full group-hover:translate-y-0 transition-transform duration-300">
                  {Object.entries(member.socials).map(([platform, href]) => (
                    <a
                      key={platform}
                      href={href}
                      aria-label={platform}
                      className="flex items-center justify-center w-8 h-8 rounded-full bg-background/90 text-foreground hover:bg-primary hover:text-primary-foreground transition-colors duration-200"
                    >
                      <Icon icon={socialIcons[platform]} width={14} height={14} />
                    </a>
                  ))}
                </div>
              </div>

              {/* Info */}
              <div className="flex flex-col gap-2 p-5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="font-semibold text-foreground text-base leading-tight">
                      {member.name}
                    </h3>
                    <p className="text-xs font-medium text-primary mt-0.5">
                      {member.role}
                    </p>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {member.bio}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
