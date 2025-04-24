correction_decision_prompt = """You are an expert in evaluating a decision about whether a diagram needs to be updated or not according to a suggestion to a diagram. \
You will be given the description of a suggestion to a diagram. You should output the decision. Yes means the diagram needs to be updated. No means the diagram does not need to be updated.\
You should put the decision inside the <decision></decision> tag.

Suggestion:
"""

get_description_prompt = """You are an expert in designing and describing a scientific figure given the \
caption and the content of the paper. You should give a detailed description of the the designed layout of \
the figure. Output the description within the <description> </description> tag. 

Generally speaking, a scientific figure may contains some of these following parts:
1. Textual Elements which represents the titles, labels etc;
2. Graphical Elements like icons, illustrations, visual tokens, emoji-like figures to clarify some concepts;
3. Connection Elements like directed edges or arrows to show information flow.

You should follow the following steps:

1. Read the paper comprehensively and extract all the information that relates to the caption.
2. Based on the caption and paper content, identify the components and design the layout of the figure.
3. Generate a detailed description of the figure. The description should comepletely come from the paper. \
And it should match the caption.
4. Check the description with the caption and the paper, make sure the description is correct and \
complete. If not, revise the description until it is correct and complete.
5. Wrap the description within the <description></description> tag.

Think step by step and make sure the description is clear and detailed which could be used to generate the figure.

Paper Content:
{paper_content}
Caption:
{caption}
"""

diagram_generation_prompt = """You are an expert in scientific visualization and {language} generation.\
Given a description of a figure from a scientific paper, generate a {language} compatible \
conceptual diagram. After generation, you need to verify to make sure it could be executed without any error.

You could follow the following steps:

1. analyze the description and identify the type, textual elements, graphical elements and layout of the figure
2. generate the executable {language} code for all the components and layout
3. make sure the code covers all the components of the description
4. for graphical elements (e.g., images, icons), insert an placeholder node with the format: `"style="shape=image;"` \
without the actual visual content, but the id should be the name of the element.
5. use clear layout: left-to-right or top-down pipeline structure.
6. do not generate legends for the figure
7. return your result in a code block wrapped with ```

Think step by step and make sure the diagram is clear and matches the description and the caption.

Description:
{description}
Code:
"""

refinement_prompt = """You are an expert in evaluating a scientific figure with the {language}. \
Given the description, the caption and the code of the figure, you need to check if there is any improvement \
in terms of logic and visual quality. 

You should follow the following steps:

1. analyze the description and the caption of the figure to undertand the components and layout of the figure
2. analyze the code and consider how the scientific figure can be enhanced to make it match the description and caption
3. consider how to arrange the components and layout of the figure to make it more applealing to the reader
4. try to avoid overlap of components as much as possible
5. for graphical elements (e.g., images, icons), make sure the size is reasonable and the placeholder node remains the same.
6. for textual elements, make sure the labels should be concise and clear, long text may break the layout
7. if the code is good enough, you should not make any changes to the code

You will first need to decide if any improvement is needed. You should wrap your decision inside the <decision></decision> tag.
You should only input yes or no inside the <decision></decision> tag.

If the decision is yes, you should then generate the improved code in a code block wrapped with ```. Output the entire enhanced code, not just the modified portions.

Think step by step and output your reasoning behind your answer.

Description:
{description}

Caption:
{caption}

Diagram:
{diagram}
"""

verification_prompt = """You are an expert of {language}. You know the rules and regulations of {language}. \
You will be given the {language} code of the diagram. You should verify the code to make sure it \
could be executed without any compilation error. If you identify any error, you should fix the error and output the fixed code. \

You will first to decide if there is any error in the code. You should wrap your decision inside the <decision></decision> tag.
You should only input yes or no inside the <decision></decision> tag.

If there are errors in the code, you should then generate the fixed code in a code block wrapped with ```

Think step by step and make sure the code is self-contained and executable.

Here are some rules to follow:
1. The child parent relationship should be correct, no child should be parent of itself or parent of its parent.
2. For each mxGeometry object, there should be a as="geometry" attribute as the end.
3. Each mxCell should have a parent
4. Each mxCell should not have a nested mxCell object and should only have one mxGeometry object
5. The special characters like <, >, &, ", ' should be properly escaped in attribute values.
6. For the graphical elements, a placeholder is allowed for a later replacement.

Diagram:
{diagram}
"""

component_replacement_planning_prompt = """You are an expert in information extraction. Given a description of a figure \
and the visual element replacement list, your job is to find the descprition of the the visual element which will be used to \
generate visual element later on. The visual element should come from either the author's input, or could \
be replaced by a vivid svg icon.

You should follow the following steps:
1. Comprehend the figure description thoroughly.
2. Identify the description of each visual element.
3. If the component is a concrete example or data from the paper, then it should be provided by the author.
4. If the component is an abstract component which could be replaced by a svg icon, then it should be provided \
by a svg generator.
5. You need to output the components result which could be replaced by an image in a valid json string as a list of \
dictionaries.

The dictionary should strictly follow the rules:
1. source: the replaced image source either be "author" or "svg".
2. description: the description of the component which will help generate the image later on.
3. id: the original id of the component which will be replaced.
4. name: the name of the component which will be replaced.

Think step by step and put put the final result in a valid json string wrapped by ```
Description:
{description}

Visual Element Replacement List:
{image_ids}
"""

svg_generation_prompt = """You are an excellent svg designer. Your job is to generate an svg given the name, \
description, width and height of the svg. You need to generate an symbolic represention with the given height \
and width. Output the svg and wraped it within ```

name: {name}
description: {description}
width: {width}
height: {height}
"""

image_search_prompt = """You are an expert in matching for an image in a given candidate_list with image names \
based on the title and description. You will need to give the index if the image is found, otherwise output -1. \
The index is zero based. Only output the number of the index.

title: {title}
description: {description}
candidate_list: {candidate_list}
index:

"""