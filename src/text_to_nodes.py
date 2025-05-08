from textnode import *
import re

def text_node_to_html_node(text_node):
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text, "")
        case TextType.ITALIC:
            return LeafNode("i", text_node.text, "")
        case TextType.CODE:
            return LeafNode("code", text_node.text, "")
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception("no such text type")
        
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text = old_node.text
        
        if delimiter not in text:
            new_nodes.append(old_node)
            continue
        
        parts = text.split(delimiter)
        
        if len(parts) % 2 == 0:
            raise ValueError(f"Missing closing delimiter: {delimiter}")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                if part:
                    new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))
        
    return new_nodes

def extract_markdown_images(text):
    markdown_images = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return markdown_images

def extract_markdown_links(text):
    markdown_links = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return markdown_links

def split_nodes_image(old_nodes):
    result = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue
            
        images = extract_markdown_images(node.text)
        if not images:
            result.append(node)
            continue

        alt_text, url = images[0]
        image_markdown = f"![{alt_text}]({url})"
        
        sections = node.text.split(image_markdown, 1)
        
        if sections[0]:
            result.append(TextNode(sections[0], TextType.TEXT))
            
        result.append(TextNode(alt_text, TextType.IMAGE, url))
        
        if len(sections) > 1 and sections[1]:
            remaining_nodes = split_nodes_image([TextNode(sections[1], TextType.TEXT)])
            result.extend(remaining_nodes)
    
    return result

def split_nodes_link(old_nodes):
    result = []
    
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            result.append(node)
            continue
            
        links = extract_markdown_links(node.text)
        if not links:
            result.append(node)
            continue
        anchor_text, url = links[0]

        link_markdown = f"[{anchor_text}]({url})"
        
        sections = node.text.split(link_markdown, 1)
        
        if sections[0]:
            result.append(TextNode(sections[0], TextType.TEXT))
            
        result.append(TextNode(anchor_text, TextType.LINK, url))
        
        if len(sections) > 1 and sections[1]:
            remaining_nodes = split_nodes_link([TextNode(sections[1], TextType.TEXT)])
            result.extend(remaining_nodes)
    
    return result

def text_to_textnodes(text):
    new_nodes = split_nodes_delimiter([TextNode(text, TextType.TEXT)], "**", TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes, "`", TextType.CODE)
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    return new_nodes