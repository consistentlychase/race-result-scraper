import pandas as pd
import requests
import json
import os
import config
from datetime import datetime





RACES = config.RACES
EVENT_ID_SEARCH_URL = config.EVENT_ID_SEARCH_URL
RESULTS_URL = config.RESULTS_URL

meta_data = [] 
folder_path = 'data'
os.makedirs(folder_path, exist_ok=True)

# **************************** GET RACE IDs FOR EACH RACE AND ALL YEARS **************************** #


def get_race_ids():
	if os.path.exists('data/race_meta_data.json'):
		print(f"A data file for 'race_meta_data' already exists.")

		# --------- FUTURE  --------- #
		# Add option to check if a file exists, and if it does, to check if the data we are getting is already there.
		# Then check if there are new races added that we need to gather info for
		# Then append file with new race id info


	else:
		for key, value in RACES.items(): # NAME, MAIN ID, LOCATION

			# --------- CREATE RACE ID DB STRUCTURE  --------- #
			# Outer loop to get NAME of CURRENT RACE
			for i in range(len(RACES)): 

				# Create the dictionary that goes inside the main list
				outer_dict = {}
				outer_key = f'{key}' # NAME OF CURRENT RACE


			# --------- GET RACE IDs -> CREATE DICT  --------- #
			response = requests.get(f"{EVENT_ID_SEARCH_URL}/{RACES[key]['event_id']}")
			response.raise_for_status()
			raw_data = response.text

			split_top = raw_data.split('/json">')
			middle = split_top[1]

			split_bottom = middle.split('</script></body></html>')
			split_data_str = split_bottom[0]

			data_dict = json.loads(split_data_str)


			# Create the list that goes inside the outer dictionary (META DATA)
			inner_list = []

			for item in data_dict['props']['pageProps']['subevents']:
				if item['wtc_distance_text'] != "51.5 KM":
					input_format = "%m/%d/%Y"
					date_object = datetime.strptime(item['wtc_eventdate_formatted'], input_format)
					output_format = "%Y-%m-%d"
					output_date_str = date_object.strftime(output_format)

					race_data = {
						'race_name': key,
						'race_date': output_date_str,
						'year': item['wtc_eventdate_formatted'].split('/')[2],
						'race_id': item['wtc_eventid'],
					}

					inner_list.append(race_data)

			outer_dict[outer_key] = inner_list

			# Append the outer dictionary to the main meta_data list
			meta_data.append(outer_dict)


		with open(f"data/race_meta_data.json", 'w') as json_file:
			json.dump(meta_data, json_file, indent=4)
			print(f"A data file for 'race_meta_data' was created.")



# **************************** USE RACE ID TO GET DATA FOR EACH RACE AND ALL YEARS **************************** #

def get_race_data():
	with open(f"data/race_meta_data.json", 'r') as file:
		data = json.load(file)


	# Get names of each race
	for i in range(len(RACES)): # DO THIS 5 TIMES
		for key, value in data[i].items(): # LOOKS AT ONE RACE AT A TIME 
			race_name = key
			race_index = data[i][race_name]


			# for this particular race (i), iterate through race_ids file
			for j in range(len(race_index)):
				race_id = data[i][race_name][j]['race_id']
				year = data[i][race_name][j]['year']
				date = data[i][race_name][j]['race_date']


				# --------- CLEAN DATA: CREATE NEW JSON FILE PER YEAR  --------- #
				race_response = requests.get(f"{RESULTS_URL}{race_id}")
				race_response.raise_for_status()
				raw_race_data = race_response.text
				race_year_dict = json.loads(raw_race_data)


				os.makedirs(f'data/clean/{race_name}', exist_ok=True)

				if os.path.exists(f'data/clean/{race_name}/{race_name}_Results_{year}.csv'):
					#print(f"A clean data file for '{race_name}_Results_{year}' already exists.")
					pass

				else:    
					list_of_athletes = []

					for k in range(len(race_year_dict['resultsJson']['value'])):
						athlete = {
							'athlete_name': race_year_dict['resultsJson']['value'][k]['wtc_ContactId']['fullname'],
							'athlete_bib': race_year_dict['resultsJson']['value'][k]['bib'],
							'gender': race_year_dict['resultsJson']['value'][k]['wtc_ContactId']['gendercode'],
							'age_group': race_year_dict['resultsJson']['value'][k]['wtc_AgeGroupId']['wtc_agegroupname'],  	
							'country': race_year_dict['resultsJson']['value'][k]['wtc_CountryRepresentingId']['wtc_name'],
							'swim_time_formatted': race_year_dict['resultsJson']['value'][k]['wtc_swimtimeformatted'],
							'swim_time_seconds': race_year_dict['resultsJson']['value'][k]['wtc_swimtime'],
							't1_time': race_year_dict['resultsJson']['value'][k]['wtc_transition1timeformatted'],	
							't1_time_seconds': race_year_dict['resultsJson']['value'][k]['wtc_transition1time'],
							'bike_time_formatted': race_year_dict['resultsJson']['value'][k]['wtc_biketimeformatted'],	
							'bike_time_seconds': race_year_dict['resultsJson']['value'][k]['wtc_biketime'],	
							't2_time': race_year_dict['resultsJson']['value'][k]['wtc_transitiontime2formatted'],	
							't2_time_seconds': race_year_dict['resultsJson']['value'][k]['wtc_transition2time'], 
							'run_time_formatted': race_year_dict['resultsJson']['value'][k]['wtc_runtimeformatted'],	
							'run_time_seconds': race_year_dict['resultsJson']['value'][k]['wtc_runtime'], 
							'finish_time_formatted': race_year_dict['resultsJson']['value'][k]['wtc_finishtimeformatted'],	
							'finish_time_seconds': race_year_dict['resultsJson']['value'][k]['wtc_finishtime'], 
							'swim_rank_gender': race_year_dict['resultsJson']['value'][k]['wtc_swimrankgender'],	
							'bike_rank_gender': race_year_dict['resultsJson']['value'][k]['wtc_bikerankgender'],	
							'run_rank_gender': race_year_dict['resultsJson']['value'][k]['wtc_runrankgender'],
							'swim_rank_group': race_year_dict['resultsJson']['value'][k]['wtc_swimrankgroup'],	
							'bike_rank_group': race_year_dict['resultsJson']['value'][k]['wtc_bikerankgroup'],	
							'run_rank_group': race_year_dict['resultsJson']['value'][k]['wtc_runrankgroup'],	
							'swim_rank_overall': race_year_dict['resultsJson']['value'][k]['wtc_swimrankoverall'],	
							'bike_rank_overall': race_year_dict['resultsJson']['value'][k]['wtc_bikerankoverall'],	
							'run_rank_overall': race_year_dict['resultsJson']['value'][k]['wtc_runrankoverall'],	
							'finish_rank_gender': race_year_dict['resultsJson']['value'][k]['wtc_finishrankgender'],	
							'finish_rank_group': race_year_dict['resultsJson']['value'][k]['wtc_finishrankgroup'],	
							'finish_rank_overall': race_year_dict['resultsJson']['value'][k]['wtc_finishrankoverall'],	
							'finished': race_year_dict['resultsJson']['value'][k]['wtc_finisher']
						}

						list_of_athletes.append(athlete)

					df_details = pd.json_normalize(list_of_athletes, max_level=1)
					df_details.to_csv(f'data/clean/{race_name}/{race_name}_Results_{year}.csv', index=False)
					print(f"A csv file for '{race_name}_Results_{year}.csv' was created.")
					#df = pd.DataFrame(list_of_athletes)
