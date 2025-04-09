"use client";

import React, { useState } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

export function Settings({ onClose }: { onClose: () => void }) {
  // State to track the list of excluded directories
  const [excludedDirectories, setExcludedDirectories] = useState<string[]>([]);

  // State to track validation errors for the input
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles adding a new directory to the excluded list.
   * Ensures the directory is not already excluded.
   */
  const handleAddDirectory = (directory: string) => {
    if (excludedDirectories.includes(directory)) {
      setError("Path is already excluded.");
      return;
    }

    // Clear error and add the directory to the list
    setError(null);
    setExcludedDirectories((prev) => [...prev, directory]);
  };

  /**
   * Opens a folder picker and adds the selected folder to the excluded list.
   * Extracts the absolute folder path using `webkitRelativePath`.
   */
  const handleFolderPicker = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files && files.length > 0) {
      // Extract the absolute folder path from the first file's `webkitRelativePath`
      const fullPath = files[0].webkitRelativePath;
      const directoryPath = "/" + fullPath.split("/")[0]; // Ensure the path starts with "/"
      handleAddDirectory(directoryPath);
    }
    event.target.value = ""; // Reset the input value to allow re-selection of the same folder
  };

  return (
    <div className="w-full h-full flex flex-col bg-background">
      <Card className="h-full rounded-none border-0 flex flex-col">
        {/* Header Section */}
        <CardHeader className="flex items-center justify-between px-4 py-3">
          <CardTitle className="text-lg font-bold">Settings</CardTitle>
          {/* Close button to exit the settings page */}
          <Button variant="ghost" size="icon" onClick={onClose}>
            ✕
          </Button>
        </CardHeader>

        {/* Main Content Section */}
        <CardContent className="flex-1 p-4 overflow-hidden">
          <h2 className="text-lg font-bold mb-4 text-center">Excluded Directories</h2>

          {/* Folder Picker Section */}
          <div className="flex justify-center mb-4">
            <label
              htmlFor="folder-picker"
              className="inline-flex items-center justify-center px-6 py-3 bg-primary text-black text-sm font-medium rounded-lg shadow-md cursor-pointer hover:bg-primary-foreground transition duration-200"
            >
              Choose Folder
            </label>
            <input
              id="folder-picker"
              type="file"
              ref={(input) => {
                if (input) {
                  input.webkitdirectory = true;
                }
              }}
              className="hidden"
              onChange={handleFolderPicker}
            />
          </div>

          {/* Display validation error messages */}
          {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}

          {/* List of Excluded Directories */}
          <ul className="divide-y divide-border">
            {excludedDirectories.map((directory, index) => (
              <li
                key={index}
                className="flex items-center justify-between py-2 px-3 bg-muted rounded-md"
              >
                <span className="text-sm text-foreground">{directory}</span>
                {/* Remove button for each directory */}
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() =>
                    setExcludedDirectories((prev) =>
                      prev.filter((dir) => dir !== directory)
                    )
                  }
                >
                  ✕
                </Button>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
}