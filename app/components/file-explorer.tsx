"use client"

import React, { useEffect, useState } from "react";
import {
  ChevronRight,
  FileText,
  Folder,
  Image,
  Inbox,
  Laptop,
  LayoutGrid,
  List,
  MessageSquare,
  MoreHorizontal,
  Music,
  Plus,
  Search,
  Settings as LucideSettings,
  Sparkles,
  Star,
  Tag,
  Trash,
  Video,
} from "lucide-react"
import path from "path-browserify"

import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Separator } from "@/components/ui/separator"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { FileItem } from "@/components/file-item"
import { FolderTree } from "@/components/folder-tree"
import { AIAssistant } from "@/components/ai-assistant"
import { getElectronAPI, type FileInfo, type ElectronAPI } from "@/lib/electron-api"
import { formatFileSize } from "@/lib/file-utils"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { toast } from "@/components/ui/use-toast"
import { Settings } from "./settings"; // Import the Settings component

function isRunningInElectron(): boolean {
  return typeof window !== "undefined" && window.navigator.userAgent.toLowerCase().includes("electron");
}

const fileTypeFilters = {
  documents: [".doc", ".docx", ".txt", ".rtf", ".pdf"],
  images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
  videos: [".mp4", ".mov", ".avi", ".mkv", ".webm"],
  audio: [".mp3", ".wav", ".ogg", ".flac", ".aac"],
};

const filterFilesByType = (files: FileInfo[], type: keyof typeof fileTypeFilters) => {
  return files.filter((file) => {
    const extension = path.extname(file.name).toLowerCase();
    return fileTypeFilters[type].includes(extension);
  });
};

export function FileExplorer() {
  const [searchQuery, setSearchQuery] = useState("")
  const [showAIAssistant, setShowAIAssistant] = useState(false)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [currentPath, setCurrentPath] = useState<string>("")
  const [files, setFiles] = useState<FileInfo[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [showNewFolderDialog, setShowNewFolderDialog] = useState(false)
  const [newFolderName, setNewFolderName] = useState("")
  const [selectedFiles, setSelectedFiles] = useState<string[]>([])
  const [rootDirectories, setRootDirectories] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [recycleBinFiles, setRecycleBinFiles] = useState<FileInfo[]>([]);
  const [showSettings, setShowSettings] = useState(false); // Track if settings page is open

  const electronAPI: ElectronAPI | undefined = getElectronAPI()

  useEffect(() => {
    const fetchRootDirectories = async () => {
      try {
        console.log("Fetching root directories... WORK PLEASE");
        const result = await window.electronAPI?.getRootDirectories();
        console.log("Root directories result:", result);

        if (!result) {
          setError("Electron API is not available.");
          return;
        }
        if (result.success) {
          console.log("Root directories fetched successfully:", result.directories);
          setRootDirectories(result.directories || []);
        } else {
          console.error("Error fetching root directories:", result.error);
          setError(result.error || "Unable to load items. Please check your permissions or try again. HI");
        }
      } catch (err) {
        console.error("Unexpected error fetching root directories:", err);
        setError("Unable to load items. Please check your permissions or try again. HEY");
      }
    };

    fetchRootDirectories();
  }, []);

  useEffect(() => {
    const fetchFiles = async () => {
      if (!isRunningInElectron() || !electronAPI) return;

      setIsLoading(true);
      try {
        console.log("Fetching files for path:", currentPath); // Debugging log
        const files = await electronAPI.listDirectory(currentPath);
        console.log("Files fetched:", files); // Debugging log
        setFiles(files);
      } catch (error) {
        console.error("Error fetching files:", error);
        toast({
          title: "Error",
          description: "Unable to load directory contents.",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    fetchFiles();
  }, [currentPath, electronAPI]);

  const fetchRecycleBin = async () => {
    if (!isRunningInElectron() || !electronAPI) return;

    try {
      const result = await electronAPI.getRecycleBin();
      if (result.success) {
        setRecycleBinFiles(result.files || []);
      } else {
        toast({
          title: "Error",
          description: result.error || "Unable to load recycle bin contents.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error("Error fetching recycle bin contents:", error);
      toast({
        title: "Error",
        description: "Unable to load recycle bin contents.",
        variant: "destructive",
      });
    }
  };

  const handleSelectDirectory = async () => {
    try {
      console.log("Opening directory picker...");
      setIsLoading(true);
      const files = await electronAPI.listDirectory("/");
      console.log("Files in selected directory:", files);

      if (!files || files.length === 0) {
        console.warn("No files returned from listDirectory");
        setFiles([]); // Explicitly set empty state
        toast({
          title: "No files found",
          description: "The selected directory is empty or inaccessible.",
          variant: "default",
        });
        return;
      }

      setFiles(files);
      setCurrentPath("/"); // Set a placeholder path
    } catch (error) {
      console.error("Error selecting directory:", error);
      toast({
        title: "Error selecting directory",
        description: error instanceof Error ? error.message : "Could not access the selected directory.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToPath = (newPath: string) => {
    setCurrentPath(newPath)
    setSelectedFiles([])
  }

  const handleFileOpen = (file: FileInfo) => {
    if (file.isDirectory) {
      console.log("Navigating to directory PLEASE NAVIGATE:", file.path); // Debugging log
      setCurrentPath(file.path); // Update the current path
    } else {
      toast({
        title: "File selected",
        description: `${file.name} (${formatFileSize(file.size)})`,
      });
    }
  };

  const handleFileDelete = async (filePath: string) => {
    if (!isRunningInElectron() || !electronAPI) return
    if (!window.confirm(`Are you sure you want to delete ${path.basename(filePath)}?`)) return
    try {
      await electronAPI.deleteFile(filePath)
      // Refresh the current directory
      const fileList = await electronAPI.listDirectory(currentPath)
      setFiles(fileList)
      toast({
        title: "File deleted",
        description: `Successfully deleted ${path.basename(filePath)}`,
      })
    } catch (error) {
      console.error("Error deleting file:", error)
      toast({
        title: "Error deleting file",
        description: "Could not delete the file",
        variant: "destructive",
      })
    }
  }

  const handleCreateFolder = async () => {
    if (!isRunningInElectron() || !electronAPI || !newFolderName.trim()) return

    try {
      const newFolderPath = path.join(currentPath, newFolderName.trim())
      await electronAPI.createDirectory(newFolderPath)

      // Refresh the current directory
      const fileList = await electronAPI.listDirectory(currentPath)
      setFiles(fileList)

      setShowNewFolderDialog(false)
      setNewFolderName("")

      toast({
        title: "Folder created",
        description: `Successfully created ${newFolderName}`,
      })
    } catch (error) {
      console.error("Error creating folder:", error)
      toast({
        title: "Error creating folder",
        description: "Could not create the folder",
        variant: "destructive",
      })
    }
  }

  const handleFileSelection = (filePath: string, isSelected: boolean) => {
    if (isSelected) {
      setSelectedFiles((prev) => [...prev, filePath])
    } else {
      setSelectedFiles((prev) => prev.filter((path) => path !== filePath))
    }
  }

  const getPathParts = () => {
    if (!currentPath) return []

    const parts = currentPath.split(path.sep).filter(Boolean)

    // On Windows, handle drive letter specially
    if (electronAPI?.platform === "win32" && currentPath.includes(":")) {
      const driveLetter = currentPath.split(":")[0] + ":"
      parts[0] = driveLetter
    }

    return parts
  }

  const buildPathFromParts = (parts: string[], index: number) => {
    if (electronAPI?.platform === "win32" && parts[0]?.includes(":")) {
      // Windows path with drive letter
      return parts.slice(0, index + 1).join(path.sep)
    } else {
      // Unix path
      return path.sep + parts.slice(0, index + 1).join(path.sep)
    }
  }

  const renderPathNavigation = () => {
    const parts = getPathParts()

    return (
      <div className="flex items-center border-b px-4 py-2 text-sm overflow-x-auto">
        {electronAPI?.platform === "win32" ? null : (
          <Button variant="ghost" size="sm" className="h-6 px-2" onClick={() => navigateToPath("/")}>
            /
          </Button>
        )}

        {parts.map((part, index) => (
          <div key={index} className="flex items-center">
            {index > 0 && <ChevronRight className="h-4 w-4 text-muted-foreground mx-1" />}
            <Button
              variant="ghost"
              size="sm"
              className="h-6 px-2 font-medium"
              onClick={() => navigateToPath(buildPathFromParts(parts, index))}
            >
              {part}
            </Button>
          </div>
        ))}
      </div>
    )
  }

  if (showSettings) {
    return <Settings onClose={() => setShowSettings(false)} />;
  }

  return (
    <div className="flex h-screen w-full overflow-hidden">
      {/* Sidebar */}
      <div className="hidden w-64 flex-col border-r bg-gray-100 p-2 md:flex">
        <div className="flex items-center justify-between py-2 ml-2 mt-3">
          <h2 className="text-lg font-bold">AI Explorer</h2>
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button variant="ghost" size="icon" onClick={() => setShowAIAssistant(true)}>
                  <Sparkles className="h-5 w-5 text-primary" />
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                <p>AI Assistant</p>
              </TooltipContent>
            </Tooltip>
          </TooltipProvider>
        </div>

        <div className="space-y-1 py-2">
          <Button variant="ghost" className="w-full justify-start" onClick={handleSelectDirectory}>
            <Laptop className="mr-2 h-4 w-4" />
            Browse Folders
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Inbox className="mr-2 h-4 w-4" />
            Recent Files
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Star className="mr-2 h-4 w-4" />
            Favorites
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Tag className="mr-2 h-4 w-4" />
            Tags
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <MessageSquare className="mr-2 h-4 w-4" />
            Smart Suggestions
          </Button>
        </div>

        <Separator className="my-2" />

        <div className="flex-1 overflow-auto">
          <h3 className="mb-2 px-2 text-sm font-medium">Folders</h3>
          {error ? (
            <p className="text-red-500 px-2">{error}</p>
          ) : (
            <ScrollArea className="h-[calc(100vh-280px)]">
              <FolderTree onSelectFolder={navigateToPath} currentPath={currentPath} />
            </ScrollArea>
          )}
        </div>

        <Separator className="my-2" />

        <div className="space-y-1 py-2">
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={fetchRecycleBin} // Fetch recycle bin contents
          >
            <Trash className="mr-2 h-4 w-4" />
            Trash
          </Button>
          <Button
            variant="ghost"
            className="w-full justify-start"
            onClick={() => setShowSettings(true)} // Open settings page
          >
            <LucideSettings className="mr-2 h-4 w-4" />
            Settings
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="flex items-center border-b p-2">
          <div className="relative flex-1 md:max-w-md">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search files or ask AI..."
              className="pl-8 pr-12"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <Button variant="ghost" size="sm" className="absolute right-1 top-1 h-7 px-2 text-xs">
                <Sparkles className="mr-1 h-3.5 w-3.5 text-primary" />
                AI Search
              </Button>
            )}
          </div>

          <div className="ml-2 flex items-center">
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={viewMode === "grid" ? "secondary" : "ghost"}
                    size="icon"
                    onClick={() => setViewMode("grid")}
                  >
                    <LayoutGrid className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>Grid View</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>

            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Button
                    variant={viewMode === "list" ? "secondary" : "ghost"}
                    size="icon"
                    onClick={() => setViewMode("list")}
                  >
                    <List className="h-4 w-4" />
                  </Button>
                </TooltipTrigger>
                <TooltipContent>
                  <p>List View</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>
        </div>

        {/* Path Navigation */}
        {renderPathNavigation()}

        {/* Content Area */}
        <Tabs defaultValue="all" className="flex-1">
          <div className="flex items-center justify-between border-b px-4">
            <TabsList className="h-9">
              <TabsTrigger value="all" className="text-xs">
                All Files
              </TabsTrigger>
              <TabsTrigger value="documents" className="text-xs">
                Documents
              </TabsTrigger>
              <TabsTrigger value="images" className="text-xs">
                Images
              </TabsTrigger>
              <TabsTrigger value="videos" className="text-xs">
                Videos
              </TabsTrigger>
              <TabsTrigger value="audio" className="text-xs">
                Audio
              </TabsTrigger>
            </TabsList>

            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" className="h-7 gap-1 text-xs">
                <Tag className="h-3.5 w-3.5" />
                Smart Tags
              </Button>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="outline" size="sm" className="h-7 gap-1 text-xs">
                    <MoreHorizontal className="h-3.5 w-3.5" />
                    Actions
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={() => setShowNewFolderDialog(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    New Folder
                  </DropdownMenuItem>
                  <DropdownMenuItem>Upload Files</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>Sort By</DropdownMenuItem>
                  <DropdownMenuItem>Group By</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>
                    <Sparkles className="mr-2 h-4 w-4 text-primary" />
                    AI Organization
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>

          <TabsContent value="all" className="flex-1 p-0 data-[state=active]:flex">
            <ScrollArea className="h-[calc(100vh-160px)]">
              {isLoading ? (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="text-center">
                    <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto"></div>
                    <p className="mt-4 text-sm text-muted-foreground">Loading files...</p>
                  </div>
                </div>
              ) : files.length === 0 ? (
                <div className="flex h-full items-center justify-center p-8">
                  <div className="text-center">
                    <Folder className="h-12 w-12 text-muted-foreground mx-auto" />
                    <h3 className="mt-4 text-lg font-medium">No files found</h3>
                    <p className="mt-2 text-sm text-muted-foreground">
                      Select a directory to view its contents.
                    </p>
                    <Button onClick={handleSelectDirectory} className="mt-4">
                      Select Directory
                    </Button>
                  </div>
                </div>
              ) : (
                <div
                  className={
                    viewMode === "grid"
                      ? "grid grid-cols-2 gap-4 p-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6"
                      : "divide-y"
                  }
                >
                  {files.map((file) => (
                    <FileItem
                      key={file.path}
                      file={file}
                      viewMode={viewMode}
                      onOpen={() => handleFileOpen(file)}
                      onDelete={() => handleFileDelete(file.path)}
                      onSelect={(isSelected) => handleFileSelection(file.path, isSelected)}
                      isSelected={selectedFiles.includes(file.path)}
                    />
                  ))}
                </div>
              )}
              {recycleBinFiles.length > 0 && (
                <div className="p-4">
                  <h3 className="text-lg font-medium">Recycle Bin</h3>
                  <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
                    {recycleBinFiles.map((file) => (
                      <FileItem
                        key={file.path}
                        file={file}
                        viewMode="grid"
                        onOpen={() => console.log("Open not supported for recycle bin items")}
                        onDelete={() => console.log("Delete not supported for recycle bin items")}
                        onSelect={() => {}}
                        isSelected={false}
                      />
                    ))}
                  </div>
                </div>
              )}
            </ScrollArea>
          </TabsContent>

          <TabsContent value="documents" className="flex-1 p-0 data-[state=active]:flex">
            <ScrollArea className="h-[calc(100vh-160px)]">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 p-4">
                {filterFilesByType(files, "documents").map((file) => (
                  <FileItem
                    key={file.path}
                    file={file}
                    viewMode={viewMode}
                    onOpen={() => handleFileOpen(file)}
                    onDelete={() => handleFileDelete(file.path)}
                    onSelect={(isSelected) => handleFileSelection(file.path, isSelected)}
                    isSelected={selectedFiles.includes(file.path)}
                  />
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="images" className="flex-1 p-0 data-[state=active]:flex">
            <ScrollArea className="h-[calc(100vh-160px)]">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 p-4">
                {filterFilesByType(files, "images").map((file) => (
                  <FileItem
                    key={file.path}
                    file={file}
                    viewMode={viewMode}
                    onOpen={() => handleFileOpen(file)}
                    onDelete={() => handleFileDelete(file.path)}
                    onSelect={(isSelected) => handleFileSelection(file.path, isSelected)}
                    isSelected={selectedFiles.includes(file.path)}
                  />
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="videos" className="flex-1 p-0 data-[state=active]:flex">
            <ScrollArea className="h-[calc(100vh-160px)]">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 p-4">
                {filterFilesByType(files, "videos").map((file) => (
                  <FileItem
                    key={file.path}
                    file={file}
                    viewMode={viewMode}
                    onOpen={() => handleFileOpen(file)}
                    onDelete={() => handleFileDelete(file.path)}
                    onSelect={(isSelected) => handleFileSelection(file.path, isSelected)}
                    isSelected={selectedFiles.includes(file.path)}
                  />
                ))}
              </div>
            </ScrollArea>
          </TabsContent>

          <TabsContent value="audio" className="flex-1 p-0 data-[state=active]:flex">
            <ScrollArea className="h-[calc(100vh-160px)]">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 p-4">
                {filterFilesByType(files, "audio").map((file) => (
                  <FileItem
                    key={file.path}
                    file={file}
                    viewMode={viewMode}
                    onOpen={() => handleFileOpen(file)}
                    onDelete={() => handleFileDelete(file.path)}
                    onSelect={(isSelected) => handleFileSelection(file.path, isSelected)}
                    isSelected={selectedFiles.includes(file.path)}
                  />
                ))}
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>

      {/* AI Assistant Sidebar */}
      {showAIAssistant && (
        <AIAssistant
          currentPath={currentPath}
          selectedFiles={selectedFiles}
          onClose={() => setShowAIAssistant(false)}
        />
      )}

      {/* New Folder Dialog */}
      <Dialog open={showNewFolderDialog} onOpenChange={setShowNewFolderDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create New Folder</DialogTitle>
            <DialogDescription>Enter a name for the new folder.</DialogDescription>
          </DialogHeader>
          <Input
            placeholder="Folder name"
            value={newFolderName}
            onChange={(e) => setNewFolderName(e.target.value)}
            autoFocus
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowNewFolderDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateFolder}>Create</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}