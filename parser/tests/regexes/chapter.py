from regex import Empty, Char, Union,Plus, Lambda, Star, Concat

# a|b|c|d|e|f|g|h|i|j|k|l|m|n|o|p|q|r|s|t|u|v|w|x|y|z|∅
__regex__ = Concat(Char("c"),Concat(Char("h"),Concat(Char("a"),Concat(Char("p"),Concat(Char("t"),Concat(Char("e"),Concat(Char("r"), Plus(Union(Char("x"),Union(Char("i"),Char("v")))))))))))

__should_match__ = r"chapter((x|i|v)+)"

__min_afd_size__ = 10

