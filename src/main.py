import shutil, os, sys
from block_markdown import *

def src_to_dest(static, public):
    if os.path.isfile(static):
        shutil.copy(static, public)
    else:
        if not os.path.exists(public):
            os.mkdir(public)
        for path in os.listdir(static):
            src_to_dest(os.path.join(static, path), os.path.join(public, path))

def extract_title(markdown):
    for line in markdown.split("\n"):
        if line.startswith("# "):
            return line[2:]
    raise Exception("no heading")

def generate_page(from_path, template_path, dest_path, basepath):
    if dest_path.endswith(".md"):
        dest_path = f"{dest_path[:-2]}html"
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    
    with open(from_path, "r") as f:
        src_md = f.read()
    
    with open(template_path, "r") as f:
        template = f.read()
    
    content = markdown_to_html_node(src_md).to_html()
    
    title = extract_title(src_md)
    
    template = template.replace("{{ Title }}", title)
    template = template.replace("{{ Content }}", content)
    template = template.replace("href=\"/", f"href=\"{basepath}")
    template = template.replace("src=\"/", f"src=\"{basepath}")
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    with open(dest_path, "w") as f:
        f.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for each in os.listdir(dir_path_content):
        if os.path.isfile(os.path.join(dir_path_content, each)):
            if each.endswith(".md"):
                generate_page(os.path.join(dir_path_content, each), template_path, os.path.join(dest_dir_path, each), basepath)
        else:
            os.makedirs(os.path.join(dest_dir_path, each), exist_ok=True)
            generate_pages_recursive(os.path.join(dir_path_content, each), template_path, os.path.join(dest_dir_path, each), basepath)


def main():
    basepath = "/"
    if len(sys.argv) > 1:
        basepath = sys.argv[1]

    
    if os.path.exists("docs"):
        shutil.rmtree("docs")
    os.mkdir("docs")
    src_to_dest("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)
    print(basepath)
    return

main()