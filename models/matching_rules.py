# models/matching_rules.py
import sqlite3
import json
from typing import List, Dict, Any

class MatchingRule:
    """Represents a customizable matching rule"""
    def __init__(self, id=None, name="", description="", priority=0, conditions=None, actions=None):
        self.id = id
        self.name = name
        self.description = description
        self.priority = priority
        self.conditions = conditions or []
        self.actions = actions or []

class MatchingRulesManager:
    """Manager for handling matching rules in the database"""
    
    def __init__(self, db_path="society_management.db"):
        self.db_path = db_path
    
    def get_all_rules(self) -> List[MatchingRule]:
        """Retrieve all matching rules from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, priority, conditions, actions
            FROM matching_rules
            ORDER BY priority DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        rules = []
        for row in rows:
            rule = MatchingRule(
                id=row[0],
                name=row[1],
                description=row[2],
                priority=row[3],
                conditions=json.loads(row[4]) if row[4] else [],
                actions=json.loads(row[5]) if row[5] else []
            )
            rules.append(rule)
            
        return rules
    
    def save_rule(self, rule: MatchingRule) -> bool:
        """Save a matching rule to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if rule.id is not None:
                # Update existing rule
                cursor.execute('''
                    UPDATE matching_rules
                    SET name=?, description=?, priority=?, conditions=?, actions=?, updated_at=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (
                    rule.name,
                    rule.description,
                    rule.priority,
                    json.dumps(rule.conditions),
                    json.dumps(rule.actions),
                    rule.id
                ))
            else:
                # Insert new rule
                cursor.execute('''
                    INSERT INTO matching_rules (name, description, priority, conditions, actions)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    rule.name,
                    rule.description,
                    rule.priority,
                    json.dumps(rule.conditions),
                    json.dumps(rule.actions)
                ))
                rule.id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error saving rule: {e}")
            return False
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a matching rule from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM matching_rules WHERE id=?', (rule_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error deleting rule: {e}")
            return False
    
    def move_rule(self, rule_id: int, new_priority: int) -> bool:
        """Update the priority of a matching rule"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE matching_rules
                SET priority=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            ''', (new_priority, rule_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            conn.close()
            print(f"Error moving rule: {e}")
            return False