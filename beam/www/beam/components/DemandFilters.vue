<template>
	<!-- filters section -->
	<BeamFilter>
		<BeamFilterOption
			:title="'Status'"
			:choices="[
				{ label: 'All', value: 'all' },
				{ label: 'Unallocated', value: 'unallocated' },
				{ label: 'Partially Allocated', value: 'partially_allocated' },
				{ label: 'Soft Allocated', value: 'soft_allocated' },
			]"
			@select="filterByStatus" />
		<BeamFilterOption
			:title="'Delivery Date'"
			:choices="[
				{ label: 'All', value: 'all' },
				{ label: 'Past', value: 'past' },
				{ label: 'Today', value: 'today' },
				{ label: 'Future', value: 'future' },
			]"
			@select="filterByDate" />
	</BeamFilter>
</template>

<script setup lang="ts">
import type { BeamFilterChoice } from '@stonecrop/beam'

defineProps<{
	filterByStatus: (choice: BeamFilterChoice) => void
	filterByDate: (choice: BeamFilterChoice) => void
}>()
</script>
