import sys
import os
import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from PyQt6.QtWidgets import *
from PyQt6.QtWebEngineWidgets import QWebEngineView

def markdown_to_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Convert Markdown to HTML with code highlighting
    html_content = markdown.markdown(
        md_content,
        extensions=['fenced_code', CodeHiliteExtension(linenums=False)]
    )

    # CSS for dark theme with syntax highlighting for code blocks
    dark_theme_css = """
    <style>
        body {
            background-color: #1e1e1e;
            color: #d4d4d4;
            font-family: Arial, sans-serif;
            padding: 15px;
        }
        a {
            color: #569cd6;
        }
        pre {
            background-color: #2d2d2d;
            color: #dcdcdc;
            padding: 10px;
            border-radius: 5px;
            overflow: auto;
        }
        code {
            color: #ce9178;
        }
        .codehilite {
            background: #2d2d2d;
            border-radius: 5px;
            padding: 10px;
            overflow: auto;
        }
        .codehilite pre {
            margin: 0;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #569cd6;
        }
    </style>
    """

    # Combine HTML with the dark theme CSS
    full_html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        {dark_theme_css}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    return full_html_content

class HelpWidget(QWidget):
    def __init__(self, chapters_dir, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Help Contents')
        self.resize(1000, 700)
        self.chapters_dir = chapters_dir

        # Layout generale
        main_layout = QVBoxLayout(self)

        # Creazione dello splitter per separare la lista dei capitoli dalla vista del contenuto
        splitter = QSplitter(self)

        # Lista dei capitoli
        self.chapters_list = QListWidget()
        self.load_chapters_list()
        splitter.addWidget(self.chapters_list)

        # WebView per visualizzare il contenuto del capitolo
        self.webView = QWebEngineView(self)
        splitter.addWidget(self.webView)

        # Configurazione della proporzione tra lista e vista del contenuto
        splitter.setStretchFactor(0, 1)  # Lista dei capitoli (fattore di ridimensionamento minore)
        splitter.setStretchFactor(1, 4)  # Vista del contenuto (fattore di ridimensionamento maggiore)

        main_layout.addWidget(splitter)

        # Pulsante di chiusura
        close_button = QPushButton("Close Help")
        close_button.clicked.connect(self.close)
        main_layout.addWidget(close_button)

        # Connessione del segnale per selezionare il capitolo
        self.chapters_list.itemClicked.connect(self.load_selected_chapter)

        # Caricare direttamente il capitolo due
        self.load_chapter_by_name("chapter2.md")

    def load_chapters_list(self):
        """
        Carica la lista dei capitoli disponibili dalla directory.
        """
        for file_name in os.listdir(self.chapters_dir):
            if file_name.endswith('.adoc') or file_name.endswith('.md'):
                self.chapters_list.addItem(file_name)

    def load_selected_chapter(self, item):
        """
        Carica il contenuto del capitolo selezionato nel QWebEngineView.
        """
        file_name = item.text()
        self.load_chapter(file_name)

    def load_chapter_by_name(self, chapter_name):
        """
        Carica un capitolo specifico per nome.
        """
        for index in range(self.chapters_list.count()):
            item = self.chapters_list.item(index)
            if item.text() == chapter_name:
                self.chapters_list.setCurrentItem(item)
                self.load_chapter(chapter_name)
                break

    def load_chapter(self, file_name):
        """
        Carica il contenuto del capitolo specificato.
        """
        file_path = os.path.join(self.chapters_dir, file_name)

        if file_name.endswith('.md'):
            html_content = markdown_to_html(file_path)
        else:
            html_content = "<h1>Unsupported file format.</h1>"

        self.webView.setHtml(html_content)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = HelpWidget('chapters')
    widget.show()
    sys.exit(app.exec())
