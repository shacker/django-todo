
try:
	# if django is not installed,
	# skips check because it blocks automated installs
	import django
	from . import check
except ModuleNotFoundError:
	# this can happen during install time, if django is not installed yet!
	pass
