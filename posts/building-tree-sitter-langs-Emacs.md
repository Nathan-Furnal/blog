---
title: "Building tree-sitter languages for Emacs"
date: 2022-12-31T00:00:00+01:00
tags: ["emacs"]
categories: ["misc"]
draft: false
---

# Building tree-sitter languages for Emacs

## Emacs 29 tree-sitter support {#emacs-29-tree-sitter-support}

If you follow Emacs' development, you'll probably have heard that the upcoming
29 release will have support for [tree-sitter](https://tree-sitter.github.io/), which is an incremental code
parser. In short, it provides a syntax tree for the source file that you're
currently viewing. This is especially useful for syntax highlighting as well as
code navigation. Since it builds a syntax tree for the language, we can actually
get proper highlighting that isn't regex dependent, Emacs' highlighting strategy
for most languages. As such, we'll get faster highlighting and avoid
re-fontification when simple characters are missing, like commas or equal signs.

The ability to navigate the code will also be enhanced, since it'll now be
possible to be more specific during the code editing process: getting variables
inside a specific class, act on all function, act on inner blocks, etc. There is
already some works to do this, in the form of [tree-edit](https://github.com/ethan-leba/tree-edit). A nice user on reddit
also added [a list of structural editing](https://www.reddit.com/r/emacs/comments/r0i031/comment/hlxwhyu/) modes for Emacs.

The new support for tree-sitter can be found by building from the `emacs-29`
branch or building from the main branch. It has been dubbed `treesit.el` and is
already documented; you'll have to type `C-h i` to open the info pages. After,
navigate to "Elisp" and then "Parsing Program Source", which is the information
page detailing the use of this new package.

Right now, some modes like _python-mode_ or _c-mode_ have a tree-sitter
equivalent, _python-ts-mode_ and _c-ts-mode_ respectively; there are other modes
as well, you just need to search for that extra "ts" in the mode's name. If you
try to use those modes though, you'll get an error explaining that the
corresponding library is not available. That's because you need, on top of
installing tree-sitter, to install a language's corresponding parsing
library. There are already some notes [on how to install](https://git.savannah.gnu.org/cgit/emacs.git/tree/admin/notes/tree-sitter/starter-guide?h=feature/tree-sitter) those languages, as well
as a script that automates it.

I wanted a simple Makefile alternative though, which is explained below.


## Building the tree-sitter parsers manually {#building-the-tree-sitter-parsers-manually}

The following _Makefile_ rests on some assumptions:

-   You already have tree-sitter installed and built Emacs **after** installing
    tree-sitter and with the `--with-tree-sitter` flag.

-   You have a Unix like system, though this should be easily to change for a DOS
    like system.

-   You're storing the different parsers in the same directory.

-   You're putting the shared libraries in the `~/.emacs.d/tree-sitter/`
    folder. If not, you need to point Emacs to the proper directory with the
    `treesit-extra-load-path` variable in your `init.el`.

For example, I have a directory called `pkgs/langs/` where I put the packages I
manage manually and I added a languages sub-folder where I clone all the
repositories, [which you can find here](https://github.com/orgs/tree-sitter/repositories), on the project's page. If I wanted to
download the Python parser, I would do:

```sh
cd ~/pkgs/langs/
git clone git@github.com:tree-sitter/tree-sitter-python.git
```

Same goes for other languages like Javascript, C/C++, Rust,...

Now, I have the following Makefile in the `pkgs/langs/` directory which builds
all the languages and stores the parsers (which are shared libraries) in the
`~/.emacs.d/tree-sitter/` directory.

```makefile
CC := gcc # or clang
SUBDIRS := $(wildcard tree-sitter-*)
EXT := so # dylib on MacOS and dll on Windows
SRC_DIR := src
CPPFLAGS := -shared -fPIC -g -O2
OUTPUT_DIR := $(HOME)/.emacs.d/tree-sitter # HOME is defined on Unix like systems
EXECS := $(patsubst %,$(OUTPUT_DIR)/lib%.$(EXT),$(SUBDIRS)) # tree-sitter-python -> libtree-sitter-python.so
# For each subdir, find the files in the source folder which are parser.c* or scanner.c*
FILES := $(foreach dir,$(SUBDIRS),$(wildcard $(dir)/$(SRC_DIR)/parser.c* $(dir)/$(SRC_DIR)/scanner.c*))

all: $(SUBDIRS)

$(SUBDIRS):
# Compiler + flags + include source + filter only files from current dir and output with correct extension
	$(CC) $(CPPFLAGS) -I$@/$(SRC_DIR) $(filter $@%,$(FILES)) -o $(OUTPUT_DIR)/lib$@.$(EXT)

clean:
	rm -f $(EXECS) # use the del command on DOS systems

# avoids considering all, clean or the subdirs as files and override targets
.PHONY:	all clean $(SUBDIRS)
```

Now, you can simply run:

```sh
make -j12 # or whatever number of cores you have
```


## Native Emacs solution {#native-emacs-solution}

I learned that as of December 30<sup>th</sup> 2022, there is a native solution to
install the grammars. One only needs to specify `treesit-language-source-alist`
with the languages and their corresponding URL to the parser repository. This
provides the required shared library in the `.emacs.d/tree-sitter` directory. I
also took the liberty to add a function that installs (or updates) all the
currently available parsers.

Like that, you can either use the interactive
`treesit-install-language-grammar` function to install or update one specific
language from the list, or my own function to update them all.

```lisp
(use-package treesit
  :commands (treesit-install-language-grammar nf/treesit-install-all-languages)
  :init
  (setq treesit-language-source-alist
   '((bash . ("https://github.com/tree-sitter/tree-sitter-bash"))
     (c . ("https://github.com/tree-sitter/tree-sitter-c"))
     (cpp . ("https://github.com/tree-sitter/tree-sitter-cpp"))
     (css . ("https://github.com/tree-sitter/tree-sitter-css"))
     (go . ("https://github.com/tree-sitter/tree-sitter-go"))
     (html . ("https://github.com/tree-sitter/tree-sitter-html"))
     (javascript . ("https://github.com/tree-sitter/tree-sitter-javascript"))
     (json . ("https://github.com/tree-sitter/tree-sitter-json"))
     (lua . ("https://github.com/Azganoth/tree-sitter-lua"))
     (make . ("https://github.com/alemuller/tree-sitter-make"))
     (ocaml . ("https://github.com/tree-sitter/tree-sitter-ocaml" "ocaml/src" "ocaml"))
     (python . ("https://github.com/tree-sitter/tree-sitter-python"))
     (php . ("https://github.com/tree-sitter/tree-sitter-php"))
     (typescript . ("https://github.com/tree-sitter/tree-sitter-typescript" "typescript/src" "typescript"))
     (ruby . ("https://github.com/tree-sitter/tree-sitter-ruby"))
     (rust . ("https://github.com/tree-sitter/tree-sitter-rust"))
     (sql . ("https://github.com/m-novikov/tree-sitter-sql"))
     (toml . ("https://github.com/tree-sitter/tree-sitter-toml"))
     (zig . ("https://github.com/GrayJack/tree-sitter-zig"))))
  :config
  (defun nf/treesit-install-all-languages ()
    "Install all languages specified by `treesit-language-source-alist'."
    (interactive)
    (let ((languages (mapcar 'car treesit-language-source-alist)))
      (dolist (lang languages)
	      (treesit-install-language-grammar lang)
	      (message "`%s' parser was installed." lang)
	      (sit-for 0.75)))))
```

Voilà!
