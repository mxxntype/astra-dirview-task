#!/usr/bin/python3

import sys
import os

from PyQt5 import QtCore
from PyQt5.QtCore import (
    QCommandLineOption,
    QCommandLineParser,
    QCoreApplication,
    QDir,
    QT_VERSION_STR,
    QSortFilterProxyModel,
)
from PyQt5.QtWidgets import (
    QWidget,
    QApplication,
    QFileIconProvider,
    QFileSystemModel,
    QTreeView,
    QLineEdit,
    QVBoxLayout,
)


class Dirview(QWidget):
    def __init__(self, path: str | None, disableIcons: bool, parent=None):
        super(Dirview, self).__init__(parent)

        filter = QLineEdit(textChanged=self.on_textChanged)
        filter.setPlaceholderText("Фильтр по имени...")
        self.tree_view = QTreeView()
        self.tree_view.setAnimated(True)
        self.tree_view.setIndentation(10)
        self.tree_view.setSortingEnabled(True)
        self.path: str = path or QDir.homePath() or os.getenv("HOME") or "/"

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.rootPath())
        self.file_model.setFilter(
            QDir.NoDotAndDotDot | QDir.Dirs | QDir.Files | QDir.Hidden
        )

        if disableIcons:
            iconProvider = self.file_model.iconProvider()
            if iconProvider:
                iconProvider.setOptions(QFileIconProvider.DontUseCustomDirectoryIcons)

        self.proxy_model = QSortFilterProxyModel(
            recursiveFilteringEnabled=True, filterRole=QFileSystemModel.FileNameRole
        )
        self.proxy_model.setSourceModel(self.file_model)

        self.tree_view.setModel(self.proxy_model)
        self.adjust_root_index(self.path)

        desktop = QApplication.desktop()
        if desktop:
            availableSize = desktop.availableGeometry(self).size()
            self.resize(availableSize / 1.5)
        self.tree_view.setColumnWidth(0, int(self.tree_view.width() / 3))
        self.setWindowTitle("dirview.py")

        layout = QVBoxLayout(self)
        layout.addWidget(filter)
        layout.addWidget(self.tree_view)

    @QtCore.pyqtSlot(str)
    def on_textChanged(self, text):
        self.proxy_model.setFilterWildcard(f"*{text}*")
        self.adjust_root_index(self.path)

    def adjust_root_index(self, path: str):
        root_index = self.file_model.index(path)
        proxy_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_index)


def main() -> None:
    app = QApplication(sys.argv)
    QCoreApplication.setApplicationVersion(QT_VERSION_STR)

    cli = QCommandLineParser()
    cli.setApplicationDescription("Astra Linux test task")
    cli.addHelpOption()
    cli.addVersionOption()

    disableIconsFlag = QCommandLineOption("c", "Отключить пользовательские иконки.")
    cli.addOption(disableIconsFlag)
    cli.addPositionalArgument("path", "Начальная директория.")
    cli.process(app)
    disableIcons: bool = cli.isSet(disableIconsFlag)
    try:
        rootPath = cli.positionalArguments().pop(0)
    except IndexError:
        rootPath = None

    dirview = Dirview(rootPath, disableIcons)
    dirview.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
