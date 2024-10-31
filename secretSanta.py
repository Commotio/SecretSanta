import argparse
import logging
import random
import os

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
		for category in self.assignments:
			msg+=f"{self.assignments[category]}: {category}\n"
		return f"{self.name}'s Top Secret Assignments:\n\n{msg}"

def createAssignments(givers,participants):
	# Create a list of participants other than the giver and randomize the order
	
	# Array of lists that per giver with order of categories
	receiver_map = []

	# Create a list of participants other than the giver and randomize the order
	for ind, giver in enumerate(givers):
		receiver_list = participants[:]
		receiver_list.pop(ind)
		random.shuffle(receiver_list)
		# Add each list to the receiver_map array
		receiver_map.append(receiver_list)

	return receiver_map

def checkAssignments(receiver_map):
	# Check to validate that no recievers are getting the same category twice
	index_value_map = {}

	# If receiver_map is empty, automatically return True (no conflicts)
	if not receiver_map:
	    return False

	for i, rec_list in enumerate(receiver_map):
	    for j, receiver in enumerate(rec_list):
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
	parser.add_argument('-c', '--categories', help='Comma separated list of categories', required=True)
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

	# validate that there's one less category than participant
	if len(args.participants.split(',')) == len(args.categories.split(','))+1:
		logging.info('Validated that there is the correct ratio of participants to categories')
	else:
		print("Incorrect number of categories to participants")
		print("There should be one less category than there are participants")
		exit(1)

	# Get initial list of participants and categories from user input
	participants = [participant.strip() for participant in args.participants.split(',')]
	categories = [category.strip() for category in args.categories.split(',')]

	logging.debug(f'List of categories {categories}')
	# Instantiate list of givers
	givers = []

	# Create a Reciever and Giver object for each participant
	for ind, participant in enumerate(participants):
		givers.append(Giver(participant, dict.fromkeys(categories)))
		logging.debug(f"Assigned the following giver: {givers[ind]}")

	receiver_map = []
	run_count = 0

	# If checkAssignments as not validated, continue running
	while not checkAssignments(receiver_map):
		receiver_map = createAssignments(givers,participants)
		run_count += 1
		logging.debug(f"createAssignments ran {run_count} times")
		logging.debug(f"receiver_map to test: {receiver_map	}")

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