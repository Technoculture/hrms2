const routes = [
	{
		name: "AttendanceRequestListView",
		path: "/attendance-requests",
		component: () => import("@/views/attendance/AttendanceRequestList.vue"),
	},
	{
		name: "AttendanceRequestFormView",
		path: "/attendance-requests/new",
		component: () => import("@/views/attendance/AttendanceRequestForm.vue"),
	},
	{
		name: "AttendanceRequestDetailView",
		path: "/attendance-requests/:id",
		props: true,
		component: () => import("@/views/attendance/AttendanceRequestForm.vue"),
	},
	{
		name: "ShiftRequestListView",
		path: "/shift-requests",
		component: () => import("@/views/attendance/ShiftRequestList.vue"),
	},
	{
		name: "ShiftRequestFormView",
		path: "/shift-requests/new",
		component: () => import("@/views/attendance/ShiftRequestForm.vue"),
	},
	{
		name: "ShiftRequestDetailView",
		path: "/shift-requests/:id",
		props: true,
		component: () => import("@/views/attendance/ShiftRequestForm.vue"),
	},
	{
		name: "ShiftAssignmentListView",
		path: "/shift-assignments",
		component: () => import("@/views/attendance/ShiftAssignmentList.vue"),
	},
	{
		name: "ShiftAssignmentFormView",
		path: "/shift-assignments/new",
		component: () => import("@/views/attendance/ShiftAssignmentForm.vue"),
	},
	{
		name: "ShiftAssignmentDetailView",
		path: "/shift-assignments/:id",
		props: true,
		component: () => import("@/views/attendance/ShiftAssignmentForm.vue"),
	},
	{
		name: "EmployeeCheckinListView",
		path: "/employee-checkins",
		component: () => import("@/views/attendance/EmployeeCheckinList.vue"),
	},
	{
		name: "AttendanceHistoryView",
		path: "/attendance-history",
		component: () => import("@/views/attendance/AttendanceHistory.vue"),
	},
	{
		name: "AttendanceRegularizationFormView",
		path: "/attendance-regularization/new",
		component: () => import("@/views/attendance/AttendanceRegularizationForm.vue"),
	},
	{
		name: "AttendanceRegularizationDetailView",
		path: "/attendance-regularization/:id",
		props: true,
		component: () => import("@/views/attendance/AttendanceRegularizationForm.vue"),
	},
	{
		name: "AttendanceRegularizationHistoryView",
		path: "/attendance-regularization-history",
		component: () => import("@/views/attendance/AttendanceRegularizationHistory.vue"),
	},
]

export default routes
