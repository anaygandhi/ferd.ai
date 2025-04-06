export interface ElectronAPI {
  listDirectory: (dirPath: string) => Promise<FileInfo[]>;
  getFileDetails: (filePath: string) => Promise<FileDetails>;
  createDirectory: (dirPath: string) => Promise<{ success: boolean }>;
  platform: "win32" | "darwin" | "linux" | "browser";
  getDownloadsPath: () => Promise<string>;
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
    const handle = await window.showDirectoryPicker();
    const files: FileInfo[] = [];
    for await (const entry of handle.values()) {
      const isDirectory = entry.kind === "directory";
      const fileInfo: FileInfo = {
        name: entry.name,
        path: `${dirPath}/${entry.name}`,
        isDirectory,
        size: isDirectory ? 0 : (await entry.getFile()).size,
        modified: isDirectory ? "" : (await entry.getFile()).lastModified.toString(),
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
  platform: "browser",
  getDownloadsPath: async () => {
    console.log("Getting Downloads path");
    return "/downloads"; // Use a placeholder path
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

