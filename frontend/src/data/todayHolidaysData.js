import { createResource } from 'frappe-ui'

// Resource factory for today's holidays
export function createTodayHolidaysResource(employee) {
  return createResource({
    url: 'hrms.api.get_today_holidays_for_employee',
    params: {
      employee: employee?.name,
    },
    auto: true,
    transform: (data) => {
      // Transform the API response to ensure consistent structure
      return {
        has_holidays_today: data?.has_holidays_today || false,
        is_manager: data?.is_manager || false,
        holiday_lists: data?.holiday_lists || []
      }
    }
  })
}

// Helper function to get initials for employee names
export function getEmployeeInitials(name) {
  return name
    .split(' ')
    .map(word => word[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}