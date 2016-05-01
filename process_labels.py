group_names = ['N', 'H', 'B']

def process_labels_time(group_name, outfile):

	labels_dict = None
	labels_avg = {}
	with open('label_times_%s.txt' % group_name) as in_file:
		labels_dict = eval(in_file.read())
	for label in labels_dict.keys():
		avg = sum(labels_dict[label])*1.0/len(labels_dict[label])
		labels_avg[label] = avg
	outfile.write('avg time: \n')
	for label in labels_avg.keys():
		outfile.write('%s\t%f\n' %(label, labels_avg[label]))
	outfile.write('-------\n')
	normalized_avg = {}
	outfile.write('normalized_avg:\n')
	min_avg = min(labels_avg.values())
	max_avg = max(labels_avg.values())
	for label in labels_avg.keys():
		normalized_avg[label] = (labels_avg[label]-min_avg)/max_avg
		outfile.write('%s\t%f\n' %(label, normalized_avg[label]))


def process_labels_count(group_name, outfile):
	labels_dict = None
	labels_avg = {}
	with open('label_counts_%s.txt' %group_name) as in_file:
		labels_avg = eval(in_file.read())
	outfile.write('-----------\n')
	outfile.write('total count\n')
	for label in labels_avg.keys():
		outfile.write('%s\t%f\n' %(label, labels_avg[label]))

	
	outfile.write('normalized count')
	normalized_avg = {}
	min_avg = min(labels_avg.values())
	max_avg = max(labels_avg.values())
	for label in labels_avg.keys():
		normalized_avg[label] = (labels_avg[label]-min_avg)*1.0/max_avg
		outfile.write('%s\t%f\n' %(label, normalized_avg[label]))

	

for group in group_names:
	with open('out_%s'%group, 'w') as outfile:
		process_labels_time(group, outfile)
		outfile.write("count\n")
		process_labels_count(group, outfile)