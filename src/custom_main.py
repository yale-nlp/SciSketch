import argparse # type: ignore
import json
from tqdm import tqdm
import os
from diagram_handler import generate_based_on_description, replace_components_with_images
from utils import concatenate_paper_text, encode_image, get_image_dimensions
from file_util import write_object_to_file, write_string_to_file
from configs import DIAGRAM_CONFIGS

def get_parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_directory", type=str, default="generated_diagram")
    parser.add_argument("--parsed_paper_directory", type=str, default="samples/parsed_papers")
    parser.add_argument("--sample_id", type=str, help="ID of the sample to process")
    parser.add_argument(
        "--language",
        type=str,
        default="drawio",
        help="code language for generated diagram", 
    )
    return parser.parse_args()

def pre_process(args):
    """
    preprocess the args to make sure it is valid and ready for the next stage
    """
    assert args.language in DIAGRAM_CONFIGS, "Language not supported"
    assert os.path.exists(
        args.parsed_paper_directory
    ), "Parsed paper directory does not exist"
    os.makedirs(args.save_directory, exist_ok=True)

def get_test_data(args):
    """
    get test data
    """
    test_data = []
    for file in os.listdir(args.parsed_paper_directory):
        if file.endswith(".json"):
            with open(f"{args.parsed_paper_directory}/{file}", "r") as f:
                data = json.load(f)
            if file.split(".")[0] == "final":
                continue
            assert data.get("caption", ""), "Caption not found in parsed paper file"
            paper_plain_text = concatenate_paper_text(data)
            test_data.append(
                {
                    "paper": paper_plain_text,
                    "caption": data["caption"],
                    "file": file.split(".")[0],
                }
            )

    if args.sample_id:
        test_data = [sample for sample in test_data if sample["file"] == args.sample_id]
    return test_data

def get_candidate_image_list(file_name: str) -> list[dict]:
    """
    get candidate image list based on the file name
    Args:
        file_name (str): file name 
    Returns:
        list[dict]: candidate image list with the following keys:
            name (str): name of the image
            mime_type (str): mime type of the image
            base64 (str): base64 encoded image
            width (float): width of the image
            height (float): height of the image
    """
    candidate_list = []
    if os.path.exists(f"input_images/{file_name}"):
        for image in os.listdir(f"input_images/{file_name}"):
            if image.endswith(".png") or image.endswith(".jpg"):
                width, height = get_image_dimensions(f"input_images/{file_name}/{image}")
                candidate_list.append(
                    {
                        "name": image.split(".")[0],
                        "mime_type": f"image/{image.split('.')[-1]}",
                        "base64": encode_image(f"input_images/{file_name}/{image}"),
                        "width": width,
                        "height": height,
                    }
                )

    return candidate_list

def process_test_data(test_data: list[dict], configs: dict, save_directory: str):
    """
    the main function for processing the test data to generate diagrams
    """
    for sample in tqdm(test_data, desc="Generating Diagram Plans"):
        candidate_list = get_candidate_image_list(sample["file"])
        initial_layout, final_layout, description, refinements, verifications = (
            generate_based_on_description(
                sample["paper"],
                sample["caption"],
                language=configs["language"],
                format=configs["parse_format"],
                candidate_list=candidate_list
            )
        )
        out = {}
        out[sample["file"]] = {
            "caption": sample["caption"],
            "description": description,
            "initial_layout": initial_layout,
            "final_layout": final_layout,
            "refinements": refinements,
            "verifications": verifications,
        }
        final_diagram, replacement_plan, images = replace_components_with_images(
            description, final_layout, candidate_list
        )
        out[sample["file"]]["replacement_plan"] = replacement_plan
        out[sample["file"]]["final_diagram"] = final_diagram

        os.makedirs(f"{save_directory}/{sample['file']}", exist_ok=True)
        output_file = f"{save_directory}/{sample['file']}/{sample['file']}.json"
        final_diagram_file = f"{save_directory}/{sample['file']}/{sample['file']}_final{configs['file_extension']}"
        write_object_to_file(out, output_file)
        write_string_to_file(final_diagram, final_diagram_file)

def main():
    """
    main function
    """
    args = get_parsed_args()
    pre_process(args)
    configs = DIAGRAM_CONFIGS.get(args.language, {})
    save_directory = args.save_directory
    test_data = get_test_data(args)
    process_test_data(test_data, configs, save_directory)

if __name__ == "__main__":
    main()