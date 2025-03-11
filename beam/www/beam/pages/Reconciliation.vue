<template>
	<Navbar>
		<template #title>
			<h1>Reconciliation</h1>
		</template>
		<template #navbaraction>
			<RouterLink :to="{ name: 'home' }">Home</RouterLink>
		</template>
	</Navbar>

	<div class="reconciliation">
		<div class="dropdown-container">
			<ADropdown label="Warehouse" :items="warehouseList" v-model="reconciliation.set_warehouse" />
			<BeamBtn class="clear-button" @click="clearField()"> X </BeamBtn>
		</div>
	</div>

	<!-- body section -->
	<ListView :items="items" :key="componentKey" />
	<div class="begin" v-if="items.length == 0">
		<span>Scan or Select Warehouses to Begin</span>
	</div>
	<!-- footer section -->
	<ControlButtons :buttons="controlButtons" />
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'

import ControlButtons from '@/components/ControlButtons.vue'
import { useBeamStore } from '@/stores/beam'
import type { ControlButton, StockReconciliation } from '@/types'

const store = useBeamStore()
const items = ref([])
const componentKey = ref(0)
const reconciliation = computed<StockReconciliation>(() => {
	const data = store.cache.mappers.reconciliation as StockReconciliation;
	return {
		set_warehouse: data?.set_warehouse || '',
		items: data?.items || [],
		purpose: data?.purpose || 'Stock Reconciliation',
	};
});

const warehouseList = ref<string[]>([])

onMounted(async () => {
	store.$patch(state => (state.cache.mappers.reconciliation = reconciliation.value))
	warehouseList.value = store.warehouseList.filter(w => !w.is_group).map(w => w.name)
})

const clearField = () =>
	store.$patch(state => (state.cache.mappers.reconciliation['set_warehouse'] = ''))

const controlButtons = computed((): ControlButton[] => [])
</script>
