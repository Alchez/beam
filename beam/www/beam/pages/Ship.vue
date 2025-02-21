<template>
	<!-- navigation section -->
	<Navbar>
		<template #title>
			<h1>Ship</h1>
		</template>
		<template #navbaraction>
			<RouterLink :to="{ name: 'home' }">Home</RouterLink>
		</template>
	</Navbar>

	<!-- filters section -->
	<DemandFilters :filterByStatus="filterByStatus" :filterByDate="filterByDate" />

	<!-- body section -->
	<ListView :items="shipList" />
</template>

<script setup lang="ts">
import type { BeamFilterChoice, ListViewItem } from '@stonecrop/beam'
import { useInfiniteScroll } from '@vueuse/core'
import { ref } from 'vue'

import DemandFilters from '@/components/DemandFilters.vue'
import { useBeamStore } from '@/stores/beam'
import type { Demand } from '@/types'

const store = useBeamStore()
const ship = ref<Demand[]>([])
const shipList = ref<ListViewItem[]>([])
const canLoadMore = ref(true)
const page = ref(1)

useInfiniteScroll(
	window,
	async () => {
		const { data } = await store.getDemand({ filters: JSON.stringify({ doctype: 'Sales Order' }), page: page.value })
		if (data.length === 0) {
			canLoadMore.value = false
			return
		}

		ship.value = [...ship.value, ...data]
		setShipments(ship.value)
		page.value++
	},
	{ canLoadMore: () => canLoadMore.value }
)

const setShipments = (data: Demand[]) => {
	const dates: string[] = []
	shipList.value = []

	// TODO: move this to the server
	for (const row of data) {
		const scheduledDate = new Date(row.delivery_date)

		// add day-divider config when date changes
		if (!dates.includes(scheduledDate.toDateString())) {
			dates.push(scheduledDate.toDateString())
			shipList.value.push({
				date: scheduledDate.toISOString(),
				linkComponent: 'BeamDayDivider',
			})
		}

		shipList.value.push({
			count: { count: row.allocated_qty, of: row.total_required_qty },
			label: `${row.doctype} - ${row.parent}`,
			linkComponent: 'ListAnchor',
			description: `
					Item: ${row.item_code}
					Warehouse: ${row.warehouse}
					${row.customer ?? `Customer: ${row.customer}`}
				`.trim(),
			route: `#/delivery-note?id=${row.parent}`,
		})
	}
}

const filterByStatus = (choice: BeamFilterChoice) => {
	let filteredShipments = ship.value

	switch (choice.value) {
		case 'unallocated':
			filteredShipments = ship.value.filter(order => order.status === 'Unallocated' || order.status === '')
			break
		case 'partially_allocated':
			filteredShipments = ship.value.filter(order => order.status === 'Partially Allocated')
			break
		case 'soft_allocated':
			filteredShipments = ship.value.filter(order => order.status === 'Soft Allocated')
			break
	}

	setShipments(filteredShipments)
}

const filterByDate = (choice: BeamFilterChoice) => {
	const today = new Date()
	const todayString = today.toISOString().split('T')[0]
	let filteredShipments = ship.value

	switch (choice.value) {
		case 'past':
			filteredShipments = ship.value.filter(order => order.delivery_date < todayString)
			break
		case 'today':
			filteredShipments = ship.value.filter(order => order.delivery_date === todayString)
			break
		case 'future':
			filteredShipments = ship.value.filter(order => order.delivery_date > todayString)
			break
	}

	setShipments(filteredShipments)
}
</script>
