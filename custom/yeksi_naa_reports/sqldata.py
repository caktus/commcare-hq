# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from collections import defaultdict
from sqlagg.columns import SumColumn, MaxColumn, SimpleColumn
from sqlagg.filters import EQ, BETWEEN
from corehq.apps.reports.datatables import DataTablesColumn, DataTablesHeader
from corehq.apps.userreports.util import get_table_name
from corehq.apps.reports.sqlreport import DatabaseColumn, SqlData
from custom.yeksi_naa_reports.utils import YEKSI_NAA_REPORTS_VISITE_DE_L_OPERATOUR, \
    YEKSI_NAA_REPORTS_VISITE_DE_L_OPERATOUR_PER_PRODUCT, YEKSI_NAA_REPORTS_LOGISTICIEN
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from django.utils.functional import cached_property
from memoized import memoized
from six.moves import range


class YeksiSqlData(SqlData):
    datatables = False
    show_charts = False
    show_total = True
    custom_total_calculate = False
    no_value = {'sort_key': 0, 'html': 0}
    fix_left_col = False

    @property
    def engine_id(self):
        return 'ucr'

    def percent_fn(self, x, y):
        return "{:.2f}%".format(100 * float(x or 0) / float(y or 1))

    @property
    @memoized
    def months(self):
        return [month.date() for month in
                rrule(freq=MONTHLY, dtstart=self.config['startdate'], until=self.config['enddate'])]

    def date_in_selected_date_range(self, date):
        return self.months[0] <= date < self.months[-1] + relativedelta(months=1)

    def denominator_exists(self, denominator):
        return denominator and denominator['html']

    def get_index_of_month_in_selected_data_range(self, date):
        for index in range(len(self.months)):
            if date < self.months[index] + relativedelta(months=1):
                return index

    def month_headers(self):
        month_headers = []
        french_months = {
            1: 'Janvier',
            2: 'Février',
            3: 'Mars',
            4: 'Avril',
            5: 'Mai',
            6: 'Juin',
            7: 'Juillet',
            8: 'Août',
            9: 'Septembre',
            10: 'Octobre',
            11: 'Novembre',
            12: 'Décembre',
        }
        for month in self.months:
            month_headers.append(DataTablesColumn("{0} {1}".format(french_months[month.month], month.year)))
        return month_headers


class VisiteDeLOperateurDataSource(YeksiSqlData):

    @property
    def filters(self):
        filters = [BETWEEN("real_date", "startdate", "enddate")]
        if 'region_id' in self.config and self.config['region_id']:
            filters.append(EQ("region_id", "region_id"))
        elif 'district_id' in self.config and self.config['district_id']:
            filters.append(EQ("district_id", "district_id"))
        elif 'pps_id' in self.config and self.config['pps_id']:
            filters.append(EQ("pps_id", "pps_id"))
        return filters

    @property
    def table_name(self):
        return get_table_name(self.config['domain'], YEKSI_NAA_REPORTS_VISITE_DE_L_OPERATOUR)

    @cached_property
    def loc_id(self):
        if 'pps_id' in self.config or 'district_id' in self.config:
            return 'pps_id'
        elif 'region_id' in self.config:
            return 'district_id'
        else:
            return 'region_id'

    @cached_property
    def loc_name(self):
        if 'pps_id' in self.config or 'district_id' in self.config:
            return 'pps_name'
        elif 'region_id' in self.config:
            return 'district_name'
        else:
            return 'region_name'

    @property
    def headers(self):
        if self.loc_id == 'pps_id':
            first_row = 'PPS'
        elif self.loc_id == 'district_id':
            first_row = 'District'
        else:
            first_row = 'Région'

        headers = DataTablesHeader(DataTablesColumn(first_row))
        for month in self.month_headers():
            headers.add_column(month)
        return headers


class VisiteDeLOperateurPerProductDataSource(YeksiSqlData):

    @property
    def filters(self):
        filters = [BETWEEN("real_date_repeat", "startdate", "enddate")]
        if 'region_id' in self.config and self.config['region_id']:
            filters.append(EQ("region_id", "region_id"))
        elif 'district_id' in self.config and self.config['district_id']:
            filters.append(EQ("district_id", "district_id"))
        elif 'pps_id' in self.config and self.config['pps_id']:
            filters.append(EQ("pps_id", "pps_id"))
        return filters

    @property
    def table_name(self):
        return get_table_name(self.config['domain'], YEKSI_NAA_REPORTS_VISITE_DE_L_OPERATOUR_PER_PRODUCT)

    @cached_property
    def loc_id(self):
        if 'pps_id' in self.config or 'district_id' in self.config:
            return 'pps_id'
        elif 'region_id' in self.config:
            return 'district_id'
        else:
            return 'region_id'

    @cached_property
    def loc_name(self):
        if 'pps_id' in self.config or 'district_id' in self.config:
            return 'pps_name'
        elif 'region_id' in self.config:
            return 'district_name'
        else:
            return 'region_name'

    @property
    def headers(self):
        if self.loc_id == 'pps_id':
            first_row = 'PPS'
        elif self.loc_id == 'district_id':
            first_row = 'District'
        else:
            first_row = 'Région'

        headers = DataTablesHeader(DataTablesColumn(first_row))
        for month in self.month_headers():
            headers.add_column(month)
        return headers


class LogisticienDataSource(YeksiSqlData):

    @property
    def filters(self):
        filters = [BETWEEN("date_echeance", "startdate", "enddate")]
        if 'region_id' in self.config and self.config['region_id']:
            filters.append(EQ("region_id", "region_id"))
        elif 'district_id' in self.config and self.config['district_id']:
            filters.append(EQ("district_id", "district_id"))
        return filters

    @property
    def table_name(self):
        return get_table_name(self.config['domain'], YEKSI_NAA_REPORTS_LOGISTICIEN)

    @cached_property
    def loc_id(self):
        if 'region_id' in self.config:
            return 'district_id'
        else:
            return 'region_id'

    @cached_property
    def loc_name(self):
        if 'region_id' in self.config:
            return 'district_name'
        else:
            return 'region_name'

    @property
    def headers(self):
        if self.loc_id == 'district_id':
            first_row = 'District'
        else:
            first_row = 'Région'

        headers = DataTablesHeader(DataTablesColumn(first_row))
        for month in self.month_headers():
            headers.add_column(month)
        return headers


class AvailabilityData(VisiteDeLOperateurDataSource):
    slug = 'disponibilité'
    comment = 'Disponibilité de la gamme au niveau PPS : combien de PPS ont eu tous les produits disponibles'
    title = 'Disponibilité'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, rows):
        total_row = ['Disponibilité (%)']
        total_numerator = 0
        total_denominator = 0
        if self.loc_id == 'pps_id':
            data = {}
            for i in range(len(self.months)):
                data[i] = {
                    'pps_is_available': sum(
                        1 for pps_data in rows if pps_data[i + 1] == '100%'
                    ),
                    'pps_count': sum(1 for pps_data in rows
                                     if pps_data[i + 1] != 'pas de données')
                }
                if data[i]['pps_count']:
                    total_row.append(
                        self.percent_fn(
                            data[i]['pps_is_available'],
                            data[i]['pps_count']
                        )
                    )
                else:
                    total_row.append('pas de données')
                total_numerator += data[i]['pps_is_available']
                total_denominator += data[i]['pps_count']

            if total_denominator:
                total_row.append(
                    self.percent_fn(
                        total_numerator,
                        total_denominator
                    )
                )
            else:
                total_row.append('pas de données')
        else:
            for i in range(len(self.months)):
                numerator = 0
                denominator = 0
                for location in rows:
                    numerator += sum(rows[location][i].values())
                    denominator += len(rows[location][i])
                total_numerator += numerator
                total_denominator += denominator
                if denominator:
                    total_row.append(self.percent_fn(numerator, denominator))
                else:
                    total_row.append('pas de données')
            if total_denominator:
                total_row.append(self.percent_fn(total_numerator, total_denominator))
            else:
                total_row.append('pas de données')
        return total_row

    @property
    def group_by(self):
        group_by = ['real_date', 'pps_id', self.loc_name]
        if self.loc_id != 'pps_id':
            group_by.append(self.loc_id)
        return group_by

    @property
    def columns(self):
        columns = [
            DatabaseColumn("PPS ID", SimpleColumn('pps_id')),
            DatabaseColumn("Date", SimpleColumn('real_date')),
            DatabaseColumn("Number of PPS with stockout", MaxColumn('pps_is_outstock')),
        ]
        if self.loc_id == 'pps_id':
            columns.append(DatabaseColumn("PPS Name", SimpleColumn('pps_name')))
        elif self.loc_id == 'district_id':
            columns.append(DatabaseColumn("District ID", SimpleColumn('district_id')))
            columns.append(DatabaseColumn("District Name", SimpleColumn('district_name')))
        else:
            columns.append(DatabaseColumn("Region ID", SimpleColumn('region_id')))
            columns.append(DatabaseColumn("Region Name", SimpleColumn('region_name')))
        return columns

    def get_availability_data_per_month_per_pps(self, records):
        data = {}
        loc_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date']):
                continue
            if record[self.loc_id] not in data:
                data[record[self.loc_id]] = ['pas de données'] * len(self.months)
                loc_names[record[self.loc_id]] = record[self.loc_name]
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date'])
            data[record[self.loc_id]][month_index] = '0%' if record['pps_is_outstock']['html'] == 1 else '100%'
        return loc_names, data

    def get_availability_data_per_month_aggregated(self, records):
        data = defaultdict(list)
        loc_names = {}
        new_data = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date']):
                continue
            if record[self.loc_id] not in data:
                for i in range(len(self.months)):
                    data[record[self.loc_id]].append(defaultdict(int))
                loc_names[record[self.loc_id]] = record[self.loc_name]
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date'])
            multiple_rows_per_pps_in_month = data[record[self.loc_id]][month_index].get(record['pps_id'])
            if not multiple_rows_per_pps_in_month or \
                    data[record[self.loc_id]][month_index][record['pps_id']] == 1:
                data[record[self.loc_id]][month_index][record['pps_id']] = 0 if \
                    record['pps_is_outstock']['html'] == 1 else 1

        for location in data:
            new_data[location] = ['pas de données'] * len(self.months)
            for month_index in range(len(self.months)):
                if data[location][month_index]:
                    new_data[location][month_index] = self.percent_fn(
                        sum(data[location][month_index].values()),
                        len(data[location][month_index])
                    )
        return loc_names, new_data, data

    def get_average_availability_in_location(self, data_per_localization):
        numerator = 0
        denominator = 0
        for data_in_month in data_per_localization:
            if data_in_month and data_in_month != 'pas de données':
                if self.loc_id == 'pps_id':
                    if data_in_month == '100%':
                        numerator += 1
                else:
                    numerator += float(data_in_month[:-1])
                denominator += 1
        if denominator:
            if self.loc_id == 'pps_id':
                return "{:.2f}%".format(numerator * 100 / denominator)
            else:
                return "{:.2f}%".format(numerator / denominator)
        else:
            return 'pas de données'

    def parse_availability_data_to_rows(self, loc_names, data):
        rows = []
        for loc_id in data:
            row = [loc_names[loc_id]]
            row.extend(data[loc_id])
            row.append(self.get_average_availability_in_location(data[loc_id]))
            rows.append(row)
        return rows

    @property
    def rows(self):
        records = self.get_data()

        if self.loc_id == 'pps_id':
            loc_names, data = self.get_availability_data_per_month_per_pps(records)
        else:
            loc_names, data, tmp = self.get_availability_data_per_month_aggregated(records)
            self.total_row = self.calculate_total_row(tmp)

        rows = self.parse_availability_data_to_rows(loc_names, data)
        if self.loc_id == 'pps_id':
            self.total_row = self.calculate_total_row(rows)
        return rows

    @property
    def headers(self):
        headers = super(AvailabilityData, self).headers
        headers.add_column(DataTablesColumn('Taux moyen de disponibilité'))
        return headers


class LossRateData(VisiteDeLOperateurPerProductDataSource):
    slug = 'taux_de_perte'
    comment = 'Taux de Perte (hors péremption)'
    title = 'Taux de Perte (hors péremption)'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, records):
        total_row = []
        data = defaultdict(lambda: defaultdict(int))
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if self.denominator_exists(record['final_pna_stock']):
                data[month_index]['final_pna_stock'] += record['final_pna_stock']['html']
                if record['loss_amt']:
                    data[month_index]['loss_amt'] += record['loss_amt']['html']

        if 'region_id' in self.config and self.config['region_id']:
            total_row.append('Taux par Région')
        elif 'district_id' in self.config and self.config['district_id']:
            total_row.append('Taux par District')
        elif 'pps_id' in self.config and self.config['pps_id']:
            total_row.append('')
        else:
            total_row.append('Taux par Pays')
        for month_index in range(len(self.months)):
            if data[month_index]:
                total_row.append(
                    self.percent_fn(
                        data[month_index]['loss_amt'],
                        data[month_index]['final_pna_stock']
                    )
                )
            else:
                total_row.append('pas de données')
        return total_row

    @property
    def group_by(self):
        return ['real_date_repeat', self.loc_id, self.loc_name]

    @property
    def columns(self):
        columns = [
            DatabaseColumn("Date", SimpleColumn('real_date_repeat')),
            DatabaseColumn("Total number of PNA lost product", SumColumn('loss_amt')),
            DatabaseColumn("PNA final stock", SumColumn('final_pna_stock')),
        ]
        if self.loc_id == 'pps_id':
            columns.append(DatabaseColumn("PPS ID", SimpleColumn('pps_id')))
            columns.append(DatabaseColumn("PPS Name", SimpleColumn('pps_name')))
        elif self.loc_id == 'district_id':
            columns.append(DatabaseColumn("District ID", SimpleColumn('district_id')))
            columns.append(DatabaseColumn("District Name", SimpleColumn('district_name')))
        else:
            columns.append(DatabaseColumn("Region ID", SimpleColumn('region_id')))
            columns.append(DatabaseColumn("Region Name", SimpleColumn('region_name')))
        return columns

    def get_loss_rate_per_month(self, records):
        data = {}
        loc_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            if record[self.loc_id] not in data:
                data[record[self.loc_id]] = ['pas de données'] * len(self.months)
                loc_names[record[self.loc_id]] = record[self.loc_name]
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if self.denominator_exists(record['final_pna_stock']):
                data[record[self.loc_id]][month_index] = self.percent_fn(
                    record['loss_amt']['html'] if record['loss_amt'] else 0,
                    record['final_pna_stock']['html']
                )
        return loc_names, data

    @property
    def rows(self):
        records = self.get_data()
        loc_names, data = self.get_loss_rate_per_month(records)
        rows = []
        for loc_id in data:
            row = [loc_names[loc_id]]
            row.extend(data[loc_id])
            rows.append(row)
        self.total_row = self.calculate_total_row(records)
        return rows

    @property
    def headers(self):
        headers = super(LossRateData, self).headers
        return headers


class ExpirationRateData(VisiteDeLOperateurPerProductDataSource):
    slug = 'taux_de_péremption'
    comment = 'Valorisation des produits périmés PNA'
    title = 'Taux de Péremption'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, records):
        total_row = []
        data = {}
        for i in range(len(self.months)):
            data[i] = {
                'expired_pna_valuation': 0,
                'final_pna_stock_valuation': 0
            }
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if self.denominator_exists(record['final_pna_stock_valuation']):
                if record['expired_pna_valuation']:
                    data[month_index]['expired_pna_valuation'] += record['expired_pna_valuation']['html']
                data[month_index]['final_pna_stock_valuation'] += record['final_pna_stock_valuation']['html']

        if 'region_id' in self.config and self.config['region_id']:
            total_row.append('Taux par Région')
        elif 'district_id' in self.config and self.config['district_id']:
            total_row.append('Taux par District')
        elif 'pps_id' in self.config and self.config['pps_id']:
            total_row.append('')
        else:
            total_row.append('Taux par Pays')
        for monthly_data in data.values():
            total_row.append(
                self.percent_fn(
                    monthly_data['expired_pna_valuation'],
                    monthly_data['final_pna_stock_valuation']
                )
            )
        return total_row

    @property
    def group_by(self):
        return ['real_date_repeat', self.loc_id, self.loc_name]

    @property
    def columns(self):
        columns = [
            DatabaseColumn("Date", SimpleColumn('real_date_repeat')),
            DatabaseColumn("Expired products valuation", SumColumn('expired_pna_valuation')),
            DatabaseColumn("Products stock valuation", SumColumn('final_pna_stock_valuation')),
        ]
        if self.loc_id == 'pps_id':
            columns.append(DatabaseColumn("PPS ID", SimpleColumn('pps_id')))
            columns.append(DatabaseColumn("PPS Name", SimpleColumn('pps_name')))
        elif self.loc_id == 'district_id':
            columns.append(DatabaseColumn("District ID", SimpleColumn('district_id')))
            columns.append(DatabaseColumn("District Name", SimpleColumn('district_name')))
        else:
            columns.append(DatabaseColumn("Region ID", SimpleColumn('region_id')))
            columns.append(DatabaseColumn("Region Name", SimpleColumn('region_name')))
        return columns

    def get_expiration_rate_per_month(self, records):
        data = {}
        loc_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            if record[self.loc_id] not in data:
                data[record[self.loc_id]] = ['pas de données'] * len(self.months)
                loc_names[record[self.loc_id]] = record[self.loc_name]
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if self.denominator_exists(record['final_pna_stock_valuation']):
                data[record[self.loc_id]][month_index] = self.percent_fn(
                    record['expired_pna_valuation']['html'] if record['expired_pna_valuation'] else None,
                    record['final_pna_stock_valuation']['html']
                )
        return loc_names, data

    @property
    def rows(self):
        records = self.get_data()
        loc_names, data = self.get_expiration_rate_per_month(records)

        rows = []
        for loc_id in data:
            row = [loc_names[loc_id]]
            row.extend(data[loc_id])
            rows.append(row)
        self.total_row = self.calculate_total_row(records)
        return rows

    @property
    def headers(self):
        headers = super(ExpirationRateData, self).headers
        return headers


class RecoveryRateByPPSData(VisiteDeLOperateurDataSource):
    slug = 'taux_de_recouvrement_au_niveau_du_pps'
    comment = 'Somme des montants payés sur total dû'
    title = 'Taux de Recouvrement au niveau du PPS'
    show_total = True
    custom_total_calculate = True

    def get_total_row(self, data):
        total_row = []
        if 'district_id' in self.config and self.config['district_id']:
            total_row.append('Taux par District')
        elif 'pps_id' in self.config and self.config['pps_id']:
            total_row.append('Taux par PPS')
        elif 'region_id' in self.config and self.config['region_id']:
            total_row.append('Taux par Région')
        else:
            total_row.append('Taux par Pays')
        for i in range(len(self.months)):
            total_row.append(self.percent_fn(
                sum(
                    data[loc_id][i]['pps_total_amt_paid'] for loc_id in data if
                    data[loc_id][i]['pps_total_amt_owed']
                ),
                sum(
                    data[loc_id][i]['pps_total_amt_owed'] for loc_id in data if
                    data[loc_id][i]['pps_total_amt_owed']
                )
            ))
        return total_row

    @property
    def group_by(self):
        group_by = ['real_date', 'pps_id', self.loc_name, 'pps_total_amt_paid', 'pps_total_amt_owed']
        if self.loc_id != 'pps_id':
            group_by.append(self.loc_id)
        return group_by

    @property
    def columns(self):
        columns = [
            DatabaseColumn("PPS ID", SimpleColumn('pps_id')),
            DatabaseColumn("Date", SimpleColumn('real_date')),
            DatabaseColumn("Total amount paid by PPS", SimpleColumn('pps_total_amt_paid')),
            DatabaseColumn("Total amount owed by PPS", SimpleColumn('pps_total_amt_owed')),
        ]
        if self.loc_id == 'pps_id':
            columns.append(DatabaseColumn("PPS Name", SimpleColumn('pps_name')))
        elif self.loc_id == 'district_id':
            columns.append(DatabaseColumn("District ID", SimpleColumn('district_id')))
            columns.append(DatabaseColumn("District Name", SimpleColumn('district_name')))
        else:
            columns.append(DatabaseColumn("Region ID", SimpleColumn('region_id')))
            columns.append(DatabaseColumn("Region Name", SimpleColumn('region_name')))
        return columns

    def get_recovery_rate_by_pps_per_month(self, records):
        data = defaultdict(list)
        loc_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date']):
                continue
            if record[self.loc_id] not in data:
                for i in range(len(self.months)):
                    data[record[self.loc_id]].append(defaultdict(int))
                loc_names[record[self.loc_id]] = record[self.loc_name]
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date'])
            if record['pps_total_amt_owed']:
                if record['pps_total_amt_paid']:
                    data[record[self.loc_id]][month_index]['pps_total_amt_paid'] += record['pps_total_amt_paid']
                data[record[self.loc_id]][month_index]['pps_total_amt_owed'] += record['pps_total_amt_owed']
        return loc_names, data

    def parse_recovery_rate_by_pps_to_rows(self, loc_name, data):
        row = [loc_name]
        for i in range(len(self.months)):
            if data[i]['pps_total_amt_owed']:
                row.append(
                    self.percent_fn(
                        data[i]['pps_total_amt_paid'],
                        data[i]['pps_total_amt_owed']
                    )
                )
            else:
                row.append('pas de données')
        return row

    @property
    def rows(self):
        records = self.get_data()
        loc_names, data = self.get_recovery_rate_by_pps_per_month(records)

        rows = []
        for loc_id in data:
            rows.append(
                self.parse_recovery_rate_by_pps_to_rows(loc_names[loc_id], data[loc_id])
            )

        self.total_row = self.get_total_row(data)
        return rows

    @property
    def headers(self):
        return super(RecoveryRateByPPSData, self).headers


class RecoveryRateByDistrictData(LogisticienDataSource):
    slug = 'taux_de_recouvrement_au_niveau_du_district'
    comment = 'Somme des montants payés sur total dû'
    title = 'Taux de Recouvrement au niveau du District'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, records):
        total_row = []
        data = {}
        for i in range(len(self.months)):
            data[i] = {
                'montant_paye': 0,
                'montant_reel_a_payer': 0
            }
        for record in records:
            if not self.date_in_selected_date_range(record['date_echeance']):
                continue
            month_index = self.get_index_of_month_in_selected_data_range(record['date_echeance'])
            if self.denominator_exists(record['montant_reel_a_payer']):
                if record['montant_paye']:
                    data[month_index]['montant_paye'] += record['montant_paye']['html']
                data[month_index]['montant_reel_a_payer'] += record['montant_reel_a_payer']['html']

        if 'region_id' in self.config and self.config['region_id']:
            total_row.append('Taux par Région')
        elif 'district_id' in self.config and self.config['district_id']:
            total_row.append('Taux par District')
        else:
            total_row.append('Taux par Pays')
        for monthly_data in data.values():
            total_row.append(
                self.percent_fn(
                    monthly_data['montant_paye'],
                    monthly_data['montant_reel_a_payer']
                )
            )
        return total_row

    @property
    def group_by(self):
        return ['date_echeance', 'district_id', 'district_name']

    @property
    def columns(self):
        columns = [
            DatabaseColumn("District ID", SimpleColumn('district_id')),
            DatabaseColumn("District Name", SimpleColumn('district_name')),
            DatabaseColumn("Date", SimpleColumn('date_echeance')),
            DatabaseColumn("Sum of the amounts paid by the district", SumColumn('montant_paye')),
            DatabaseColumn("Total amount owed by the district to PNA", SumColumn('montant_reel_a_payer')),
        ]
        return columns

    def get_recovery_rate_by_district_per_month(self, records):
        data = {}
        district_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['date_echeance']):
                continue
            if record['district_id'] not in data:
                data[record['district_id']] = ['pas de données'] * len(self.months)
                district_names[record['district_id']] = record['district_name']
            month_index = self.get_index_of_month_in_selected_data_range(record['date_echeance'])
            if self.denominator_exists(record['montant_reel_a_payer']):
                data[record['district_id']][month_index] = self.percent_fn(
                    record['montant_paye']['html'] if record['montant_paye'] else None,
                    record['montant_reel_a_payer']['html']
                )
        return district_names, data

    @property
    def rows(self):
        records = self.get_data()
        district_names, data = self.get_recovery_rate_by_district_per_month(records)

        rows = []
        for district in data:
            row = [district_names[district]]
            row.extend(data[district])
            rows.append(row)
        self.total_row = self.calculate_total_row(records)
        return rows

    @property
    def headers(self):
        headers = super(RecoveryRateByDistrictData, self).headers
        return headers


class RuptureRateByPPSData(VisiteDeLOperateurDataSource):
    slug = 'taux_de_rupture_par_pps'
    comment = 'Nombre de produits en rupture sur le nombre total de produits du PPS'
    title = 'Taux de Rupture par PPS'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, records):
        total_row = []
        data = {}
        for i in range(len(self.months)):
            data[i] = {
                'nb_products_stockout': 0,
                'count_products_select': 0
            }
        for record in records:
            if not self.date_in_selected_date_range(record['real_date']):
                continue
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date'])
            if record['count_products_select']:
                if record['nb_products_stockout']:
                    data[month_index]['nb_products_stockout'] += record['nb_products_stockout']
                data[month_index]['count_products_select'] += record['count_products_select']

        if 'region_id' in self.config and self.config['region_id']:
            total_row.append('Taux par Région')
        elif 'district_id' in self.config and self.config['district_id']:
            total_row.append('Taux par District')
        elif 'pps_id' in self.config and self.config['pps_id']:
            total_row.append('')
        else:
            total_row.append('Taux par Pays')
        for monthly_data in data.values():
            total_row.append(
                self.percent_fn(
                    monthly_data['nb_products_stockout'],
                    monthly_data['count_products_select']
                )
            )
        return total_row

    @property
    def group_by(self):
        return ['real_date', 'pps_id', 'pps_name', 'nb_products_stockout', 'count_products_select']

    @property
    def columns(self):
        columns = [
            DatabaseColumn("PPS ID", SimpleColumn('pps_id')),
            DatabaseColumn("PPS Name", SimpleColumn('pps_name')),
            DatabaseColumn("Date", SimpleColumn('real_date')),
            DatabaseColumn("Number of stockout products", SimpleColumn('nb_products_stockout')),
            DatabaseColumn("Number of products in pps", SimpleColumn('count_products_select')),
        ]
        return columns

    @property
    def rows(self):
        records = self.get_data()
        data = {}
        pps_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date']):
                continue
            if record['pps_id'] not in data:
                data[record['pps_id']] = ['pas de données'] * len(self.months)
                pps_names[record['pps_id']] = record['pps_name']
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date'])
            if record['count_products_select']:
                data[record['pps_id']][month_index] = self.percent_fn(
                    record['nb_products_stockout'],
                    record['count_products_select']
                )

        rows = []
        for pps in data:
            row = [pps_names[pps]]
            row.extend(data[pps])
            rows.append(row)
        self.total_row = self.calculate_total_row(records)
        return rows

    @cached_property
    def loc_id(self):
        return 'pps_id'

    @property
    def headers(self):
        headers = super(RuptureRateByPPSData, self).headers
        return headers


class SatisfactionRateAfterDeliveryData(VisiteDeLOperateurPerProductDataSource):
    slug = 'taux_de_satisfaction_après_livraison'
    comment = '% de produits commandés vs. deliverés'
    title = 'Taux de satisfaction (après livraison)'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, products):
        total_row = ['Total (CFA)']
        for i in range(len(self.months)):
            total_row.append(self.percent_fn(
                sum(
                    products[product_id][i]['amt_delivered_convenience'] for product_id in products if
                    products[product_id][i]['ideal_topup']
                ),
                sum(
                    products[product_id][i]['ideal_topup'] for product_id in products if
                    products[product_id][i]['ideal_topup']
                )
            ))
        return total_row

    @property
    def group_by(self):
        return ['real_date_repeat', 'product_id', 'product_name']

    @property
    def columns(self):
        columns = [
            DatabaseColumn("Date", SimpleColumn('real_date_repeat')),
            DatabaseColumn("Product ID", SimpleColumn('product_id')),
            DatabaseColumn("Product Name", SimpleColumn('product_name')),
            DatabaseColumn("Quantity of the product delivered", SumColumn('amt_delivered_convenience')),
            DatabaseColumn("Quantity of the product  suggested", SumColumn('ideal_topup')),
        ]
        return columns

    def get_product_satisfaction_rate_per_month(self, records):
        data = defaultdict(list)
        product_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            if record['product_id'] not in data:
                for i in range(len(self.months)):
                    data[record['product_id']].append(defaultdict(int))
                product_names[record['product_id']] = record['product_name']
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if self.denominator_exists(record['ideal_topup']):
                if record['amt_delivered_convenience']:
                    data[record['product_id']][month_index]['amt_delivered_convenience'] += \
                        record['amt_delivered_convenience']['html']
                data[record['product_id']][month_index]['ideal_topup'] += record['ideal_topup']['html']
        return product_names, data

    def parse_satisfaction_rate_to_rows(self, product_names, data):
        rows = []
        for product_id in data:
            row = [product_names[product_id]]
            for i in range(len(self.months)):
                if data[product_id][i]['ideal_topup']:
                    row.append(
                        self.percent_fn(data[product_id][i]['amt_delivered_convenience'],
                                        data[product_id][i]['ideal_topup'])
                    )
                else:
                    row.append('pas de données')
            rows.append(row)
        return rows

    @property
    def rows(self):
        records = self.get_data()
        product_names, data = self.get_product_satisfaction_rate_per_month(records)
        self.total_row = self.calculate_total_row(data)
        return self.parse_satisfaction_rate_to_rows(product_names, data)

    @property
    def headers(self):
        headers = DataTablesHeader(DataTablesColumn('Produit'))
        for month in self.month_headers():
            headers.add_column(month)
        return headers


class ValuationOfPNAStockPerProductData(VisiteDeLOperateurPerProductDataSource):
    slug = 'valeur_des_stocks_pna_disponible_chaque_produit'
    comment = 'Valeur des stocks PNA disponible (chaque produit)'
    title = 'Valeur des stocks PNA disponible (chaque produit)'
    show_total = True
    custom_total_calculate = True

    def calculate_total_row(self, records):
        total_row = []
        data = defaultdict(int)
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if record['final_pna_stock_valuation']:
                data[month_index] += record['final_pna_stock_valuation']['html']

        total_row.append('Total (CFA)')
        for month_index in range(len(self.months)):
            if data[month_index]:
                total_row.append(
                    '{:.2f}'.format(data[month_index])
                )
            else:
                total_row.append('pas de données')
        return total_row

    @property
    def group_by(self):
        return ['real_date_repeat', 'product_id', 'product_name']

    @property
    def columns(self):
        columns = [
            DatabaseColumn("Date", SimpleColumn('real_date_repeat')),
            DatabaseColumn("Product ID", SimpleColumn('product_id')),
            DatabaseColumn("Product Name", SimpleColumn('product_name')),
            DatabaseColumn("Products stock valuation", SumColumn('final_pna_stock_valuation')),
        ]
        return columns

    def get_product_valuation_of_pna_stock_per_month(self, records):
        data = {}
        product_names = {}
        for record in records:
            if not self.date_in_selected_date_range(record['real_date_repeat']):
                continue
            if record['product_id'] not in data:
                data[record['product_id']] = [0] * len(self.months)
                product_names[record['product_id']] = record['product_name']
            month_index = self.get_index_of_month_in_selected_data_range(record['real_date_repeat'])
            if record['final_pna_stock_valuation']:
                data[record['product_id']][month_index] += record['final_pna_stock_valuation']['html']
        return product_names, data

    @property
    def rows(self):
        records = self.get_data()
        product_names, data = self.get_product_valuation_of_pna_stock_per_month(records)

        rows = []
        for product_id in data:
            row = [product_names[product_id]]
            row.extend(['{:.2f}'.format(float(value)) for value in data[product_id]])
            rows.append(row)
        self.total_row = self.calculate_total_row(records)
        return rows

    @property
    def headers(self):
        headers = DataTablesHeader(DataTablesColumn('Produit'))
        for month in self.month_headers():
            headers.add_column(month)
        return headers
