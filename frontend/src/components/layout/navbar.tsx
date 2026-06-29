"use client";

import { usePathname } from "next/navigation";
import { useAppStore } from "@/store/app-store";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Sun, Moon, Bell, Menu, Sparkles, CheckCircle2 } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Sidebar } from "./sidebar";
import { useState, useEffect } from "react";

interface NavbarProps {
  sidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
}

export function Navbar({ sidebarCollapsed, setSidebarCollapsed }: NavbarProps) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const notifications = useAppStore((state) => state.notifications);
  const clearNotifications = useAppStore((state) => state.clearNotifications);
  
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  // Format path to breadcrumb title
  const getBreadcrumbs = () => {
    const segments = pathname.split("/").filter(Boolean);
    if (segments.length === 0) return "Home";
    return segments
      .map((seg) => seg.charAt(0).toUpperCase() + seg.slice(1))
      .join(" / ");
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-background px-6 z-20">
      {/* Mobile Drawer Trigger & Breadcrumbs */}
      <div className="flex items-center gap-4">
        <Sheet>
          <SheetTrigger render={
            <Button variant="ghost" size="icon" className="md:hidden">
              <Menu className="h-5 w-5" />
            </Button>
          } />
          <SheetContent side="left" className="p-0 w-64 bg-background">
            <Sidebar collapsed={false} setCollapsed={() => {}} />
          </SheetContent>
        </Sheet>
        
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-muted-foreground">Pages</span>
          <span className="text-sm font-medium text-muted-foreground">/</span>
          <span className="text-sm font-semibold text-foreground">{getBreadcrumbs()}</span>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center gap-4">
        {/* Connection status */}
        <div className="hidden sm:flex items-center gap-1.5 rounded-full border border-border bg-accent/30 px-3 py-1 text-xs text-muted-foreground">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
          <span>Backend Connected</span>
        </div>

        {/* Notifications Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-5 w-5" />
              {notifications.length > 0 && (
                <span className="absolute right-1 top-1 flex h-2 w-2 rounded-full bg-destructive animate-pulse" />
              )}
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <DropdownMenuLabel className="flex items-center justify-between">
              <span>Notifications ({notifications.length})</span>
              {notifications.length > 0 && (
                <Button
                  variant="ghost"
                  className="h-auto p-0 text-xs text-muted-foreground hover:text-foreground"
                  onClick={clearNotifications}
                >
                  Clear all
                </Button>
              )}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <div className="max-h-64 overflow-y-auto">
              {notifications.length === 0 ? (
                <div className="p-4 text-center text-xs text-muted-foreground">
                  No new notifications.
                </div>
              ) : (
                notifications.map((notif) => (
                  <DropdownMenuItem
                    key={notif.id}
                    className="flex flex-col items-start gap-1 p-3 text-xs"
                  >
                    <div className="flex w-full items-center justify-between">
                      <span className="font-semibold">{notif.title}</span>
                      <span className="text-[10px] text-muted-foreground">
                        {new Date(notif.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <span className="text-muted-foreground">{notif.message}</span>
                  </DropdownMenuItem>
                ))
              )}
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme toggle */}
        {mounted && (
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          >
            {theme === "dark" ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </Button>
        )}
      </div>
    </header>
  );
}
