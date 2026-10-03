<template>
  <section class="chat-zone" aria-labelledby="chat-title">
    <header>
      <div>
        <p class="eyebrow">DESIGN CONVERSATION</p>
        <h2 id="chat-title">Develop this direction</h2>
      </div>
    </header>
    <div class="messages" aria-live="polite">
      <p class="system-note">
        Local notes only. An agent is not connected. Export the session to share the brief and
        drawings.
      </p>
      <p v-if="!messages.length" class="empty-note">
        What should this option explore? Add a brief, a constraint, or a design question.
      </p>
      <p v-for="note in messages" :key="note.id" class="user-message">
        {{ note.text }}
      </p>
    </div>
    <form @submit.prevent="addMessage">
      <label class="sr-only" for="message">Design note</label
      ><input
        id="message"
        v-model="message"
        placeholder="Describe your idea for this option…"
        maxlength="4000"
      /><button class="primary" :disabled="!message.trim()">Add note ↑</button>
    </form>
    <label class="chat-option-selector"
      >Working on
      <select :value="activeId" @change="selectOption">
        <option v-for="option in options" :key="option.id" :value="option.id">
          {{ option.name }}
        </option>
      </select></label
    >
  </section>
</template>

<script lang="ts">
import { defineComponent, type PropType } from 'vue'
import type { DesignOption } from '../models/DesignOption'
export default defineComponent({
  name: 'DesignConversation',
  props: {
    messages: { type: Array as PropType<DesignOption['messages']>, required: true },
    options: { type: Array as PropType<DesignOption[]>, required: true },
    activeId: { type: String, required: true },
  },
  emits: { submit: (_text: string) => true, select: (_id: string) => true },
  data() {
    return { message: '' }
  },
  watch: {
    activeId() {
      this.message = ''
    },
  },
  methods: {
    addMessage() {
      const text = this.message.trim()
      if (text) {
        this.$emit('submit', text)
        this.message = ''
      }
    },
    selectOption(event: Event) {
      this.$emit('select', (event.target as HTMLSelectElement).value)
    },
  },
})
</script>
