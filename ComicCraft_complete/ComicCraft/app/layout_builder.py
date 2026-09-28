def build_comic_layout(outline: list[dict], story: list[dict], image_paths: list[str]) -> list[dict]:
    story_by_number = {int(p["panel_number"]): p for p in story}
    layout = []
    for panel in outline:
        number = int(panel["panel_number"])
        narrative = story_by_number.get(number, {})
        layout.append({
            "panel_number": number,
            "title": panel.get("title", f"Panel {number}"),
            "scene_description": panel.get("scene_description", ""),
            "image_prompt": panel.get("image_prompt", ""),
            "image_path": image_paths[number - 1],
            "caption": narrative.get("caption", ""),
            "narration": narrative.get("narration", ""),
            "dialogue": narrative.get("dialogue", ""),
        })
    return layout
