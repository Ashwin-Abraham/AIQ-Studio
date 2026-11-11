import type { WorkflowStatus } from "./WorkflowStatus";
import type { ProjectFile } from "./ProjectFile";

export interface StageRecord {
  status?: WorkflowStatus;
  summary?: string;
  decisions?: string[];
  files?: ProjectFile[];
}
