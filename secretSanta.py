import argparse
import logging
import random
import os
from collections import Counter

class Giver:

	def __init__(self, name, assignments=None):
	    self.name = name
	    self.assignments = assignments if assignments is not None else {}

	def assign(self, receiver_list=None):
		if receiver_list is None:
			receiver_list = []

		for ind, category in enumerate(self.assignments):
			self.assignments[category] = receiver_list[ind]

	def __str__(self):
		msg = str()
		if len(self.assignments) >1:
			for category in self.assignments:
				msg+=f"{self.assignments[category]}: {category}\n"
		else:
			msg = f"{self.assignments[None]}\n"
		return f"{self.name}'s Top Secret Assignment:\n\n{msg}"

def createAssignments(givers,participants,number_of_categories):
	# Create a list of participants other than the giver and randomize the order
	
	# Array of lists that per giver with order of categories
	receiver_map = []
	participant_gift_count = {}

	# Create list of potential receivers
	available_participants = participants[:]

	# Create a list of participants other than the giver and randomize the order
	for ind, giver in enumerate(givers):
		potential_receivers = available_participants[:]

		if giver.name in potential_receivers:
			# Remove the giver from the list of potential receivers
			potential_receivers.remove(giver.name)
		
		# Randomize the list
		random.shuffle(potential_receivers)

		# Take the first x participants (x is number of categories/how many gifts each person will give)
		receiver_list = potential_receivers[:number_of_categories]

		for i,rec in enumerate(receiver_list):
			if rec in participant_gift_count:
				participant_gift_count[rec] += 1
				if participant_gift_count[rec]>=number_of_categories:
					available_participants.remove(rec)
			else:
				participant_gift_count[rec] = 1

		# Add each list to the receiver_map array
		receiver_map.append(receiver_list)

	return receiver_map

def checkAssignments(receiver_map):
	# Check to validate that no recievers are getting the same category twice
	index_value_map = {}
	receiver_counts = {}

	# If receiver_map is empty (if this is the first run)
	# or if lists are not the same length (if someone was assigned less people)
	# return False and try again
	if not receiver_map or len(set(map(len,receiver_map)))!=1:
	    return False

	for i, rec_list in enumerate(receiver_map):
	    for j, receiver in enumerate(rec_list):
	    	# Validate that user is not in the same index twice
        	if (j, receiver) in index_value_map:
        		return False  # Conflict found
        	else:
        		index_value_map[(j, receiver)] = i


	return True  # No conflicts found

def finalizeAssignments(givers, receiver_map):
	for ind, giver in enumerate(givers):
		giver.assign(receiver_map[ind])

def writeAssignmentsFile(givers,path):
	for giver in givers:
		file = os.path.join(path, f"{giver.name}_SecretSantaAssignments.txt")
		with open(file, 'w') as f:
			f.write(f"{giver}")

def main():
	parser=argparse.ArgumentParser()
	parser.add_argument('-c', '--categories', help='Comma separated list of categories')
	parser.add_argument('-p', '--participants', help='Comma separated list of participants', required=True)
	parser.add_argument('-o', '--output_files', help='Output each participant\'s assignments to a separate file', action='store_true')
	parser.add_argument('-of', '--output_path', help='Change directory to save files', default='.\\')	
	parser.add_argument('-v', '--verbose', help='Set logging level to info', action='store_true')
	parser.add_argument('-vv', '--very_verbose', help='Set logging level to debug', action='store_true')
	args = parser.parse_args()
	
	#configure logging
	if args.verbose:
		logging.basicConfig(level=logging.INFO)
	elif args.very_verbose:
		logging.basicConfig(level=logging.DEBUG)

	# Get initial list of participants and categories from user input
	participants = [participant.strip() for participant in args.participants.split(',')]
	if args.categories:
		categories = [category.strip() for category in args.categories.split(',')]
	else:
		categories = [None]

	# Stop if duplicates in participants
	if len(participants) != len(set(participants)):
		counts = Counter(participants)
		duplicates = [i for i, count in counts.items() if count > 1]
		print(f"Error: The following participant(s) are duplicated:\n\n{duplicates}\n")
		print("Please rerun with a unique list of participants")
		exit(1)

	# Stop if duplicates in categories
	elif len(categories) != len(set(categories)):
		counts = Counter(categories)
		duplicates = [i for i, count in counts.items() if count > 1]
		print(f"Error: The following category or categories are duplicated:\n\n{duplicates}\n")
		print("Please rerun with a unique list of categories")
		exit(1)

	if len(participants) > len(categories):
		logging.debug('Validated that there are more participants than categories')
	else:
		print("Incorrect number of categories to participants")
		print("There should be at least one less category than there are participants")
		exit(1)


	logging.debug(f'List of categories {categories}')
	# Instantiate list of givers
	givers = []

	# Create a Reciever and Giver object for each participant
	for ind, participant in enumerate(participants):
		givers.append(Giver(participant, dict.fromkeys(categories)))
		logging.debug(f"Assigned the following giver: {givers[ind]}")

	receiver_map = []
	# Set max number of attempts to prevent infinite loop
	run_count = 0
	max_attempts = 10000

	# If checkAssignments as not validated, continue running
	while not checkAssignments(receiver_map):
		receiver_map = createAssignments(givers,participants,len(categories))
		run_count += 1
		logging.debug(f"createAssignments Attempt {run_count}\n {receiver_map}")

		if run_count >= max_attempts:
			logging.error("Max number of attempts reached")
			exit(1)

	logging.info(f"succeeded with in {run_count} tries with the following map: {receiver_map}")
	finalizeAssignments(givers,receiver_map)

	if args.output_files:
		# Check provided output path
		if os.path.exists(args.output_path):
	   		logging.debug("Path exists")
		else:
			print("Path does not exist")
			exit(1)

	    # Write the files if the path exists
		writeAssignmentsFile(givers,args.output_path)
	else:
		for giver in givers:
			print(giver)

if __name__ == '__main__':
	main()
