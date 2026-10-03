import { createApp } from 'vue'
import VueKonva from 'vue-konva'
import ConceptDesigner from './ConceptDesigner.vue'
import './style.css'

createApp(ConceptDesigner).use(VueKonva).mount('#app')
