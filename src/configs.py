DIAGRAM_CONFIGS = {
    "mermaid": {
        "language": "mermaid",
        "file_extension": ".mmd",
        "parse_format": "mermaid",
        # "output_directory": "generated_diagram_mermaid",
    },
    "tikz": {
        "language": "tikz/LaTeX",
        "file_extension": ".tex",
        "parse_format": "latex",
        # "output_directory": "generated_diagram_latex",
    },
    "drawio": {
        "language": "drwaio mxGraph/xml",
        "file_extension": ".drawio",
        "parse_format": "xml",
        # "output_directory": "generated_diagram_drawio_with_image",
    },
    "svg": {
        "language": "svg",
        "file_extension": ".svg",
        "parse_format": "svg",
        # "output_directory": "generated_diagram_svg",
    },
}

ENGINE_CONFIGS = {
    "text_analysis": "gpt-4.1",
    "layout_generation": "gpt-4.1",
    "layout_refinement": "gpt-4.1",
    "graphic_code_verification": "gpt-4.1",
    "element_discriminator": "gpt-4.1",
    "image_retrieval": "gpt-4.1",
    "svg_generation": "gpt-4.1",
}