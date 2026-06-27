"use client"

import * as React from "react"
import { Eye, EyeOff } from "lucide-react"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui/input"

type PasswordInputProps = Omit<React.ComponentProps<"input">, "type">

function PasswordInput({ className, ...props }: PasswordInputProps) {
  const [show, setShow] = React.useState(false)

  return (
    <div className="relative">
      <Input
        type={show ? "text" : "password"}
        className={cn("pr-9", className)}
        {...props}
      />
      <button
        type="button"
        tabIndex={-1}
        onClick={() => setShow((s) => !s)}
        className="absolute inset-y-0 right-0 flex items-center px-2.5 text-muted-foreground hover:text-foreground transition-colors disabled:pointer-events-none"
        disabled={props.disabled}
        aria-label={show ? "Hide password" : "Show password"}
      >
        {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
      </button>
    </div>
  )
}

export { PasswordInput }
