import type { ProjectFolder } from "./models/ProjectFolder";

interface DirectoryHandle {
  name: string;
  values(): AsyncIterable<{ kind: "directory" | "file"; name: string }>;
}

interface SketchUpFolderResult {
  folder?: ProjectFolder;
  error?: boolean;
}

const host = window as Window & {
  showDirectoryPicker?: (options: { mode: "read" }) => Promise<DirectoryHandle>;
  sketchup?: { selectProjectFolder?: () => void };
};

export function canSelectProjectFolder(): boolean {
  return Boolean(
    host.sketchup?.selectProjectFolder || host.showDirectoryPicker,
  );
}

export async function selectProjectFolder(): Promise<
  ProjectFolder | undefined
> {
  const folder = host.sketchup?.selectProjectFolder
    ? await selectSketchUpFolder()
    : await selectBrowserFolder();

  if (folder) {
    folder.subfolders.sort((first, second) =>
      first.localeCompare(second, undefined, { numeric: true }),
    );
  }
  return folder;
}

async function selectBrowserFolder(): Promise<ProjectFolder | undefined> {
  let directory: DirectoryHandle;
  try {
    if (!host.showDirectoryPicker)
      throw new Error("Folder picker unavailable.");
    directory = await host.showDirectoryPicker({ mode: "read" });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") return;
    throw error;
  }

  const subfolders: string[] = [];
  for await (const entry of directory.values()) {
    if (entry.kind === "directory") subfolders.push(entry.name);
  }
  return { name: directory.name, subfolders };
}

function selectSketchUpFolder(): Promise<ProjectFolder | undefined> {
  const eventName = "aiq-project-folder-selected";
  return new Promise((resolve, reject) => {
    function cleanup() {
      host.removeEventListener(eventName, receive);
      host.clearTimeout(timeout);
    }
    function receive(event: Event) {
      cleanup();
      const result = (event as CustomEvent<SketchUpFolderResult>).detail;
      if (result.error)
        reject(new Error("SketchUp could not read the folder."));
      else resolve(result.folder);
    }
    const timeout = host.setTimeout(() => {
      cleanup();
      reject(new Error("SketchUp did not return a folder."));
    }, 300_000);
    host.addEventListener(eventName, receive);
    try {
      host.sketchup!.selectProjectFolder!();
    } catch (error) {
      cleanup();
      reject(error);
    }
  });
}
