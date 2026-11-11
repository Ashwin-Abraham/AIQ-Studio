<script lang="ts">
import { defineComponent, type PropType } from "vue";
import type { ProjectManifest } from "./models/ProjectManifest";
import type { ProjectFolder } from "./models/ProjectFolder";
import { stages } from "./WorkflowService";
import ProjectHeader from "./components/ProjectHeader.vue";
import WorkflowDiagram from "./components/WorkflowDiagram.vue";
import StageDetails from "./components/StageDetails.vue";
import ProjectFilesPanel from "./components/ProjectFilesPanel.vue";
import AiChatPanel from "./components/AiChatPanel.vue";

export default defineComponent({
  name: "ProjectOrchestrator",
  components: {
    ProjectHeader,
    WorkflowDiagram,
    StageDetails,
    ProjectFilesPanel,
    AiChatPanel,
  },
  props: {
    project: { type: Object as PropType<ProjectManifest>, required: true },
    fileBase: { type: String, default: "./" },
    initialFolder: {
      type: Object as PropType<ProjectFolder>,
      default: undefined,
    },
  },
  data() {
    return { stages, selectedId: "site-analysis" };
  },
  computed: {
    title() {
      return this.project.name || "Site planning workflow";
    },
    records() {
      return this.project.workflow?.nodes || {};
    },
    selectedStage() {
      return this.stages.find((stage) => stage.id === this.selectedId)!;
    },
    selectedRecord() {
      return this.records[this.selectedId] || {};
    },
  },
});
</script>

<template>
  <ProjectHeader :title="title" />
  <main class="project-layout">
    <div class="task-selector">
      <WorkflowDiagram
        :stages="stages"
        :records="records"
        :selected-id="selectedId"
        @select="selectedId = $event"
      />
      <StageDetails
        :stage="selectedStage"
        :record="selectedRecord"
        :file-base="fileBase"
      />
    </div>
    <ProjectFilesPanel :initial-folder="initialFolder" />
    <AiChatPanel />
  </main>
</template>

<style scoped>
.project-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
  padding: 18px;
  max-width: 1900px;
  margin: auto;
}
.task-selector {
  grid-column: 1 / -1;
  display: grid;
  gap: 10px;
  min-width: 0;
}
.project-layout > .workspace-panel {
  align-self: stretch;
}
@media (max-width: 600px) {
  .project-layout {
    grid-template-columns: 1fr;
  }
}
</style>
