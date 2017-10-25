from os import listdir
from os.path import isfile, join

import itertools
import SiMPle

MP3_FILES = ["/home/felipev/Desktop/Luiz Gonzaga - As 40 melhores/%s" % f for f in listdir("/home/felipev/Desktop/Luiz Gonzaga - As 40 melhores") if f.endswith("mp3") and isfile(join("/home/felipev/Desktop/Luiz Gonzaga - As 40 melhores", f))]
COMBINATIONS = itertools.combinations(MP3_FILES, 2)

SIMILARITY_FILE = open("similarties.csv", "w")

for combination in list(COMBINATIONS):
    SIMILARITY_FILE.write("%s,%s,%f\n" % (combination[0].split("/")[-1], combination[1].split("/")[-1], SiMPle.similarity_by_simple(combination[0], combination[1])))

SIMILARITY_FILE.close()