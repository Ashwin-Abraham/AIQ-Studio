<script lang="ts">
import { defineComponent } from "vue";
export default defineComponent({
  name: "ProjectHeader",
  props: { title: { type: String, required: true } },
});
</script>

<template>
  <header class="project-header">
    <div class="eyebrow">AIQ Studio / Project record</div>
    <h1>{{ title }}</h1>
    <p>
      Choose a step to see its purpose, current decision and files. The diagram
      shows the path from project inputs to detailed concept design.
    </p>
  </header>
</template>

<style scoped>
.project-header {
  padding: 28px clamp(18px, 3vw, 48px) 20px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}
h1 {
  font-size: clamp(25px, 2.4vw, 38px);
  letter-spacing: -0.035em;
  margin: 7px 0 6px;
}
p {
  margin: 0;
  color: var(--muted);
  max-width: 72ch;
  line-height: 1.55;
}
</style>
