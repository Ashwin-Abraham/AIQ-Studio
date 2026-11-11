<script lang="ts">
import { defineComponent, type PropType } from "vue";
import {
  canSelectProjectFolder,
  selectProjectFolder,
} from "../ProjectFolderService";
import type { ProjectFolder } from "../models/ProjectFolder";

export default defineComponent({
  name: "ProjectFilesPanel",
  props: {
    initialFolder: {
      type: Object as PropType<ProjectFolder>,
      default: undefined,
    },
  },
  data() {
    return {
      folder: this.initialFolder,
      selecting: false,
      error: false,
      canSelect: canSelectProjectFolder(),
    };
  },
  computed: {
    buttonLabel() {
      if (this.selecting) return "Selecting…";
      return this.folder ? "Change folder" : "Select folder";
    },
  },
  methods: {
    async chooseFolder() {
      this.selecting = true;
      this.error = false;
      try {
        const folder = await selectProjectFolder();
        if (folder) this.folder = folder;
      } catch {
        this.error = true;
      } finally {
        this.selecting = false;
      }
    },
  },
});
</script>

<template>
  <section class="workspace-panel panel" aria-labelledby="project-files-title">
    <div class="workspace-panel-header">
      <h2 id="project-files-title">Project files</h2>
      <button
        type="button"
        class="folder-button"
        :disabled="!canSelect || selecting"
        @click="chooseFolder"
      >
        {{ buttonLabel }}
      </button>
    </div>
    <div class="workspace-panel-body" aria-live="polite">
      <p v-if="error" class="folder-error">
        Could not read that folder. Select it again or choose another folder.
      </p>
      <p v-if="!canSelect" class="workspace-note">
        Open this page in Edge, Chrome, or the SketchUp trial to select a
        folder.
      </p>
      <template v-if="folder">
        <h3 class="folder-name">{{ folder.name }}</h3>
        <ul
          v-if="folder.subfolders.length"
          class="folder-list"
          aria-label="Subfolders"
        >
          <li v-for="name in folder.subfolders" :key="name">
            <span class="folder-icon" aria-hidden="true"></span>
            {{ name }}
          </li>
        </ul>
        <p v-else class="workspace-note">This folder has no subfolders.</p>
      </template>
      <p v-else-if="canSelect" class="workspace-note">
        Select a project folder to see its immediate subfolders.
      </p>
    </div>
  </section>
</template>

<style scoped>
.folder-button {
  padding: 7px 12px;
  border: 1px solid var(--blue);
  border-radius: 6px;
  background: var(--blue);
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.folder-button:disabled {
  opacity: 0.6;
  cursor: default;
}
.folder-name {
  margin: 0 0 10px;
  font-size: 15px;
  overflow-wrap: anywhere;
}
.folder-list {
  display: grid;
  gap: 6px;
  list-style: none;
  padding: 0;
  margin: 0;
}
.folder-list li {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 8px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: white;
  font-size: 14px;
  overflow-wrap: anywhere;
}
.folder-icon {
  flex: 0 0 16px;
  height: 11px;
  border: 1px solid var(--blue);
  border-radius: 2px;
  background: var(--paper);
}
.folder-error {
  margin: 0 0 12px;
  color: #9b342e;
  font-size: 14px;
}
</style>
