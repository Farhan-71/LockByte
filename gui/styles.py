"""Dark mode stylesheet for LockByte GUI based on the provided design."""

DARK_THEME = """
/* Global Styles */
QWidget {
    background-color: #141d26;
    color: #e2e2d2;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 12px;
}

/* Sidebar Styles */
#Sidebar {
    background-color: #16212c;
    border-right: 1px solid #293c4f;
}

#SidebarBrand {
    border-bottom: 1px solid #293c4f;
    background-color: #16212c;
}

#SidebarBrand QLabel {
    font-size: 16px;
    font-weight: 700;
    color: #e2e2d2;
    letter-spacing: -0.55px;
}

#SidebarEyebrow {
    color: #596b7d;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1.35px;
    padding-left: 14px;
}

#SidebarNav QPushButton {
    background-color: transparent;
    color: #94a5b4;
    border: 1px solid transparent;
    border-radius: 6px;
    text-align: left;
    padding: 10px 12px;
    font-size: 12px;
    font-weight: 500;
    margin: 2px 14px;
}

#SidebarNav QPushButton:hover {
    background-color: #1b2936;
    color: #d5d8d5;
}

#SidebarNav QPushButton:checked {
    background-color: #241822; /* Approx for rgba(197,31,93,0.1) on #16212c */
    color: #e2e2d2;
    border-left: 3px solid #c51f5d;
    border-radius: 6px;
}

#SidebarBottom {
    border-top: 1px solid #293c4f;
    background-color: #16212c;
}

#VaultStatusTitle {
    color: #c7cdce;
    font-size: 11px;
    font-weight: 600;
}

#VaultStatusSub {
    color: #5b6d7f;
    font-size: 9px;
}

/* Page Headers */
#PageHeader {
    border-bottom: 1px solid #293c4f;
    background-color: #141d26;
}

#PageTitle {
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.55px;
    color: #e2e2d2;
}

#PageSubtitle {
    color: #8295a7;
    font-size: 11px;
}

#VaultSecureBadge {
    color: #80aa91;
    font-size: 11px;
    font-weight: 600;
}

#ProfileButton {
    background-color: #1e2d3b;
    border: 1px solid #32485e;
    border-radius: 17px;
    color: #b8c2c8;
}

#ProfileButton:hover {
    border-color: #61788f;
    color: #e2e2d2;
}

/* Auth Cards */
#AuthCard {
    background-color: #192632;
    border: 1px solid #32485e;
    border-radius: 10px;
}

/* Setup Cards */
#SetupCard {
    background-color: #192632;
    border: 1px solid #32485e;
    border-radius: 8px;
}

#SetupCard:hover {
    border: 1px solid #4e6a84;
}

/* Content Surfaces */
.ContentSurface, #ContentSurface {
    background-color: #192632;
    border: 1px solid #32485e;
    border-radius: 8px;
}

/* Headings */
QLabel#Header {
    font-size: 25px;
    font-weight: 600;
    color: #e2e2d2;
    letter-spacing: -0.8px;
}

/* Generic Buttons */
QPushButton {
    background-color: #1e2d3b;
    color: #b8c2c8;
    border: 1px solid #32485e;
    border-radius: 6px;
    padding: 8px 15px;
    font-weight: 600;
    font-size: 11px;
}

QPushButton:hover {
    background-color: #27394b;
    border-color: #586f87;
    color: #e2e2d2;
}

QPushButton:pressed {
    background-color: #1b2936;
}

/* Primary Action Buttons */
QPushButton#PrimaryButton {
    background-color: #c51f5d;
    color: #e2e2d2;
    border: 1px solid #c51f5d;
}

QPushButton#PrimaryButton:hover {
    background-color: #d63270;
    border-color: #d63270;
}

QPushButton#PrimaryButton:pressed {
    background-color: #a91b50;
    border-color: #a91b50;
}

/* Text Buttons */
QPushButton#TextButton {
    background-color: transparent;
    border: none;
    color: #a2b1bc;
    font-weight: normal;
}
QPushButton#TextButton:hover {
    color: #e2e2d2;
}

/* Inputs */
QLineEdit, QTextEdit, QComboBox {
    background-color: #151f29;
    border: 1px solid #364e66;
    border-radius: 6px;
    padding: 8px 13px;
    color: #ececdd;
    font-size: 12px;
}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #c51f5d;
}

/* Data Tables */
QTableWidget {
    background-color: #141d26;
    color: #b3bfc7;
    gridline-color: transparent;
    border: none;
    font-size: 11px;
    outline: none;
}

QHeaderView::section {
    background-color: #182531;
    color: #66798c;
    border: none;
    border-bottom: 1px solid #2d4257;
    font-weight: 600;
    font-size: 9px;
    text-transform: uppercase;
    padding: 0px 15px;
    text-align: left;
    height: 39px;
}

QTableWidget::item {
    border-bottom: 1px solid #293c4f;
    padding: 0px;
}

QTableWidget::item:selected {
    background-color: #1d2c39;
    color: #e2e2d2;
}

/* Settings Dropdown Button */
QPushButton#SettingsComboButton {
    background-color: transparent;
    color: #92a3b2;
    border: none;
    padding: 0;
    text-align: right;
    font-size: 9px;
    font-weight: normal;
}
QPushButton#SettingsComboButton:hover {
    color: #e2e2d2;
    background-color: transparent;
}

/* Checkboxes */
QCheckBox {
    spacing: 8px;
    color: #a1b0bb;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid #45617b;
    border-radius: 3px;
    background: transparent;
}
QCheckBox::indicator:checked {
    background: #c51f5d;
    border-color: #c51f5d;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #3a546d;
    height: 4px;
    background: #20303f;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    background: #c51f5d;
    width: 14px;
    margin: -5px 0;
    border-radius: 7px;
}
QSlider::sub-page:horizontal {
    background: #c51f5d;
    border-radius: 2px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #32485e;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #4e6a84;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""