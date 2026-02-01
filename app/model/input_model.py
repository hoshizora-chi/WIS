from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex
from datetime import datetime


class InputTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        # Example domain data (replace later)
        self.headers = ["Tgl/Hari", "Jam Mulai", "JP", "Agenda", "Nama WI"]
        self._data = [
            ["19-10-2026", "14:00", 3, "P1 - Pendidikan Pancasila", "Yeli"],
            ["15-10-2026", "13:00", 3, "P2 - Pendidikan Kewarganegaraan", "Busur"],
        ]
        self.delegates = {
            0: "date",
            1: "time",
            2: "int",
            4: "wi"
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
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        if col == 2 and not self.is_int(value):
            return False
        elif col == 1 and not self.is_time(value):
            return False
        elif col == 0 and not self.is_date(value):
            return False

        self._data[row][col] = value
        self.dataChanged.emit(index, index, [role])

        return True

    def insertRows(self, row, count=1, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)

        for _ in range(count):
            self._data.insert(row, self._empty_row())

        self.endInsertRows()
        return True

    def removeRows(self, row, count=1, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        for _ in range(count):
            del self._data[row]

        self.endRemoveRows()
        return True

    def _empty_row(self):
        res = []
        for i in range(0, len(self.headers)):
            res.append("")
        return res

    def to_json(self):
        return self._data

    def from_json(self, data):
        self.beginResetModel()
        self._data = data
        if len(data) == 0:
            self._data = [["" for i in range(0, len(self.headers))]]
        self.endResetModel()

    def clear(self):
        self.beginResetModel()
        self._data = [["" for i in range(0, len(self.headers))]]
        self.endResetModel()

    def is_date(self, text: str) -> bool:
        text = text.strip()
        try:
            # adjust format if needed
            datetime.strptime(text, "%d-%m-%Y")
            return True
        except ValueError:
            return False

    def is_time(self, text: str) -> bool:
        text = text.strip()
        try:
            datetime.strptime(text, "%H:%M")
            return True
        except ValueError:
            return False

    def is_int(self, text: str) -> bool:
        text = text.strip()
        if not text:
            return False
        try:
            int(text)
            return True
        except ValueError:
            return False

    def total_jp_for_name(self, name: str) -> int:
        total = 0
        for row in self._data:
            if row[4] == name:          # column 4 = Name
                total += int(row[2])    # column 2 = JP
        return total

    def update_wi_name(self, old_name, new_name):
        for i, row in enumerate(self._data):
            if row[4] == old_name:
                self._data[i][4] = new_name
                index = self.index(i, 4)
                self.dataChanged.emit(index, index, [Qt.EditRole])
