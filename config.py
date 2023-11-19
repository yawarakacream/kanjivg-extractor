from utility import pathstr


input_kvg_path = lambda charcode: pathstr("kanjivg", "kanji", f"{charcode}.svg")
output_main_kvg_path = lambda charcode: pathstr("output", charcode[:-2] + "00", charcode)
output_radical_clustering_path = lambda dataset_name, n_clusters, image_size, stroke_width, blur: pathstr(
    "output-radical-clustering",
    f"{dataset_name} n_clusters={n_clusters} (imsize={image_size},sw={stroke_width},blur={blur})",
)

font_path = pathstr("~/datadisk/dataset/font/NotoSansJP-Regular.ttf")
