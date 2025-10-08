"""
This module provides the DataExport mixin class for exporting tabular data from Scrapxd models
to CSV and XLSX formats. It supports FilmList, EntryList and FilmSearch models,
handling nested structures and filename sanitization.
"""
import re
import csv
import logging
from typing import List, Dict, Any

# Get a logger instance for this module
log = logging.getLogger(__name__)

class DataExport:
    """
    Mixin class to add data export functionality to Scrapxd models.
    """
    def _normalize_filename(self, name: str) -> str:
        """
        Takes a string and sanitizes it to be a valid filename.
        Removes invalid characters and replaces spaces with underscores.
        """
        # Removes non-alphanumeric characters
        sanitized_name = re.sub(r'[^\w\s-]', '', name).strip()
        # Replaces whitespaces for an underscore
        sanitized_name = re.sub(r'[-\s]+', '_', sanitized_name)
        return sanitized_name.lower()

    def _get_filename(self, extension: str) -> str:
        """
        Generates a default, safe filename based on the object's attributes.
        """
        base_name = "export"

        if hasattr(self, 'title') and self.title:
            base_name = self.title
        elif hasattr(self, 'query') and self.query:
            base_name = self.query
        elif hasattr(self, 'username') and self.username:
            base_name = f"{self.username}"

        return f"{self._normalize_filename(base_name)}{extension}"
    
    def _get_export_data(self) -> List[Dict[str, Any]]:
        """
        Prepares and returns the data to be exported as a list of dictionaries.
        """
        from .models import FilmList, FilmSearchResult, EntryList

        if isinstance(self, (FilmList, FilmSearchResult)):
            dumped_data = self.model_dump()['films']
            for film_dict in dumped_data:
                film_dict.pop('fetcher', None)
            return dumped_data
        
        elif isinstance(self, EntryList):
            dumped_data = self.model_dump()['entries']
            flattened_data = []
            for entry in dumped_data:
                flat_item = {}
                film_data = entry.pop('film', {})
                film_data.pop('fetcher', None)

                for key, value in film_data.items():
                    flat_item[f"film_{key}"] = value
                
                flat_item.update(entry)
                flattened_data.append(flat_item)
            return flattened_data

        else:
            return []

    def to_csv(self, filename: str = "export", file_dir: str = None, filepath: str = None):
        """
        Exports the data to a CSV file.
        The method retrieves exportable data and writes it to a CSV file. The file path can be specified directly via `filepath`,
        or constructed using `filename` and `file_dir`. If no data is available, a warning is logged and the method returns.

        Args:
            filename (str, optional): The base name for the CSV file (without extension). Defaults to "export".
            file_dir (str, optional): The directory where the CSV file will be saved. If not provided, the file is saved in the current directory.
            filepath (str, optional): The full path to the CSV file. If provided, overrides `filename` and `file_dir`.

        Returns:
            None
        """
        data_to_export = self._get_export_data()
        if not data_to_export:
            log.warning("No data to export for the given model.")
            return

        if not filepath and not filename:
            filename = self._get_filename(extension=".csv")
        elif filepath:
            path = f"{filepath.replace(".csv", "")}.csv"
        else:
            path = f"{file_dir}/{filename.replace(".csv", "")}.csv" if file_dir else f"{filename.replace(".csv", "")}.csv"
        
        with open(path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=data_to_export[0].keys())
            
            writer.writeheader()
            writer.writerows(data_to_export)

    def to_xlsx(self, filename: str = "export", file_dir: str = None, filepath: str = None):
        """
        Exports the data to a XLSX file.
        The method retrieves exportable data and writes it to a XLSX file. The file path can be specified directly via `filepath`,
        or constructed using `filename` and `file_dir`. If no data is available, a warning is logged and the method returns.

        Args:
            filename (str, optional): The base name for the XLSX file (without extension). Defaults to "export".
            file_dir (str, optional): The directory where the XLSX file will be saved. If not provided, the file is saved in the current directory.
            filepath (str, optional): The full path to the XLSX file. If provided, overrides `filename` and `file_dir`.
            
        Returns:
            None
        """
        try:
            import openpyxl
        except ImportError:
            log.error("openpyxl is not installed. Please install it with `pip install scrapxd[export]` to use XLSX export functionality.")
            return

        data_to_export = self._get_export_data()
        if not data_to_export:
            log.warning("No data to export for the given model.")
            return
        
        if not filepath and not filename:
            filename = self._get_filename(extension=".xlsx")
        elif filepath:
            path = f"{filepath.replace(".xlsx", "")}.xlsx"
        else:
            path = f"{file_dir}/{filename.replace(".xlsx", "")}.xlsx" if file_dir else f"{filename.replace(".xlsx", "")}.xlsx"
        
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        
        headers = list(data_to_export[0].keys())
        sheet.append(headers)

        for item in data_to_export:
            row_values = []
            for header in headers:
                value = item.get(header, "")
                # If value is a list or dict, convert to string
                if isinstance(value, (list, dict)):
                    # ['A', 'B'] -> "A, B"
                    # {'a': 1} -> "{'a': 1}"
                    row_values.append(str(value))
                else:
                    row_values.append(value)
            sheet.append(row_values)

        workbook.save(path)
        workbook.close()