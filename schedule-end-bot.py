from datetime import datetime
import requests



# http://stackoverflow.com/questions/8419564/ddg#8419655
def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return (d2 - d1).days


def fetch_schedule_ending_date(school_id):
	response = requests.get("https://api.classclock.app/v0/bellschedules/" + school_id, headers={"Accept:", "application/json"})
	if response.status_code == 200:
		response = response.json()
		dates = []
		data = response.get("data")
		for schedule in data:
			dates.extend(schedule.dates)

		dates.sort()
		print(dates)



fetch_schedule_ending_date("522c21a0ce6011e9b6830242ac1f0874")