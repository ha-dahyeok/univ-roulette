import os
import re

file_path = "lib/screens/home_screen.dart"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add _buildCustomChip method
custom_chip_code = """  Widget _buildCustomChip({
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
    Color? selectedColor,
  }) {
    final activeColor = selectedColor ?? _primaryColor;
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isSelected ? activeColor : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: isSelected ? Colors.transparent : Colors.grey.shade300, width: 1.5),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: activeColor.withValues(alpha: 0.3),
                    blurRadius: 8,
                    offset: const Offset(0, 4),
                  )
                ]
              : [],
        ),
        child: Text(
          label,
          style: TextStyle(
            fontWeight: isSelected ? FontWeight.bold : FontWeight.w600,
            color: isSelected ? Colors.white : Colors.black87,
            height: 1.2,
          ),
        ),
      ),
    );
  }

  Widget _buildSectionCard({required Widget child}) {"""

content = content.replace("  Widget _buildSectionCard({required Widget child}) {", custom_chip_code)

# 1. Replace University ChoiceChip
old_univ_chip = """                          return ChoiceChip(
                            label: Text(univ, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: isSelected ? Colors.white : Colors.black87)),
                            labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.black87),
                            showCheckmark: false,
                            selected: isSelected,
                            selectedColor: _primaryColor,
                            backgroundColor: Colors.grey.shade100,
                            shadowColor: isSelected ? Colors.black26 : Colors.transparent,
                            surfaceTintColor: Colors.transparent,
                            elevation: isSelected ? 4 : 0,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                            onSelected: (selected) {
                              setState(() {
                                if (selected) {
                                  _selectedUniv = univ;
                                } else {
                                  _selectedUniv = '';
                                }
                                _selectedGates.clear(); // 대학이 바뀌면 선택된 게이트 초기화
                              });
                            },
                          );"""

new_univ_chip = """                          return _buildCustomChip(
                            label: univ,
                            isSelected: isSelected,
                            onTap: () {
                              setState(() {
                                if (isSelected) {
                                  _selectedUniv = '';
                                } else {
                                  _selectedUniv = univ;
                                }
                                _selectedGates.clear(); // 대학이 바뀌면 선택된 게이트 초기화
                              });
                            },
                          );"""

content = content.replace(old_univ_chip, new_univ_chip)

# 2. Replace All Gates FilterChip
old_all_gates_chip = """                            FilterChip(
                              label: Text(
                                '전체 입구',
                                style: TextStyle(fontWeight: _isAllGatesSelected ? FontWeight.bold : FontWeight.normal, color: _isAllGatesSelected ? Colors.white : Colors.black87),
                              ),
                              showCheckmark: false,
                              selected: _isAllGatesSelected,
                              onSelected: _toggleAllGates,
                              selectedColor: _primaryColor.withValues(alpha: 0.8),
                              backgroundColor: Colors.grey.shade100,
                              elevation: _isAllGatesSelected ? 4 : 0,
                            ),"""

new_all_gates_chip = """                            _buildCustomChip(
                              label: '전체 입구',
                              isSelected: _isAllGatesSelected,
                              selectedColor: _primaryColor.withValues(alpha: 0.8),
                              onTap: () {
                                _toggleAllGates(!_isAllGatesSelected);
                              },
                            ),"""

content = content.replace(old_all_gates_chip, new_all_gates_chip)

# 3. Replace Specific Gate FilterChip
old_gate_chip = """                              return FilterChip(
                                label: Text(gate, style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: isSelected ? Colors.white : Colors.black87)),
                                showCheckmark: false,
                                selected: isSelected,
                                selectedColor: _primaryColor.withValues(alpha: 0.8),
                                backgroundColor: Colors.grey.shade100,
                                elevation: isSelected ? 4 : 0,
                                onSelected: (bool selected) {
                                  setState(() {
                                    if (selected) {
                                      _selectedGates.add(gate);
                                    } else {
                                      _selectedGates.remove(gate);
                                    }
                                  });
                                },
                              );"""

new_gate_chip = """                              return _buildCustomChip(
                                label: gate,
                                isSelected: isSelected,
                                selectedColor: _primaryColor.withValues(alpha: 0.8),
                                onTap: () {
                                  setState(() {
                                    if (isSelected) {
                                      _selectedGates.remove(gate);
                                    } else {
                                      _selectedGates.add(gate);
                                    }
                                  });
                                },
                              );"""

content = content.replace(old_gate_chip, new_gate_chip)

# 4. Replace Budget ChoiceChip
old_budget_chip = """                          return ChoiceChip(
                            label: Text(
                              _budgetDescriptions[budget] ?? '${budget}원',
                              style: TextStyle(fontWeight: isSelected ? FontWeight.bold : FontWeight.normal, color: isSelected ? Colors.white : Colors.black87),
                            ),
                            showCheckmark: false,
                            selected: isSelected,
                            selectedColor: _primaryColor,
                            backgroundColor: Colors.grey.shade100,
                            elevation: isSelected ? 4 : 0,
                            onSelected: (selected) {
                              setState(() {
                                if (selected) {
                                  _selectedBudgets.add(budget);
                                } else {
                                  _selectedBudgets.remove(budget);
                                }
                              });
                            },
                          );"""

new_budget_chip = """                          return _buildCustomChip(
                            label: _budgetDescriptions[budget] ?? '${budget}원',
                            isSelected: isSelected,
                            onTap: () {
                              setState(() {
                                if (isSelected) {
                                  _selectedBudgets.remove(budget);
                                } else {
                                  _selectedBudgets.add(budget);
                                }
                              });
                            },
                          );"""

content = content.replace(old_budget_chip, new_budget_chip)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
