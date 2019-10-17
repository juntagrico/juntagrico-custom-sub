import csv
import os
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('files', nargs='+', type=str)

    @staticmethod
    def clean_row(row):
        item1 = {** row}
        rv = []
        prod = row['product[Product.name]']
        amount = row['amount']
        if amount == '0':  # clean empty entries
            return []

        if prod == "Käserei fix":
            small = int(amount) % 2
            large = int(amount) // 2  # in juntagrico, a large Wochenkäse counts as 2 units
            if large:
                item1['product[Product.name]'] = "Wochenkäse gross"
                item1['amount'] = large
                rv.append(item1)
            if small:
                item2 = {**item1}
                item2['product[Product.name]'] = "Wochenkäse klein"
                item2['amount'] = small
                rv.append(item2)

        elif prod == "Käse":
            item1['product[Product.name]'] = "Zusatzkäse"
            rv.append(item1)

        else:
            rv.append(item1)
        return rv

    def handle(self, *args, **options):

        for f in options['files']:
            dir_name = os.path.dirname(os.path.abspath(f))
            out_file_name = os.path.join(dir_name, 'SubscriptionContentItem.csv')
            out_file = open(out_file_name, 'w', newline='')
            with open(f, newline='', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile)
                writer = csv.DictWriter(out_file, reader.fieldnames)
                writer.writeheader()
                for row in reader:
                    rows = self.clean_row(row)
                    for r in rows:
                        writer.writerow(r)
            out_file.close()
