"use client";

import { useState } from "react";
import { motion } from "motion/react";
import { CheckCircle2, TrendingUp, Code2, LayoutGrid } from "lucide-react";
import { cn } from "@/lib/utils";

type BillingCycle = "monthly" | "annual";

const plans = [
  {
    id: "starter",
    icon: TrendingUp,
    name: "Starter",
    monthlyPrice: 0,
    annualPrice: 0,
    priceLabel: "free trial",
    description: "Perfect for individuals exploring the platform.",
    featured: false,
    cta: "Get Started",
    ctaHref: "/signup",
    features: [
      "1 user",
      "Monthly active agents",
      "1,000/month agent interactions",
      "No credit card required",
    ],
  },
  {
    id: "professional",
    icon: Code2,
    name: "Professional",
    monthlyPrice: 77,
    annualPrice: 69,
    priceLabel: "month",
    description: "For growing teams that need more power and scale.",
    featured: true,
    cta: "Start 14-Day Trial",
    ctaHref: "/signup",
    features: [
      "3 users included",
      "50 monthly active agents",
      "50,000/month agent interactions",
      "Advanced analytics overview",
      "Priority Support / SLA",
    ],
  },
  {
    id: "enterprise",
    icon: LayoutGrid,
    name: "Enterprise",
    monthlyPrice: null,
    annualPrice: null,
    priceLabel: null,
    description: "Custom solutions for large-scale organisations.",
    featured: false,
    cta: "Contact Sales",
    ctaHref: "/contact",
    features: [
      "Unlimited users",
      "Unlimited monthly active agents",
      "Unlimited agent interactions",
      "Advanced analytics overview",
      "Priority Support / SLA",
      "Dedicated onboarding and training",
      "Custom integrations",
      "On-premise deployment",
    ],
  },
];

export default function PricingSection() {
  const [billing, setBilling] = useState<BillingCycle>("monthly");

  return (
    <section id="pricing" className="w-full py-16 md:py-24">
      <div className="container mx-auto px-4 max-w-6xl">

        {/* Heading */}
        <motion.h2
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="text-4xl md:text-5xl lg:text-6xl font-semibold text-center leading-tight mb-10"
        >
          Simple pricing,
          <br />
          scaled to your needs
        </motion.h2>

        {/* Billing toggle */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.15, ease: "easeOut" }}
          className="flex items-center justify-center mb-14"
        >
          <div className="inline-flex items-center gap-1 bg-muted rounded-full p-1">
            <button
              onClick={() => setBilling("monthly")}
              className={cn(
                "px-5 py-2 rounded-full text-sm font-medium transition-all duration-200",
                billing === "monthly"
                  ? "bg-foreground text-background shadow"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              Monthly
            </button>
            <button
              onClick={() => setBilling("annual")}
              className={cn(
                "px-5 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center gap-2",
                billing === "annual"
                  ? "bg-foreground text-background shadow"
                  : "text-muted-foreground hover:text-foreground",
              )}
            >
              Annual
              <span className="bg-primary text-primary-foreground text-xs font-bold px-2 py-0.5 rounded-full">
                -10%
              </span>
            </button>
          </div>
        </motion.div>

        {/* Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-stretch">
          {plans.map((plan, index) => {
            const Icon = plan.icon;
            const price =
              plan.monthlyPrice === null
                ? null
                : billing === "annual"
                ? plan.annualPrice
                : plan.monthlyPrice;

            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 32 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: index * 0.1, ease: "easeOut" }}
                className={cn(
                  "relative flex flex-col rounded-2xl p-7 border transition-all duration-300",
                  plan.featured
                    ? "bg-primary border-primary text-primary-foreground shadow-2xl shadow-primary/30 scale-[1.02]"
                    : "bg-card border-border text-card-foreground",
                )}
              >
                {/* Icon */}
                <div
                  className={cn(
                    "w-10 h-10 rounded-lg flex items-center justify-center mb-5",
                    plan.featured
                      ? "bg-primary-foreground/20"
                      : "bg-muted",
                  )}
                >
                  <Icon
                    className={cn(
                      "w-5 h-5",
                      plan.featured ? "text-primary-foreground" : "text-foreground",
                    )}
                  />
                </div>

                {/* Plan name */}
                <p
                  className={cn(
                    "text-sm font-medium mb-1",
                    plan.featured ? "text-primary-foreground/80" : "text-muted-foreground",
                  )}
                >
                  {plan.name}
                </p>

                {/* Price */}
                {price !== null ? (
                  <div className="flex items-end gap-1 mb-6">
                    <span className="text-5xl font-bold leading-none">
                      ${price}
                    </span>
                    {plan.priceLabel && (
                      <span
                        className={cn(
                          "text-sm mb-1",
                          plan.featured ? "text-primary-foreground/70" : "text-muted-foreground",
                        )}
                      >
                        /{plan.priceLabel}
                      </span>
                    )}
                  </div>
                ) : (
                  <div className="mb-6">
                    <span className="text-4xl font-bold leading-none">Let&apos;s Talk</span>
                  </div>
                )}

                {/* Divider */}
                <div
                  className={cn(
                    "border-t border-dashed mb-5",
                    plan.featured ? "border-primary-foreground/30" : "border-border",
                  )}
                />

                {/* Features label */}
                <p
                  className={cn(
                    "text-xs font-semibold uppercase tracking-widest mb-4",
                    plan.featured ? "text-primary-foreground/70" : "text-muted-foreground",
                  )}
                >
                  What&apos;s included:
                </p>

                {/* Feature list */}
                <ul className="flex flex-col gap-3 flex-1 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-2.5 text-sm">
                      <CheckCircle2
                        className={cn(
                          "w-4 h-4 mt-0.5 shrink-0",
                          plan.featured ? "text-primary-foreground" : "text-primary",
                        )}
                      />
                      <span
                        className={cn(
                          plan.featured ? "text-primary-foreground/90" : "text-foreground",
                        )}
                      >
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                {/* Divider */}
                <div
                  className={cn(
                    "border-t border-dashed mb-6",
                    plan.featured ? "border-primary-foreground/30" : "border-border",
                  )}
                />

                {/* CTA */}
                <a
                  href={plan.ctaHref}
                  className={cn(
                    "w-full py-3 rounded-full text-sm font-semibold text-center transition-all duration-200",
                    plan.featured
                      ? "bg-background text-foreground hover:bg-background/90"
                      : "bg-primary text-primary-foreground hover:bg-primary/90",
                  )}
                >
                  {plan.cta}
                </a>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
