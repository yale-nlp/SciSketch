import re

def parse_content_with_tag(content: str, tag: str) -> str:
    pattern = rf"<{tag}>(.*?)</{tag}>"

    # Find the first match (content inside the tag)
    match = re.search(pattern, content, re.DOTALL)

    if match:
        extracted_content = match.group(1).strip()  # Get content and remove extra spaces
        return extracted_content
    else:
        print(f"No content found inside <{tag}> tags.")
        return content

def parse_content_with_format(content: str, format: str) -> str:
    pattern = rf"```{format}(.*?)```"
    matches = re.findall(pattern, content, re.DOTALL)
    if matches:
        extracted_contents = [match.strip() for match in matches]
        for i in reversed(range(len(extracted_contents))):
            if "decision" not in extracted_contents[i]:
                return extracted_contents[i]
        return extracted_contents[-1]
    else:
        print(f"No content found in {format} format.")
        if not format:
            return content
        return parse_content_with_format(content, "")