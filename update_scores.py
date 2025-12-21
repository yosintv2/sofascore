def update_readme(content):
    file_path = "README.md"
    
    # Check if file exists; if not, create it with markers
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Football Live Scores\n\n\n")

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_readme = []
    skip = False
    found_markers = False
    
    for line in lines:
        if "" in line:
            new_readme.append(line)
            new_readme.append(content + "\n")
            skip = True
            found_markers = True
        elif "" in line:
            new_readme.append(line)
            skip = False
        elif not skip:
            new_readme.append(line)

    # If markers weren't found, just append to the end
    if not found_markers:
        new_readme.append("\n\n" + content + "\n")

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(new_readme)
