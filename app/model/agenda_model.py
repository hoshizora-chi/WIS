from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex


class AgendaTableModel(QAbstractTableModel):
    def __init__(self):
        super().__init__()

        # Example domain data (replace later)
        self.headers = ["Agenda", "Pelatihan"]
        self._data = [
            ["P1", "Pendidikan Kewarganegaraan"],
            ["P2", "Pendidikan Pancasila"]
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
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            self._input_error = None
            return False

        row = index.row()
        col = index.column()

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
