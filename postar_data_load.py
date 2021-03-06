# This file contains functions for loading data from the postar database.

import os
import bisect

from config import annotation_column_delimiter

postar_all_column_names = ["chrom", "chromStart", "chromEnd", "postarID", "nil", "strand", "rbpName", "dataSource",
                           "cellType", "expSource", "postarScore"]
postar_all_column_descriptions = ["chromosome number", "start coordinate", "end coordinate", "POSTAR database ID",
                                  "not sure", "strand", "RBP Name", "Data Source", "Cell type", "experimental source",
                                  "score"]

postar_columns_of_interest = [3, 7, 8, 9, 10]
postar_default_label_index = [8]
postar_default_mouse_over_index = 9

postar_column_names = [postar_all_column_names[i] for i in postar_columns_of_interest]
postar_column_descriptions = [postar_all_column_descriptions[i] for i in postar_columns_of_interest]


class Query(object):

    def __init__(self, query):
        self.query = query

    def __lt__(self, line):
        RNA_chr_no, RNA_start_chr_coord, RNA_end_chr_coord = self.query
        s = line.split()

        return (s[0], int(s[1]), int(s[2])) > ('chr' + str(RNA_chr_no), RNA_start_chr_coord, RNA_end_chr_coord)


class FileSearcher(object):

    def __init__(self, file_pointer):
        self.file_pointer = file_pointer
        self.file_pointer.seek(0, os.SEEK_END)
        self.num_bytes = self.file_pointer.tell() - 1

    def __len__(self):
        return self.num_bytes

    def __getitem__(self, i):
        if i >= len(self) or i < 0:
            raise ValueError("Index Out of Bounds!")
        ls = i
        le = i + 1

        self.file_pointer.seek(ls)
        while ls > 0 and self.file_pointer.read(1) != "\n":
            ls = ls - 1
            self.file_pointer.seek(ls)

        self.file_pointer.seek(le)
        while le < self.num_bytes and self.file_pointer.read(1) != "\n":
            le = le + 1
            self.file_pointer.seek(le)

        self.file_pointer.seek(ls)
        current_line = self.file_pointer.read(le - ls)
        return current_line


def binary_search_populate(file_path, rna_info, debug=False):
    # TODO: Fix a bug here that causes genes without any data to start collecting the whole genome!!
    RNA, RNA_chr_no, RNA_start_chr_coord, RNA_end_chr_coord = rna_info
    query = Query((RNA_chr_no, RNA_start_chr_coord, RNA_end_chr_coord))
    f = open(file_path)
    search_file = FileSearcher(f)
    f.seek(bisect.bisect(search_file, query) + 1)
    s = f.readline().split()
    isFound = False
    seen = []
    while s:
        if s[0] == 'chr' + str(RNA_chr_no) and int(s[1]) > RNA_start_chr_coord and int(s[2]) < RNA_end_chr_coord:
            isFound = True

            if debug:
                if (s[7]) not in seen:
                    print(';'.join(s))
                    seen += [s[7]]

            rbp = s[6]
            start, end = s[1], s[2]
            start = int(start) - RNA_start_chr_coord
            end = int(end) - RNA_start_chr_coord

            # TODO: Consider reformatting the annotation for visual appeal
            # annotation = ", ".join([s[i] for i in [3, 4, 5, 7, 8, 9, 10]])
            # annotation = ", ".join([s[i] for i in [7, 8, 9, 10]])
            annotation = annotation_column_delimiter.join([s[i] for i in postar_columns_of_interest])
            yield rbp, start, end, annotation

        elif isFound:
            break

        s = f.readline().split()


def postar_data_load(rna_info):
    file_path = "../Raw Data/POSTAR ClipDB/human_RBP_binding_sites_sorted.txt"
    return binary_search_populate(file_path, rna_info)
