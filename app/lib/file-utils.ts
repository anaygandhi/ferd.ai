import {
    FileArchive,
    FileAudio,
    FileCode,
    FileImage,
    FileSpreadsheet,
    FileText,
    FileType,
    FileVideo,
    File,
  } from "lucide-react"
  import path from "path-browserify"
  
  export function formatFileSize(bytes: number): string {
    if (bytes === 0) return "0 Bytes"
  
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB", "TB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
  
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }
  
  export function getFileTypeIcon(filename: string) {
    const extension = path.extname(filename).toLowerCase()
  
    // Document types
    if ([".doc", ".docx", ".txt", ".rtf"].includes(extension)) {
      return FileText
    }
    // Spreadsheet types
    if ([".xls", ".xlsx", ".csv"].includes(extension)) {
      return FileSpreadsheet
    }
    // Presentation types
    if ([".ppt", ".pptx"].includes(extension)) {
      return FileType
    }
    // PDF
    if (extension === ".pdf") {
      return FileText
    }
    // Image types
    if ([".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"].includes(extension)) {
      return FileImage
    }
    // Video types
    if ([".mp4", ".mov", ".avi", ".mkv", ".webm"].includes(extension)) {
      return FileVideo
    }
    // Audio types
    if ([".mp3", ".wav", ".ogg", ".flac", ".aac"].includes(extension)) {
      return FileAudio
    }
    // Archive types
    if ([".zip", ".rar", ".7z", ".tar", ".gz"].includes(extension)) {
      return FileArchive
    }
    // Code types
    if ([".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".py", ".java", ".c", ".cpp"].includes(extension)) {
      return FileCode
    }
  
    // Default file icon
    return File
  }
  
  