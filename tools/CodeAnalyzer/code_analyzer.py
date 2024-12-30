import sys
import ast
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QMenuBar, QMenu, QAction, 
                            QFileDialog, QSplitter, QMessageBox, QPushButton,
                            QTabWidget, QToolBar)
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FF6B6B"))
        keywords = ['def', 'class', 'import', 'from', 'as', 'return', 'if', 'elif', 
                   'else', 'try', 'except', 'for', 'while', 'in', 'with', 'self']
        for word in keywords:
            self.highlighting_rules.append((f"\\b{word}\\b", keyword_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#98C379"))
        self.highlighting_rules.append(("\".*\"", string_format))
        self.highlighting_rules.append(("\'.*\'", string_format))  # Corrected line

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#5C6370"))
        self.highlighting_rules.append(("#.*", comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

class CodeAnalyzer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = None
        self.structure = {
            "imports": [],
            "classes": [],
            "functions": [],
            "global_variables": []
        }
    
    def parse_file(self):
        with open(self.file_path, 'r') as file:
            content = file.read()
            self.tree = ast.parse(content)
    
    def extract_docstring(self, node):
        return ast.get_docstring(node) or ""
    
    def analyze(self):
        if not hasattr(self, 'tree'):
            self.parse_file()
        
        for node in self.tree.body:
            if isinstance(node, ast.Import):
                for name in node.names:
                    self.structure["imports"].append(name.name)
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    self.structure["imports"].append(f"{module}.{name.name}")
            
            elif isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "docstring": self.extract_docstring(node),
                    "methods": []
                }
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "docstring": self.extract_docstring(item),
                            "args": [arg.arg for arg in item.args.args]
                        }
                        class_info["methods"].append(method_info)
                
                self.structure["classes"].append(class_info)
            
            elif isinstance(node, ast.FunctionDef):
                function_info = {
                    "name": node.name,
                    "docstring": self.extract_docstring(node),
                    "args": [arg.arg for arg in node.args.args]
                }
                self.structure["functions"].append(function_info)
            
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        self.structure["global_variables"].append(target.id)
    
    def get_json(self):
        return json.dumps(self.structure, indent=2)

class CodeAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Python Code Analyzer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Setup central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        
        analyze_action = QAction('Analyze', self)
        analyze_action.triggered.connect(self.analyzeCode)
        self.toolbar.addAction(analyze_action)
        
        markdown_action = QAction('Generate MD', self)
        markdown_action.triggered.connect(self.generateMarkdown)
        self.toolbar.addAction(markdown_action)
        
        
        # Splitter and text areas
        splitter = QSplitter(Qt.Horizontal)
        
        # Source code editor with syntax highlighting
        self.source_text = QTextEdit()
        self.source_text.setPlaceholderText("Original Python Code")
        self.python_highlighter = PythonHighlighter(self.source_text.document())
        
        # Tab widget for JSON and Markdown views
        self.tab_widget = QTabWidget()
        self.json_view = QTextEdit()
        self.markdown_view = QTextEdit()
        
        self.tab_widget.addTab(self.json_view, "JSON")
        self.tab_widget.addTab(self.markdown_view, "Markdown")
        
        splitter.addWidget(self.source_text)
        splitter.addWidget(self.tab_widget)
        layout.addWidget(splitter)
        
        self.createMenuBar()
        
    def createMenuBar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        open_action = QAction('Open...', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.openFile)
        
        save_analysis_action = QAction('Save Analysis...', self)
        save_analysis_action.setShortcut('Ctrl+S')
        save_analysis_action.triggered.connect(self.saveAnalysis)
        
        clear_action = QAction('Clear', self)
        clear_action.setShortcut('Ctrl+L')
        clear_action.triggered.connect(self.clearAll)
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(open_action)
        file_menu.addAction(save_analysis_action)
        file_menu.addSeparator()
        file_menu.addAction(clear_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Analysis menu
        analysis_menu = menubar.addMenu('Analysis')
        
        analyze_action = QAction('Analyze Code', self)
        analyze_action.setShortcut('F5')
        analyze_action.triggered.connect(self.analyzeCode)
        
        markdown_action = QAction('Generate Markdown', self)
        markdown_action.setShortcut('F6')
        markdown_action.triggered.connect(self.generateMarkdown)
        
        analysis_menu.addAction(analyze_action)
        analysis_menu.addAction(markdown_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.showAbout)
        
        help_menu.addAction(about_action)
    
    def openFile(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Python File", "", "Python Files (*.py);;All Files (*)")
        
        if file_name:
            try:
                with open(file_name, 'r') as file:
                    content = file.read()
                    self.source_text.setText(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file: {str(e)}")
    
    def saveAnalysis(self):
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:
            default_ext = "JSON Files (*.json)"
        else:
            default_ext = "Markdown Files (*.md)"
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save Analysis", "", f"{default_ext};;Text Files (*.txt);;All Files (*)")
        
        if file_name:
            try:
                with open(file_name, 'w') as file:
                    if current_tab == 0:
                        file.write(self.json_view.toPlainText())
                    else:
                        file.write(self.markdown_view.toPlainText())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
    
    def clearAll(self):
        self.source_text.clear()
        self.json_view.clear()
        self.markdown_view.clear()
    
    def analyzeCode(self):
        source_code = self.source_text.toPlainText()
        if not source_code.strip():
            QMessageBox.warning(self, "Warning", "No code to analyze!")
            return
        
        try:
            analyzer = CodeAnalyzer("temp.py")
            analyzer.tree = ast.parse(source_code)
            analyzer.analyze()
            
            analysis_result = json.dumps(analyzer.structure, indent=2)
            self.json_view.setText(analysis_result)
            self.tab_widget.setCurrentIndex(0)  # Switch to JSON tab
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
    
    def generateMarkdown(self):
        try:
            analysis_text = self.json_view.toPlainText()
            if not analysis_text:
                QMessageBox.warning(self, "Warning", "Please analyze the code first!")
                return
            
            structure = json.loads(analysis_text)
            markdown = self.structureToMarkdown(structure)
            self.markdown_view.setText(markdown)
            self.tab_widget.setCurrentIndex(1)  # Switch to Markdown tab
            self.saveMDOption(markdown)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate markdown: {str(e)}")

    def structureToMarkdown(self, structure):
        markdown = "# Code Structure Analysis\n\n"
        
        if structure["imports"]:
            markdown += "## Imports\n"
            for imp in structure["imports"]:
                markdown += f"- `{imp}`\n"
            markdown += "\n"
        
        if structure["classes"]:
            markdown += "## Classes\n"
            for class_info in structure["classes"]:
                markdown += f"### {class_info['name']}\n"
                if class_info["docstring"]:
                    markdown += f"{class_info['docstring']}\n\n"
                
                if class_info["methods"]:
                    markdown += "#### Methods\n"
                    for method in class_info["methods"]:
                        args_str = ", ".join(method["args"])
                        markdown += f"- `{method['name']}({args_str})`\n"
                        if method["docstring"]:
                            markdown += f"  - {method['docstring']}\n"
                markdown += "\n"
        
        if structure["functions"]:
            markdown += "## Functions\n"
            for func in structure["functions"]:
                args_str = ", ".join(func["args"])
                markdown += f"### `{func['name']}({args_str})`\n"
                if func["docstring"]:
                    markdown += f"{func['docstring']}\n"
                markdown += "\n"
        
        if structure["global_variables"]:
            markdown += "## Global Variables\n"
            for var in structure["global_variables"]:
                markdown += f"- `{var}`\n"
            markdown += "\n"
        
        return markdown

    def saveMDOption(self, markdown):
        reply = QMessageBox.question(self, 'Save Markdown',
                                   'Would you like to save the markdown to a file?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Markdown", "", "Markdown Files (*.md);;All Files (*)")
            
            if file_name:
                try:
                    with open(file_name, 'w') as file:
                        file.write(markdown)
                    QMessageBox.information(self, "Success", 
                                          "Markdown file saved successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", 
                                       f"Could not save markdown file: {str(e)}")
    
    def showAbout(self):
        QMessageBox.about(self, "About Python Code Analyzer",
                         "Python Code Analyzer\n\n"
                         "A tool for analyzing Python code structure.\n"
                         "Created with PyQt5 and Python's ast module.")

def main():
    app = QApplication(sys.argv)
    ex = CodeAnalyzerGUI()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
