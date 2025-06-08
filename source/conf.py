import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.resolve().as_posix())

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Nat's blog"
copyright = "2025, Nathan Furnal"  # noqa: A001
author = "Nathan Furnal"
version = "2025.06.02"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.duration", "sphinx.ext.githubpages", "sphinx_copybutton"]

templates_path = ["_templates"]
exclude_patterns = []
today_fmt = "%Y-%m-%d"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

pygments_style = "style.ModusOperandiStyle"
pygments_dark_style = "style.ModusVivendiStyle"
html_title = (
    "Gribouillis <p style='font-size:0.65em;'><em>small mindless sketch</em></p>"
)
html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["luciole.css", "juliamono.css", "custom.css"]

html_theme_options = {
    # Light mode (Modus Operandi) colors
    "light_css_variables": {
        # Dark mode inherits fonts from light mode, only set it once
        "font-stack": "Luciole, sans-serif",
        "font-stack--monospace": "Julia Mono, monospace",
        "font-stack--headings": "Luciole, serif",
        # Main brand colors
        "color-brand-primary": "#0031a9",  # blue
        "color-brand-content": "#0031a9",  # blue
        # Foreground (text) colors
        "color-foreground-primary": "#000000",  # fg-main
        "color-foreground-secondary": "#595959",  # fg-dim
        "color-foreground-muted": "#9f9f9f",  # border
        "color-foreground-border": "#9f9f9f",  # border
        # Background colors
        "color-background-primary": "#ffffff",  # bg-main
        "color-background-secondary": "#f0f0f0",  # bg-dim
        "color-background-hover": "#c0deff",  # bg-completion
        "color-background-border": "#9f9f9f",  # border
        # Admonition colors (using Modus nuanced backgrounds)
        "color-admonition-background": "#f3f3ff",  # bg-blue-nuanced
        # API documentation colors
        "color-api-background": "#f3f3ff",  # bg-blue-nuanced
        "color-api-background-hover": "#c0deff",  # bg-completion
        "color-api-overall": "#0031a9",  # blue
        # Highlighted text
        "color-highlighted-background": "#c0deff",  # bg-completion
        "color-highlighted-text": "#000000",  # fg-main
        # Guild navigation
        "color-guilabel-background": "#e0e0e0",  # bg-inactive
        "color-guilabel-border": "#9f9f9f",  # border
        "color-guilabel-text": "#000000",  # fg-main
        # Inline code
        "color-inline-code-background": "#f3f3ff",  # bg-blue-nuanced
        # Link colors
        "color-link": "#0031a9",  # blue
        "color-link-underline": "#0031a9",  # blue
        "color-link--hover": "#354fcf",  # blue-warmer
        "color-link-underline--hover": "#354fcf",  # blue-warmer
        # Problematic (error) content
        "color-problematic": "#a60000",  # red
        # Sidebar colors
        "color-sidebar-background": "#f0f0f0",  # bg-dim
        "color-sidebar-background-border": "#9f9f9f",  # border
        "color-sidebar-brand-text": "#000000",  # fg-main
        "color-sidebar-caption-text": "#595959",  # fg-dim
        "color-sidebar-link-text": "#000000",  # fg-main
        "color-sidebar-link-text--top-level": "#000000",  # fg-main
        "color-sidebar-item-background--current": "#c0deff",  # bg-completion
        "color-sidebar-item-background--hover": "#94d4ff",  # bg-hover
        "color-sidebar-item-expander-background": "#e0e0e0",  # bg-inactive
        "color-sidebar-item-expander-background--hover": "#c4c4c4",  # bg-active
        "color-sidebar-search-background": "#ffffff",  # bg-main
        "color-sidebar-search-background--focus": "#ffffff",  # bg-main
        "color-sidebar-search-border": "#9f9f9f",  # border
        "color-sidebar-search-icon": "#595959",  # fg-dim
        # Table colors
        "color-table-background": "#ffffff",  # bg-main
        "color-table-border": "#9f9f9f",  # border
        "color-table-header-background": "#e0e0e0",  # bg-inactive
        "color-table-header-text": "#000000",  # fg-main
        # Announcement banner
        "color-announcement-background": "#fff3da",  # bg-yellow-nuanced
        "color-announcement-text": "#553d00",  # fg-changed
        # Cards and containers
        "color-card-background": "#ffffff",  # bg-main
        "color-card-border": "#9f9f9f",  # border
        "color-card-marginals-background": "#f0f0f0",  # bg-dim
    },
    # Dark mode (Modus Vivendi) colors
    "dark_css_variables": {
        # Main brand colors
        "color-brand-primary": "#2fafff",  # blue
        "color-brand-content": "#2fafff",  # blue
        # Foreground (text) colors
        "color-foreground-primary": "#ffffff",  # fg-main
        "color-foreground-secondary": "#989898",  # fg-dim
        "color-foreground-muted": "#646464",  # border
        "color-foreground-border": "#646464",  # border
        # Background colors
        "color-background-primary": "#000000",  # bg-main
        "color-background-secondary": "#1e1e1e",  # bg-dim
        "color-background-hover": "#2f447f",  # bg-completion
        "color-background-border": "#646464",  # border
        # Admonition colors
        "color-admonition-background": "#0f0e39",  # bg-blue-nuanced
        # API documentation colors
        "color-api-background": "#0f0e39",  # bg-blue-nuanced
        "color-api-background-hover": "#2f447f",  # bg-completion
        "color-api-overall": "#2fafff",  # blue
        # Highlighted text
        "color-highlighted-background": "#2f447f",  # bg-completion
        "color-highlighted-text": "#ffffff",  # fg-main
        # Guild navigation
        "color-guilabel-background": "#303030",  # bg-inactive
        "color-guilabel-border": "#646464",  # border
        "color-guilabel-text": "#ffffff",  # fg-main
        # Inline code
        "color-inline-code-background": "#0f0e39",  # bg-blue-nuanced
        # Link colors
        "color-link": "#2fafff",  # blue
        "color-link-underline": "#2fafff",  # blue
        "color-link--hover": "#79a8ff",  # blue-warmer
        "color-link-underline--hover": "#79a8ff",  # blue-warmer
        # Problematic (error) content
        "color-problematic": "#ff5f59",  # red
        # Sidebar colors
        "color-sidebar-background": "#1e1e1e",  # bg-dim
        "color-sidebar-background-border": "#646464",  # border
        "color-sidebar-brand-text": "#ffffff",  # fg-main
        "color-sidebar-caption-text": "#989898",  # fg-dim
        "color-sidebar-link-text": "#ffffff",  # fg-main
        "color-sidebar-link-text--top-level": "#ffffff",  # fg-main
        "color-sidebar-item-background--current": "#2f447f",  # bg-completion
        "color-sidebar-item-background--hover": "#004f70",  # bg-hover
        "color-sidebar-item-expander-background": "#303030",  # bg-inactive
        "color-sidebar-item-expander-background--hover": "#535353",  # bg-active
        "color-sidebar-search-background": "#000000",  # bg-main
        "color-sidebar-search-background--focus": "#000000",  # bg-main
        "color-sidebar-search-border": "#646464",  # border
        "color-sidebar-search-icon": "#989898",  # fg-dim
        # Table colors
        "color-table-background": "#000000",  # bg-main
        "color-table-border": "#646464",  # border
        "color-table-header-background": "#303030",  # bg-inactive
        "color-table-header-text": "#ffffff",  # fg-main
        # Announcement banner
        "color-announcement-background": "#221000",  # bg-yellow-nuanced
        "color-announcement-text": "#efef80",  # fg-changed
        # Cards and containers
        "color-card-background": "#000000",  # bg-main
        "color-card-border": "#646464",  # border
        "color-card-marginals-background": "#1e1e1e",  # bg-dim
    },
    # Other Furo options
    "sidebar_hide_name": False,  # Show project name in sidebar
    "navigation_with_keys": True,  # Allow keyboard navigation
}
