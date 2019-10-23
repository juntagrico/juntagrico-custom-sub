import csv
import os
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from juntagrico import models as jm
from juntagrico_custom_sub import models as csm


class Command(BaseCommand):
    """
    Basecommand to insert data into the database from a csv file.
    To execute it, run python manage.py import_data path1 [path2, ...]
    The filename needs to be called table_name.csv, where table_name
    refers to a table either in Juntagrico or in Juntagrico_Custom_Sub
    """

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    @staticmethod
    def name_to_model(table_name):
        if hasattr(jm, table_name):
            return getattr(jm, table_name)
        elif hasattr(csm, table_name):
            return getattr(csm, table_name)
        else:
            raise ValueError(f'{table_name} could not be associated with a model')

    def resolve_foreign_keys(self, row):
        rv = {}
        for cell in row.items():
            if cell[1] == '':  # clean empty entries
                continue
            elif "[" in cell[0]:
                column, fk_relationship = cell[0].split("[")
                fk_table_name, fk_column = fk_relationship.split(".")
                fk_column = fk_column.strip("]")
                fk_table = self.name_to_model(fk_table_name)
                try:
                    related_object = fk_table.objects.get(**{fk_column: cell[1]})
                except fk_table.DoesNotExist:
                    raise ValueError(f'{cell[1]} not valid for {fk_column} in {fk_table}')
                except fk_table.MultipleObjectsReturned:
                    raise ValueError(f'{cell[1]} returned multiple items for {fk_column} in {fk_table}')
                except Exception:
                    raise ValueError(f'Problem with {fk_column} in {fk_table}, value is {cell[1]}')
                rv[column] = related_object
            else:
                rv[cell[0]] = cell[1]
        return rv

    def handle(self, *args, **options):
        for f in options['files']:
            table_name = os.path.basename(f).split('.')[0]
            table = self.name_to_model(table_name)
            with open(f, newline='', encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row = self.resolve_foreign_keys(row)
                    try:
                        table.objects.update_or_create(**row)
                    except IntegrityError:
                        print(f'{row} already in DB')
