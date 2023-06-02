import json
import os

parent_dir = "C:/Users/Daniel/Desktop/Python/MVP Bot"

def addVote(userid, employee, month, year):
	file_path = f'{parent_dir}/resources/votes/{year}/{month}.json'
	if os.path.isfile(file_path) == True:
		file = open(file_path, "r+")
		file_data = json.load(file)
		for employeevalues in file_data:
				if userid in file_data[employeevalues]:
					file_data[employeevalues].remove(userid)
		file_data[employee].append(userid)
		with open(file_path, "w+") as file:
			json.dump(file_data, file)
		return True
	else:
		return False

def createVote(employee1, employee2, employee3, month, year):
	path = f'{parent_dir}/resources/votes/{year}'
	if os.path.exists(f'{path}') == False:
		os.mkdir(f'{path}')
	file_path = f'{path}/{month.capitalize()}.json'
	json_object = {employee1: [], employee2: [], employee3: []}
	with open(file_path, 'w+') as file:
		json.dump(json_object, file)
