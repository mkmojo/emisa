import os
import ast
import sys
import numpy
import matplotlib.pyplot as plt


def parse_inputfile(input_filename):
    path = os.path.join(os.getcwd(), input_filename)
    fhand = open(path)
    t = list()
    for line in fhand:
        line = line.split()
        if len(line) == 0: continue
        t = t + line

    journal_ids = t

    if len(t) <= 0:
        print "Input Error: too few eco paper ids"
        sys.exit()
    for i, journal_id in enumerate(journal_ids):
        try:
            int(journal_id)
        except:
            print "Input Error:", i + 1, " th element must be a number instead of :", journal_ids[i]
            sys.exit()
    return journal_ids


def draw_chart(intput_list):
    x = list()
    y = list()
    for item in intput_list:
        x.append(item[0])
        y.append(item[1])
    plt.plot(x, y, 'o')
    plt.axis([min(x) - 10, max(x) + 10, min(y), max(y) + 0.1])
    plt.show()


#dist is a dictionary
def save_distribution(dist, dist_filename):
    t = []
    for key, val in dist.items():
        t.append((int(key), val))
    t.sort()

    with open(dist_filename, 'w') as fhand:
        for item in t:
            fhand.write(str(item[0]) + " " + str(item[1]) + "\n")


def do_data_process(wanted_journal_ids):

    num_totals = []
    num_wanteds = []
    num_citations = []
    distributions = []

    files = os.listdir(os.getcwd())
    for file_name in files:
        # open file looks like cite*.txt
        if not (file_name[len(file_name) - 4:] == ".txt" and file_name.startswith("cite")): continue
        try:
            fhand = open(file_name)
            print "File:", file_name
        except:
            print "Open fail:", file_name

        # count number of journals
        num_wanted = 0  #number of wanted papers in that year
        num_total = 0  #number of all papers in that year
        children_paper_counts = {}
        distribution = {}
        for line in fhand:
            #skip first line
            if line.startswith("year"): continue
            num_total = num_total + 1

            #extract counter ends
            atpos = line.find("Counter")
            line_fst_hlf = line[:atpos].split()
            counter_start = atpos + len("Counter") + 1
            counter_end = line.find(")", counter_start)

            year, journal_id, counter = line_fst_hlf[0], line_fst_hlf[1], \
                                        line[counter_start:counter_end]

            #Ignore those that are not listed papers
            if journal_id not in wanted_journal_ids: continue

            counter = ast.literal_eval(counter)
            #pretend that data point does not even show up in the dataset
            if "NULL" in counter.keys():
                continue
            #accumulate counters
            for key, val in counter.items():
                children_paper_counts[key] = children_paper_counts.get(key, 0) + val

            num_wanted = num_wanted + 1
        try:
            fhand.close()
        except:
            print "Close fail:", file_name


        num_citation = sum(children_paper_counts.values())
        for key, val in children_paper_counts.items():
            distribution[key] = float(val) / num_citation

        print "num_uniq_child_paper_cite_year:", len(children_paper_counts)
        print "num_total_child_citation:", num_citation
        print "num_wanted_paper:", num_wanted
        print "num_total_paper:", num_total
        print ""

        distributions.append((int(year), distribution))
        num_totals.append((int(year), num_total))
        num_wanteds.append((int(year), num_wanted))
        num_citations.append((int(year), num_citation))

    return distributions, num_totals, num_wanteds, num_citations


def main():
    if len(sys.argv) < 2:
        print "Example: python plot.py eco_journal_ids.txt"
        sys.exit()

    #parse input file
    wanted_journal_ids = parse_inputfile(sys.argv[1])
    print "journal_ids:", ', '.join(wanted_journal_ids)

    print "Start counting:.."
    distributions, num_totals, num_wanteds, num_citations = do_data_process(wanted_journal_ids)

    #save distributions
    for item in distributions:
        dist_filename = "dist_" + str(item[0]) + ".dist"
        save_distribution(item[1], dist_filename)

if __name__ == "__main__":
    main()
