<template>
	<!-- navigation section -->
	<Navbar>
		<template #title>
			<h1>Receive</h1>
		</template>
		<template #navbaraction>
			<RouterLink :to="{ name: 'home' }">Home</RouterLink>
		</template>
	</Navbar>

	<!-- filters section -->
	<DemandFilters :filterByStatus="filterByStatus" :filterByDate="filterByDate" />

	<!-- body section -->
	<ListView :items="receiveList" />
</template>

<script setup lang="ts">
import type { BeamFilterChoice, ListViewItem } from '@stonecrop/beam'
import { useInfiniteScroll } from '@vueuse/core'
import { ref } from 'vue'

import DemandFilters from '@/components/DemandFilters.vue'
import { useBeamStore } from '@/stores/beam'
import type { Receive } from '@/types'

const store = useBeamStore()
const receive = ref<Receive[]>([])
const receiveList = ref<ListViewItem[]>([])
const canLoadMore = ref(true)
const page = ref(1)

useInfiniteScroll(
	window,
	async () => {
		const { data } = await store.getReceiving({ order_by: 'creation asc', page: page.value })
		if (data.length === 0) {
			canLoadMore.value = false
			return
		}

		receive.value = [...receive.value, ...data]
		setReceive(receive.value)
		page.value++
	},
	{ canLoadMore: () => canLoadMore.value }
)

const setReceive = (data: Receive[]) => {
	const dates: string[] = []
	receiveList.value = []

	// TODO: move this to the server
	for (const row of data) {
		const scheduledDate = new Date(row.schedule_date)

		// add day-divider config when date changes
		if (!dates.includes(scheduledDate.toDateString())) {
			dates.push(scheduledDate.toDateString())
			receiveList.value.push({
				date: scheduledDate.toISOString(),
				linkComponent: 'BeamDayDivider',
			})
		}

		receiveList.value.push({
			count: { count: row.received_qty, of: row.stock_qty },
			label: `${row.item_code} from ${row.warehouse}`,
			linkComponent: 'ListAnchor',
			description: `
					[${row.parent}]
					Warehouse: ${row.warehouse}
					Supplier: ${row.supplier}
				`.trim(),
			route: `#/purchase_order/${row.parent || 'new-purchase-order'}`,
		})
	}
}

const filterByStatus = (choice: BeamFilterChoice) => {
	let filteredReceive = receive.value

	switch (choice.value) {
		case 'unallocated':
			filteredReceive = receive.value.filter(order => order.status === 'Unallocated' || order.status === '')
			break
		case 'partially_allocated':
			filteredReceive = receive.value.filter(order => order.status === 'Partially Allocated')
			break
		case 'soft_allocated':
			filteredReceive = receive.value.filter(order => order.status === 'Soft Allocated')
			break
	}

	setReceive(filteredReceive)
}

const filterByDate = (choice: BeamFilterChoice) => {
	const today = new Date()
	const todayString = today.toISOString().split('T')[0]
	let filteredReceive = receive.value

	switch (choice.value) {
		case 'past':
			filteredReceive = receive.value.filter(order => order.schedule_date < todayString)
			break
		case 'today':
			filteredReceive = receive.value.filter(order => order.schedule_date === todayString)
			break
		case 'future':
			filteredReceive = receive.value.filter(order => order.schedule_date > todayString)
			break
	}

	setReceive(filteredReceive)
}
</script>

<style>
@import url('@stonecrop/beam/styles');

.beam_list-text label,
.beam_list-text p {
	white-space: pre-line !important;
}
</style>
