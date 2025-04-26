import os
import pandas as pd
from django.conf import settings


class ExcelStorage:
    def __init__(self):
        self.storage_path = settings.EXCEL_STORAGE_PATH
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path)

        # Initialize Excel files if they don't exist
        self.label_name_file = os.path.join(
            self.storage_path, 'label_names.xlsx')
        self.label_lists_file = os.path.join(
            self.storage_path, 'label_lists.xlsx')

        if not os.path.exists(self.label_name_file):
            pd.DataFrame(columns=['labelName1', 'labelName2', 'labelName3', 'labelName4',
                                  'labelName5', 'labelName6', 'labelName7', 'labelName8',
                                  'labelName9']).to_excel(self.label_name_file, index=False)

        if not os.path.exists(self.label_lists_file):
            pd.DataFrame(columns=['imgName', 'label1', 'label2', 'label3', 'label4',
                                  'label5', 'label6', 'label7', 'label8', 'label9']).to_excel(self.label_lists_file, index=False)

    def save_label_name(self, **kwargs):
        df = pd.read_excel(self.label_name_file)
        new_row = pd.DataFrame([kwargs])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(self.label_name_file, index=False)

    def save_label_list(self, **kwargs):
        df = pd.read_excel(self.label_lists_file)
        new_row = pd.DataFrame([kwargs])
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_excel(self.label_lists_file, index=False)

    def get_all_label_names(self):
        return pd.read_excel(self.label_name_file).to_dict('records')

    def get_all_label_lists(self):
        return pd.read_excel(self.label_lists_file).to_dict('records')
