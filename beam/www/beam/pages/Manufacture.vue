<template>
	<Navbar>
		<template #title>
			<h1>Manufacture</h1>
		</template>
		<template #navbaraction>
			<RouterLink :to="{ name: 'home' }">Home</RouterLink>
		</template>
	</Navbar>

	<!-- setup filters -->
	<BeamFilter>
		<BeamFilterOption
			:title="'Status'"
			:choices="[
				{ label: 'All', value: 'all' },
				{ label: 'Complete', value: 'complete' },
				{ label: 'Incomplete', value: 'incomplete' },
			]"
			@select="filterByStatus" />
		<BeamFilterOption
			:title="'Delivery Start Date'"
			:choices="[
				{ label: 'All', value: 'all' },
				{ label: 'Past', value: 'past' },
				{ label: 'Today', value: 'today' },
				{ label: 'Future', value: 'future' },
			]"
			@select="filterByDate" />
	</BeamFilter>

	<!-- setup list view -->
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
	if (choice.value === 'all') {
		setItems(orders.value)
	} else if (choice.value === 'complete') {
		const completedOrders = orders.value.filter(order => order.status === 'Completed')
		setItems(completedOrders)
	} else if (choice.value === 'incomplete') {
		const incompleteOrders = orders.value.filter(order => order.status !== 'Completed')
		setItems(incompleteOrders)
	}
}

const filterByDate = (choice: BeamFilterChoice) => {
	const today = new Date()
	const todayString = today.toISOString().split('T')[0]

	if (choice.value === 'all') {
		setItems(orders.value)
	} else if (choice.value === 'past') {
		const pastOrders = orders.value.filter(order => order.planned_start_date < todayString)
		setItems(pastOrders)
	} else if (choice.value === 'today') {
		const todayOrders = orders.value.filter(order => order.planned_start_date === todayString)
		setItems(todayOrders)
	} else if (choice.value === 'future') {
		const futureOrders = orders.value.filter(order => order.planned_start_date > todayString)
		setItems(futureOrders)
	}
}
</script>
