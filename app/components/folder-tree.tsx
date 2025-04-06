<<<<<<< HEAD
"use client"

import { useState, useEffect } from "react"
import { ChevronRight, FileText, Folder, FolderOpen } from "lucide-react"
import path from "path-browserify"
import { cn } from "@/lib/utils"
import { getElectronAPI, type FileInfo } from "@/lib/electron-api"
import { toast } from "@/components/ui/use-toast"

interface FolderTreeProps {
  onSelectFolder: (path: string) => void
  currentPath: string
}

export function FolderTree({ onSelectFolder, currentPath }: FolderTreeProps) {
  const [rootItems, setRootItems] = useState<FileInfo[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const electronAPI = getElectronAPI()

  useEffect(() => {
    console.log("FolderTree useEffect triggered. Running in browser environment.");
    const loadRootItems = async () => {
      try {
        console.log("Opening directory picker...");
        const files = await electronAPI.listDirectory("/");
        console.log("Files in selected directory:", files);

        if (!files || files.length === 0) {
          console.warn("No files returned from listDirectory");
          setRootItems([]); // Explicitly set empty state
          return;
        }

        setRootItems(files); // Include both directories and files
      } catch (error) {
        console.error("Error loading root items:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadRootItems();
  }, [electronAPI]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (rootItems.length === 0) {
    return (
      <div className="flex items-center justify-center p-4 text-sm text-muted-foreground">
        Unable to load items. Please check your permissions or try again.
      </div>
    )
  }

  return (
    <div className="space-y-1 px-2">
      {rootItems.map((item) => (
        <FolderItem
          key={item.path}
          item={item}
          level={0}
          onSelectFolder={onSelectFolder}
          currentPath={currentPath}
        />
      ))}
    </div>
  )
}

interface FolderItemProps {
  item: FileInfo
  level: number
  onSelectFolder: (path: string) => void
  currentPath: string
}

function FolderItem({ item, level, onSelectFolder, currentPath }: FolderItemProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [subItems, setSubItems] = useState<FileInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [hasLoaded, setHasLoaded] = useState(false)

  const electronAPI = getElectronAPI()

  // Check if this folder is in the current path
  const isInCurrentPath = currentPath.startsWith(item.path)

  // Auto-expand if this folder is in the current path
  useEffect(() => {
    if (isInCurrentPath && !isOpen && !hasLoaded) {
      setIsOpen(true)
    }
  }, [isInCurrentPath, isOpen, hasLoaded])

  // Load sub-items (directories and files) when expanded
  useEffect(() => {
    if (item.isDirectory && isOpen && !hasLoaded) {
      const loadSubItems = async () => {
        setIsLoading(true)
        try {
          const files = await electronAPI.listDirectory(item.path)
          console.log(`Loaded sub-items for ${item.path}:`, files) // Debugging log
          setSubItems(files) // Include both directories and files
          setHasLoaded(true)
        } catch (error) {
          console.error(`Error loading sub-items for ${item.path}:`, error)
          toast({
            title: "Error loading folder",
            description: "Unable to access this folder. It may be restricted or protected.",
            variant: "destructive",
          })
        } finally {
          setIsLoading(false)
        }
      }

      loadSubItems()
    }
  }, [isOpen, hasLoaded, item.path, electronAPI])

  const handleClick = () => {
    if (item.isDirectory) {
      setIsOpen(!isOpen)
      onSelectFolder(item.path)
    }
  }

  return (
    <div>
      <button
        className={cn(
          "flex w-full items-center rounded-md px-2 py-1 text-left text-sm",
          currentPath === item.path ? "bg-primary/10 font-medium" : "hover:bg-muted",
          level === 0 && "font-medium",
        )}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={handleClick}
      >
        {item.isDirectory ? (
          <>
            <ChevronRight
              className={cn("mr-1 h-4 w-4 shrink-0 text-muted-foreground transition-transform", isOpen && "rotate-90")}
            />
            {isOpen ? (
              <FolderOpen className="mr-2 h-4 w-4 text-orange-400" />
            ) : (
              <Folder className="mr-2 h-4 w-4 text-blue-400" />
            )}
          </>
        ) : (
          <FileText className="mr-2 h-4 w-4 text-muted-foreground" />
        )}
        {item.name}
      </button>

      {isOpen && item.isDirectory && (
        <div className="mt-1">
          {isLoading ? (
            <div
              className="flex items-center py-1 px-2 text-sm text-muted-foreground"
              style={{ paddingLeft: `${(level + 1) * 12 + 8}px` }}
            >
              <div className="h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent mr-2"></div>
              Loading...
            </div>
          ) : subItems.length === 0 ? (
            <div
              className="py-1 px-2 text-sm text-muted-foreground"
              style={{ paddingLeft: `${(level + 1) * 12 + 8}px` }}
            >
              No items
            </div>
          ) : (
            subItems.map((subItem) => (
              <FolderItem
                key={subItem.path}
                item={subItem}
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

=======
"use client"

import { useState, useEffect } from "react"
import { ChevronRight, Folder, FolderOpen } from "lucide-react"
import { getElectronAPI, type FileInfo } from "@/lib/electron-api"
import { toast } from "@/components/ui/use-toast"

interface FolderTreeProps {
  onSelectFolder: (path: string) => void
  currentPath: string
}

export function FolderTree({ onSelectFolder, currentPath }: FolderTreeProps) {
  const [rootItems, setRootItems] = useState<FileInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const electronAPI = getElectronAPI();

  useEffect(() => {
    const loadRootItems = async () => {
      try {
        const result = await electronAPI.getRootDirectories();
        if (!result || !result.success) {
          console.warn("Failed to fetch root directories:", result?.error);
          setRootItems([]);
          return;
        }

        const rootDirectories = (result.directories || []).map((dir) => ({
          name: dir,
          path: dir,
          isDirectory: true,
          size: 0,
          modified: "",
          created: "",
          type: "directory",
        }));

        setRootItems(rootDirectories);
      } catch (error) {
        console.error("Error fetching root directories:", error);
      } finally {
        setIsLoading(false);
      }
    };

    loadRootItems();
  }, [electronAPI]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent"></div>
      </div>
    );
  }

  if (rootItems.length === 0) {
    return (
      <div className="flex items-center justify-center p-4 text-sm text-muted-foreground">
        Unable to load items. Please check your permissions or try again.
      </div>
    );
  }

  return (
    <div className="space-y-1 px-2">
      {rootItems.map((item) => (
        <FolderItem
          key={item.path}
          item={item}
          level={0}
          onSelectFolder={onSelectFolder}
          currentPath={currentPath}
        />
      ))}
    </div>
  );
}

interface FolderItemProps {
  item: FileInfo
  level: number
  onSelectFolder: (path: string) => void
  currentPath: string
}

function FolderItem({ item, level, onSelectFolder, currentPath }: FolderItemProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [subItems, setSubItems] = useState<FileInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasLoaded, setHasLoaded] = useState(false);

  const electronAPI = getElectronAPI();

  useEffect(() => {
    if (item.isDirectory && isOpen && !hasLoaded) {
      const loadSubItems = async () => {
        setIsLoading(true);
        try {
          const files = await electronAPI.listDirectory(item.path);
          const directories = files.filter((file) => file.isDirectory); // Only include directories
          setSubItems(directories);
          setHasLoaded(true);
        } catch (error) {
          console.error(`Error loading sub-items for ${item.path}:`, error);
          toast({
            title: "Error loading folder",
            description: "Unable to access this folder. It may be restricted or protected.",
            variant: "destructive",
          });
        } finally {
          setIsLoading(false);
        }
      };

      loadSubItems();
    }
  }, [isOpen, hasLoaded, item.path, electronAPI]);

  const handleClick = () => {
    if (item.isDirectory) {
      setIsOpen(!isOpen);
      onSelectFolder(item.path); // Update the current path
    }
  };

  return (
    <div>
      <button
        className={`flex w-full items-center rounded-md px-2 py-1 text-left text-sm ${
          currentPath === item.path ? "bg-primary/10 font-medium" : "hover:bg-muted"
        }`}
        style={{ paddingLeft: `${level * 12 + 8}px` }}
        onClick={handleClick}
      >
        {item.isDirectory ? (
          <>
            <ChevronRight
              className={`mr-1 h-4 w-4 shrink-0 text-muted-foreground transition-transform ${
                isOpen ? "rotate-90" : ""
              }`}
            />
            {isOpen ? (
              <FolderOpen className="mr-2 h-4 w-4 text-orange-400" />
            ) : (
              <Folder className="mr-2 h-4 w-4 text-blue-400" />
            )}
          </>
        ) : null}
        {item.name}
      </button>

      {isOpen && item.isDirectory && (
        <div className="mt-1">
          {isLoading ? (
            <div
              className="flex items-center py-1 px-2 text-sm text-muted-foreground"
              style={{ paddingLeft: `${(level + 1) * 12 + 8}px` }}
            >
              <div className="h-3 w-3 animate-spin rounded-full border-2 border-primary border-t-transparent mr-2"></div>
              Loading...
            </div>
          ) : subItems.length === 0 ? (
            <div
              className="py-1 px-2 text-sm text-muted-foreground"
              style={{ paddingLeft: `${(level + 1) * 12 + 8}px` }}
            >
              No items
            </div>
          ) : (
            subItems.map((subItem) => (
              <FolderItem
                key={subItem.path}
                item={subItem}
                level={level + 1}
                onSelectFolder={onSelectFolder}
                currentPath={currentPath}
              />
            ))
          )}
        </div>
      )}
    </div>
  );
}

>>>>>>> 3c70f7a4850487db4692c20f46c896efc384d853
