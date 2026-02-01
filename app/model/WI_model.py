from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal


class WITableModel(QAbstractTableModel):
    nameChanged = Signal(str, str)
    WIChanged = Signal()

    def __init__(self, input_model):
        super().__init__()

        # Example domain data (replace later)
        self.headers = ["Nama", "JP"]
        self._data = [
            ["Yeli", 2],
            ["Busur", 5],
        ]
        self.delegates = {
        }

        self.input_model = input_model

        self.input_model.dataChanged.connect(self.recalculate)
        self.input_model.rowsInserted.connect(self.recalculate)
        self.input_model.rowsRemoved.connect(self.recalculate)
        self.input_model.modelReset.connect(self.recalculate)
        self.recalculate()

    def recalculate(self, *args):
        for row in self._data:
            name = row[0]
            row[1] = self.input_model.total_jp_for_name(name)

        self.beginResetModel()
        self.endResetModel()

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        if index.column() == 1:
            flags &= ~Qt.ItemIsEditable

        return flags

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

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            self._input_error = None
            return False

        row = index.row()
        col = index.column()

        if col == 0:  # "Nama" column
            new_name = value
            # Check for duplicates
            for r in range(self.rowCount()):
                if r != row and self.data(self.index(r, 0), Qt.EditRole) == new_name:
                    print(f"Error: Name '{new_name}' already exists.")
                    return False

            old_name = self._data[row][col]
            if old_name != new_name:
                self.nameChanged.emit(old_name, new_name)

        self._data[row][col] = value
        self.dataChanged.emit(index, index, [role])
        self.WIChanged.emit()

        return True

    def insertRows(self, row, count=1, parent=QModelIndex()):
        self.beginInsertRows(parent, row, row + count - 1)

        for _ in range(count):
            self._data.insert(row, self._empty_row())

        self.WIChanged.emit()
        self.endInsertRows()
        return True

    def removeRows(self, row, count=1, parent=QModelIndex()):
        self.beginRemoveRows(parent, row, row + count - 1)

        for _ in range(count):
            del self._data[row]

        self.WIChanged.emit()
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
        self.WIChanged.emit()

    def clear(self):
        self.beginResetModel()
        self._data = [["" for i in range(0, len(self.headers))]]
        self.endResetModel()
        self.WIChanged.emit()
