import { createApp } from "vue";
import ProjectOrchestrator from "./ProjectOrchestrator.vue";
import { loadProject } from "./WorkflowService";
import "./styles.css";

createApp(ProjectOrchestrator, loadProject()).mount("#app");
