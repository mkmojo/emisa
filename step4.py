__author__ = 'qqy'

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

def parallel_save_total_cites_per_paper_over_time(file_name, prefix, wanted_journal_ids ):
    if not (file_name[len(file_name) - 4:] == ".txt" and file_name.startswith("cite")): return
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
                if key == "CURR":
                    key = year
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
        print "Example: python plot.py eco_journal_ids.txt cite_ref1993.txt"
        sys.exit()

    #parse input file
    wanted_journal_ids = parse_inputfile(sys.argv[1])
    print "journal_ids:", ', '.join(wanted_journal_ids)

    infile = sys.argv[2]
    #save total cites per parent paper over time
    parallel_save_total_cites_per_paper_over_time(file_name=infile, prefix="results/eco/step4", \
                                                  wanted_journal_ids=wanted_journal_ids)

if __name__ == "__main__":
    main()