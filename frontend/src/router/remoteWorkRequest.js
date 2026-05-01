const routes = [
	{
		name: "RemoteWorkRequestHistoryView",
		path: "/remote-work-requests",
		component: () => import("@/views/remoteWorkRequest/History.vue"),
	},
	{
		name: "RemoteWorkRequestFormView",
		path: "/remote-work-requests/new",
		component: () => import("@/views/remoteWorkRequest/Form.vue"),
	},
	{
		name: "RemoteWorkRequestDetailView",
		path: "/remote-work-requests/:id",
		props: true,
		component: () => import("@/views/remoteWorkRequest/Form.vue"),
	},
]

export default routes
