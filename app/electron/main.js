"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const electron_1 = require("electron");
const path = __importStar(require("path"));
const fs = __importStar(require("fs"));
const os = __importStar(require("os"));
const { execSync } = require("child_process");

// Keep a global reference of the window object to avoid garbage collection
let mainWindow = null;

// Create the browser window
function createWindow() {
    mainWindow = new electron_1.BrowserWindow({
        width: 1200,
        height: 800,
        webPreferences: {
            preload: path.join(__dirname, "preload.js"),
            contextIsolation: true,
            nodeIntegration: false,
        },
        titleBarStyle: "hiddenInset", // For a more native look on macOS
        autoHideMenuBar: true, // Hide menu bar by default (Windows/Linux)
    });
    // In development, load from the local dev server
    // In production, load from the built Next.js app
    const url = process.env.NODE_ENV === "development"
        ? "http://localhost:3000"
        : "http://localhost:3000";
    mainWindow.loadURL(url);
    // Open DevTools in development
    if (process.env.NODE_ENV === "development") {
        mainWindow.webContents.openDevTools();
    }
    mainWindow.on("closed", () => {
        mainWindow = null;
    });
}

// Initialize the app
electron_1.app.whenReady().then(() => {
    createWindow();
    electron_1.app.on("activate", () => {
        // On macOS, re-create the window when dock icon is clicked
        if (mainWindow === null)
            createWindow();
    });
});

// Quit when all windows are closed, except on macOS
electron_1.app.on("window-all-closed", () => {
    if (process.platform !== "darwin")
        electron_1.app.quit();
});

// File system operations
electron_1.ipcMain.handle("list-directory", async (_, dirPath) => {
    try {
        // If no path is provided, use the home directory
        const directory = dirPath || os.homedir();
        const files = await fs.promises.readdir(directory, { withFileTypes: true });
        const fileList = await Promise.all(files.map(async (file) => {
            const filePath = path.join(directory, file.name);
            let stats;
            try {
                stats = await fs.promises.stat(filePath);
            } catch (error) {
                // Skip files we can't access
                return null;
            }
            return {
                name: file.name,
                path: filePath,
                isDirectory: file.isDirectory(),
                size: stats.size,
                modified: stats.mtime.toISOString(),
                created: stats.birthtime.toISOString(),
                type: file.isDirectory() ? "directory" : path.extname(file.name).slice(1) || "file",
            };
        }));
        // Filter out null entries (files we couldn't access)
        return fileList.filter(Boolean);
    } catch (error) {
        console.error("Error listing directory:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("get-file-details", async (_, filePath) => {
    try {
        const stats = await fs.promises.stat(filePath);
        return {
            size: stats.size,
            modified: stats.mtime.toISOString(),
            created: stats.birthtime.toISOString(),
            isDirectory: stats.isDirectory(),
        };
    } catch (error) {
        console.error("Error getting file details:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("move-file", async (_, sourcePath, destinationPath) => {
    try {
        await fs.promises.rename(sourcePath, destinationPath);
        return { success: true };
    } catch (error) {
        console.error("Error moving file:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("copy-file", async (_, sourcePath, destinationPath) => {
    try {
        await fs.promises.copyFile(sourcePath, destinationPath);
        return { success: true };
    } catch (error) {
        console.error("Error copying file:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("delete-file", async (_, filePath) => {
    try {
        const stats = await fs.promises.stat(filePath);
        if (stats.isDirectory()) {
            await fs.promises.rmdir(filePath, { recursive: true });
        } else {
            await fs.promises.unlink(filePath);
        }
        return { success: true };
    } catch (error) {
        console.error("Error deleting file:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("create-directory", async (_, dirPath) => {
    try {
        await fs.promises.mkdir(dirPath, { recursive: true });
        return { success: true };
    } catch (error) {
        console.error("Error creating directory:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("read-file", async (_, filePath) => {
    try {
        const content = await fs.promises.readFile(filePath, "utf8");
        return content;
    } catch (error) {
        console.error("Error reading file:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("write-file", async (_, filePath, content) => {
    try {
        await fs.promises.writeFile(filePath, content, "utf8");
        return { success: true };
    } catch (error) {
        console.error("Error writing file:", error);
        throw error;
    }
});
electron_1.ipcMain.handle("select-directory", async () => {
    if (!mainWindow)
        return null;
    const result = await electron_1.dialog.showOpenDialog(mainWindow, {
        properties: ["openDirectory"],
    });
    if (result.canceled)
        return null;
    return result.filePaths[0];
});
electron_1.ipcMain.handle("select-file", async (_, options = {}) => {
    if (!mainWindow)
        return null;
    const result = await electron_1.dialog.showOpenDialog(mainWindow, {
        properties: ["openFile"],
        ...options,
    });
    if (result.canceled)
        return null;
    return result.filePaths[0];
});
electron_1.ipcMain.handle("save-file-dialog", async (_, options = {}) => {
    if (!mainWindow)
        return null;
    const result = await electron_1.dialog.showSaveDialog(mainWindow, options);
    if (result.canceled)
        return null;
    return result.filePath;
});

const isWSL = () => {
    const release = os.release().toLowerCase();
    console.log("This is the release:", release);
    return release.includes("microsoft") || release.includes("wsl");
};



electron_1.ipcMain.handle("get-root-directories", async () => {
    try {
        let rootDirectories;

        if (process.platform === "win32") {
            if (isWSL()) {
                // WSL: Include /mnt/ directories for Windows drives
                const mntDrives = fs
                    .readdirSync("/mnt")
                    .filter((drive) => /^[a-z]$/i.test(drive)) // Only single-letter drives (e.g., c, d)
                    .map((drive) => `/mnt/${drive}`);
                rootDirectories = ["/", ...mntDrives];
            } else {
                // Native Windows: Dynamically fetch drives using PowerShell
                try {
                    const powershellScript = `Get-WmiObject Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | ForEach-Object {$_.Name}`;
                    const drives = execSync(`powershell -Command "${powershellScript}"`)
                        .toString()
                        .split("\n")
                        .map(drive => drive.trim())
                        .filter(drive => drive !== ""); // Remove empty strings
                    rootDirectories = drives;
                } catch (error) {
                    console.error("Error fetching drives using PowerShell:", error);
                    rootDirectories = ["C:\\"]; // Fallback to C:\\ if PowerShell fails
                }
            }
        } else {
            // macOS/Linux
            rootDirectories = ["/"];
        }

        console.log("Root directories fetched in main process:", rootDirectories);
        return { success: true, directories: rootDirectories };
    } catch (err) {
        console.error("Error fetching root directories in main process:", err);
        return { success: false, error: err.message };
    }
});

electron_1.ipcMain.handle("get-recycle-bin", async () => {
    try {
        console.log("get-recycle-bin handler invoked");
        const trashPath =
            process.platform === "win32"
                ? "C:\\$Recycle.Bin" // Windows Recycle Bin (requires special handling)
                : path.join(os.homedir(), ".Trash"); // macOS/Linux Trash folder

        const files = await fs.promises.readdir(trashPath, { withFileTypes: true });
        const fileList = files.map((file) => ({
            name: file.name,
            path: path.join(trashPath, file.name),
            isDirectory: file.isDirectory(),
        }));

        console.log("Recycle bin contents:", fileList);
        return { success: true, files: fileList };
    } catch (error) {
        console.error("Error fetching recycle bin contents:", error);
        return { success: false, error: error.message };
    }
});
