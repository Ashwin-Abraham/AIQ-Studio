<script lang="ts">
import { defineComponent, type PropType } from "vue";
import type { WorkflowStage } from "../models/WorkflowStage";
import type { StageRecord } from "../models/StageRecord";
import { projectFileUrl, statusLabels } from "../WorkflowService";
export default defineComponent({
  name: "StageDetails",
  props: {
    stage: { type: Object as PropType<WorkflowStage>, required: true },
    record: { type: Object as PropType<StageRecord>, required: true },
    fileBase: { type: String, default: "./" },
  },
  computed: {
    status() {
      return statusLabels[this.record.status || "not-started"];
    },
    summary() {
      return this.record.summary || "No summary recorded.";
    },
    decisions() {
      return this.record.decisions || [];
    },
    files() {
      return (this.record.files || []).map((file) => ({
        ...file,
        href: projectFileUrl(file.path, this.fileBase),
      }));
    },
  },
});
</script>

<template>
  <aside class="details panel" aria-live="polite">
    <div>
      <div class="eyebrow">{{ stage.type }}</div>
      <h2>{{ stage.label }}</h2>
      <span class="badge">{{ status }}</span>
      <p>{{ stage.description }}</p>
    </div>
    <section>
      <h3>Current summary</h3>
      <p :class="{ 'empty-note': !record.summary }">{{ summary }}</p>
    </section>
    <section>
      <h3>Decisions</h3>
      <ul v-if="decisions.length">
        <li v-for="decision in decisions" :key="decision">{{ decision }}</li>
      </ul>
      <p v-else class="empty-note">No decisions recorded.</p>
    </section>
    <section>
      <h3>Files</h3>
      <ul v-if="files.length">
        <li v-for="file in files" :key="file.path">
          <a v-if="file.href" :href="file.href">{{ file.label || file.path }}</a
          ><span v-else>{{ file.label || file.path }}</span>
        </li>
      </ul>
      <p v-else class="empty-note">No files recorded.</p>
    </section>
  </aside>
</template>

<style scoped>
.details {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 20px;
  padding: 18px 22px;
  min-width: 0;
}
h2 {
  font-size: 25px;
  letter-spacing: -0.025em;
  margin: 10px 0;
}
.badge {
  display: inline-block;
  padding: 5px 9px;
  border-radius: 6px;
  background: #edf2ef;
  color: var(--green);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
p,
li {
  line-height: 1.55;
  overflow-wrap: anywhere;
}
p {
  color: #42585b;
  margin: 8px 0 0;
}
section {
  border-left: 1px solid var(--border);
  padding-left: 16px;
}
h3 {
  margin: 0 0 10px;
  font-size: 14px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}
ul {
  padding-left: 18px;
  margin: 0;
}
li {
  margin: 7px 0;
}
a {
  color: var(--blue);
}
.empty-note {
  font-style: italic;
  color: var(--muted);
}
@media (max-width: 820px) {
  .details {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
@media (max-width: 600px) {
  .details {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  section {
    border-left: 0;
    border-top: 1px solid var(--border);
    padding: 12px 0 0;
  }
}
</style>
