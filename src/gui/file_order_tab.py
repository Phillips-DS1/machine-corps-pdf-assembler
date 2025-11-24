# src/gui/file_order_tab.py
# ... existing code ...

class FileOrderTab(QWidget):
    # ... init_ui additions ...
    apply_btn = QPushButton("Apply Order")
    apply_btn.clicked.connect(self.manager.apply_order)
    btn_layout.addWidget(apply_btn)

    # In refresh_list: Also reset any staged_order if present