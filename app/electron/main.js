const { app, BrowserWindow, ipcMain } = require("electron");
const path = require("path");
const fs = require("fs");

console.log("Working directory:", __dirname); // Debugging log
console.log("Main.js path:", path.join(__dirname, "main.js")); // Debugging log

let mainWindow;

app.on("ready", () => {
  console.log("Electron app is starting..."); // Debugging log

  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"), // Ensure this path is correct
      contextIsolation: true,
      enableRemoteModule: false,
    },
  });

  // Load the Next.js app
  const startURL = process.env.NODE_ENV === "development"
    ? "http://localhost:3000" // Development server
    : `file://${path.join(__dirname, "out", "index.html")}`; // Production build

  console.log("Loading URL:", startURL); // Debugging log
  mainWindow.loadURL(startURL);

  mainWindow.on("closed", () => {
    console.log("Electron window closed."); // Debugging log
    mainWindow = null;
  });

  mainWindow.webContents.on("did-finish-load", () => {
    console.log("Electron window finished loading."); // Debugging log
  });
});

ipcMain.handle("get-downloads-path", () => {
  console.log("get-downloads-path IPC handler called."); // Debugging log
  return app.getPath("downloads"); // Returns the Downloads directory path
});

ipcMain.handle("delete-file", async (event, filePath) => {
  try {
    fs.unlinkSync(filePath);
    console.log(`File deleted: ${filePath}`);
    return { success: true };
  } catch (err) {
    console.error(`Error deleting file ${filePath}:`, err);
    return { success: false, error: err.message };
  }
});

ipcMain.handle("create-directory", async (event, dirPath) => {
  try {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`Directory created: ${dirPath}`);
    return { success: true };
  } catch (err) {
    console.error(`Error creating directory ${dirPath}:`, err);
    return { success: false, error: err.message };
  }
});

app.on("window-all-closed", () => {
  console.log("All windows closed."); // Debugging log
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  console.log("App activated."); // Debugging log
  if (mainWindow === null) {
    app.emit("ready");
  }
});
