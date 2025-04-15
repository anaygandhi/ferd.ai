"use client"

import { useState } from "react"
import {
  Calendar,
  Copy,
  File,
  FileArchive,
  FileAudio,
  FileCode,
  FileImage,
  FileSpreadsheet,
  FileText,
  FileType,
  FileVideo,
  MoreHorizontal,
  Pencil,
  Tag,
  Trash,
  Folder,
  Download,
  Share,
} from "lucide-react"
import path from "path-browserify"
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuSeparator,
  ContextMenuSub,
  ContextMenuSubContent,
  ContextMenuSubTrigger,
  ContextMenuTrigger,
} from "@/components/ui/context-menu"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import type { FileInfo } from "@/lib/electron-api"
import { formatFileSize } from "@/lib/file-utils"

interface FileItemProps {
  file: FileInfo
  viewMode: "grid" | "list"
  onOpen: () => void
  onDelete: () => void
  onSelect: (isSelected: boolean) => void
  isSelected: boolean
}

export function FileItem({ file, viewMode, onOpen, onDelete, onSelect, isSelected }: FileItemProps) {
  const [isHovered, setIsHovered] = useState(false);

  const handleFileClick = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering parent events
    onOpen(); // Trigger the onOpen handler
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.stopPropagation(); // Prevent triggering parent events
    onSelect(e.target.checked); // Trigger the onSelect handler
  };

  const getFileIcon = () => {
    if (file.isDirectory) {
      return <Folder className="h-6 w-6 text-blue-400" />
    }

    const extension = path.extname(file.name).toLowerCase()

    // Document types
    if ([".doc", ".docx", ".txt", ".rtf"].includes(extension)) {
      return <FileText className="h-6 w-6 text-blue-500" />
    }
    // Spreadsheet types
    if ([".xls", ".xlsx", ".csv"].includes(extension)) {
      return <FileSpreadsheet className="h-6 w-6 text-green-500" />
    }
    // Presentation types
    if ([".ppt", ".pptx"].includes(extension)) {
      return <FileType className="h-6 w-6 text-orange-500" />
    }
    // PDF
    if (extension === ".pdf") {
      return <FileText className="h-6 w-6 text-red-500" />
    }
    // Image types
    if ([".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"].includes(extension)) {
      return <FileImage className="h-6 w-6 text-purple-500" />
    }
    // Video types
    if ([".mp4", ".mov", ".avi", ".mkv", ".webm"].includes(extension)) {
      return <FileVideo className="h-6 w-6 text-pink-500" />
    }
    // Audio types
    if ([".mp3", ".wav", ".ogg", ".flac", ".aac"].includes(extension)) {
      return <FileAudio className="h-6 w-6 text-yellow-500" />
    }
    // Archive types
    if ([".zip", ".rar", ".7z", ".tar", ".gz"].includes(extension)) {
      return <FileArchive className="h-6 w-6 text-gray-500" />
    }
    // Code types
    if ([".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".py", ".java", ".c", ".cpp"].includes(extension)) {
      return <FileCode className="h-6 w-6 text-cyan-500" />
    }

    // Default file icon
    return <File className="h-6 w-6 text-gray-500" />
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()

    // Today
    if (date.toDateString() === now.toDateString()) {
      return `Today, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    }

    // Yesterday
    const yesterday = new Date(now)
    yesterday.setDate(now.getDate() - 1)
    if (date.toDateString() === yesterday.toDateString()) {
      return `Yesterday, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    }

    // Within the last week
    const oneWeekAgo = new Date(now)
    oneWeekAgo.setDate(now.getDate() - 7)
    if (date > oneWeekAgo) {
      return date.toLocaleDateString([], { weekday: "long" })
    }

    // Older
    return date.toLocaleDateString([], { year: "numeric", month: "short", day: "numeric" })
  }

  const renderGridItem = () => (
    <ContextMenu>
      <ContextMenuTrigger>
        <div
          className={`group flex cursor-pointer flex-col items-center rounded-lg p-2 transition-colors ${
            isSelected ? "bg-primary/10" : "hover:bg-muted"
          }`}
          onClick={handleFileClick} // Trigger onOpen on click
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div className="relative mb-2 flex h-24 w-24 items-center justify-center rounded-md border bg-background p-2">
            {getFileIcon()}
            {(isSelected || isHovered) && (
                <div className="absolute top-1 left-1">
                <Checkbox
                  checked={isSelected}
                  onChange={(e) => handleCheckboxChange(e as React.ChangeEvent<HTMLInputElement>)} // Trigger onSelect on checkbox change
                  onClick={(e: React.MouseEvent<HTMLButtonElement>) => e.stopPropagation()} // Prevent checkbox click from triggering onOpen
                />
                </div>
            )}
          </div>
          <div className="w-full text-center">
            <p className="truncate text-sm font-medium">{file.name}</p>
            <p className="text-xs text-muted-foreground">{file.isDirectory ? "--" : formatFileSize(file.size)}</p>
          </div>
        </div>
      </ContextMenuTrigger>
      <FileContextMenu file={file} onOpen={onOpen} onDelete={onDelete} />
    </ContextMenu>
  );

  const renderListItem = () => (
    <ContextMenu>
      <ContextMenuTrigger>
        <div
          className={`group flex cursor-pointer items-center justify-between px-4 py-2 transition-colors ${
            isSelected ? "bg-primary/10" : "hover:bg-muted"
          }`}
          onClick={handleFileClick} // Trigger onOpen on click
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          <div className="flex items-center gap-3">
            <Checkbox
              checked={isSelected}
              onChange={(e) => handleCheckboxChange(e as React.ChangeEvent<HTMLInputElement>)} // Trigger onSelect on checkbox change
              onClick={(e: React.MouseEvent<HTMLButtonElement>) => e.stopPropagation()} // Prevent checkbox click from triggering onOpen
            />
            {getFileIcon()}
            <div>
              <p className="font-medium">{file.name}</p>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{file.isDirectory ? "Folder" : path.extname(file.name).slice(1).toUpperCase() || "File"}</span>
                {!file.isDirectory && (
                  <>
                    <span>•</span>
                    <span>{formatFileSize(file.size)}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Calendar className="h-3.5 w-3.5" />
              {formatDate(file.modified)}
            </div>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-8 w-8">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={onOpen}>Open</DropdownMenuItem>
                <DropdownMenuItem>Download</DropdownMenuItem>
                <DropdownMenuItem>Share</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem>Rename</DropdownMenuItem>
                <DropdownMenuItem>Move</DropdownMenuItem>
                <DropdownMenuItem>Copy</DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  className="text-destructive"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete();
                  }}
                >
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </ContextMenuTrigger>
      <FileContextMenu file={file} onOpen={onOpen} onDelete={onDelete} />
    </ContextMenu>
  );

  return viewMode === "grid" ? renderGridItem() : renderListItem();
}

interface FileContextMenuProps {
  file: FileInfo
  onOpen: () => void
  onDelete: () => void
}

function FileContextMenu({ file, onOpen, onDelete }: FileContextMenuProps) {
  return (
    <ContextMenuContent className="w-48 bg-white shadow-lg rounded-md">
      <ContextMenuItem onClick={onOpen}>
        <File className="mr-2 h-4 w-4 text-muted-foreground" />
        Open
      </ContextMenuItem>
      {!file.isDirectory && (
        <ContextMenuItem>
          <Download className="mr-2 h-4 w-4 text-muted-foreground" />
          Download
        </ContextMenuItem>
      )}
      <ContextMenuItem>
        <Share className="mr-2 h-4 w-4 text-muted-foreground" />
        Share
      </ContextMenuItem>
      <ContextMenuSeparator />
      <ContextMenuItem>
        <Pencil className="mr-2 h-4 w-4 text-muted-foreground" />
        Rename
      </ContextMenuItem>
      <ContextMenuSub>
        <ContextMenuSubTrigger>
          <Folder className="mr-2 h-4 w-4 text-muted-foreground" />
          Move To
        </ContextMenuSubTrigger>
        <ContextMenuSubContent className="w-48 bg-white shadow-lg rounded-md">
          <ContextMenuItem>Documents</ContextMenuItem>
          <ContextMenuItem>Pictures</ContextMenuItem>
          <ContextMenuItem>Downloads</ContextMenuItem>
          <ContextMenuSeparator />
          <ContextMenuItem>Choose Location...</ContextMenuItem>
        </ContextMenuSubContent>
      </ContextMenuSub>
      <ContextMenuSeparator />
      <ContextMenuItem
        className="text-destructive"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
      >
        <Trash className="mr-2 h-4 w-4 text-destructive" />
        Delete
      </ContextMenuItem>
    </ContextMenuContent>
  );
}

