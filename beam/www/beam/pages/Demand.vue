<template>
	<!-- navigation section -->
	<Navbar>
		<template #title>
			<h1>Demand</h1>
		</template>
		<template #navbaraction>
			<RouterLink :to="{ name: 'home' }">Home</RouterLink>
		</template>
	</Navbar>

	<!-- filters section -->
	<DemandFilters :filterByStatus="filterByStatus" :filterByDate="filterByDate" />

	<!-- body section -->
	<ListView :items="demandList" />
</template>

<script setup lang="ts">
import type { BeamFilterChoice, ListViewItem } from '@stonecrop/beam'
import { useInfiniteScroll } from '@vueuse/core'
import { ref } from 'vue'

import DemandFilters from '@/components/DemandFilters.vue'
import { useBeamStore } from '@/stores/beam'
import type { Demand } from '@/types'

declare const frappe: any

const store = useBeamStore()
const demand = ref<Demand[]>([])
const demandList = ref<ListViewItem[]>([])
const canLoadMore = ref(true)
const page = ref(1)

useInfiniteScroll(
	window,
	async () => {
		const { data } = await store.getDemand({ order_by: 'creation asc', page: page.value })
		if (!data || data.length === 0) {
			canLoadMore.value = false
			return
		}

		demand.value = [...demand.value, ...data]
		setDemand(demand.value)
		page.value++
	},
	{ canLoadMore: () => canLoadMore.value }
)

const setDemand = (data: Demand[]) => {
	const dates: string[] = []
	demandList.value = []

	// TODO: move this to the server
	for (const row of data) {
		const scheduledDate = new Date(row.allocated_date)

		// add day-divider config when date changes
		if (!dates.includes(scheduledDate.toDateString())) {
			dates.push(scheduledDate.toDateString())
			demandList.value.push({
				date: scheduledDate.toISOString(),
				linkComponent: 'BeamDayDivider',
			})
		}

		demandList.value.push({
			label: `${row.item_code} from ${row.item_warehouse}`,
			linkComponent: 'ListAnchor',
			route: `#/${frappe.scrub(row.doctype)}/${row.parent}`,
			description: `
					[${row.parent}]
					Production Item: ${row.production_item}
					BOM No: ${row.bom_no}
				`.trim(),
			count: {
				count: +row.allocated_qty.toFixed(2),
				of: +row.total_required_qty.toFixed(2),
			},
		})
	}
}

const filterByStatus = (choice: BeamFilterChoice) => {
	let filteredDemand = demand.value

	switch (choice.value) {
		case 'unallocated':
			filteredDemand = demand.value.filter(order => order.status === 'Unallocated' || order.status === '')
			break
		case 'partially_allocated':
			filteredDemand = demand.value.filter(order => order.status === 'Partially Allocated')
			break
		case 'soft_allocated':
			filteredDemand = demand.value.filter(order => order.status === 'Soft Allocated')
			break
	}

	setDemand(filteredDemand)
}

const filterByDate = (choice: BeamFilterChoice) => {
	const today = new Date()
	const todayString = today.toISOString().split('T')[0]
	let filteredDemand = demand.value

	switch (choice.value) {
		case 'past':
			filteredDemand = demand.value.filter(order => order.delivery_date < todayString)
			break
		case 'today':
			filteredDemand = demand.value.filter(order => order.delivery_date === todayString)
			break
		case 'future':
			filteredDemand = demand.value.filter(order => order.delivery_date > todayString)
			break
	}

	setDemand(filteredDemand)
}
</script>
