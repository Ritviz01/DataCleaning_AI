"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import {
  LayoutDashboard,
  Upload,
  Database,
  Bot,
  GitBranch,
  BarChart3,
  History,
  Settings,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from "lucide-react";

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
}

export function Sidebar({ collapsed, setCollapsed }: SidebarProps) {
  const pathname = usePathname();

  const navigation = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Upload Dataset", href: "/upload", icon: Upload },
    { name: "Dataset Explorer", href: "/datasets", icon: Database },
    { name: "AI Copilot", href: "/copilot", icon: Bot },
    { name: "Pipeline Builder", href: "/pipelines", icon: GitBranch },
    { name: "Dashboard Generator", href: "/dashboards", icon: BarChart3 },
    { name: "Audit Logs", href: "/audit", icon: History },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  return (
    <aside
      className={cn(
        "relative flex flex-col border-r border-border bg-background transition-all duration-300 z-30",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Header */}
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <Sparkles className="h-6 w-6 text-primary animate-pulse" />
          {!collapsed && (
            <span className="bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent text-lg font-bold">
              DataClean AI
            </span>
          )}
        </Link>
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-4 top-20 h-8 w-8 rounded-full border border-border bg-background shadow-md hover:bg-accent"
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronLeft className="h-4 w-4" />
          )}
        </Button>
      </div>

      {/* Nav Link Items */}
      <nav className="flex-1 space-y-1 p-2 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "group flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition-all hover:bg-accent hover:text-accent-foreground",
                isActive
                  ? "bg-primary text-primary-foreground hover:bg-primary/95"
                  : "text-muted-foreground"
              )}
            >
              <item.icon className="h-5 w-5 shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </Link>
          );
        })}
      </nav>

      {/* Footer info */}
      {!collapsed && (
        <div className="p-4 border-t border-border">
          <div className="flex items-center gap-2 rounded-lg bg-accent/50 p-2.5">
            <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center font-bold text-primary">
              DC
            </div>
            <div>
              <p className="text-xs font-semibold">Enterprise Hub</p>
              <p className="text-[10px] text-muted-foreground">Version 1.0.0</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
