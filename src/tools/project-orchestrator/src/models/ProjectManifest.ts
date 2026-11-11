import type { StageRecord } from "./StageRecord";

export interface ProjectManifest {
  name?: string;
  workflow?: { nodes?: Record<string, StageRecord> };
}
