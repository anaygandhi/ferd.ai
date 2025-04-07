"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getElectronAPI = getElectronAPI;
const browserElectronAPI = {
    listDirectory: async (dirPath) => {
        console.log(`Listing directory: ${dirPath}`);
        if (!window.showDirectoryPicker) {
            throw new Error("showDirectoryPicker is not supported in this environment.");
        }
        const handle = await window.showDirectoryPicker();
        const files = [];
        for await (const [name, entry] of handle.entries()) {
            const isDirectory = entry.kind === "directory";
            const fileInfo = {
                name,
                path: `${dirPath}/${name}`,
                isDirectory,
                size: isDirectory ? 0 : entry.kind === "file" ? (await entry.getFile()).size : 0,
                modified: isDirectory ? "" : new Date((await entry.getFile()).lastModified).toISOString(),
                created: "",
                type: isDirectory ? "directory" : "file",
            };
            files.push(fileInfo);
        }
        return files;
    },
    getFileDetails: async (filePath) => {
        console.log(`Getting file details for: ${filePath}`);
        return { size: 0, modified: "", created: "", isDirectory: false };
    },
    createDirectory: async (dirPath) => {
        console.log(`Creating directory: ${dirPath}`);
        return { success: false };
    },
    deleteFile: async (filePath) => {
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
};
function getElectronAPI() {
    if (typeof window !== "undefined" && window.electronAPI) {
        console.log("Running in Electron environment. Using Electron API.");
        return window.electronAPI;
    }
    console.warn("Running in browser environment. Using browser-compatible Electron API.");
    return browserElectronAPI;
}
