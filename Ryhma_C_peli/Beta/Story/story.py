import textwrap

story = '''Hero wakes up to a call from the european council.
The climate stabilizer had been stolen over night by the infamous
villain with the big black cape (in short: BBC).
The only information the council can give is, that BBC is
hiding and moving along the biggest european Airports, be train.
NOW! It is up to you hero, to find the BBC and get the climate stabilizer back!
To help you, the european council sponsors your cross country flights,
but be aware that each 100km flown raise the climate by 0.5 degrees celsius.
Warming the climate by 6 degrees will lead to the world overheating
and exploding, so be fast and intelligent.
along your journey you will get hints of where the villain has been last seen
in form of a compass point. Get going now!'''


wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list = wrapper.wrap(text=story)

def getStory():
    return word_list