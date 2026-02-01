from qtpy.QtCore import QAbstractTableModel, Qt, QModelIndex, Signal
from datetime import datetime, timedelta


class InputTableModel(QAbstractTableModel):
    validationFailed = Signal(str)

    def __init__(self, jp_duration):
        super().__init__()

        self.jp_duration = jp_duration

        # Example domain data (replace later)
        self.headers = [
                "Tgl/Hari",
                "Jam Mulai",
                "JP",
                "Jam Berakhir",
                "Pelatihan",
                "Agenda",
                "Nama WI"
        ]
        self._data = [
            ["19-10-2026", "14:00", 3, "", "", "Pendidikan Pancasila", "Yeli"],
            ["15-10-2026", "13:00", 3, "", "", "Pendidikan Kewarganegaraan", "Busur"],
        ]
        self.delegates = {
            0: "date",
            1: "time",
            2: "int",
            6: "wi"
        }

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role in (Qt.DisplayRole, Qt.EditRole):
            if col == 3:  # Jam Berakhir
                jam_mulai_str = self._data[row][1]
                jp_str = self._data[row][2]
                try:
                    jam_mulai = datetime.strptime(jam_mulai_str, "%H:%M")
                    jp = int(jp_str)
                    jam_berakhir = jam_mulai + timedelta(minutes=jp * self.jp_duration)
                    return jam_berakhir.strftime("%H:%M")
                except (ValueError, TypeError):
                    return ""
            return self._data[row][col]

        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.headers[section]

        return section + 1

    def flags(self, index):
        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() != 3:  # Make Jam Berakhir not editable
            flags |= Qt.ItemIsEditable
        return flags

    def setData(self, index, value, role=Qt.EditRole):
        if role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        # --- Validation logic starts here ---
        wi_name = self._data[row][6] if col != 6 else value
        date_str = self._data[row][0] if col != 0 else value
        start_time_str = self._data[row][1] if col != 1 else value
        jp_str = self._data[row][2] if col != 2 else value

        if wi_name and date_str and self.is_time(start_time_str) and self.is_int(jp_str):
            try:
                start_time = datetime.strptime(start_time_str, "%H:%M")
                jp = int(jp_str)
                end_time = start_time + timedelta(minutes=jp * self.jp_duration)

                for i in range(self.rowCount()):
                    if i == row:
                        continue

                    other_wi_name = self._data[i][6]
                    other_date_str = self._data[i][0]

                    if wi_name == other_wi_name and date_str == other_date_str:
                        other_start_str = self._data[i][1]
                        other_jp_str = self._data[i][2]

                        if self.is_time(other_start_str) and self.is_int(other_jp_str):
                            other_start_time = datetime.strptime(other_start_str, "%H:%M")
                            other_jp = int(other_jp_str)
                            other_end_time = other_start_time + timedelta(minutes=other_jp * self.jp_duration)

                            if start_time < other_end_time and other_start_time < end_time:
                                self.validationFailed.emit(f"Jadwal bentrok untuk {wi_name} pada {date_str}!")
                                return False
            except (ValueError, TypeError):
                pass  # Cannot validate if data is malformed, allow change

        if col == 2 and not self.is_int(value):
            return False
        elif col == 1 and not self.is_time(value):
            return False
        elif col == 0 and not self.is_date(value):
            return False

        self._data[row][col] = value
        self.dataChanged.emit(index, index, [role])

        if col in (1, 2):  # If Jam Mulai or JP changes, update Jam Berakhir
            jam_berakhir_index = self.index(row, 3)
            self.dataChanged.emit(jam_berakhir_index, jam_berakhir_index, [Qt.DisplayRole])

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
        self._data = data
        if len(self._data) == 0:
            self._data = [["" for _ in range(len(self.headers))]]
        self.endResetModel()

    def clear(self):
        self.beginResetModel()
        self._data = [["" for i in range(0, len(self.headers))]]
        self.endResetModel()

    def set_jp_duration(self, jp_duration):
        self.jp_duration = jp_duration
        # Trigger update for the whole Jam Berakhir column
        self.dataChanged.emit(self.index(0, 3), self.index(self.rowCount() - 1, 3))

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
            if row[6] == name:
                if self.is_int(str(row[2])):
                    total += int(row[2])
        return total

    def recap_for_name(self, name):
        res = []
        for row in self._data:
            if row[6] == name:
                if self.is_date(str(row[2])):
                    res.append([
                        str(row[2]),
                        str(row[4]),
                        str(row[5]),
                        str(row[6]),
                    ])

        res.sort(key=lambda r: datetime.strptime(r[0], "%d-%m-%Y"))

    def update_wi_name(self, old_name, new_name):
        for i, row in enumerate(self._data):
            if row[6] == old_name:
                self._data[i][6] = new_name
                index = self.index(i, 6)
                self.dataChanged.emit(index, index, [Qt.EditRole])
