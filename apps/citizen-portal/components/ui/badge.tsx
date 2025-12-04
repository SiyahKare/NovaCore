import * as React from "react"
import { cn } from "@/lib/utils"

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "outline" | "secondary" | "destructive"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors",
        {
          "bg-slate-800 text-slate-100": variant === "default",
          "border border-slate-700 bg-transparent": variant === "outline",
          "bg-slate-700 text-slate-200": variant === "secondary",
          "bg-red-500/20 text-red-300": variant === "destructive",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }

