from utility import pathstr


input_kvg_path = lambda charcode: pathstr("kanjivg", "kanji", f"{charcode}.svg")
output_main_kvg_path = lambda charcode: pathstr("output", charcode[:-2] + "00", charcode)
output_radical_clustering_path = "output-radical-clustering"

font_path = pathstr("~/datadisk/dataset/font/NotoSansJP-Regular.ttf")
