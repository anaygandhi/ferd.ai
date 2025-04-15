"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
console.log("Preload script loaded. Exposing electronAPI.");
// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
electron_1.contextBridge.exposeInMainWorld("electronAPI", {
    // File system operations
    listDirectory: (dirPath) => electron_1.ipcRenderer.invoke("list-directory", dirPath),
    getFileDetails: (filePath) => electron_1.ipcRenderer.invoke("get-file-details", filePath),
    moveFile: (sourcePath, destinationPath) => electron_1.ipcRenderer.invoke("move-file", sourcePath, destinationPath),
    copyFile: (sourcePath, destinationPath) => electron_1.ipcRenderer.invoke("copy-file", sourcePath, destinationPath),
    deleteFile: (filePath) => electron_1.ipcRenderer.invoke("delete-file", filePath),
    createDirectory: (dirPath) => electron_1.ipcRenderer.invoke("create-directory", dirPath),
    readFile: (filePath) => electron_1.ipcRenderer.invoke("read-file", filePath),
    writeFile: (filePath, content) => electron_1.ipcRenderer.invoke("write-file", filePath, content),
    // Dialog operations
    selectDirectory: () => electron_1.ipcRenderer.invoke("select-directory"),
    selectFile: (options) => electron_1.ipcRenderer.invoke("select-file", options),
    saveFileDialog: (options) => electron_1.ipcRenderer.invoke("save-file-dialog", options),
    // App info
    platform: process.platform,
    getRootDirectories: () => {
        console.log("Invoking get-root-directories from renderer process");
        return electron_1.ipcRenderer.invoke("get-root-directories").then((response) => {
            console.log("Response from get-root-directories:", response);
            return response;
        });
    },
});
