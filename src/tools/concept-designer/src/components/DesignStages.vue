<template>
  <aside class="stage-panel" aria-label="Design stages">
    <div class="stage-heading">
      <p class="eyebrow">DESIGN STAGES</p>
      <button aria-label="Add stage" title="Add stage" @click="openAdd">Add +</button>
    </div>
    <div
      v-for="stage in stageEntries"
      :key="stage.id"
      class="stage-entry"
      :class="{ current: activeStage === stage.index }"
    >
      <div class="stage-capsule">
        <button
          class="stage-number"
          :aria-label="`Select stage ${stage.index + 1}: ${stage.name}`"
          :aria-current="activeStage === stage.index ? 'step' : undefined"
          @click="$emit('select', stage.index)"
        >
          {{ stage.index + 1 }}
        </button>
        <button
          v-if="editingId !== stage.id || activeStage !== stage.index"
          class="stage-name"
          :aria-label="`Stage ${stage.index + 1}: ${stage.name}`"
          :title="activeStage === stage.index ? 'Rename stage' : 'Select stage'"
          @click="activateName(stage.index)"
        >
          {{ stage.name }}
        </button>
        <input
          v-else
          :value="stage.name"
          :aria-label="`Stage ${stage.index + 1} name`"
          maxlength="40"
          @input="rename(stage.index, $event)"
          @blur="completeName(stage.index, $event)"
          @keydown.enter="blurInput"
        />
      </div>
      <button
        class="stage-delete"
        :aria-label="`Delete stage ${stage.index + 1}: ${stage.name}`"
        :disabled="names.length === 1"
        :title="names.length === 1 ? 'Keep at least one stage' : 'Delete stage'"
        @click="openDelete(stage.index)"
      >
        <svg
          class="trash-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.7"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M4 7h16M9 7V4h6v3M6 7l1 13h10l1-13M10 10v7M14 10v7" />
        </svg>
      </button>
    </div>
    <dialog ref="addDialog" class="stage-dialog" aria-labelledby="add-stage-title">
      <form @submit.prevent="createStage">
        <h2 id="add-stage-title">Add stage</h2>
        <label for="new-stage-name">Stage name</label>
        <input id="new-stage-name" v-model="newName" maxlength="40" required autofocus />
        <div class="dialog-actions">
          <button type="button" @click="closeDialog('addDialog')">Cancel</button>
          <button class="primary" type="submit" :disabled="!newName.trim()">Create stage</button>
        </div>
      </form>
    </dialog>
    <dialog ref="deleteDialog" class="stage-dialog" aria-labelledby="delete-stage-title">
      <h2 id="delete-stage-title">Delete stage?</h2>
      <p>Delete {{ pendingName }} stage and its drawings?</p>
      <div class="dialog-actions">
        <button autofocus @click="closeDialog('deleteDialog')">Cancel</button>
        <button class="primary" @click="confirmDelete">Delete stage</button>
      </div>
    </dialog>
  </aside>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
export default defineComponent({
  name: 'DesignStages',
  props: {
    names: { type: Array as PropType<string[]>, required: true },
    ids: { type: Array as PropType<string[]>, required: true },
    activeStage: { type: Number, required: true },
  },
  emits: {
    select: (_index: number) => true,
    rename: (_index: number, _name: string) => true,
    add: (_name: string) => true,
    remove: (_index: number) => true,
  },
  data() {
    return { newName: 'Develop', pendingId: '', editingId: '' }
  },
  computed: {
    stageEntries() {
      return this.names.map((name, index) => ({ id: this.ids[index], name, index }))
    },
    pendingName(): string {
      return this.names[this.ids.indexOf(this.pendingId)] ?? ''
    },
  },
  watch: {
    activeStage() {
      this.editingId = ''
    },
  },
  methods: {
    async activateName(index: number) {
      if (this.activeStage !== index) {
        this.$emit('select', index)
        return
      }
      this.editingId = this.ids[index]
      await this.$nextTick()
      const input = (this.$el as HTMLElement).querySelector<HTMLInputElement>('.stage-entry input')
      input?.focus()
      input?.select()
    },
    openAdd() {
      this.newName = 'Develop'
      ;(this.$refs.addDialog as HTMLDialogElement).showModal()
    },
    openDelete(index: number) {
      this.pendingId = this.ids[index]
      ;(this.$refs.deleteDialog as HTMLDialogElement).showModal()
    },
    closeDialog(ref: string) {
      ;(this.$refs[ref] as HTMLDialogElement).close()
    },
    createStage() {
      const name = this.newName.trim()
      if (!name) return
      this.closeDialog('addDialog')
      this.$emit('add', name)
    },
    confirmDelete() {
      const index = this.ids.indexOf(this.pendingId)
      this.closeDialog('deleteDialog')
      if (index >= 0) this.$emit('remove', index)
    },
    rename(index: number, event: Event) {
      this.$emit('rename', index, (event.target as HTMLInputElement).value)
    },
    completeName(index: number, event: Event) {
      const input = event.target as HTMLInputElement
      const name = input.value.trim() || 'Develop'
      this.$emit('rename', index, name)
      input.value = name
      this.editingId = ''
    },
    blurInput(event: KeyboardEvent) {
      ;(event.target as HTMLInputElement).blur()
    },
  },
})
</script>
