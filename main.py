#   iY Lab
#   Project: Developing a tool for exploring  RNA-Protein interactions
#
#   Name 	: Muhammad Nahin Khan
#   AndrewID  : mnk1
#   File Created: 01/26/2020
#
#   Script written by M. Nahin Khan
#   mnk1@andrew.cmu.edu

# RNPFind is a program that allows the user to input one RNA template molecule and to analyse the RBPs that bind
# on to it.

# Introduction:
# RNPFind takes as input the name of one RNA-encoding gene, or the coordinates of a region of interest
# on the hg38 human genome. In the future we plan on supporting an arbitrary RNA sequence as input to the program.

# The program then takes as input a preferred set of data sources from which it should extract the RNA-RBP binding
# information from (e.g. experimental-based ones like POSTAR or computational-prediction-based databases like RBPDB).
# Currently, RNPFind supports automated data extraction from RBPDB, ATTRACT, and POSTAR. Furthermore, custom-data
# (for example data obtained from one's own experiments) are also supported for inputting to the program. If you wish
# to add support for any other data source / algorithm of your liking, I recommend looking at "data_load_functions.py",
# which outlines ways for you to contribute your own source and integrating it into RNPFind.

# After loading RBP-Protein binding data, RNPFind then does internal processing to efficiently store the binding sites
# of RBPs on the template RNA. For details on how this might work, take a look at "bind_analysis.py" and
# "binding_analysis_binding_sites.py".

# Finally, after internal processing, RNPFind has multiple analysis features for getting useful information out of the
# RBP-binding data. Some of these analysis methods may require additional input from the user, such as certain
# computation parameters. Currently, we support two main analysis features: visualization on UCSC genome browser
# (within which we have integrated viewing density plots) and correlation matrix generation. For details on supporting
# other analysis functions that you may be interested in contributing, check out "analysis_functions.py"!


# Responsible for managing the loading of RNA-RBP interaction data:
from load_data import load_data
# Functions that help with interacting with the user to get their preference:
from user_input import get_user_rna_preference, get_user_data_source_preference, get_user_analysis_preference
# Responsible for managing the analysis functions that manipulate the RNA-RBP interaction data to get a useful output:
from analysis_functions import analysis_method_functions


def analysis_script():
    # Start by getting the transcript of interest to analyze
    [RNA_name, RNA_chr_no, RNA_start_chr_coord, RNA_end_chr_coord] = get_user_rna_preference()
    RNAInfo = [RNA_name, RNA_chr_no, RNA_start_chr_coord, RNA_end_chr_coord]

    # what data sources does the user want to collect data from today? (e.g. attract, postar, etc.)
    data_load_sources = get_user_data_source_preference()

    # load RNA-RBP interaction data using the selected data sources on the RNA molecule of interest
    # bigStorage stores data on binding sites of RBPs on the RNA molecule from each data source. For more details on
    # how bigStorage is structured, consult load_data.py!
    print("Collecting data now...")
    bigStorage = load_data(data_load_sources, RNAInfo)
    print("complete!")

    # BIOGRID is a database that stores information on protein-protein interaction evidence in the literature from
    # experiment. In future versions of RNPFind, BIOGRID data should be helpful in a variety of inquiries when
    # investigating relationships between RBPs that bind on RNA molecules.
    # Todo: Consider collecting and using BIOGRID data in a meaningful way

    # Give a quick summary on the data that has been loaded, in terms of total number of RBPs and binding sites
    # collected for the RNA molecule of interest
    no_rbps = 0
    no_sites = 0
    for no_rbp, no_site in [bigStorage[k].summary(is_return=True) for k in bigStorage]:
        no_rbps += no_rbp
        no_sites += no_site

    print("We have populated " + str(no_rbps) + " different RBPs with " + str(no_sites)
          + " different binding sites on the " + RNA_name + " RNA_name sequence across the "
          + str(RNA_end_chr_coord - RNA_start_chr_coord) + " bases specified!")

    # We now proceed to perform any number of analysis methods that the user may wish to apply to the data obtained
    while True:
        analysis_method = get_user_analysis_preference()
        analysis_method_function = analysis_method_functions[analysis_method]
        analysis_method_function(bigStorage, RNAInfo)

        print("")
        print("Thanks!")
        print("")
        print("Would you like to try another analysis method?")
        print(">")
        yn = input()
        if "n" in yn:
            break

    # Being here means the user does not want to analyze the same RNA anymore. We re-run this script, so the user could
    # maybe analyze a different RNA molecule if they want to. Yes, this means there is no smooth way to exit the
    # application as of now except by terminating the program.
    analysis_script()


if __name__ == '__main__':
    analysis_script()
