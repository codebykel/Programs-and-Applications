import prcs
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs.dialogs import Messagebox
from tkinter import filedialog
from threading import Thread


class App(tb.Window):
    def __init__(self):
        super().__init__(
            title="PDF Highlighter", 
            themename="litera", 
            resizable=(False, False)
        )
        self.geometry("300x230")
        self.position_center()

        self.progressBar = tb.Progressbar(self)
        self.progressBar.pack(padx=10, pady=(3, 0), fill=X)

        # = Widgets for getting the directory of the PDF the will be highlighted =

        self.frameDir = tb.LabelFrame(self, text="Open File Directory", padding=5)

        tb.Button(self.frameDir, text="Open File", command=self.openFile).grid(row=0, column=0, padx=(0, 5))

        self.dir = tb.Entry(self.frameDir)
        self.dir.grid(row=0, column=1)

        self.frameDir.pack(pady=5)


        # ====== Widgets for choosing the highlight mode ===========

        self.frameHmode = tb.LabelFrame(self, text="Highlight Mode", padding=5)
        self.mode = tb.StringVar()

        tb.Radiobutton(
            self.frameHmode, 
            text="Summary", 
            variable=self.mode, 
            value="summary",
            command=self.click
        ).grid(row=0, column=0, padx=(50, 5))

        tb.Radiobutton(
            self.frameHmode, 
            text="Keyword", 
            variable=self.mode, 
            value="keyword",
            command=self.click
        ).grid(row=0, column=1, padx=(5, 50))

        self.keyword = tb.Entry(self.frameHmode, width=31)

        self.frameHmode.pack(fill=X, padx=11)

        # ================ Submit =====================================

        tb.Button(
            self, 
            text="Highlight", 
            command=lambda:Thread(target=self.highlight).start()
        ).pack(pady=15)



    # Hide or show the entry for keywords based on the chosen radio button.
    def click(self):
        if self.mode.get() == "keyword":
            self.keyword.grid(row=1, column=0, columnspan=2, padx=(0, 5), pady=(5, 0))
        else:
            self.keyword.grid_forget()

        
    def openFile(self):
        dir = filedialog.askopenfilename(
            title="Select PDF",
            initialdir="~/Documents",
            filetypes=[("PDF Files", "*.pdf")]
        )

        # Delete the current directory from the entry and insert a new one if the user had chosen a new directory.
        if dir:
            self.dir.delete(0, END)
            self.dir.insert(0, dir)
    

    def highlight(self):
        self.progressBar.configure(bootstyle=PRIMARY)

        pages = prcs.extractText(self.dir.get(), self.progressBar)

        if pages[0] == 400:
            Messagebox.show_warning("Invalid File Directory")
            return
        
        pageHighlights = prcs.getHighlight(
            self.mode.get(), 
            self.keyword.get().split(", "), 
            pages,
            self.progressBar
        )

        prcs.makeHighlightedPDF(
            self.mode.get(),
            pageHighlights, 
            self.dir.get(),
            self.progressBar,
        )

        self.progressBar.configure(bootstyle=SUCCESS)


if __name__ == "__main__":
    app = App()
    app.mainloop()