# Updated src/gui/main_window.py
# ... existing imports ...
from src.gui.file_order_tab import FileOrderTab

# In __init__:
# ... existing code ...

# In init_ui:
self.file_order_tab = FileOrderTab(self.config_manager, self)
self.tabs.addTab(self.file_order_tab, "File Order")

# Ensure input folder changes trigger refresh across tabs if needed