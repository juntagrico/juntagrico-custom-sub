import csv
import pytz
from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from juntagrico import models as jm

from juntagrico_custom_sub import models as csm


class Command(BaseCommand):
    """
    Basecommand to insert assigmenents from a csv file into the database.
    To execute it, run python manage.py import_data path1 [path2, ...]
    The filename needs to be called table_name.csv, where table_name
    refers to a table either in Juntagrico or in Juntagrico_Custom_Sub
    """
    migration_job_type = jm.JobType.objects.get(name='Vergangener Job')

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    def parse_row(self, row):
        if row['date'] == '2019':
            return None
        else:
            rv = {** row}
            time = datetime.strptime(row['date'], '%d/%m/%Y')
            time = time.replace(tzinfo=pytz.timezone('Europe/Zurich'))
            recurring_job = jm.RecuringJob.objects.filter(time=time, type=self.migration_job_type).first()
            if not recurring_job:
                recurring_job = jm.RecuringJob.objects.create(time=time, type=self.migration_job_type, slots=0)
            recurring_job.slots += 1
            recurring_job.save()
            rv['job_id'] = recurring_job.id
            rv['amount'] = 1
            del rv['date']
        return rv

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
            table = jm.Assignment
            with open(f, newline='', encoding="utf-8-sig") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    row = self.parse_row(row)
                    if row:
                        row = self.resolve_foreign_keys(row)
                        try:
                            table.objects.update_or_create(**row)
                        except IntegrityError:
                            print(f'{row} already in DB')
