import prcs
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from threading import Thread


class App(tb.Window):
    def __init__(self):
        super().__init__(
            title="Highlight",
            themename="superhero",
            resizable=(False, False)
        )
        self.geometry("300x235")
        self.position_center()

        self.progressBar = tb.Progressbar(self)
        self.progressBar.pack(padx=10, pady=(3, 0), fill=X)

        # = Widgets for getting the directory of the PDF that will be highlighted =

        self.frameDir = tb.LabelFrame(self, text="Open File Directory", padding=5)

        tb.Button(
            self.frameDir, 
            text="Open File",
            command=self.openFile,
            bootstyle=DANGER,
        ).grid(row=0, column=0, padx=(0, 5))

        self.dir = tb.Entry(self.frameDir)
        self.dir.grid(row=0, column=1)

        self.frameDir.pack(pady=5)

        # ====== Widgets for choosing the highlight mode ===========

        self.frameHmode = tb.LabelFrame(self, text="Highlight Mode", padding=5)

        self.mode = tb.StringVar()

        """
        I chose the radio button from tkinter rather than ttkbootstrap
        due to an unknown error where the program instantly crushes
        whenever I run the compiled version from pyinstaller.
        """
        tk.Radiobutton(
            self.frameHmode, 
            text="Summary", 
            variable=self.mode, 
            value="summary",
            command=self.click
        ).grid(row=0, column=0, padx=(40, 5))

        tk.Radiobutton(
            self.frameHmode, 
            text="Keyword", 
            variable=self.mode, 
            value="keyword",
            command=self.click
        ).grid(row=0, column=1, padx=(5, 40))

        self.keyword = tb.Entry(self.frameHmode, width=31)

        self.frameHmode.pack(fill=X, padx=11)

        # ================ Submit =====================================

        tb.Button(
            self, 
            text="Highlight", 
            bootstyle=DANGER,
            command=lambda:Thread(target=self.highlight).start()
        ).pack(pady=15)

    
    def openFile(self):
        dir = tk.filedialog.askopenfilename(
            title="Select PDF",
            initialdir="~/Documents",
            filetypes=[("PDF Files", "*.pdf")]
        )

        """ 
        Delete the current directory from entry and insert
        a new one if the user has chosen a new directory. 
        """
        if dir:
            self.dir.delete(0, END)
            self.dir.insert(0, dir) 


    # Hide or show the entry for keywords based on the chosen radio button.
    def click(self):
        if self.mode.get() == "keyword":
            self.keyword.grid(row=1, column=0, columnspan=2, padx=(0, 5), pady=(5, 0))
        else:
            self.keyword.grid_forget()

    
    def highlight(self):
        self.progressBar.configure(bootstyle=PRIMARY)

        dir = self.dir.get().strip()

        # Ensure that the path to file is not empty.
        if dir == "":
            tk.messagebox.showerror(
                title="Error", 
                message="There is no file to highlight"
            )
            return

        pages, status = prcs.extractText(dir, self.progressBar)

        # Ensure that the directory is valid. Status will return 200 if valid.
        if status == 404:
            tk.messagebox.showerror(
                title="Error", 
                message="Invalid File Directory"
            )
            return

        # Ensure that the user had chosen a highlight mode.
        if self.mode.get() == "":
            tk.messagebox.showerror(
                title="Error", 
                message="Choose highlight mode first"
            )
            self.progressBar.configure(bootstyle=WARNING)
            return
        
        mode = self.mode.get()
        keywords = self.keyword.get().split(", ")

        pageHighlights = prcs.getHighlight(
            mode, 
            keywords, 
            pages,
            self.progressBar
        )

        prcs.makeHighlightedPDF(
            mode,
            keywords,
            pageHighlights, 
            dir,
            self.progressBar,
        )

        self.progressBar.configure(bootstyle=SUCCESS)


if __name__ == "__main__":
    app = App()
    app.mainloop()
