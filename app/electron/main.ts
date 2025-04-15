import { app, BrowserWindow, ipcMain, dialog } from "electron"
import * as path from "path"
import * as fs from "fs"
import * as os from "os"

// Keep a global reference of the window object to avoid garbage collection
let mainWindow: BrowserWindow | null = null

// Create the browser window
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
    titleBarStyle: "hiddenInset", // For a more native look on macOS
    autoHideMenuBar: true, // Hide menu bar by default (Windows/Linux)
  })

  // In development, load from the local dev server
  // In production, load from the built Next.js app
  const url =
    process.env.NODE_ENV === "development"
      ? "http://localhost:3000"
      : `file://${path.join(__dirname, "../out/index.html")}`

  mainWindow.loadURL(url)

  // Open DevTools in development
  if (process.env.NODE_ENV === "development") {
    mainWindow.webContents.openDevTools()
  }

  mainWindow.on("closed", () => {
    mainWindow = null
  })
}

// Initialize the app
app.whenReady().then(() => {
  createWindow()

  app.on("activate", () => {
    // On macOS, re-create the window when dock icon is clicked
    if (mainWindow === null) createWindow()
  })
})

// Quit when all windows are closed, except on macOS
app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit()
})

// File system operations
ipcMain.handle("list-directory", async (_, dirPath) => {
  try {
    // If no path is provided, use the home directory
    const directory = dirPath || os.homedir()
    const files = await fs.promises.readdir(directory, { withFileTypes: true })

    const fileList = await Promise.all(
      files.map(async (file) => {
        const filePath = path.join(directory, file.name)
        let stats

        try {
          stats = await fs.promises.stat(filePath)
        } catch (error) {
          // Skip files we can't access
          return null
        }

        return {
          name: file.name,
          path: filePath,
          isDirectory: file.isDirectory(),
          size: stats.size,
          modified: stats.mtime.toISOString(),
          created: stats.birthtime.toISOString(),
          type: file.isDirectory() ? "directory" : path.extname(file.name).slice(1) || "file",
        }
      }),
    )

    // Filter out null entries (files we couldn't access)
    return fileList.filter(Boolean)
  } catch (error) {
    console.error("Error listing directory:", error)
    throw error
  }
})

ipcMain.handle("get-file-details", async (_, filePath) => {
  try {
    const stats = await fs.promises.stat(filePath)
    return {
      size: stats.size,
      modified: stats.mtime.toISOString(),
      created: stats.birthtime.toISOString(),
      isDirectory: stats.isDirectory(),
    }
  } catch (error) {
    console.error("Error getting file details:", error)
    throw error
  }
})

ipcMain.handle("move-file", async (_, sourcePath, destinationPath) => {
  try {
    await fs.promises.rename(sourcePath, destinationPath)
    return { success: true }
  } catch (error) {
    console.error("Error moving file:", error)
    throw error
  }
})

ipcMain.handle("copy-file", async (_, sourcePath, destinationPath) => {
  try {
    await fs.promises.copyFile(sourcePath, destinationPath)
    return { success: true }
  } catch (error) {
    console.error("Error copying file:", error)
    throw error
  }
})

ipcMain.handle("delete-file", async (_, filePath) => {
  try {
    const stats = await fs.promises.stat(filePath)

    if (stats.isDirectory()) {
      await fs.promises.rmdir(filePath, { recursive: true })
    } else {
      await fs.promises.unlink(filePath)
    }

    return { success: true }
  } catch (error) {
    console.error("Error deleting file:", error)
    throw error
  }
})

ipcMain.handle("create-directory", async (_, dirPath) => {
  try {
    await fs.promises.mkdir(dirPath, { recursive: true })
    return { success: true }
  } catch (error) {
    console.error("Error creating directory:", error)
    throw error
  }
})

ipcMain.handle("read-file", async (_, filePath) => {
  try {
    const content = await fs.promises.readFile(filePath, "utf8")
    return content
  } catch (error) {
    console.error("Error reading file:", error)
    throw error
  }
})

ipcMain.handle("write-file", async (_, filePath, content) => {
  try {
    await fs.promises.writeFile(filePath, content, "utf8")
    return { success: true }
  } catch (error) {
    console.error("Error writing file:", error)
    throw error
  }
})

ipcMain.handle("select-directory", async () => {
  if (!mainWindow) return null

  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ["openDirectory"],
  })

  if (result.canceled) return null
  return result.filePaths[0]
})

ipcMain.handle("select-file", async (_, options = {}) => {
  if (!mainWindow) return null

  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ["openFile"],
    ...options,
  })

  if (result.canceled) return null
  return result.filePaths[0]
})

ipcMain.handle("save-file-dialog", async (_, options = {}) => {
  if (!mainWindow) return null

  const result = await dialog.showSaveDialog(mainWindow, options)

  if (result.canceled) return null
  return result.filePath
})

