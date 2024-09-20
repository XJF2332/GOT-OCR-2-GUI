import matplotlib.pyplot as plt

latex = r"""\documentclass{article}%
\usepackage[T1]{fontenc}%
\usepackage[utf8]{inputenc}%
\usepackage{lmodern}%
\usepackage{textcomp}%
\usepackage{lastpage}%
%
%
%
\begin{document}%
\normalsize%

\documentclass{article}
\usepackage{amsmath}
\begin{document}
\section{Introduction}
Here is some text and an equation:
\begin{equation}
E = mc^2
\end{equation}
\end{document}
%
\end{document}"""

# 使用LaTeX
plt.figure(figsize=(8, 6))
plt.title(latex)
plt.savefig('latex_matplotlib.pdf')
