from utility import pathstr


input_kvg_path = lambda charcode: pathstr("kanjivg", "kanji", f"{charcode}.svg")

output_root_path = pathstr("output")

output_main_kvg_path = lambda charcode: pathstr(
    output_root_path,
    "main",
    charcode[:-2] + "00",
    charcode
)

output_radical_clustering_path = lambda dataset_name, n_clusters, image_size, stroke_width, blur: pathstr(
    output_root_path,
    "radical-clustering",
    f"{dataset_name} n_clusters={n_clusters} (imsize={image_size},sw={stroke_width},blur={blur})",
)

output_composition_path = lambda composition_name: pathstr(
    output_root_path,
    "composition",
    f"{composition_name}.json"
)
