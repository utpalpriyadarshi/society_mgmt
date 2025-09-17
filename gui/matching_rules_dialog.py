# Matching rules dialog for reconciliation tab
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QCheckBox, QDateEdit, QDialogButtonBox, QGroupBox,
                             QListWidget, QListWidgetItem, QTextEdit, QSpinBox,
                             QDoubleSpinBox, QMessageBox, QScrollArea, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate, Qt
from models.matching_rules import MatchingRule, MatchingRulesManager

class MatchingRulesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Matching Rules")
        self.setModal(True)
        self.resize(900, 700)  # Increased size for better visibility
        self.setMinimumSize(700, 500)  # Set minimum size
        self.rules_manager = MatchingRulesManager()
        self.rules = []
        self.editing_rule = None  # Track which rule is being edited
        self.setup_ui()
        self.load_rules()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Rules list
        rules_layout = QHBoxLayout()
        
        # Available rules list
        self.rules_list = QListWidget()
        self.rules_list.currentItemChanged.connect(self.on_rule_selected)
        rules_layout.addWidget(self.rules_list)
        
        # Rule buttons
        buttons_layout = QVBoxLayout()
        self.new_rule_button = QPushButton("New Rule")
        self.new_rule_button.clicked.connect(self.new_rule)
        buttons_layout.addWidget(self.new_rule_button)
        
        self.edit_rule_button = QPushButton("Edit Rule")
        self.edit_rule_button.clicked.connect(self.edit_rule)
        self.edit_rule_button.setEnabled(False)
        buttons_layout.addWidget(self.edit_rule_button)
        
        self.delete_rule_button = QPushButton("Delete Rule")
        self.delete_rule_button.clicked.connect(self.delete_rule)
        self.delete_rule_button.setEnabled(False)
        buttons_layout.addWidget(self.delete_rule_button)
        
        self.up_button = QPushButton("Move Up")
        self.up_button.clicked.connect(self.move_rule_up)
        self.up_button.setEnabled(False)
        buttons_layout.addWidget(self.up_button)
        
        self.down_button = QPushButton("Move Down")
        self.down_button.clicked.connect(self.move_rule_down)
        self.down_button.setEnabled(False)
        buttons_layout.addWidget(self.down_button)
        
        buttons_layout.addStretch()
        rules_layout.addLayout(buttons_layout)
        
        main_layout.addLayout(rules_layout)
        
        # Rule editor
        self.rule_editor = QGroupBox("Rule Editor")
        editor_layout = QFormLayout()
        
        self.rule_name = QLineEdit()
        self.rule_name.setEnabled(False)
        editor_layout.addRow("Rule Name:", self.rule_name)
        
        self.rule_description = QTextEdit()
        self.rule_description.setEnabled(False)
        self.rule_description.setMaximumHeight(60)
        editor_layout.addRow("Description:", self.rule_description)
        
        self.rule_priority = QSpinBox()
        self.rule_priority.setEnabled(False)
        self.rule_priority.setRange(0, 100)
        self.rule_priority.setValue(50)
        editor_layout.addRow("Priority:", self.rule_priority)
        
        # Conditions
        conditions_group = QGroupBox("Conditions")
        conditions_layout = QVBoxLayout()
        
        # Add condition button
        add_condition_layout = QHBoxLayout()
        add_condition_layout.addWidget(QLabel("Add Condition:"))
        self.condition_type = QComboBox()
        self.condition_type.setEnabled(False)
        self.condition_type.addItems(["Amount Match", "Date Proximity", "Description Keywords", 
                                     "Flat Number Match", "Transaction Type Match"])
        add_condition_layout.addWidget(self.condition_type)
        self.add_condition_button = QPushButton("Add")
        self.add_condition_button.setEnabled(False)
        self.add_condition_button.clicked.connect(self.add_condition)
        add_condition_layout.addWidget(self.add_condition_button)
        conditions_layout.addLayout(add_condition_layout)
        
        # Conditions list
        self.conditions_list = QListWidget()
        self.conditions_list.setEnabled(False)
        self.conditions_list.setMinimumHeight(100)  # Increased minimum height
        conditions_layout.addWidget(self.conditions_list)
        
        conditions_group.setLayout(conditions_layout)
        editor_layout.addRow(conditions_group)
        
        # Actions
        actions_group = QGroupBox("Actions")
        actions_layout = QVBoxLayout()
        
        # Add action button
        add_action_layout = QHBoxLayout()
        add_action_layout.addWidget(QLabel("Add Action:"))
        self.action_type = QComboBox()
        self.action_type.setEnabled(False)
        self.action_type.addItems(["Auto-Match", "Highlight", "Flag for Review", "Send Notification"])
        add_action_layout.addWidget(self.action_type)
        self.add_action_button = QPushButton("Add")
        self.add_action_button.setEnabled(False)
        self.add_action_button.clicked.connect(self.add_action)
        add_action_layout.addWidget(self.add_action_button)
        actions_layout.addLayout(add_action_layout)
        
        # Actions list
        self.actions_list = QListWidget()
        self.actions_list.setEnabled(False)
        self.actions_list.setMinimumHeight(100)  # Increased minimum height
        actions_layout.addWidget(self.actions_list)
        
        actions_group.setLayout(actions_layout)
        editor_layout.addRow(actions_group)
        
        # Save/Cancel buttons for rule editor
        editor_buttons_layout = QHBoxLayout()
        self.save_rule_button = QPushButton("Save Rule")
        self.save_rule_button.setEnabled(False)
        self.save_rule_button.clicked.connect(self.save_rule)
        editor_buttons_layout.addWidget(self.save_rule_button)
        
        self.cancel_rule_button = QPushButton("Cancel")
        self.cancel_rule_button.setEnabled(False)
        self.cancel_rule_button.clicked.connect(self.cancel_rule_edit)
        editor_buttons_layout.addWidget(self.cancel_rule_button)
        
        editor_layout.addRow(editor_buttons_layout)
        self.rule_editor.setLayout(editor_layout)
        
        # Wrap rule editor in a scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.rule_editor)
        self.scroll_area.setMinimumHeight(250)  # Increased minimum height
        self.scroll_area.setMaximumHeight(500)  # Increased maximum height
        main_layout.addWidget(self.scroll_area)
        
        # Global matching settings
        settings_group = QGroupBox("Global Matching Settings")
        settings_layout = QFormLayout()
        
        self.date_tolerance = QSpinBox()
        self.date_tolerance.setRange(0, 30)
        self.date_tolerance.setValue(3)
        self.date_tolerance.setSuffix(" days")
        settings_layout.addRow("Date Tolerance:", self.date_tolerance)
        
        self.amount_tolerance = QDoubleSpinBox()
        self.amount_tolerance.setRange(0, 1000)
        self.amount_tolerance.setValue(0.01)
        self.amount_tolerance.setPrefix("₹")
        settings_layout.addRow("Amount Tolerance:", self.amount_tolerance)
        
        self.auto_apply_rules = QCheckBox("Auto-apply rules during matching")
        self.auto_apply_rules.setChecked(True)
        settings_layout.addRow(self.auto_apply_rules)
        
        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)
        
        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
        
    def load_rules(self):
        """Load matching rules from the database"""
        self.rules = self.rules_manager.get_all_rules()
        self.update_rules_list()
        
    def update_rules_list(self):
        """Update the rules list display"""
        self.rules_list.clear()
        for rule in sorted(self.rules, key=lambda r: r.priority, reverse=True):
            item = QListWidgetItem(f"[{rule.priority}] {rule.name}")
            item.setData(Qt.UserRole, rule)
            self.rules_list.addItem(item)
            
    def on_rule_selected(self, current, previous):
        """Handle rule selection"""
        self.edit_rule_button.setEnabled(current is not None)
        self.delete_rule_button.setEnabled(current is not None)
        self.up_button.setEnabled(current is not None)
        self.down_button.setEnabled(current is not None)
        
    def new_rule(self):
        """Create a new rule"""
        self.rules_list.clearSelection()
        self.rule_name.clear()
        self.rule_description.clear()
        self.rule_priority.setValue(50)
        self.conditions_list.clear()
        self.actions_list.clear()
        # Mark that we're creating a new rule
        self.editing_rule = None
        # Enable the editor controls
        self.rule_name.setEnabled(True)
        self.rule_description.setEnabled(True)
        self.rule_priority.setEnabled(True)
        self.condition_type.setEnabled(True)
        self.add_condition_button.setEnabled(True)
        self.conditions_list.setEnabled(True)
        self.action_type.setEnabled(True)
        self.add_action_button.setEnabled(True)
        self.actions_list.setEnabled(True)
        self.save_rule_button.setEnabled(True)
        self.cancel_rule_button.setEnabled(True)
        
    def edit_rule(self):
        """Edit the selected rule"""
        current_item = self.rules_list.currentItem()
        if not current_item:
            return
            
        rule = current_item.data(Qt.UserRole)
        self.editing_rule = rule  # Store reference to the rule being edited
        self.rule_name.setText(rule.name)
        self.rule_description.setPlainText(rule.description)
        self.rule_priority.setValue(rule.priority)
        
        # Clear and repopulate conditions and actions
        self.conditions_list.clear()
        for condition in rule.conditions:
            item = QListWidgetItem(condition)
            self.conditions_list.addItem(item)
            
        self.actions_list.clear()
        for action in rule.actions:
            item = QListWidgetItem(action)
            self.actions_list.addItem(item)
            
        # Enable the editor controls
        self.rule_name.setEnabled(True)
        self.rule_description.setEnabled(True)
        self.rule_priority.setEnabled(True)
        self.condition_type.setEnabled(True)
        self.add_condition_button.setEnabled(True)
        self.conditions_list.setEnabled(True)
        self.action_type.setEnabled(True)
        self.add_action_button.setEnabled(True)
        self.actions_list.setEnabled(True)
        self.save_rule_button.setEnabled(True)
        self.cancel_rule_button.setEnabled(True)
            
    def delete_rule(self):
        """Delete the selected rule"""
        current_item = self.rules_list.currentItem()
        if not current_item:
            return
            
        rule = current_item.data(Qt.UserRole)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Rule",
            f"Are you sure you want to delete the rule '{rule.name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete from database
            if rule.id is not None:
                if not self.rules_manager.delete_rule(rule.id):
                    QMessageBox.warning(self, "Delete Error", "Failed to delete rule from database.")
                    return
            
            # Remove from local list
            self.rules.remove(rule)
            self.update_rules_list()
            
            # Disable editor controls
            self.rule_name.setEnabled(False)
            self.rule_description.setEnabled(False)
            self.rule_priority.setEnabled(False)
            self.condition_type.setEnabled(False)
            self.add_condition_button.setEnabled(False)
            self.conditions_list.setEnabled(False)
            self.action_type.setEnabled(False)
            self.add_action_button.setEnabled(False)
            self.actions_list.setEnabled(False)
            self.save_rule_button.setEnabled(False)
            self.cancel_rule_button.setEnabled(False)
            
    def move_rule_up(self):
        """Move the selected rule up in priority"""
        current_row = self.rules_list.currentRow()
        if current_row > 0:
            # Get the rules at current and previous positions
            current_rule = self.rules[current_row]
            prev_rule = self.rules[current_row - 1]
            
            # Swap priorities
            current_priority = current_rule.priority
            prev_priority = prev_rule.priority
            
            # Update priorities in database
            if current_rule.id is not None:
                self.rules_manager.move_rule(current_rule.id, prev_priority)
            if prev_rule.id is not None:
                self.rules_manager.move_rule(prev_rule.id, current_priority)
            
            # Swap priorities in memory
            current_rule.priority = prev_priority
            prev_rule.priority = current_priority
            
            # Update the UI
            self.update_rules_list()
            # Select the moved item
            self.rules_list.setCurrentRow(current_row - 1)
            
    def move_rule_down(self):
        """Move the selected rule down in priority"""
        current_row = self.rules_list.currentRow()
        if current_row < len(self.rules) - 1:
            # Get the rules at current and next positions
            current_rule = self.rules[current_row]
            next_rule = self.rules[current_row + 1]
            
            # Swap priorities
            current_priority = current_rule.priority
            next_priority = next_rule.priority
            
            # Update priorities in database
            if current_rule.id is not None:
                self.rules_manager.move_rule(current_rule.id, next_priority)
            if next_rule.id is not None:
                self.rules_manager.move_rule(next_rule.id, current_priority)
            
            # Swap priorities in memory
            current_rule.priority = next_priority
            next_rule.priority = current_priority
            
            # Update the UI
            self.update_rules_list()
            # Select the moved item
            self.rules_list.setCurrentRow(current_row + 1)
            
    def add_condition(self):
        """Add a condition to the current rule"""
        condition_text = self.condition_type.currentText()
        item = QListWidgetItem(condition_text)
        self.conditions_list.addItem(item)
        
    def add_action(self):
        """Add an action to the current rule"""
        action_text = self.action_type.currentText()
        item = QListWidgetItem(action_text)
        self.actions_list.addItem(item)
        
    def save_rule(self):
        """Save the current rule (either new or existing)"""
        name = self.rule_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a rule name.")
            return
            
        # Create or update rule object
        if self.editing_rule is not None:
            # Update existing rule
            rule = self.editing_rule
            rule.name = name
            rule.description = self.rule_description.toPlainText()
            rule.priority = self.rule_priority.value()
            rule.conditions = []
            rule.actions = []
        else:
            # Create new rule
            rule = MatchingRule(
                name=name,
                description=self.rule_description.toPlainText(),
                priority=self.rule_priority.value()
            )
        
        # Add conditions and actions
        for i in range(self.conditions_list.count()):
            item = self.conditions_list.item(i)
            rule.conditions.append(item.text())
            
        for i in range(self.actions_list.count()):
            item = self.actions_list.item(i)
            rule.actions.append(item.text())
            
        # Save to database
        if not self.rules_manager.save_rule(rule):
            QMessageBox.warning(self, "Save Error", "Failed to save rule to database.")
            return
            
        # If it's a new rule, add it to the rules list
        if self.editing_rule is None:
            self.rules.append(rule)
        
        # Update the UI
        self.update_rules_list()
        
        # Disable the editor controls
        self.rule_name.setEnabled(False)
        self.rule_description.setEnabled(False)
        self.rule_priority.setEnabled(False)
        self.condition_type.setEnabled(False)
        self.add_condition_button.setEnabled(False)
        self.conditions_list.setEnabled(False)
        self.action_type.setEnabled(False)
        self.add_action_button.setEnabled(False)
        self.actions_list.setEnabled(False)
        self.save_rule_button.setEnabled(False)
        self.cancel_rule_button.setEnabled(False)
        
        # If we were editing, clear the selection to avoid confusion
        if self.editing_rule is not None:
            self.rules_list.clearSelection()
            
        # Clear the editing rule reference
        self.editing_rule = None
        
        # Update button states
        self.on_rule_selected(self.rules_list.currentItem(), None)
        
    def cancel_rule_edit(self):
        """Cancel rule editing"""
        # Disable editor controls
        self.rule_name.setEnabled(False)
        self.rule_description.setEnabled(False)
        self.rule_priority.setEnabled(False)
        self.condition_type.setEnabled(False)
        self.add_condition_button.setEnabled(False)
        self.conditions_list.setEnabled(False)
        self.action_type.setEnabled(False)
        self.add_action_button.setEnabled(False)
        self.actions_list.setEnabled(False)
        self.save_rule_button.setEnabled(False)
        self.cancel_rule_button.setEnabled(False)
        self.rules_list.clearSelection()
        self.editing_rule = None  # Clear the editing rule reference
        
    def get_matching_settings(self):
        """Return the current matching settings"""
        return {
            'date_tolerance': self.date_tolerance.value(),
            'amount_tolerance': self.amount_tolerance.value(),
            'auto_apply_rules': self.auto_apply_rules.isChecked(),
            'rules': self.rules
        }