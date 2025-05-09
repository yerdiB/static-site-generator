import enum
from htmlnode import *
from inline_markdown import *
import re

class BlockType(enum.Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

def markdown_to_blocks(markdown):
    markdown = markdown.strip()
    blocks = markdown.split("\n\n")
    return [block for block in blocks if block.strip()]

def block_to_block_type(block):
    lines = block.split("\n")
    lines = list(filter(lambda line: line != "" and line != "\n", lines))

    if not lines:
        return BlockType.PARAGRAPH
    
    if lines[0].startswith("```") and lines[len(lines) - 1].endswith("```"):
        return BlockType.CODE
    if lines[0].startswith(("# ", "## ", "### ", "#### ","##### ", "###### ")):
        return BlockType.HEADING
    if all(line.startswith('>') for line in lines):
        return BlockType.QUOTE
    if all(line.startswith('- ') for line in lines):
        return BlockType.UNORDERED_LIST
    if all(line.startswith(f"{i+1}. ") for i, line in enumerate(lines)):
        return BlockType.ORDERED_LIST
    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    blocks = [block for block in blocks if block.strip()]  
    leaf_nodes = []
    for block in blocks:
        type_of_block = block_to_block_type(block)
        match type_of_block:
            case BlockType.PARAGRAPH:
                leaf_nodes.append(text_to_html_node(block))
            case BlockType.HEADING:
                leaf_nodes.append(text_to_html_node(block))
            case BlockType.CODE:
                lines = block.strip().split("\n")
                content_lines = lines[1:-1]
                content = "\n".join(content_lines) + "\n" 
                leaf_nodes.append(ParentNode(f"pre", [text_node_to_html_node(TextNode(content, TextType.CODE))]))
            case BlockType.QUOTE:
                leaf_nodes.append(text_to_html_node(block))
            case BlockType.UNORDERED_LIST:
                leaf_nodes.append(text_to_html_node(block))
            case BlockType.ORDERED_LIST:
                leaf_nodes.append(text_to_html_node(block))
    return ParentNode("div", leaf_nodes)
        
def text_to_html_node(block):
    leaf_nodes = []
    text_nodes = []
    tag = ""
    match block_to_block_type(block):
        case BlockType.HEADING:
            hash_count = 0
            while block[hash_count] == "#":
                hash_count += 1
            tag = f"h{hash_count}"
            block = block[(hash_count + 1):]
            text_nodes.extend(text_to_textnodes(block))
            leaf_nodes.extend(list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes)))
            return ParentNode(tag, leaf_nodes)
        case BlockType.PARAGRAPH:
            block = " ".join([line.strip() for line in block.split("\n")])
            text_nodes.extend(text_to_textnodes(block))
            leaf_nodes.extend(list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes)))
            return ParentNode("p", leaf_nodes)
        case BlockType.QUOTE:
            text_nodes.extend(text_to_textnodes("\n".join(list(map(lambda line: (line.removeprefix(">")).strip(), block.split("\n"))))))
            leaf_nodes.extend(list(map(lambda text_node: text_node_to_html_node(text_node), text_nodes)))
            return ParentNode(f"blockquote", leaf_nodes)
        case BlockType.UNORDERED_LIST:
            for line in block.split("\n"):
                line = line[2:]
                text_nodes.extend(text_to_textnodes(line))
                leaf_nodes.append(ParentNode("li", list(map(lambda text_node: text_node_to_html_node(text_node), text_to_textnodes(line)))))
            return ParentNode(f"ul", leaf_nodes)
        case BlockType.ORDERED_LIST:
            for line in block.split("\n"):
                line = re.sub(r"\d+\. ", "", line)
                leaf_nodes.append(ParentNode("li", list(map(lambda text_node: text_node_to_html_node(text_node), text_to_textnodes(line)))))
            return ParentNode(f"ol", leaf_nodes)