"""
Contains the list of keywords for the CodeEditor autocompletion.
Includes Python built-ins, Matplotlib, and Seaborn functions.
"""

PYTHON_KEYWORDS = [
    "def", "class", "if", "else", "elif", "while", "for", "in", "return", 
    "try", "except", "import", "from", "as", "True", "False", "None", 
    "and", "or", "not", "break", "continue", "pass", "lambda", "with", 
    "is", "global", "raise", "yield", "print", "range", "len", "list", 
    "dict", "set", "str", "int", "float", "bool", "super", "__init__",
    "self", "open", "zip", "enumerate", "isinstance", "abs", "all", "any",
    "bin", "callable", "chr", "classmethod", "compile", "complex", "delattr",
    "dir", "divmod", "eval", "exec", "filter", "format", "getattr", "globals",
    "hasattr", "hash", "help", "hex", "id", "input", "issubclass", "iter",
    "locals", "map", "max", "min", "next", "object", "oct", "ord", "pow",
    "property", "repr", "reversed", "round", "setattr", "slice", "sorted",
    "staticmethod", "sum", "tuple", "type", "vars"
]

MATPLOTLIB_KEYWORDS = [
    "plot", "scatter", "bar", "barh", "hist", "boxplot", "violinplot",
    "errorbar", "pie", "stackplot", "stem", "step", "fill_between",
    "imshow", "pcolormesh", "contour", "contourf", "quiver", "streamplot",
    "xlabel", "ylabel", "title", "legend", "grid", "xlim", "ylim",
    "xticks", "yticks", "axis", "axhline", "axvline", "axhspan", "axvspan",
    "text", "annotate", "figure", "subplots", "subplot", "savefig", "show",
    "clf", "cla", "close", "gcf", "gca", "tight_layout", "margins",
    "subplots_adjust", "twinx", "twiny", "semilogx", "semilogy", "loglog"
]

SEABORN_KEYWORDS = [
    "scatterplot", "lineplot", "displot", "histplot", "kdeplot", "ecdfplot",
    "rugplot", "catplot", "stripplot", "swarmplot", "boxplot", "violinplot",
    "boxenplot", "pointplot", "barplot", "countplot", "lmplot", "regplot",
    "residplot", "heatmap", "clustermap", "pairplot", "jointplot", "relplot",
    "set_theme", "set_style", "set_palette", "set_context", "color_palette",
    "light_palette", "dark_palette", "diverging_palette", "cubehelix_palette",
    "despine", "move_legend"
]

AUTOCOMPLETE_KEYWORDS = sorted(list(set(
    PYTHON_KEYWORDS + MATPLOTLIB_KEYWORDS + SEABORN_KEYWORDS
)))