import subprocess

latex_content = r"""
\documentclass{article}
\begin{document}
Hello, world!
\end{document}
"""

with open("output.tex", "w") as f:
    f.write(latex_content)

subprocess.run(["pdflatex", "output.tex"])
