from markdown_it import MarkdownIt
from md_toc import build_toc

def generate_toc(input_file, output_file):
    toc = build_toc(input_file, keep_header_levels=6)

    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(toc)
        file.write('\n\n')
        file.write(content)

    print(f"Table of Contents generated in '{output_file}'")

input_file = '../README.zh-cn.md'
output_file = '../README_TOC.zh-cn.md'

generate_toc(input_file, output_file)
