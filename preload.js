const { contextBridge, ipcRenderer } = require("electron");
const fs = require("fs");
const path = require("path");

console.log("Preload script loaded."); // Debugging log

contextBridge.exposeInMainWorld("electronAPI", {
  listDirectory: (dirPath) => {
    console.log(`Listing directory: ${dirPath}`);
    return new Promise((resolve, reject) => {
      fs.readdir(dirPath, { withFileTypes: true }, (err, entries) => {
        if (err) {
          console.error(`Error reading directory ${dirPath}:`, err);
          reject(`Unable to access directory: ${err.message}`);
          return;
        }

        const files = entries.map((entry) => ({
          name: entry.name,
          path: path.join(dirPath, entry.name),
          isDirectory: entry.isDirectory(),
          size: entry.isDirectory() ? 0 : fs.statSync(path.join(dirPath, entry.name)).size,
          modified: fs.statSync(path.join(dirPath, entry.name)).mtime.toISOString(),
          created: fs.statSync(path.join(dirPath, entry.name)).birthtime.toISOString(),
          type: entry.isDirectory() ? "directory" : "file",
        }));

        resolve(files);
      });
    });
  },
  deleteFile: (filePath) => ipcRenderer.invoke("delete-file", filePath),
  createDirectory: (dirPath) => ipcRenderer.invoke("create-directory", dirPath),
  getDownloadsPath: () => ipcRenderer.invoke("get-downloads-path"),
});
