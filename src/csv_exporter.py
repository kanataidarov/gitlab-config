from collections import defaultdict
from printer_utils import Printer
from const import Roles

import csv


class CsvExporter: 
    """Utilities for exporting to csv.

    Attributes: 
        printer: Printer object from printer_utils.
        roles (dict): GitLab user roles.
    """

    def __init__(self):
        self.printer = Printer()
        self.roles = defaultdict(str)

    def csv_group_members(self, args, selected_group_ids, out_path="Members.csv"): 
        """Exports members of specified groups into csv. 
        :args Command Line arguments, includes defaults of optional arguments. 
        :selected_group_ids List of Ids for selected Gitlab Groups.
        :out_path Path to the output file in `csv` format.  
        """
        file = open(out_path, mode="w")
        writer = csv.writer(file, delimiter=";")
        for group_id in selected_group_ids: 
            members = self.printer.response_json(args, f'groups/{group_id}/pending_members')
            
            print(len(members))
            for member in members: 
                writer.writerow([member["username"], Roles.TABLE[int(member["access_level"])]])

        file.close()

