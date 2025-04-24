from typing import Tuple
from prompts import (
    get_description_prompt,
    diagram_generation_prompt,
    refinement_prompt,
    verification_prompt,
    component_replacement_planning_prompt,
    svg_generation_prompt,
    image_search_prompt,
)
import json
import base64
import logging

from configs import ENGINE_CONFIGS
from foundation_model_util import call_api
from string_utli import parse_content_with_tag, parse_content_with_format
from xml_util import find_image_placeholders_with_dimensions, replace_component_by_id, fix_drawio_xml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

def get_diagram_description(paper_content: str, caption: str, engine: str = ENGINE_CONFIGS['text_analysis']) -> str:
    """
    Generate a description of the diagram based on the paper content and caption
    @param paper_content: str, the paper content
    @param caption: str, the caption of the diagram
    @return: str, the description
    """
    description_prompt = get_description_prompt.replace("{paper_content}", paper_content).replace("{caption}", caption)
    logging.debug(f"Get diagram description prompt: {description_prompt}")
    description_chatlog = [
        {"role": "user", "content": description_prompt},
    ]
    description_raw = call_api(description_chatlog, engine=engine)
    description = parse_content_with_tag(description_raw, "description")
    return description

def generate_initial_layout_with_description(description: str, language: str = "drwaio mxGraph/xml", format="xml") -> str:
    """
    Generate an initial diagram based on the description
    @param description: str, the description of the diagram
    @param language: str, the graphic code language of the diagram
    @param format: str, the graphic code format of the diagram
    @return: str, the initial diagram
    """
    diagram_parse_prompt = (
        diagram_generation_prompt.replace("{description}", description)
        .replace("{language}", language)
    )
    logging.debug(f"Generate initial diagram layout prompt:\n {diagram_parse_prompt}")
    diagram_chatlog = [
        {"role": "user", "content": diagram_parse_prompt},
    ]
    diagram_raw = call_api(diagram_chatlog, engine=ENGINE_CONFIGS['layout_generation'])
    diagram = parse_content_with_format(diagram_raw, format)
    return diagram

def refine_diagram(diagram: str, description: str, caption: str, language: str, format: str, iteration_num: int = 4) -> Tuple[str, list[str]]:
    """
    Refine the diagram iteratively
    @param diagram: str, the initial_diagram
    @param description: str, the description of the diagram
    @param caption: str, the caption of the diagram
    @param language: str, the graphic code language of the diagram
    @param format: str, the graphic code format of the diagram
    @param iteration_num: int, the number of iterations
    @return: Tuple[str, list[str]]: 
            - A string representing the final, refined diagram.
            - A list of intermediate diagram versions from each iteration.
    """
    refinement_chatlog = []
    refinements = []
    prompt_content = (
            refinement_prompt.replace("{diagram}", diagram)
            .replace("{description}", description)
            .replace("{caption}", caption)
            .replace("{language}", language)
    )
    refinement_chatlog.append(
            {"role": "user", "content": prompt_content}
    )
    logging.debug(f"Refine diagram prompt: {prompt_content}")
    for i in range(iteration_num):
        logging.info(f"Refining diagram, iteration: {i}")
        refinement = call_api(refinement_chatlog, engine=ENGINE_CONFIGS['layout_refinement'])
        refinements.append(refinement)

        decision = parse_content_with_tag(refinement, "decision")
        if decision.lower() == "yes" or decision.lower() == "y":
            diagram = parse_content_with_format(refinement, format)
        else:
            break

        refinement_chatlog.append(
            {"role": "assistant", "content": refinement}
        )
        refinement_chatlog.append(
            {"role": "user", "content": f"Is there any improvement to \
                make the refined diagram above more precise and appealing to the reader?"}
        )
    return diagram, refinements

def verify_diagram(diagram: str, language: str, format: str, iteration_num: int = 4) -> Tuple[str, list[str]]:
    """
    Verify the diagram iteratively
    @param diagram: str, the initial_diagram
    @param language: str, the graphic code language of the diagram
    @param format: str, the graphic code format of the diagram
    @param iteration_num: int, the number of iterations
    @return: Tuple[str, list[str]]:
            - A string representing the final, verified diagram.
            - A list of intermediate diagram versions from each iteration.
    """
    diagram_chatlog = []
    verifications = []
    verification = (
        verification_prompt.replace("{diagram}", diagram)
      .replace("{language}", language)
    )
    diagram_chatlog.append(
        {"role": "user", "content": verification}
    )
    logger.debug(f"Verify diagram prompt: {verification}")
    for i in range(iteration_num):
        logger.info(f"Verifying diagram, iteration: {i}")
        verification = call_api(diagram_chatlog, engine=ENGINE_CONFIGS['graphic_code_verification'])
        verifications.append(verification)
        decision = parse_content_with_tag(verification, "decision")
        if decision.lower() == "yes" or decision.lower() == "y":
            diagram = parse_content_with_format(verification, format)
        else:
            break
        diagram_chatlog.append(
            {"role": "assistant", "content": verification}
        )
        diagram_chatlog.append(
            {"role": "user", "content": f"Is there any error in the above corrected code? If yes, you should then generate the fixed code in code block wrapped with ```."}
        )
    return diagram, verifications

def generate_based_on_description(
    paper_content: str, caption: str, language: str = "drwaio mxGraph/xml", format="xml", candidate_list=[]
) -> Tuple[str, str, str, list, list]:
    logger.info("Generating diagram based on description")
    description = get_diagram_description(paper_content, caption)
    logger.debug(f"Generated description:\n {description}")
    logger.info("Generating initial layout")
    initial_layout = generate_initial_layout_with_description(description, language=language, format=format)
    logger.debug(f"Generated initial layout:\n {initial_layout}")
    logger.info("Refining diagram")
    refined_layout, refinements = refine_diagram(initial_layout, description, caption, language, format)
    logger.debug(f"Refined layout:\n {refined_layout}")
    logger.info("Verifying diagram")
    verified_layout, verifications = verify_diagram(refined_layout, language, format)
    logger.debug(f"Verified layout:\n{verified_layout}")
    final_layout = fix_drawio_xml(verified_layout)
    logger.debug(f"Final layout:\n {final_layout}")
    return initial_layout, final_layout, description, refinements, verifications

def generate_svg_image(name: str, description: str, width: str = '100', height: str = '100', engine: str = ENGINE_CONFIGS['svg_generation']) -> str:
    """
    Generate an SVG image based on the given title, description
    @param name: str, the name of the diagram
    @param description: str, the description of the diagram
    @param engine: str, the llm engine to use
    @return: str, the SVG image
    """
    svg_prompt = svg_generation_prompt.replace("{name}", name).replace(
        "{description}", description
    ).replace("{width}", width).replace("{height}", height)
    svg_chatlog = [
        {"role": "user", "content": svg_prompt},
    ]
    svg_image_raw = call_api(svg_chatlog, engine=engine)
    svg_image = parse_content_with_format(svg_image_raw, "svg")
    return svg_image

def get_author_image(title: str, description: str, candidate_list: list, engine:str = ENGINE_CONFIGS['image_retrieval']) -> Tuple[int | str, str]:
    """
    Search for an image based on the given title, description, if none of the images are found \
    then generate the image based on the title and description
    @param title: str, the title of the image
    @param description: str, the description of the image
    @param candidate_list: list, the list of candidate images:
        - name (str): name of the image
        - mime_type (str): mime type of the image
        - base64 (str): base64 encoded image
        - width (float): width of the image
        - height (float): height of the image
    @param engine: str, the llm engine to use
    @return: str, the image
    """
    image_names = [candidate["name"] for candidate in candidate_list]

    # Search for an image based on the given title, description
    search_prompt = (
        image_search_prompt.replace("{title}", title)
        .replace("{candidate_list}", json.dumps(image_names))
        .replace("{description}", description)
    )

    search_chatlog = [
        {"role": "user", "content": search_prompt},
    ]

    image_index = -1
    if len(candidate_list) > 0:
        image_index = int(call_api(search_chatlog, engine=engine))

    return image_index, "author"

def generate_replacement_plan(description: str, candidate_list: list = [], engine:str = ENGINE_CONFIGS['element_discriminator']) -> list:
    # Replacement plan for components by llm
    replacement_prompt = component_replacement_planning_prompt.replace(
        "{description}", description
    ).replace("{image_ids}", json.dumps(candidate_list))
    logger.debug(f"Replacement prompt:\n {replacement_prompt}")

    replacement_chatlog = [
        {"role": "user", "content": replacement_prompt},
    ]

    replacement_plan_raw = call_api(replacement_chatlog, engine=engine)
    return json.loads(parse_content_with_format(replacement_plan_raw, "json"))

def generate_replacement_images(plan: list, candidate_list: list) -> list:
    """
    Generate images based on the given plan
    @param plan: list, the plan
    @param candidate_list: list, the list of candidate images:
        - name (str): name of the image
        - mime_type (str): mime type of the image
        - base64 (str): base64 encoded image
        - width (float): width of the image
        - height (float): height of the image
    @return: list, the images
    """
    images = []
    for component in plan:
        if component.get("source", "") == "svg" or len(candidate_list) == 0:
            svg_image = generate_svg_image(
                component["name"], component["description"], component["width"], component["height"]
            )
            images.append({"id": component["id"], "mime_type": "image/svg+xml", "base64": base64.b64encode(svg_image.encode('utf-8')).decode('utf-8'), "source": "svg", "value": component["value"]})
        elif component.get("source", "") == "author":
            index, source = get_author_image(component["name"], component["description"], candidate_list)
            if 0 <= index < len(candidate_list):
                images.append({"id": component["id"], "mime_type": candidate_list[index]["mime_type"],"base64": candidate_list[index]["base64"], "source": source, "value": component["value"]})
    return images

def replace_components_with_images(description: str, diagram: str, candidate_list: list = [], engine:str = ENGINE_CONFIGS['element_discriminator']) -> Tuple[str, list]:
    """
    Replace components in the diagram with images.
    @param diagram: str, the diagram
    @return: the diagram with images, the image replacement plan
    """
    replacement_images = find_image_placeholders_with_dimensions(diagram)
    image_ids = [image["id"] for image in replacement_images]
    id_to_image_map = {image["id"]: image for image in replacement_images}
    logger.info(f"Replacement image ids:\n {image_ids}")
    logger.info(f"Replacement images:\n {replacement_images}")
    plan = generate_replacement_plan(description, image_ids, engine)
    logger.info(f"Replacement plan:\n {plan}")
    final_plan = []
    for component in plan:
        if component["id"] in id_to_image_map:
            component["width"] = id_to_image_map[component["id"]]["width"]
            component["height"] = id_to_image_map[component["id"]]["height"]
            component["value"] = id_to_image_map[component["id"]]["value"]
            final_plan.append(component)

    images = generate_replacement_images(final_plan, candidate_list)

    # Replace components with images
    for image in images:
        diagram = replace_component_by_id(diagram, image)
        
    return diagram, final_plan, images
