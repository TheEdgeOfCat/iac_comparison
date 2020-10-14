# -*- coding: utf-8 -*-

# -- Project information -----------------------------------------------------
project = 'edifice-corb serverless architecture'
copyright = '2020, Pavle Portic'
author = 'Pavle Portic'
version = '0.1.0'

# -- General configuration ---------------------------------------------------
extensions = ['sphinx_revealjs']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = [
	'_build',
	'Dockerfile',
	'watch.sh',
]
pygments_style = None

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'
html_theme_options = {
	'revealjs_theme': 'league',
}
html_static_path = ['_static']

# -- Options for Reveal.js output ---------------------------------------------
revealjs_style_theme = 'black'
revealjs_script_conf = '''
	{
		controls: true,
		progress: true,
		history: true,
		center: true,
		transition: "slide",
	}
'''
revealjs_script_plugins = [
	{
		'src': 'revealjs/plugin/notes/notes.js',
		'options': '{async: true}',
	},
	{
		'src': 'revealjs/plugin/highlight/highlight.js',
		'options': '{async: true, callback: function() { hljs.initHighlightingOnLoad(); }}',
	},
]
