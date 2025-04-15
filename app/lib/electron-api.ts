export interface ElectronAPI {
  listDirectory: (dirPath: string) => Promise<FileInfo[]>;
  getFileDetails: (filePath: string) => Promise<FileDetails>;
  createDirectory: (dirPath: string) => Promise<{ success: boolean }>;
  deleteFile: (filePath: string) => Promise<void>;
  platform: "win32" | "darwin" | "linux" | "browser";
  getDownloadsPath: () => Promise<string>;
  getRootDirectories: () => Promise<{ success: boolean; directories?: string[]; error?: string }>;
  getRecycleBin: () => Promise<{ success: boolean; files?: FileInfo[]; error?: string }>;
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
    showDirectoryPicker?: () => Promise<FileSystemDirectoryHandle>;
  }
}

// Extend the FileSystemDirectoryHandle interface for keys, values, and entries methods
interface FileSystemDirectoryHandle {
  [Symbol.asyncIterator](): AsyncIterableIterator<[string, FileSystemHandle]>;
  entries(): AsyncIterableIterator<[string, FileSystemHandle]>;
  keys(): AsyncIterableIterator<string>;
  values(): AsyncIterableIterator<FileSystemHandle>;
}

export interface FileInfo {
  name: string;
  path: string;
  isDirectory: boolean;
  size: number;
  modified: string;
  created: string;
  type: string;
}

export interface FileDetails {
  size: number;
  modified: string;
  created: string;
  isDirectory: boolean;
}

const browserElectronAPI: ElectronAPI = {
  listDirectory: async (dirPath: string) => {
    console.log(`Listing directory: ${dirPath}`);
    if (!window.showDirectoryPicker) {
      throw new Error("showDirectoryPicker is not supported in this environment.");
    }
    const handle = await window.showDirectoryPicker();
    const files: FileInfo[] = [];
    for await (const [name, entry] of handle.entries()) {
      const isDirectory = entry.kind === "directory";
      const fileInfo: FileInfo = {
        name,
        path: `${dirPath}/${name}`,
        isDirectory,
        size: isDirectory ? 0 : entry.kind === "file" ? (await (entry as FileSystemFileHandle).getFile()).size : 0,
        modified: isDirectory ? "" : new Date((await (entry as FileSystemFileHandle).getFile()).lastModified).toISOString(),
        created: "",
        type: isDirectory ? "directory" : "file",
      };
      files.push(fileInfo);
    }
    return files;
  },
  getFileDetails: async (filePath: string) => {
    console.log(`Getting file details for: ${filePath}`);
    return { size: 0, modified: "", created: "", isDirectory: false };
  },
  createDirectory: async (dirPath: string) => {
    console.log(`Creating directory: ${dirPath}`);
    return { success: false };
  },
  deleteFile: async (filePath: string) => {
    console.log(`Deleting file: ${filePath}`);
    return Promise.resolve();
  },
  platform: "browser",
  getDownloadsPath: async () => {
    console.log("Getting Downloads path");
    return "/downloads";
  },
  getRootDirectories: async () => {
    console.log("Getting root directories (browser environment)");
    return {
      success: true,
      directories: ["/Downloads"], // Simulated Downloads directory
    };
  },
  getRecycleBin: async () => {
    console.log("Getting recycle bin (browser environment)");
    return {
      success: true,
      files: [],
    };
  },
};

export function getElectronAPI(): ElectronAPI {
  if (typeof window !== "undefined" && window.electronAPI) {
    console.log("Running in Electron environment. Using Electron API.");
    return window.electronAPI as ElectronAPI;
  }

  console.warn("Running in browser environment. Using browser-compatible Electron API.");
  return browserElectronAPI;
}

