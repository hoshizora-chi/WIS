from qtpy.QtWidgets import QWidget, QVBoxLayout, QTableView, QSizePolicy
from qtpy.QtWidgets import QStyledItemDelegate, QTimeEdit, QDateEdit, QLineEdit
from qtpy.QtCore import QDate
from qtpy.QtGui import QIntValidator
from qtpy.QtCore import QTime
from qtpy.QtWidgets import QHeaderView
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QMenu


class TablePage(QWidget):
    def __init__(self, model):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # important
        layout.setSpacing(0)

        self.table = QTableView(self)
        self.table.setModel(model)

        self.table.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.table)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(
            self.open_context_menu
        )
        for col, delegate in model.delegates.items():
            if delegate == "date":
                self.table.setItemDelegateForColumn(col, DateDelegate(self.table))
            elif delegate == "int":
                self.table.setItemDelegateForColumn(col, IntDelegate(self.table))
            elif delegate == "time":
                self.table.setItemDelegateForColumn(col, TimeDelegate(self.table))

    def open_context_menu(self, pos):
        index = self.table.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        model = self.table.model()

        menu = QMenu(self)

        insert_before = menu.addAction("Insert row before")
        insert_after = menu.addAction("Insert row after")
        delete_row = menu.addAction("Delete row")

        action = menu.exec_(self.table.viewport().mapToGlobal(pos))

        if action == insert_before:
            model.insertRows(row)

        elif action == insert_after:
            model.insertRows(row + 1)

        elif action == delete_row:
            selected_len = len(self.table.selectionModel().selectedIndexes())
            has_multiple = selected_len > 1
            if has_multiple:
                self.removeSelectedRows()
            else:
                model.removeRows(row)

            if len(model._data) == 0:
                model.insertRows(row)

    def removeSelectedRows(self):
        selection = self.table.selectionModel().selectedIndexes()
        if not selection:
            return

        model = self.table.model()

        source_model = model
        rows = sorted(
            {i.row() for i in selection},
            reverse=True
        )

        for row in rows:
            source_model.removeRows(row)


class TimeDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QTimeEdit(parent)
        editor.setDisplayFormat("H:mm")
        editor.setTime(QTime.currentTime())
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.EditRole)
        time = QTime.fromString(text, "H:mm")
        if time.isValid():
            editor.setTime(time)

    def setModelData(self, editor, model, index):
        model.setData(
            index,
            editor.time().toString("H:mm"),
            Qt.EditRole
        )


class IntDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        editor.setValidator(QIntValidator(editor))
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text(), Qt.EditRole)


class DateDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QDateEdit(parent)
        editor.setCalendarPopup(True)
        editor.setDisplayFormat("dd-MM-yyyy")
        editor.setDate(QDate.currentDate())
        return editor

    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.EditRole)
        date = QDate.fromString(text, "dd-MM-yyyy")
        if date.isValid():
            editor.setDate(date)

    def setModelData(self, editor, model, index):
        model.setData(
            index,
            editor.date().toString("dd-MM-yyyy"),
            Qt.EditRole
        )
