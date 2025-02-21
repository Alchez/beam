<template>
	<!-- navigation section -->
	<Navbar>
		<template #title>
			<h1>Manufacture</h1>
		</template>
		<template #navbaraction>
			<RouterLink :to="{ name: 'home' }">Home</RouterLink>
		</template>
	</Navbar>

	<!-- filters section -->
	<BeamFilter>
		<BeamFilterOption
			:title="'Status'"
			:choices="[
				{ label: 'All', value: 'all' },
				{ label: 'Not Started', value: 'not_started' },
				{ label: 'In Process', value: 'in_process' },
				{ label: 'Completed', value: 'completed' },
			]"
			@select="filterByStatus" />
		<BeamFilterOption
			:title="'Start Date'"
			:choices="[
				{ label: 'All', value: 'all' },
				{ label: 'Past', value: 'past' },
				{ label: 'Today', value: 'today' },
				{ label: 'Future', value: 'future' },
			]"
			@select="filterByDate" />
	</BeamFilter>

	<!-- body section -->
	<ListView :items="items" />
</template>

<script setup lang="ts">
import type { BeamFilterChoice, ListViewItem } from '@stonecrop/beam'
import { onMounted, ref } from 'vue'

import { useBeamStore } from '@/stores/beam'
import type { WorkOrder } from '@/types'

const orders = ref<WorkOrder[]>([])
const items = ref<ListViewItem[]>([])
const store = useBeamStore()

onMounted(async () => {
	orders.value = await store.getAll<WorkOrder[]>('Work Order', {
		fields: JSON.stringify(['name', 'item_name', 'qty', 'produced_qty', 'planned_start_date', 'status']),
		order_by: 'creation asc',
	})

	setItems(orders.value)
})

const setItems = (orders: WorkOrder[]) => {
	items.value = []
	const dates: string[] = []
	orders.forEach(row => {
		const plannedDate = new Date(row.planned_start_date)
		const formattedDate = store.formatDate(plannedDate)

		// add day-divider config when date changes
		if (!dates.includes(plannedDate.toDateString())) {
			dates.push(plannedDate.toDateString())
			items.value.push({
				date: plannedDate.toISOString(),
				linkComponent: 'BeamDayDivider',
			})
		}

		items.value.push({
			...row,
			label: `${row.name} - ${row.item_name}`,
			description: formattedDate ? `Start: ${formattedDate}` : '',
			count: { count: row.produced_qty, of: row.qty },
			linkComponent: 'ListAnchor',
			route: `#/work_order/${row.name}`,
		})
	})
}

const filterByStatus = (choice: BeamFilterChoice) => {
	let filteredOrders = orders.value

	switch (choice.value) {
		case 'not_started':
			filteredOrders = orders.value.filter(order => order.status === 'Not Started')
			break
		case 'in_process':
			filteredOrders = orders.value.filter(order => order.status === 'In Process')
			break
		case 'completed':
			filteredOrders = orders.value.filter(order => order.status === 'Completed')
			break
	}

	setItems(filteredOrders)
}

const filterByDate = (choice: BeamFilterChoice) => {
	const today = new Date()
	const todayString = today.toISOString().split('T')[0]
	let filteredOrders = orders.value

	switch (choice.value) {
		case 'past':
			filteredOrders = orders.value.filter(order => order.planned_start_date < todayString)
			break
		case 'today':
			filteredOrders = orders.value.filter(order => order.planned_start_date === todayString)
			break
		case 'future':
			filteredOrders = orders.value.filter(order => order.planned_start_date > todayString)
			break
	}

	setItems(filteredOrders)
}
</script>
