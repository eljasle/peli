import textwrap

story = '''Hero wakes up to a call from the European Council. The climate stabilizer has been stolen overnight by the infamous villain with the big black cape (BBC). The only information the council can provide is that BBC is hiding in Belgium and not moving.
Now, it is up to you, hero, to find the BBC and recover the climate stabilizer! To assist you, the European Council sponsors your flights between small airports in Belgium. However, be aware that each 100km flown raises the climate by 0.5°C. Warming the climate by 6 degrees will lead to the world overheating and exploding, so be fast and intelligent.
Along your journey, spies will provide you with information on where the villain has been last seen in form of a compass point. Also if you get close enough to the villain, you will be informed!
The worlds destiny lies in your hands, go now!'''


wrapper = textwrap.TextWrapper(width=80, break_long_words=False, replace_whitespace=False)
# Wrap text
word_list = wrapper.wrap(text=story)


def getStory():
    return word_list