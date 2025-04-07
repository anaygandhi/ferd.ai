import { contextBridge, ipcRenderer } from "electron"
import { ElectronAPI } from "../lib/electron-api"; // Adjust the path if necessary
import os from "os";

declare global {
  interface Window {
    electronAPI?: ElectronAPI;
  }
}

console.log("Preload script loaded. Exposing electronAPI.");

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld("electronAPI", {
  // File system operations
  listDirectory: (dirPath: string) => ipcRenderer.invoke("list-directory", dirPath),
  getFileDetails: (filePath: string) => ipcRenderer.invoke("get-file-details", filePath),
  moveFile: (sourcePath: string, destinationPath: string) =>
    ipcRenderer.invoke("move-file", sourcePath, destinationPath),
  copyFile: (sourcePath: string, destinationPath: string) =>
    ipcRenderer.invoke("copy-file", sourcePath, destinationPath),
  deleteFile: (filePath: string) => ipcRenderer.invoke("delete-file", filePath),
  createDirectory: (dirPath: string) => ipcRenderer.invoke("create-directory", dirPath),
  readFile: (filePath: string) => ipcRenderer.invoke("read-file", filePath),
  writeFile: (filePath: string, content: string) => ipcRenderer.invoke("write-file", filePath, content),
  getRecycleBin: () => ipcRenderer.invoke("get-recycle-bin"),

  // Dialog operations
  selectDirectory: () => ipcRenderer.invoke("select-directory"),
  selectFile: (options?: any) => ipcRenderer.invoke("select-file", options),
  saveFileDialog: (options?: any) => ipcRenderer.invoke("save-file-dialog", options),

  // App info
  platform: process.platform,
  isWSL: () => {
    const release = os.release().toLowerCase();
    return release.includes("microsoft") || release.includes("wsl");
  },
  getRootDirectories: () => {
    console.log("Invoking get-root-directories from renderer process");
    return ipcRenderer.invoke("get-root-directories").then((response) => {
      console.log("Response from get-root-directories:", response);
      return response;
    });
  },
});

