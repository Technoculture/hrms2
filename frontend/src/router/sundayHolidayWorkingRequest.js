const routes = [
	{
		name: "SundayHolidayWorkingRequestHistoryView",
		path: "/sunday-holiday-working-requests",
		component: () => import("@/views/sundayHolidayWorkingRequest/History.vue"),
	},
	{
		name: "SundayHolidayWorkingRequestFormView", 
		path: "/sunday-holiday-working-requests/new",
		component: () => import("@/views/sundayHolidayWorkingRequest/Form.vue"),
	},
	{
		name: "SundayHolidayWorkingRequestDetailView",
		path: "/sunday-holiday-working-requests/:id",
		props: true,
		component: () => import("@/views/sundayHolidayWorkingRequest/Form.vue"),
	},
]

export default routes