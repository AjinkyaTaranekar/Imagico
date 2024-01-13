import re


def clean_filename(name):
    # Replace spaces with underscores
    cleaned_name = name.replace(" ", "_")

    # Remove characters that might cause issues in filenames
    cleaned_name = re.sub(r"[^\w.-]", "", cleaned_name)

    return cleaned_name
