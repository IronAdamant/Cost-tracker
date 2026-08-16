"""First-run setup, account creation, and local user selection."""

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from cost_tracker.app_paths import AppPaths
from cost_tracker.constants import APP_NAME
from cost_tracker.create_user_dialog import CreateUserDialog
from cost_tracker.user_account_store import UserAccountError, UserAccountStore


class StartWindow(QMainWindow):
    user_authenticated = Signal(str)

    def __init__(self, paths: AppPaths, accounts: UserAccountStore) -> None:
        super().__init__()
        self.paths = paths
        self.accounts = accounts
        self.setWindowTitle(APP_NAME)
        self.setMinimumWidth(420)

        self.stack = QStackedWidget()
        self.setCentralWidget(self._wrap(self.stack))
        self.home_page = QWidget()
        self.users_page = QWidget()
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.users_page)

        self._build_home()
        self._refresh_home()

    def _wrap(self, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.addWidget(widget)
        return container

    def _build_home(self) -> None:
        layout = QVBoxLayout(self.home_page)
        title = QLabel(APP_NAME)
        title.setObjectName("title")
        subtitle = QLabel("Local cost tracking with CSV files. One computer, multiple users.")
        subtitle.setObjectName("subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(12)

        self.folder_label = QLabel()
        self.folder_label.setWordWrap(True)
        browse = QPushButton("Choose data folder")
        browse.clicked.connect(self._choose_folder)
        layout.addWidget(self.folder_label)
        layout.addWidget(browse)
        layout.addSpacing(16)

        self.existing_button = QPushButton("Existing users")
        self.existing_button.setProperty("cssClass", "primary")
        self.existing_button.clicked.connect(self._show_users)
        self.create_button = QPushButton("Create user")
        self.create_button.clicked.connect(self._create_user)
        layout.addWidget(self.existing_button)
        layout.addWidget(self.create_button)
        layout.addStretch()

    def _refresh_home(self) -> None:
        configured = "saved" if self.paths.is_configured else "default until you choose another"
        self.folder_label.setText(
            f"Data folder ({configured}):\n{self.paths.data_directory}"
        )
        self.existing_button.setVisible(self.accounts.has_users())
        if self.accounts.has_users():
            self.create_button.setText("Create another user")
            self.create_button.setProperty("cssClass", "")
        else:
            self.create_button.setText("Create user")
            self.create_button.setProperty("cssClass", "primary")
        self.create_button.style().unpolish(self.create_button)
        self.create_button.style().polish(self.create_button)
        self.existing_button.style().unpolish(self.existing_button)
        self.existing_button.style().polish(self.existing_button)

    def _choose_folder(self) -> None:
        chosen = QFileDialog.getExistingDirectory(
            self,
            "Select data folder",
            str(self.paths.data_directory),
        )
        if not chosen:
            return
        self.paths.data_directory = Path(chosen)
        self.paths.save()
        self.accounts = UserAccountStore(self.paths.data_directory)
        self._refresh_home()

    def _ensure_configured(self) -> None:
        if not self.paths.is_configured:
            self.paths.save()
            self.accounts = UserAccountStore(self.paths.data_directory)

    def _create_user(self) -> None:
        dialog = CreateUserDialog(self)
        if dialog.exec() != CreateUserDialog.DialogCode.Accepted:
            return
        self._ensure_configured()
        try:
            self.accounts.create_user(dialog.username(), dialog.password())
        except UserAccountError as exc:
            QMessageBox.warning(self, "Could not create user", str(exc))
            return
        self._refresh_home()
        self.user_authenticated.emit(dialog.username())

    def _show_users(self) -> None:
        page_layout = self.users_page.layout()
        if page_layout is not None:
            while page_layout.count():
                item = page_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        else:
            page_layout = QVBoxLayout(self.users_page)

        heading = QLabel("Choose a user")
        heading.setObjectName("title")
        page_layout.addWidget(heading)
        for username in self.accounts.usernames:
            button = QPushButton(username)
            button.clicked.connect(lambda checked=False, name=username: self._login(name))
            page_layout.addWidget(button)
        back = QPushButton("Back")
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_page))
        page_layout.addWidget(back)
        page_layout.addStretch()
        self.stack.setCurrentWidget(self.users_page)

    def _login(self, username: str) -> None:
        if self.accounts.requires_password(username):
            password, accepted = QInputDialog.getText(
                self,
                "Password",
                f"Password for {username}:",
                QLineEdit.EchoMode.Password,
            )
            if not accepted:
                return
            if not self.accounts.verify(username, password):
                QMessageBox.warning(self, "Login failed", "Incorrect password.")
                return
        self.user_authenticated.emit(username)
