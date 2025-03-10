import os
from utils.utils import setup_logging
from deep_translator import GoogleTranslator

def translate_file(input_file, output_file, target_lang='en'):
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Translate the text from German ('de') to English ('en')
    translator = GoogleTranslator(source='de', target=target_lang)
    translated_text = translator.translate(text)

    # Write the translated text to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(translated_text)

    logger.info(f"Translated '{input_file}' to '{output_file}'")

def translate_directory(input_dir, output_dir, target_lang='en'):
    for root, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.txt'):
                input_file_path = os.path.join(root, file)

                # Determine the relative path to preserve directory structure
                relative_path = os.path.relpath(root, input_dir)
                output_subdir = os.path.join(output_dir, relative_path)
                os.makedirs(output_subdir, exist_ok=True)

                # Append '_translated' before the file extension for the output file name
                filename, ext = os.path.splitext(file)
                output_file_name = f"{filename}_translated{ext}"
                output_file_path = os.path.join(output_subdir, output_file_name)

                translate_file(input_file_path, output_file_path, target_lang)

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Running Translate...")

    # Set the input and output directories
    input_directory = "trial"
    output_directory = "trial_translated"

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    translate_directory(input_directory, output_directory)

    logger.info("Translation complete")