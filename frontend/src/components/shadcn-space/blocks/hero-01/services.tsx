"use client";

import { motion } from "motion/react";
import {
  Palette,
  Code2,
  Smartphone,
  BarChart3,
  Search,
  Layers,
} from "lucide-react";

const services = [
  {
    icon: Palette,
    title: "Brand Identity",
    description:
      "We build memorable brand systems — from logo and color palette to typography and guidelines — that communicate who you are at a glance.",
  },
  {
    icon: Layers,
    title: "UI / UX Design",
    description:
      "Human-centered interfaces that delight users. We research, prototype, and test until every interaction feels natural and effortless.",
  },
  {
    icon: Code2,
    title: "Web Development",
    description:
      "Performant, accessible, and maintainable web applications built with modern frameworks and a keen eye for detail.",
  },
  {
    icon: Smartphone,
    title: "Mobile Apps",
    description:
      "Native and cross-platform mobile experiences designed for both iOS and Android, optimized for speed and user retention.",
  },
  {
    icon: BarChart3,
    title: "Digital Strategy",
    description:
      "Data-informed growth plans that align your digital presence with business objectives — turning visitors into loyal customers.",
  },
  {
    icon: Search,
    title: "SEO & Analytics",
    description:
      "We improve your search visibility and instrument your product with the right metrics so you always know what's working.",
  },
];

export default function ServicesSection() {
  return (
    <section id="services" className="w-full py-16 md:py-24 bg-muted/40">
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
            Our Services
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
          What we{" "}
          <span className="font-serif italic tracking-tight">
            do best
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
          From first spark to final pixel, we offer end-to-end services that cover
          every stage of your product journey.
        </motion.p>

        {/* Cards grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, index) => {
            const Icon = service.icon;
            return (
              <motion.div
                key={service.title}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.08, ease: "easeOut" }}
                className="group relative flex flex-col gap-4 rounded-2xl border border-border bg-card p-6 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 transition-all duration-300"
              >
                {/* Icon */}
                <div className="w-11 h-11 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors duration-300">
                  <Icon className="w-5 h-5 text-primary" />
                </div>

                {/* Title */}
                <h3 className="text-lg font-semibold text-foreground">
                  {service.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {service.description}
                </p>

                {/* Hover accent line */}
                <div className="absolute bottom-0 left-6 right-6 h-0.5 bg-linear-to-r from-primary/60 to-primary/20 rounded-full scale-x-0 group-hover:scale-x-100 transition-transform duration-500 origin-left" />
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
