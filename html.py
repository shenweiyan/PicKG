import os

def get_directory_tree(path):
    tree = {}
    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        rel_path = os.path.relpath(root, path)
        if rel_path == '.':
            current_dict = tree
        else:
            parts = rel_path.split(os.sep)
            current_dict = tree
            for part in parts:
                if part not in current_dict:
                    current_dict[part] = {}
                current_dict = current_dict[part]
        
        # Add files to the current dictionary, but only if it's not a nested directory dictionary
        if 'files' not in current_dict:
            current_dict['files'] = files
        else:
            # This branch shouldn't happen if the directory structure is flat (no nested dirs with same name as files),
            # but just in case, we'll merge the files list (though this is logically incorrect if it does happen).
            # Normally, we'd want to handle this case more gracefully.
            current_dict['files'].extend(files)
    
    # Optionally clean up empty 'files' entries that may have been left due to merging (though the above logic should prevent this).
    def clean_tree(t):
        if isinstance(t, dict):
            for k, v in list(t.items()):
                if isinstance(v, dict):
                    clean_tree(v)
                elif k == 'files' and not v:
                    del t[k]
        return t
    
    return clean_tree(tree)

def render_html_tree(tree, indent=0, base_path='.'):
    html = []
    for key, value in tree.items():
        if isinstance(value, dict):
            folder_link = f'<a href="{os.path.join(base_path, key)}">{key}</a>'
            html.append(' ' * indent + f'<ul><li>{folder_link}')
            # Recursively render the subtree, updating the base_path
            html.append(render_html_tree(value, indent + 4, os.path.join(base_path, key)))
            html.append(' ' * indent + '</li></ul>')
        else:  # 'files' key
            files_html = ''.join([f'<a href="{os.path.join(base_path, key, f)}">{f}</a><br>' for f in value])
            #html.append(' ' * indent + f'<ul><li>{key}<ul>{files_html}</ul></li></ul>')
            html.append(f'<ul>{files_html}</ul>')
    return '\n'.join(html)

def main():
    current_directory = os.getcwd()
    directory_tree = get_directory_tree(current_directory)
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Directory Tree</title>
        <style>
            ul {{
                list-style-type: none;
            }}
            li {{
                margin: 5px 0;
            }}
            a {{
                text-decoration: none;
                color: blue;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        {render_html_tree(directory_tree)}
    </body>
    </html>
    """
    
    with open('directory_tree.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print("Directory tree has been saved to 'directory_tree.html'. Open it in your browser.")

if __name__ == "__main__":
    main()
