import click, sh

import json, csv
from pathlib import Path
import numbers

@click.command()
#@click.option('--headless', '-hl', default=True, is_flag=True, help='Run in headless mode')
@click.option('--count', default=1, help='Number of tests to run. Default is 1.')
@click.option('--output-file', default='output', help='Name of csv file w/o extension. Default is "output".')
#@click.option('--html', default=False, is_flag=True, help='Generate full HTML reports')
@click.argument('link')

def cli(link, count, output_file):
	"""This script runs Lighthouse using the command line interface."""
	output = 'output'

	click.echo("******** Start Point Loma ********")

	outputPath = Path(output_file+'.csv')
	if outputPath.is_file():
		if output_file != output:
			confirmMessage = 'File {0} already exists. Proceeding will overwrite existing file. \nContinue?'.format(output_file+'.csv')
		else:
			confirmMessage = 'Default file already exists. Proceeding will overwrite existing file. \nContinue?'
		
		if (click.confirm(confirmMessage)) == False:
			click.echo("******** Quitting Point Loma ********")
			return;

	click.echo("Running lighthouse on '{0}'".format(link))

	fmp_avg = 0
	si_avg = 0
	eil_avg = 0
	tti_avg = 0

	for x in range(count):
		y = x+1
		click.echo("---Test #{0}---".format(y))
		click.echo("Running lighthouse...")

		filename = "./results{0}.json".format(y)
		sh.lighthouse(link, "--output", "json", "--output-path", filename)

		click.echo("Exporting results for test {0} to csv file...".format(y))

		with open(filename) as json_data:
			d = json.load(json_data)

			# extract data from json files
			timestamp = d["generatedTime"]
			firstMeaningfulPaint = d["audits"]["first-meaningful-paint"]["rawValue"]
			speedIndex = d["audits"]["speed-index-metric"]["rawValue"]
			estimatedInputLatency = d["audits"]["estimated-input-latency"]["rawValue"]
			timeToInteractive = d["audits"]["time-to-interactive"]["rawValue"]

			# check for non numeric values before adding to average
			if [isinstance(firstMeaningfulPaint, numbers.Number)] or firstMeaningfulPaint.isdigit():
				fmp_avg = fmp_avg + firstMeaningfulPaint

			if [isinstance(speedIndex, numbers.Number)] or speedIndex.isdigit():
				si_avg = si_avg + speedIndex

			if [isinstance(estimatedInputLatency, numbers.Number)] or estimatedInputLatency.isdigit():
				eil_avg = eil_avg + estimatedInputLatency

			if [isinstance(timeToInteractive, numbers.Number)] or timeToInteractive.isdigit():
				tti_avg = tti_avg + timeToInteractive

			# rows hardcoded for now
			if count == 1:
				header = ["********* Test {0} *********".format(y), "{0}".format(link)]
			else:
				header = ["********* Test {0} *********".format(y), ""]

			data1 =	["Timestamp", timestamp]
			data2 =	["First Meaningful Paint", firstMeaningfulPaint]
			data3 =	["Speed Index", speedIndex]
			data4 =	["Estimated Input Latency", estimatedInputLatency]
			data5 =	["Time to Interactive", timeToInteractive]
			newLine = ["", ""]

			# if output file is specified, set it
			if output_file != output:
				output = output_file

			# convert to csv file
			output = output + '.csv'

			# default is to overwrite existing files
			if x == 0:
				read_mode = 'w'
			else:
				read_mode = 'a'

			# add data to csv file
			with open(output, read_mode) as csvfile:
				wr = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
				wr.writerow(header)
				wr.writerow(data1)
				wr.writerow(data2)
				wr.writerow(data3)
				wr.writerow(data4)
				wr.writerow(data5)
				wr.writerow(newLine)

	if count != 1:
		# append averages to end of file
		read_mode = 'a'

		with open(output, read_mode) as csvfile:
			wr = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
			
			fmp_avg = fmp_avg/count
			si_avg = si_avg/count
			eil_avg = eil_avg/count
			tti_avg = tti_avg/count

			header = ["********* Average {0} Tests *********".format(y), "{0}".format(link)]
			#data1 =	["Timestamp", timestamp]
			data2 =	["First Meaningful Paint", fmp_avg]
			data3 =	["Speed Index", si_avg]
			data4 =	["Estimated Input Latency", eil_avg]
			data5 =	["Time to Interactive", tti_avg]
			newLine = ["", ""]

			wr.writerow(header)
			#wr.writerow(data1)
			wr.writerow(data2)
			wr.writerow(data3)
			wr.writerow(data4)
			wr.writerow(data5)
			wr.writerow(newLine)

	click.echo("******** Finish Point Loma ********")