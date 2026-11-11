import exampleProject from "../../../../examples/site-planning-project/project.json";
import type { ProjectManifest } from "./models/ProjectManifest";
import type { ProjectFolder } from "./models/ProjectFolder";
import type { WorkflowStatus } from "./models/WorkflowStatus";
import type { WorkflowStage } from "./models/WorkflowStage";

declare const __EXAMPLE_BASE__: string;
declare const __EXAMPLE_FOLDER__: ProjectFolder;

export const statusLabels: Record<WorkflowStatus, string> = {
  complete: "Complete",
  "in-progress": "In progress",
  review: "Review",
  "not-started": "Not started",
};

export const stages: WorkflowStage[] = [
  {
    id: "site-data",
    label: "Site data",
    type: "Input",
    x: 26,
    y: 18,
    width: 195,
    description:
      "The supplied evidence about the site, including boundaries, surveys and existing conditions.",
  },
  {
    id: "programme-brief",
    label: "Programme brief",
    type: "Input",
    x: 26,
    y: 100,
    width: 195,
    description:
      "The requested uses, areas and capacities. Project goals and planning rules have separate records.",
  },
  {
    id: "project-goals",
    label: "Project goals",
    type: "Input",
    x: 26,
    y: 182,
    width: 195,
    description:
      "The project outcomes and priorities that guide design choices.",
  },
  {
    id: "site-analysis",
    label: "Site analysis",
    type: "Analysis",
    x: 282,
    y: 100,
    width: 184,
    description:
      "An interpretation of the site evidence against the brief and project goals.",
  },
  {
    id: "parti-diagramming",
    label: "Parti diagramming",
    type: "Design",
    x: 530,
    y: 18,
    width: 207,
    description:
      "A simple diagram that explains the driving spatial or cultural idea.",
  },
  {
    id: "pre-concept",
    label: "Pre-concept",
    type: "Design",
    x: 530,
    y: 100,
    width: 207,
    description:
      "Early options that test broad spatial relationships and design direction.",
  },
  {
    id: "conceptual-programme-brief",
    label: "Conceptual programme brief",
    subtitle: "programme brief",
    type: "Brief",
    x: 530,
    y: 182,
    width: 207,
    description:
      "A first distribution of the programme across the site or design option.",
  },
  {
    id: "concept-design",
    label: "Concept design",
    type: "Design",
    x: 800,
    y: 182,
    width: 187,
    description:
      "A developed concept with approximate zones, movement and form.",
  },
  {
    id: "detailed-concept-design",
    label: "Detailed concept design",
    subtitle: "concept design",
    type: "Design",
    x: 1050,
    y: 182,
    width: 178,
    description:
      "A more precise concept that tests areas, geometry and model implications.",
  },
];

export const edges = [
  "M221 45 H243 Q251 45 251 53 V105 Q251 113 259 113 H280",
  "M221 127 H280",
  "M221 209 H243 Q251 209 251 201 V149 Q251 141 259 141 H280",
  "M466 113 H485 Q493 113 493 105 V53 Q493 45 501 45 H528",
  "M466 127 H528",
  "M466 141 H485 Q493 141 493 149 V201 Q493 209 501 209 H528",
  "M374 154 V240 Q374 248 382 248 H885 Q893 248 893 240 V238",
  "M633 154 V180",
  "M737 209 H798",
  "M987 209 H1048",
];

export function loadProject(): {
  project: ProjectManifest;
  fileBase: string;
  initialFolder?: ProjectFolder;
} {
  const embedded = document.getElementById("project-data");
  if (embedded) {
    return {
      project: JSON.parse(embedded.textContent || "{}"),
      fileBase: "./",
    };
  }
  return {
    project: exampleProject as ProjectManifest,
    fileBase: __EXAMPLE_BASE__,
    initialFolder: __EXAMPLE_FOLDER__,
  };
}

export function projectFileUrl(path: string, base: string): string | undefined {
  const parts = path.split("/");
  if (
    !path ||
    parts.some((part) => !part || part === ".." || part === ".") ||
    /[:\\?#]/.test(path) ||
    Array.from(path).some((character) => character.charCodeAt(0) < 32)
  )
    return undefined;
  return base + parts.map(encodeURIComponent).join("/");
}
