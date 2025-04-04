// Type definitions for the Electron API exposed by the preload script
export interface ElectronAPI {
    listDirectory: (dirPath: string) => Promise<FileInfo[]>
    getFileDetails: (filePath: string) => Promise<FileDetails>
    moveFile: (sourcePath: string, destinationPath: string) => Promise<{ success: boolean }>
    copyFile: (sourcePath: string, destinationPath: string) => Promise<{ success: boolean }>
    deleteFile: (filePath: string) => Promise<{ success: boolean }>
    createDirectory: (dirPath: string) => Promise<{ success: boolean }>
    readFile: (filePath: string) => Promise<string>
    writeFile: (filePath: string, content: string) => Promise<{ success: boolean }>
    selectDirectory: () => Promise<string | null>
    selectFile: (options?: { filters?: { name: string; extensions: string[] }[]; title?: string; defaultPath?: string }) => Promise<string | null>
    saveFileDialog: (options?: { title?: string; defaultPath?: string; filters?: { name: string; extensions: string[] }[] }) => Promise<string | null>
    platform: "win32" | "darwin" | "linux"
  }
  
  export interface FileInfo {
    name: string
    path: string
    isDirectory: boolean
    size: number
    modified: string
    created: string
    type: string
  }
  
  export interface FileDetails {
    size: number
    modified: string
    created: string
    isDirectory: boolean
  }
  
  // Helper to safely access the Electron API
  export function getElectronAPI(): ElectronAPI | undefined {
    // Check if we're in an Electron environment
    if (typeof window !== "undefined" && window.electronAPI) {
      return window.electronAPI as ElectronAPI
    }
    return undefined
  }
  
  // Declare global window interface
  declare global {
    interface Window {
      electronAPI?: ElectronAPI
    }
  }
  
  