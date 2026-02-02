from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex
from datetime import datetime


class RecapTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        # Example domain data (replace later)
        self.headers = ["-"]
        self._data = [
        ]
        self.delegates = {
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        value = self._data[index.row()][index.column()]

        if role in (Qt.DisplayRole, Qt.EditRole):
            return value

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.headers[section]

        return section + 1

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled

    def _empty_row(self):
        res = []
        for i in range(0, len(self.headers)):
            res.append("")
        return res

    def to_json(self):
        pass

    def from_json(self, data):
        self.clear()

    def clear(self):
        self.beginResetModel()
        self._data = [["" for i in range(0, len(self.headers))]]
        self.endResetModel()

    def get_wi_name(self, data):
        self.headers = [name for name, JP in data]
        if not self.headers:
            return

        self.headerDataChanged.emit(
            Qt.Horizontal,
            0,
            len(self.headers) - 1
        )

        self.headers.sort()
        self.headers = ["Tgl"] + self.headers

    def get_recap(self, data, data_wi):
        data_res = {
                name: [] for name, jp in data_wi
        }

        for row in data:
            if row[6] in data_res and\
               row[0] != "" and\
               row[4] != "" and\
               row[5] != "":
                data_res[row[6]].append([
                    str(row[0]),
                    str(row[4]),
                    str(row[5]),
                ])

        for name, item in data_res.items():
            item.sort(key=lambda r: datetime.strptime(r[0], "%d-%m-%Y"))

        all_dates = set()

        for items in data_res.values():
            for date, _, _ in items:
                all_dates.add(date)

        all_dates = sorted(
            all_dates,
            key=lambda d: datetime.strptime(d, "%d-%m-%Y")
        )

        lookup = {}
        for name, items in data_res.items():
            for date, v1, v2 in items:
                if (date, name) in lookup:
                    lookup[(date, name)] += " \n| " + v1 + " - " + v2
                else:
                    lookup[(date, name)] = "| " + v1 + " - " + v2

        names = sorted(data_res.keys())
        result = []
        for date in all_dates:
            row = [date]
            for name in names:
                row.append(lookup.get((date, name), "-"))
            result.append(row)

        self.beginResetModel()
        self._data = result
        self.endResetModel()
