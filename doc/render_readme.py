# import argparse
import logging
import json
from jinja2 import Environment, FileSystemLoader
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.interfaces import Context
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor

# from pydoc_markdown.contrib.processors.google import GoogleProcessor
# from wvutils.path import resolve_path

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def load_config(config_file: str) -> dict:
    # TODO: Resolve paths here
    with open(config_file, mode="r", encoding="utf-8") as file:
        return json.loads(file.read())


def render_library_contents(directory: str, packages: list[str]) -> str:
    """Render the library contents section of the readme.

    Args:
        directory (str): The directory to search for modules.
        packages (list[str]): The packages to search for modules.

    Returns:
        str: The rendered library contents section.
    """
    # context = Context(directory=resolve_path(directory))
    context = Context(directory=directory)
    session = PydocMarkdown(
        loaders=[
            PythonLoader(packages=packages, encoding="utf-8"),
        ],
        processors=[
            FilterProcessor(
                expression="not name.startswith('_') and default()",
                documented_only=True,
                exclude_private=True,
                exclude_special=True,
                do_not_filter_modules=True,
                skip_empty_modules=True,
            ),
            SmartProcessor(),
            CrossrefProcessor(),
        ],
        renderer=MarkdownRenderer(
            filename="library_content.md",
            encoding="utf-8",
            insert_header_anchors=True,
            html_headers=False,
            code_headers=True,
            descriptive_class_title=True,
            descriptive_module_title=True,
            add_module_prefix=True,
            add_method_class_prefix=True,
            add_member_class_prefix=True,
            # add_full_prefix=True,
            # sub_prefix=True,
            data_code_block=False,
            data_expression_maxlength=100,
            classdef_code_block=True,
            signature_with_decorators=True,
            signature_in_header=False,
            signature_code_block=True,
            # signature_with_vertical_bar=True,
            signature_with_def=True,
            signature_class_prefix=False,
            render_typehint_in_data_header=True,
            code_lang=True,
            toc_maxdepth=2,
            render_module_header=True,
            docstrings_as_blockquote=True,
            source_format="[[view_source]]({url})",
            escape_html_in_docstring=False,
            format_code=True,
            format_code_style="pep8",
        ),
    )
    session.init(context)
    session.ensure_initialized()
    modules = session.load_modules()
    session.process(modules)
    # session.run_hooks("post-render")
    session.render(modules, run_hooks=True)
    with open("library_content.md", mode="r", encoding="utf-8") as file:
        return file.read()


def main() -> None:  # config_file: str, template_file: str, output_file: str, replace: bool) -> None:
    # Load the config
    with open("config.json", mode="r", encoding="utf-8") as file:
        config = json.loads(file.read())

    # Generate the library documentation
    library_contents = render_library_contents(config["directory"], config["packages"])
    logger.info(f"{library_contents = }")

    # Render the markdown readme
    # TODO: Move this to a separate function?
    loader = FileSystemLoader(config["templates_folder"])
    environment = Environment(loader=loader, auto_reload=False)
    template = environment.get_template(config["main_template"])
    rendered = template.render(
        **config["template_data"],
        library_contents=library_contents,
    )
    # logger.info(rendered)
    with open(config["output_file"], mode="w", encoding="utf-8") as file:
        file.write(rendered)


if __name__ == "__main__":
    # TODO: Implement argparse here
    main()
