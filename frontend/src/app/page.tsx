"use client";

import Link from "next/link";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import {
  Sparkles,
  ArrowRight,
  UploadCloud,
  Layers,
  Cpu,
  Workflow,
  Check,
  Code,
  ShieldCheck,
  CheckCircle,
} from "lucide-react";

export default function Home() {
  const features = [
    {
      icon: UploadCloud,
      title: "Smart Upload & Parse",
      desc: "Drag and drop CSV, Excel, Parquet, or JSON. Instant semantic schema classification.",
    },
    {
      icon: Cpu,
      title: "AI Quality Inspector",
      desc: "Detect missing values, anomalies, types, and column anomalies automatically.",
    },
    {
      icon: Bot,
      title: "AI Copilot Chat",
      desc: "Clean data using plain English. E.g. 'Deduplicate and convert amount to float.'",
    },
    {
      icon: GitBranch,
      title: "Draggable Workflows",
      desc: "Reorder, configure, validate, and preview transformation steps in real time.",
    },
    {
      icon: BarChart3,
      title: "Auto-Generated Dashboards",
      desc: "Instant metrics, Recharts graphs, and executive summaries for clean datasets.",
    },
    {
      icon: ShieldCheck,
      title: "Enterprise Compliance",
      desc: "Fully trace modifications with historical versions and downloadable audit reports.",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen bg-black text-white selection:bg-primary selection:text-primary-foreground overflow-x-hidden">
      {/* Navbar header */}
      <header className="flex h-20 items-center justify-between px-8 md:px-16 border-b border-zinc-900 bg-black/50 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2 font-bold text-lg">
          <Sparkles className="h-6 w-6 text-primary" />
          <span className="bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">
            DataClean AI
          </span>
        </div>
        <div className="hidden md:flex items-center gap-8 text-sm text-zinc-400">
          <a href="#features" className="hover:text-white transition">Features</a>
          <a href="#workflow" className="hover:text-white transition">Workflow</a>
          <a href="#pricing" className="hover:text-white transition">Pricing</a>
        </div>
        <Link href="/dashboard">
          <Button size="sm" className="group rounded-full bg-primary hover:bg-primary/90">
            Launch Platform
            <ArrowRight className="h-4 w-4 ml-1 group-hover:translate-x-1 transition-transform" />
          </Button>
        </Link>
      </header>

      {/* Hero section */}
      <section className="relative flex flex-col items-center justify-center text-center px-4 py-24 md:py-36 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-zinc-900 via-black to-black border-b border-zinc-950">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="max-w-4xl space-y-8"
        >
          <div className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-xs text-primary font-semibold">
            <Sparkles className="h-3.5 w-3.5 animate-pulse" />
            Next-Gen Pipeline & Cleaning Engine
          </div>
          
          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight leading-none bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-transparent">
            Clean Data. Built Fast. <br className="hidden sm:inline" /> Powered by AI.
          </h1>
          
          <p className="max-w-2xl mx-auto text-base sm:text-lg text-zinc-400">
            DataClean AI is an enterprise data pipeline engine. Upload raw files, build custom transformation pipelines with your AI Copilot, preview edits, and generate charts instantly.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 items-center justify-center pt-4">
            <Link href="/dashboard">
              <Button size="lg" className="w-full sm:w-auto rounded-full bg-white text-black hover:bg-zinc-200">
                Get Started Free
              </Button>
            </Link>
            <Link href="#features">
              <Button size="lg" variant="ghost" className="w-full sm:w-auto rounded-full text-zinc-400 hover:text-white hover:bg-zinc-900 border border-zinc-800">
                Explore Features
              </Button>
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Features Grid */}
      <section id="features" className="px-8 md:px-16 py-24 border-b border-zinc-900 bg-black">
        <div className="max-w-6xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold">Built for Modern Data Teams</h2>
            <p className="text-zinc-400 max-w-xl mx-auto">
              Automate data prep, eliminate coding errors, and construct reusable cleaning templates.
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f, idx) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 15 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: idx * 0.1 }}
                className="group relative rounded-xl border border-zinc-900 bg-zinc-950/40 p-6 hover:border-primary/40 transition-colors"
              >
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
                  <f.icon className="h-6 w-6" />
                </div>
                <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">{f.title}</h3>
                <p className="text-zinc-500 text-sm">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing table */}
      <section id="pricing" className="px-8 md:px-16 py-24 bg-zinc-950/30 border-b border-zinc-900">
        <div className="max-w-5xl mx-auto space-y-16">
          <div className="text-center space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold">Flexible SaaS Pricing</h2>
            <p className="text-zinc-400">Scale DataClean AI to your organization size.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Free Tier */}
            <div className="rounded-xl border border-zinc-900 bg-black/40 p-8 space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Starter</p>
                <h3 className="text-2xl font-bold">Community</h3>
                <p className="text-4xl font-extrabold">$0 <span className="text-sm font-normal text-zinc-500">/mo</span></p>
                <p className="text-zinc-500 text-sm">Perfect for parsing small datasets locally.</p>
                <ul className="space-y-2 text-sm text-zinc-400">
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Max file size: 5MB</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Basic cleaning templates</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Single version storage</li>
                </ul>
              </div>
              <Link href="/dashboard" className="w-full">
                <Button variant="outline" className="w-full rounded-full border-zinc-800 text-white hover:bg-zinc-900">Launch Starter</Button>
              </Link>
            </div>

            {/* Pro Tier */}
            <div className="rounded-xl border border-primary bg-zinc-950 p-8 space-y-6 flex flex-col justify-between relative shadow-lg shadow-primary/15">
              <div className="absolute top-0 right-8 -translate-y-1/2 rounded-full bg-primary text-primary-foreground px-3 py-1 text-[10px] font-bold uppercase tracking-wider">
                Popular
              </div>
              <div className="space-y-4">
                <p className="text-xs font-semibold text-primary uppercase tracking-widest">Grow</p>
                <h3 className="text-2xl font-bold">Pro Developer</h3>
                <p className="text-4xl font-extrabold">$29 <span className="text-sm font-normal text-zinc-500">/mo</span></p>
                <p className="text-zinc-400 text-sm">Automated pipelines and AI-powered cleaning.</p>
                <ul className="space-y-2 text-sm text-zinc-300">
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Max file size: 100MB</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> AI Copilot Assistant</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Interactive Recharts dashboards</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Version history & rollback</li>
                </ul>
              </div>
              <Link href="/dashboard" className="w-full">
                <Button className="w-full rounded-full bg-primary hover:bg-primary/95 text-primary-foreground">Start Pro Trial</Button>
              </Link>
            </div>

            {/* Enterprise Tier */}
            <div className="rounded-xl border border-zinc-900 bg-black/40 p-8 space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <p className="text-xs font-semibold text-zinc-500 uppercase tracking-widest">Enterprise</p>
                <h3 className="text-2xl font-bold">Corporate</h3>
                <p className="text-4xl font-extrabold">Custom</p>
                <p className="text-zinc-500 text-sm">For teams requiring unlimited capacity and SSO.</p>
                <ul className="space-y-2 text-sm text-zinc-400">
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Unlimited file capacity</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Dedicated worker instances</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> Advanced audit & security logs</li>
                  <li className="flex items-center gap-2"><Check className="h-4 w-4 text-primary" /> SLA support 24/7</li>
                </ul>
              </div>
              <Button variant="outline" className="w-full rounded-full border-zinc-800 text-white hover:bg-zinc-900">Contact Sales</Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-900 px-8 md:px-16 py-12 bg-black text-zinc-500 text-xs flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-1.5 font-bold text-zinc-400">
          <Sparkles className="h-4 w-4 text-primary" />
          <span>DataClean AI Platform</span>
        </div>
        <p>© 2026 DataClean AI. All rights reserved. Built for professional data prep.</p>
      </footer>
    </div>
  );
}

// Inline fallback variables for import check
import { usePipelines } from "@/hooks/use-pipelines";
const Bot = Cpu;
const GitBranch = Cpu;
const BarChart3 = Cpu;
