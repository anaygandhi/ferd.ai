"use client"

import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Menu } from "lucide-react"

import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"

const sidebarVariants = cva(
  "fixed inset-y-0 left-0 z-50 flex w-[var(--sidebar-width)] flex-col bg-background transition-all duration-300 ease-in-out data-[expanded=false]:w-[var(--sidebar-width-collapsed)]",
  {
    variants: {
      variant: {
        default: "border-r",
        outline: "border-r",
        ghost: "",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

interface SidebarContextValue {
  expanded: boolean
  setExpanded: React.Dispatch<React.SetStateAction<boolean>>
  width: string
  collapsedWidth: string
}

const SidebarContext = React.createContext<SidebarContextValue>({
  expanded: true,
  setExpanded: () => undefined,
  width: "240px",
  collapsedWidth: "0px",
})

const useSidebar = () => {
  const context = React.useContext(SidebarContext)
  if (!context) {
    throw new Error("useSidebar must be used within a SidebarProvider")
  }
  return context
}

interface SidebarProviderProps {
  children: React.ReactNode
  width?: string
  collapsedWidth?: string
  defaultExpanded?: boolean
}

const SidebarProvider = ({
  children,
  width = "240px",
  collapsedWidth = "0px",
  defaultExpanded = true,
}: SidebarProviderProps) => {
  const [expanded, setExpanded] = React.useState(defaultExpanded)

  React.useEffect(() => {
    document.documentElement.style.setProperty("--sidebar-width", width)
    document.documentElement.style.setProperty("--sidebar-width-collapsed", collapsedWidth)
  }, [width, collapsedWidth])

  return (
    <SidebarContext.Provider value={{ expanded, setExpanded, width, collapsedWidth }}>
      {children}
    </SidebarContext.Provider>
  )
}

interface SidebarProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof sidebarVariants> {}

const Sidebar = React.forwardRef<HTMLDivElement, SidebarProps>(({ className, variant, ...props }, ref) => {
  const { expanded } = useSidebar()

  return <div ref={ref} data-expanded={expanded} className={cn(sidebarVariants({ variant }), className)} {...props} />
})
Sidebar.displayName = "Sidebar"

const SidebarTrigger = React.forwardRef<HTMLButtonElement, React.ButtonHTMLAttributes<HTMLButtonElement>>(
  ({ className, ...props }, ref) => {
    const { expanded, setExpanded } = useSidebar()

    return (
      <Button
        ref={ref}
        variant="ghost"
        size="icon"
        className={cn("h-9 w-9", className)}
        onClick={() => setExpanded(!expanded)}
        {...props}
      >
        <Menu className="h-4 w-4" />
        <span className="sr-only">Toggle Sidebar</span>
      </Button>
    )
  },
)
SidebarTrigger.displayName = "SidebarTrigger"

const SidebarContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("flex flex-1 flex-col overflow-hidden", className)} {...props} />
  },
)
SidebarContent.displayName = "SidebarContent"

const SidebarRail = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    const { expanded } = useSidebar()

    return (
      <div
        ref={ref}
        data-expanded={expanded}
        className={cn(
          "absolute inset-y-0 right-0 w-1 bg-muted/80 transition-all duration-300 ease-in-out data-[expanded=false]:w-0",
          className,
        )}
        {...props}
      />
    )
  },
)
SidebarRail.displayName = "SidebarRail"

const SidebarInset = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    const { expanded } = useSidebar()

    return (
      <div
        ref={ref}
        data-expanded={expanded}
        className={cn(
          "ml-[var(--sidebar-width)] flex flex-1 flex-col transition-all duration-300 ease-in-out data-[expanded=false]:ml-[var(--sidebar-width-collapsed)]",
          className,
        )}
        {...props}
      />
    )
  },
)
SidebarInset.displayName = "SidebarInset"

const SidebarGroup = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("px-3 py-2", className)} {...props} />
  },
)
SidebarGroup.displayName = "SidebarGroup"

const SidebarGroupLabel = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("mb-2 px-4 text-xs font-semibold text-muted-foreground", className)} {...props} />
    )
  },
)
SidebarGroupLabel.displayName = "SidebarGroupLabel"

const SidebarGroupContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("space-y-1", className)} {...props} />
  },
)
SidebarGroupContent.displayName = "SidebarGroupContent"

const SidebarMenu = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("space-y-1", className)} {...props} />
  },
)
SidebarMenu.displayName = "SidebarMenu"

const SidebarMenuItem = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("flex items-center justify-between", className)} {...props} />
  },
)
SidebarMenuItem.displayName = "SidebarMenuItem"

interface SidebarMenuButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  isActive?: boolean
}

const SidebarMenuButton = React.forwardRef<HTMLButtonElement, SidebarMenuButtonProps>(
  ({ className, isActive, ...props }, ref) => {
    return (
      <button
        ref={ref}
        data-active={isActive}
        className={cn(
          "flex w-full items-center rounded-md px-3 py-2 text-sm font-medium ring-offset-background transition-colors hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 data-[active=true]:bg-accent data-[active=true]:text-accent-foreground",
          className,
        )}
        {...props}
      />
    )
  },
)
SidebarMenuButton.displayName = "SidebarMenuButton"

const SidebarMenuBadge = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "ml-auto flex h-6 w-6 items-center justify-center rounded-full bg-primary/10 text-xs font-medium text-primary",
          className,
        )}
        {...props}
      />
    )
  },
)
SidebarMenuBadge.displayName = "SidebarMenuBadge"

const SidebarMenuSub = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("pl-6 pt-1", className)} {...props} />
  },
)
SidebarMenuSub.displayName = "SidebarMenuSub"

export {
  Sidebar,
  SidebarProvider,
  SidebarTrigger,
  SidebarContent,
  SidebarRail,
  SidebarInset,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuBadge,
  SidebarMenuSub,
  useSidebar,
}

