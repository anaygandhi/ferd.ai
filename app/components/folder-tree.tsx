"use client"

import { useState, useEffect } from "react"
import { ChevronRight, Folder, FolderOpen } from "lucide-react"
import path from "path-browserify"
import { cn } from "@/lib/utils"
import { getElectronAPI, type FileInfo } from "@/lib/electron-api"

interface FolderTreeProps {
  onSelectFolder: (path: string) => void
  currentPath: string
}

export function FolderTree({ onSelectFolder, currentPath }: FolderTreeProps) {
  const [rootFolders, setRootFolders] = useState<FileInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const electronAPI = getElectronAPI()
  const isElectron = !!electronAPI

  useEffect(() => {
    if (isElectron) {
      const loadRootFolders = async () => {
        try {
          // For Windows, we'd want to list drives
          // For macOS/Linux, we'd start with root or home
          if (electronAPI.platform === "win32") {
            // Mock Windows drives for now
            // In a real app, we'd use a native API to list drives
            setRootFolders([
              { name: "C:", path: "C:", isDirectory: true, size: 0, modified: "", created: "", type: "directory" },
              { name: "D:", path: "D:", isDirectory: true, size: 0, modified: "", created: "", type: "directory" },
            ])
          } else {
            // For Unix-like systems, start with home
            const files = await electronAPI.listDirectory("")
            const homePath = path.dirname(files[0]?.path || "")

            // Get parent directories up to root
            let currentDir = homePath
            const roots = []

            while (currentDir !== path.parse(currentDir).root) {
              roots.unshift({
                name: path.basename(currentDir),
                path: currentDir,
                isDirectory: true,
                size: 0,
                modified: "",
                created: "",
                type: "directory",
              })
              currentDir = path.dirname(currentDir)
            }

            // Add root
            roots.unshift({
              name: "/",
              path: path.parse(homePath).root,
              isDirectory: true,
              size: 0,
              modified: "",
              created: "",
              type: "directory",
            })

            setRootFolders(roots)
          }
        } catch (error) {
          console.error("Error loading root folders:", error)
        } finally {
          setIsLoading(false)
        }
      }

      loadRootFolders()
    } else {
      // Mock data for web preview
      setRootFolders([
        { name: "Home", path: "/home/user", isDirectory: true, size: 0, modified: "", created: "", type: "directory" },
      ])
      setIsLoading(false)
    }
  }, [isElectron, electronAPI])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
      </div>
    )
  }

  return (
    <div className="space-y-1 px-2">
      {rootFolders.map((folder) => (
        <FolderItem
          key={folder.path}
          folder={folder}
          level={0}
          onSelectFolder={onSelectFolder}
          currentPath={currentPath}
        />
      ))}
    </div>
  )
}

interface FolderItemProps {
  folder: FileInfo
  level: number
  onSelectFolder: (path: string) => void
  currentPath: string
}

function FolderItem({ folder, level, onSelectFolder, currentPath }: FolderItemProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [subfolders, setSubfolders] = useState<FileInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasLoaded, setHasLoaded] = useState(false)

  const electronAPI = getElectronAPI()
  const isElectron = !!electronAPI

  // Check if this folder is in the current path
  const isInCurrentPath = currentPath.startsWith(folder.path)

  // Auto-expand if this folder is in the current path
  useEffect(() => {
    if (isInCurrentPath && !isOpen && !hasLoaded) {
      setIsOpen(true)
    }
  }, [isInCurrentPath, isOpen, hasLoaded])

  // Load subfolders when expanded
  useEffect(() => {
    if (isElectron && isOpen && !hasLoaded) {
      const loadSubfolders = async () => {
        setIsLoading(true)
        try {
          const files = await electronAPI.listDirectory(folder.path)
          // Filter to only include directories
          const dirs = files.filter((file) => file.isDirectory)
          setSubfolders(dirs)
          setHasLoaded(true)
        } catch (error) {
          console.error(`Error loading subfolders for ${folder.path}:`, error)
          setSubfolders([])
        } finally {
          setIsLoading(false)
        }
      }

      loadSubfolders()
    }
  }, [isElectron, isOpen, hasLoaded, folder.path, electronAPI])

  const handleClick = () => {
    if (folder.isDirectory) {
      setIsOpen(!isOpen)
      onSelectFolder(folder.path)
    }
  }

  return (
    <div>
      <button
        className={cn(
          "flex w-full items-center rounded-md px-2 py-1 text-left text-sm",
          currentPath === folder.path ? "bg-primary/10 font-medium" : "hover:bg-muted",
          level === 0 && "font-medium",
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={handleClick}
      >
        <ChevronRight
          className={cn("mr-1 h-4 w-4 shrink-0 text-muted-foreground transition-transform", isOpen && "rotate-90")}
        />
        {isOpen ? (
          <FolderOpen className="mr-2 h-4 w-4 text-orange-400" />
        ) : (
          <Folder className="mr-2 h-4 w-4 text-blue-400" />
        )}
        {folder.name}
      </button>

      {isOpen && (
        <div className="mt-1">
          {isLoading ? (
            <div
              className="flex items-center py-1 px-2 text-sm text-muted-foreground"
              style={{ paddingLeft: `${(level + 1) * 12 + 8}px` }}
            >
              <div className="h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent mr-2"></div>
              Loading...
            </div>
          ) : subfolders.length === 0 ? (
            <div
              className="py-1 px-2 text-sm text-muted-foreground"
              style={{ paddingLeft: `${(level + 1) * 12 + 8}px` }}
            >
              No subfolders
            </div>
          ) : (
            subfolders.map((subfolder) => (
              <FolderItem
                key={subfolder.path}
                folder={subfolder}
                level={level + 1}
                onSelectFolder={onSelectFolder}
                currentPath={currentPath}
              />
            ))
          )}
        </div>
      )}
    </div>
  )
}

