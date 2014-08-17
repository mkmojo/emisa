import os
import ast
import sys
import matplotlib.pyplot as plt


def save(path, ext='png', close=True, verbose=True):
    """Save a figure from pyplot.

    Parameters
    ----------
    path : string
        The path (and filename, without the extension) to save the
        figure to.

    ext : string (default='png')
        The file extension. This must be supported by the active
        matplotlib backend (see matplotlib.backends module).  Most
        backends support 'png', 'pdf', 'ps', 'eps', and 'svg'.

    close : boolean (default=True)
        Whether to close the figure after saving.  If you want to save
        the figure multiple times (e.g., to multiple formats), you
        should NOT close it in between saves or you will have to
        re-plot it.

    verbose : boolean (default=True)
        Whether to print information about when and where the image
        has been saved.

    """

    # Extract the directory and filename from the given path
    directory = os.path.split(path)[0]
    filename = "%s.%s" % (os.path.split(path)[1], ext)
    if directory == '':
        directory = '.'

    # If the directory does not exist, create it
    if not os.path.exists(directory):
        os.makedirs(directory)

    # The final path to save to
    savepath = os.path.join(directory, filename)

    if verbose:
        print("Saving figure to '%s'..." % savepath),

    # Actually save the figure
    plt.savefig(savepath)

    # Close it
    if close:
        plt.close()

    if verbose:
        print("Done")


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


def draw_chart(intput_list, dist_filename, prefix):
    x = list()
    y = list()
    for item in intput_list:
        x.append(item[0])
        y.append(item[1])
    plt.plot(x, y, 'o')
    plt.axis([min(x) - 10, max(x) + 10, 0, max(y) + 0.1])
    save(os.path.join(prefix, dist_filename), ext='png', close=True, verbose=True)
    plt.close()


#dist is a dictionary
def save_distribution(year, dist, dist_filename, prefix):
    t = []
    for key, val in dist.items():
        if key == "CURR":
            key = int(year)
        t.append((int(key), val))
    t.sort()

    dist_file_path = os.path.join(prefix + "/src", dist_filename)
    if not os.path.exists(os.path.dirname(dist_file_path)):
        os.makedirs(os.path.dirname(dist_file_path))
    with open(dist_file_path, 'w') as fhand:
        for item in t:
            fhand.write(str(item[0]) + " " + str(item[1]) + "\n")

    draw_chart(t, dist_filename, prefix + "/images")


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
            num_total += 1

            #extract counter ends
            atpos = line.find("Counter")
            line_fst_hlf = line[:atpos].split()
            counter_start = atpos + len("Counter") + 1
            counter_end = line.find(")", counter_start)

            year, journal_id, counter = line_fst_hlf[0], line_fst_hlf[1], \
                                        line[counter_start:counter_end]

            #Ignore those that are not listed papers
            #Chose eco_papers
            if journal_id not in wanted_journal_ids: continue

            counter = ast.literal_eval(counter)
            #pretend that data point does not even show up in the dataset
            if "NULL" in counter.keys():
                continue
            #accumulate counters
            for key, val in counter.items():
                children_paper_counts[key] = children_paper_counts.get(key, 0) + val

            num_wanted += 1
        try:
            fhand.close()
        except:
            print "Close fail:", file_name

        #total number of citation for that year
        num_children_total_citation = sum(children_paper_counts.values())
        for key, val in children_paper_counts.items():
            distribution[key] = float(val) / num_wanted

        print "num_uniq_child_paper_cite_year:", len(children_paper_counts)
        print "num_total_child_citation:", num_children_total_citation
        print "num_wanted_paper:", num_wanted
        print "num_total_paper:", num_total
        print ""

        distributions.append((int(year), distribution))
        num_totals.append((int(year), num_total))
        num_wanteds.append((int(year), num_wanted))
        num_citations.append((int(year), num_children_total_citation))
    return distributions, num_totals, num_wanteds, num_citations


def save_num_totals(prefix, filename, num_totals):
    file_path = os.path.join(os.getcwd(), prefix + "/src", filename)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w') as fhand:
        num_totals.sort()
        for item in num_totals:
            year = item[0]
            val = item[1]
            fhand.write(str(year) + " " + str(val) + "\n")
    draw_chart(num_totals, filename, prefix + "/images")


def save_num_wanteds(prefix, filename, num_totals):
    file_path = os.path.join(os.getcwd(), prefix + "/src", filename)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w') as fhand:
        num_totals.sort()
        for item in num_totals:
            year = item[0]
            val = item[1]
            fhand.write(str(year) + " " + str(val) + "\n")
    draw_chart(num_totals, filename, prefix + "/images")


def save_num_citations(prefix, filename, num_totals):
    file_path = os.path.join(os.getcwd(), prefix + "/src", filename)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w') as fhand:
        num_totals.sort()
        for item in num_totals:
            year = item[0]
            val = item[1]
            fhand.write(str(year) + " " + str(val) + "\n")
    draw_chart(num_totals, filename, prefix + "/images")


def save_num_ratio(prefix, filename, num_totals):
    file_path = os.path.join(os.getcwd(), prefix + "/src", filename)
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    with open(file_path, 'w') as fhand:
        num_totals.sort()
        for item in num_totals:
            year = item[0]
            val = item[1]
            fhand.write(str(year) + " " + str(val) + "\n")
    draw_chart(num_totals, filename, prefix + "/images")


def calculate_ratio(num_wanteds, num_totals):
    assert len(num_wanteds) == len(num_totals)
    num_wanteds.sort()
    num_totals.sort()
    ratio = []
    for i in xrange(len(num_wanteds)):
        assert num_wanteds[i][0] == num_totals[i][0]
        ratio.append((num_wanteds[i][0], float(num_wanteds[i][1]) / num_totals[i][1]))
    return ratio


def save_total_cites_per_paper_over_time(prefix, wanted_journal_ids):
    files = os.listdir(os.getcwd())
    for file_name in files:
        if not (file_name[len(file_name) - 4:] == ".txt" and file_name.startswith("cite")): continue

        with open(file_name, 'r') as fhand:
            for line in fhand:

                if line.startswith("year"): continue

                #extract counter ends
                atpos = line.find("Counter")
                line_fst_hlf = line[:atpos].split()
                counter_start = atpos + len("Counter") + 1
                counter_end = line.find(")", counter_start)

                year, journal_id, parent_paper_id, counter = line_fst_hlf[0], line_fst_hlf[1], \
                                                             line[(atpos - 16):(atpos - 1)],  \
                                                             line[counter_start:counter_end]

                #Ignore those that are not listed papers
                #Chose eco_papers
                if journal_id not in wanted_journal_ids: continue

                counter = ast.literal_eval(counter)
                #pretend that data point does not even show up in the dataset
                if "NULL" in counter.keys(): continue

                #save graph to disk
                lst = []
                for key, val in counter.items():
                    lst.append((int(key), val))
                lst.sort()
                draw_chart(lst, parent_paper_id, prefix + "/images" +"/" + file_name)


                #save src file to disk
                file_path = os.path.join(os.getcwd(), prefix + "/src", file_name, parent_paper_id)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                with open(file_path, 'w') as out_fhand:
                    for item in lst:
                        x = item[0]
                        y = item[1]
                        out_fhand.write(str(x) + ' ' + str(y) + '\n')



def main():
    if len(sys.argv) < 2:
        print "Example: python plot.py eco_journal_ids.txt"
        sys.exit()

    #parse input file
    wanted_journal_ids = parse_inputfile(sys.argv[1])
    print "journal_ids:", ', '.join(wanted_journal_ids)

    print "Start counting:.."
    distributions, num_totals, num_wanteds, num_citations = do_data_process(wanted_journal_ids)

    ratios = calculate_ratio(num_wanteds, num_totals)

    #save distributions
    for item in distributions:
        year = item[0]
        distribution = item[1]
        dist_filename = "dist_" + str(year) + ".dist"
        save_distribution(year, distribution, dist_filename, "results/step1")

    #save ratio of total_eco_paper/totol_all_paper to file
    save_num_ratio(prefix="results/step2", filename= \
        "ratio.txt", num_totals=ratios)

    #save total number parents papers each year to file
    save_num_totals(prefix="results/step3", filename= \
        "total_paper.txt", num_totals=num_totals)

    #save total cites per parent paper over time
    save_total_cites_per_paper_over_time(prefix="results/step4", wanted_journal_ids=wanted_journal_ids)

    #save total number of citations each year to file
    save_num_citations(prefix="results/step5", filename= \
        "total_citation.txt", num_totals=num_citations)


if __name__ == "__main__":
    main()
