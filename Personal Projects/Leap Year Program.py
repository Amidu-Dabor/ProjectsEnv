def is_leap(year, month):
	"""
 	Takes input for year and month, checks if year is a leap year and if the month of February has 29 days.
 	"""
	month_days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
	days = month_days[month - 1]
	
	if (year % 4 == 0 and month == 2) and ((year % 100 != 0) or (year % 400 == 0)):
		print(f"Leap year: {days} days")
	elif month == 2:
		print(f"Not a leap year: {days} days")
	else:
		print(f"The month selected has {days} days")


year = int(input("Enter a year: "))
month = int(input("Enter a month: "))
result = is_leap(year, month)












