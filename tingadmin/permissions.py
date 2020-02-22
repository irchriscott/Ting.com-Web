# -*- coding: utf-8 -*-
from __future__ import unicode_literals

restaurant = [
	{'category': 'restaurant', 'permission': 'can_update_restaurant', 		'title': 'Update Profile'},
	{'category': 'restaurant', 'permission': 'can_update_configurations', 	'title': 'Update Configuration'}
]


promotion = [
	{'category': 'promotion', 'permission': 'can_add_promotion', 	'title': 'Add'},
	{'category': 'promotion', 'permission': 'can_view_promotion', 	'title': 'View'},
	{'category': 'promotion', 'permission': 'can_update_promotion', 'title': 'Update'},
	{'category': 'promotion', 'permission': 'can_avail_promotion', 	'title': 'Avail / Unavail'},
	{'category': 'promotion', 'permission': 'can_delete_promotion', 'title': 'Delete'}
]

branch = [
	{'category': 'branch', 'permission': 'can_add_branch', 		'title': 'Add'},
	{'category': 'branch', 'permission': 'can_view_branch', 	'title': 'View'},
	{'category': 'branch', 'permission': 'can_update_branch', 	'title': 'Update'},
	{'category': 'branch', 'permission': 'can_avail_branch', 	'title': 'Avail / Unavail'},
]

tables = [
	{'category': 'table', 'permission': 'can_add_table', 	'title': 'Add'},
	{'category': 'table', 'permission': 'can_view_table', 	'title': 'View'},
	{'category': 'table', 'permission': 'can_update_table', 'title': 'Update'},
	{'category': 'table', 'permission': 'can_avail_table', 	'title': 'Avail / Unavail'}
]

administrators = [
	{'category': 'admin', 'permission': 'can_add_admin', 		'title': 'Add'},
	{'category': 'admin', 'permission': 'can_view_admin', 		'title': 'View Branch'},
	{'category': 'admin', 'permission': 'can_view_all_admin', 	'title': 'View All'},
	{'category': 'admin', 'permission': 'can_update_admin', 	'title': 'Update'},
	{'category': 'admin', 'permission': 'can_disable_admin', 	'title': 'Disable / Enable'},
	{'category': 'admin', 'permission': 'can_move_admin', 		'title': 'Move'},
]

category = [
	{'category': 'category', 'permission': 'can_add_category', 		'title': 'Add'},
	{'category': 'category', 'permission': 'can_view_category', 	'title': 'View'},	
	{'category': 'category', 'permission': 'can_update_category', 	'title': 'Update'},
	{'category': 'category', 'permission': 'can_delete_category', 	'title': 'Delete'}
]

menus = [
	{'category': 'menu', 'permission': 'can_add_menu', 		'title': 'Add'},
	{'category': 'menu', 'permission': 'can_view_menu', 	'title': 'View'},
	{'category': 'menu', 'permission': 'can_update_menu', 	'title': 'Update'},
	{'category': 'menu', 'permission': 'can_avail_menu', 	'title': 'Avail / Unavail'},
	{'category': 'menu', 'permission': 'can_delete_menu', 	'title': 'Delete'}
]

placements = [
	{'category': 'placement', 'permission': 'can_view_placements', 	'title': 'View'},
	{'category': 'placement', 'permission': 'can_assign_table', 	'title': 'Assign Table To Waiter'},
	{'category': 'placement', 'permission': 'can_done_placement', 	'title': 'Done Placement'}
]

orders = [
	{'category': 'orders', 'permission': 'can_view_orders', 	'title': 'View'},
	{'category': 'orders', 'permission': 'can_receive_orders', 	'title': 'Receive'},
	{'category': 'orders', 'permission': 'can_accept_orders', 	'title': 'Accept / Decline'}
]

bills = [
	{'category': 'bill', 'permission': 'can_send_bill', 	'title': 'Send'},
	{'category': 'bill', 'permission': 'can_complete_bill', 'title': 'Complete'}
]

booking = [
	{'category': 'booking', 'permission': 'can_view_booking', 	'title': 'View'},
	{'category': 'booking', 'permission': 'can_accept_booking', 'title': 'Accept / Decline'},
	{'category': 'booking', 'permission': 'can_cancel_booking', 'title': 'Cancel'}
]

management = [
	{'category': 'management', 'permission': 'can_view_reports', 	'title': 'View Reports'},
	{'category': 'management', 'permission': 'can_print_reports', 	'title': 'Print Reports'},
	{'category': 'management', 'permission': 'can_view_incomes', 	'title': 'View Incomes'},
	{'category': 'management', 'permission': 'can_print_incomes', 	'title': 'Print Incomes'}
]

permissions = branch + restaurant + tables + administrators + category + menus + orders + bills + booking + management + promotion + placements

global_permissions = [
						'can_view_table', 
						'can_view_admin', 
						'can_view_category', 
						'can_view_menu', 
						'can_view_orders', 
						'can_view_booking'
					]

admin_permissions = global_permissions + [
						'can_add_branch',
						'can_view_branch',
						'can_update_branch',
						'can_avail_branch',
						'can_update_restaurant',
						'can_update_configurations',
						'can_add_table',
						'can_update_table',
						'can_avail_table',
						'can_add_admin',
						'can_update_admin',
						'can_disable_admin',
						'can_add_category',
						'can_update_category',
						'can_delete_category',
						'can_add_menu',
						'can_update_menu',
						'can_avail_menu',
						'can_delete_menu',
						'can_view_reports',
						'can_print_reports',
						'can_view_incomes',
						'can_print_incomes',
						'can_move_admin',
						'can_add_promotion',
						'can_view_promotion',
						'can_update_promotion',
						'can_avail_promotion',
						'can_delete_promotion'
					]

supervisor_permissions = global_permissions + [
							'can_add_table',
							'can_update_table',
							'can_avail_table',
							'can_assign_table',
							'can_add_category',
							'can_update_category',
							'can_delete_category',
							'can_add_menu',
							'can_view_menu',
							'can_update_menu',
							'can_avail_menu',
							'can_add_promotion',
							'can_view_promotion',
							'can_update_promotion',
							'can_avail_promotion',
							'can_delete_promotion',
							'can_receive_orders',
							'can_accept_orders',
							'can_send_bill',
							'can_complete_bill',
							'can_accept_booking',
							'can_cancel_booking',
							'can_view_reports',
							'can_view_placements',
							'can_assign_table'
						]

chef_permissions = global_permissions + [
						'can_update_category',
						'can_update_menu',
						'can_avail_menu',
						'can_receive_orders',
						'can_accept_orders',
						'can_view_placements',
						'can_assign_table'
					]

waiter_permissions = global_permissions + [
						'can_avail_table',
						'can_avail_menu',
						'can_send_bill',
						'can_complete_bill',
						'can_accept_booking',
						'can_cancel_booking',
						'can_accept_orders',
						'can_receive_orders'
					]

accountant_permission = global_permissions + [
							'can_send_bill',
							'can_complete_bill',
							'can_view_reports',
							'can_print_reports',
							'can_view_incomes',
							'can_print_incomes'
						]


advertisment_account_permissions = [
						'can_update_restaurant',
						'can_add_branch',
						'can_view_branch',
						'can_update_branch',
						'can_avail_branch',
						'can_move_admin',
						'can_add_admin',
						'can_view_admin',
						'can_update_admin',
						'can_disable_admin',
						'can_add_category',
						'can_view_category',
						'can_update_category',
						'can_delete_category',
						'can_add_menu',
						'can_view_menu',
						'can_update_menu',
						'can_avail_menu',
						'can_delete_menu',
						'can_add_promotion',
						'can_view_promotion',
						'can_update_promotion',
						'can_avail_promotion',
						'can_delete_promotion'
					]


advertisment_new_account_permissions  = [
						'can_view_branch',
						'can_view_admin',
						'can_add_category',
						'can_view_category',
						'can_update_category',
						'can_delete_category',
						'can_add_menu',
						'can_view_menu',
						'can_update_menu',
						'can_avail_menu',
						'can_delete_menu',
						'can_add_promotion',
						'can_view_promotion',
						'can_update_promotion',
						'can_avail_promotion',
						'can_delete_promotion'
					]