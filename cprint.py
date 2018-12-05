"""
Cross-platform colored printing to the console using `colorama <https://github.com/tartley/colorama>`_ module.

Usage:
    from cprint import print, Color

    print("Test", color=Color.GREEN)
"""
import builtins
import enum
import os
from typing import Union, Type, Tuple, TextIO, Optional

import colorama

__author__ = "Bojan Potočnik"


class _Fore(enum.Enum):
    """
    All foreground colors supported by :mod:`colorama`.
    """
    BLACK = colorama.Fore.BLACK
    RED = colorama.Fore.RED
    GREEN = colorama.Fore.GREEN
    YELLOW = colorama.Fore.YELLOW
    BLUE = colorama.Fore.BLUE
    MAGENTA = colorama.Fore.MAGENTA
    CYAN = colorama.Fore.CYAN
    WHITE = colorama.Fore.WHITE
    RESET = colorama.Fore.RESET

    # These are fairly well supported, but not part of the standard.
    BLACK_LIGHT = colorama.Fore.LIGHTBLACK_EX
    RED_LIGHT = colorama.Fore.LIGHTRED_EX
    GREEN_LIGHT = colorama.Fore.LIGHTGREEN_EX
    YELLOW_LIGHT = colorama.Fore.LIGHTYELLOW_EX
    BLUE_LIGHT = colorama.Fore.LIGHTBLUE_EX
    MAGENTA_LIGHT = colorama.Fore.LIGHTMAGENTA_EX
    CYAN_LIGHT = colorama.Fore.LIGHTCYAN_EX
    WHITE_LIGHT = colorama.Fore.LIGHTWHITE_EX

    def __str__(self):
        return self.value


class Fore(enum.Enum):
    """
    Foreground colors.
    """
    BLACK = _Fore.BLACK.value
    RED = _Fore.RED.value
    GREEN = _Fore.GREEN.value
    YELLOW = _Fore.YELLOW.value
    BLUE = _Fore.BLUE.value
    MAGENTA = _Fore.MAGENTA.value
    CYAN = _Fore.CYAN.value
    WHITE = _Fore.WHITE.value
    RESET = _Fore.RESET.value

    # These are fairly well supported, but not part of the standard.
    BLACK_LIGHT = _Fore.BLACK_LIGHT.value
    RED_LIGHT = _Fore.RED_LIGHT.value
    GREEN_LIGHT = _Fore.GREEN_LIGHT.value
    YELLOW_LIGHT = _Fore.YELLOW_LIGHT.value
    BLUE_LIGHT = _Fore.BLUE_LIGHT.value
    MAGENTA_LIGHT = _Fore.MAGENTA_LIGHT.value
    CYAN_LIGHT = _Fore.CYAN_LIGHT.value
    WHITE_LIGHT = _Fore.WHITE_LIGHT.value

    def __str__(self):
        return self.value


class _Back(enum.Enum):
    """
    All background colors supported by :mod:`colorama`.
    """
    BLACK = colorama.Back.BLACK
    RED = colorama.Back.RED
    GREEN = colorama.Back.GREEN
    YELLOW = colorama.Back.YELLOW
    BLUE = colorama.Back.BLUE
    MAGENTA = colorama.Back.MAGENTA
    CYAN = colorama.Back.CYAN
    WHITE = colorama.Back.WHITE
    RESET = colorama.Back.RESET

    # These are fairly well supported, but not part of the standard.
    BLACK_LIGHT = colorama.Back.LIGHTBLACK_EX
    RED_LIGHT = colorama.Back.LIGHTRED_EX
    GREEN_LIGHT = colorama.Back.LIGHTGREEN_EX
    YELLOW_LIGHT = colorama.Back.LIGHTYELLOW_EX
    BLUE_LIGHT = colorama.Back.LIGHTBLUE_EX
    MAGENTA_LIGHT = colorama.Back.LIGHTMAGENTA_EX
    CYAN_LIGHT = colorama.Back.LIGHTCYAN_EX
    WHITE_LIGHT = colorama.Back.LIGHTWHITE_EX

    def __str__(self):
        return self.value


class Back(enum.Enum):
    """
    Background colors.
    """
    # Changing the background color is intentionally not supported.
    # As example, BLACK looks black in CMD but it is white in PyCharm console.
    # Some of the other colors looks weird.
    # This shall maybe be supported some day for e.g. progress bars, however it is not on list of priorities.
    RESET = _Back.RESET.value

    def __str__(self):
        return self.value


class _Style(enum.Enum):
    """
    All styles supported by :mod:`colorama`.
    """
    BRIGHT = colorama.Style.BRIGHT
    DIM = colorama.Style.DIM
    NORMAL = colorama.Style.NORMAL
    RESET_ALL = colorama.Style.RESET_ALL

    def __str__(self):
        return self.value


class Style(enum.Enum):
    """
    Styles.
    """
    # No difference has been seen between DIM and NORMAL in PyCharm or CMD.
    BRIGHT = _Style.BRIGHT.value
    NORMAL = _Style.NORMAL.value
    RESET_ALL = _Style.RESET_ALL.value

    def __str__(self):
        return self.value


class Color(enum.Enum):
    """
    All supported and actually useful colors combinations.

    Only BLACK background is used.

    Light versions of colors are preferred over bright style (they are mostly equivalent
    concerning the colors but bold in some consoles).

    :note: PyCharm color scheme changes these colors, as can be seen or edited in
           `File -> Settings... -> Editor -> Color Scheme -> Console Colors`.
    """
    # `+ Back.RESET.value + Style.NORMAL.value` is common to all colors defined here
    # and therefore not appended. As this is default style, it will work properly
    # unless changed (and it is never changed using these colors).

    DEFAULT = Style.RESET_ALL.value
    """
    No style defined.
    """

    WHITE = Fore.WHITE_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    White on black.\n
    Equivalents are: WHITE|RESET|BRIGHT, RESET|RESET|BRIGHT, WHITE_LIGHT|RESET|BRIGHT, WHITE_LIGHT|RESET|NORMAL.
    """

    LIGHT_GRAY = Fore.WHITE.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Light gray on black.\n
    This is always the result of `Style.RESET_ALL` irrespective of `Fore` and `Back`.\n
    Equivalents are: *|*|RESET_ALL, WHITE|RESET|NORMAL, RESET|RESET|NORMAL.
    """

    GRAY = Fore.BLACK_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Gray on black.\n
    Equivalents are: BLACK|RESET|BRIGHT, BLACK_LIGHT|RESET|BRIGHT, BLACK_LIGHT|RESET|NORMAL.
    """

    BLACK = Fore.BLACK.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Black on black.
    """

    DARK_RED = Fore.RED.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Dark red on black.
    """

    RED = Fore.RED_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Red on black.\n
    Equivalents are: RED|RESET|BRIGHT, RED_LIGHT|RESET|BRIGHT, RED_LIGHT|RESET|NORMAL.
    """

    DARK_YELLOW = Fore.YELLOW.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Dark yellow on black.
    """

    YELLOW = Fore.YELLOW_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Yellow on black.\n
    Equivalents are: YELLOW|RESET|BRIGHT, YELLOW_LIGHT|RESET|BRIGHT, YELLOW_LIGHT|RESET|NORMAL.
    """

    DARK_GREEN = Fore.GREEN.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Dark green on black.
    """

    GREEN = Fore.GREEN_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Green on black.\n
    Equivalents are: GREEN|RESET|BRIGHT, GREEN_LIGHT|RESET|BRIGHT, GREEN_LIGHT|RESET|NORMAL.
    """

    DARK_CYAN = Fore.CYAN.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Dark cyan on black.
    """

    CYAN = Fore.CYAN_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Cyan on black.\n
    Equivalents are: CYAN|RESET|BRIGHT, CYAN_LIGHT|RESET|BRIGHT, CYAN_LIGHT|RESET|NORMAL.
    """

    DARK_BLUE = Fore.BLUE.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Dark blue on black.
    """

    BLUE = Fore.BLUE_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Blue on black.\n
    Equivalents are: BLUE|RESET|BRIGHT, BLUE_LIGHT|RESET|BRIGHT, BLUE_LIGHT|RESET|NORMAL.
    """

    PURPLE = Fore.MAGENTA.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Purple (magenta, dark magenta, purple) on black.
    """

    MAGENTA = Fore.MAGENTA_LIGHT.value  # + Back.RESET.value + Style.NORMAL.value
    """
    Magenta (pink, light magenta, hot magenta) on black.\n
    Equivalents are: MAGENTA|RESET|BRIGHT, MAGENTA_LIGHT|RESET|BRIGHT, MAGENTA_LIGHT|RESET|NORMAL.
    """

    def __str__(self):
        return self.value

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """
        Get RGB representation of the foreground color (as background is always black).
        Tested in CMD and verified on
        `ANSI Escape Code > Colors <https://en.wikipedia.org/wiki/ANSI_escape_code#Colors>`_.

        :return: Tuple (red, green, blue) values ranging [0, 255].
        """
        return {
            self.DEFAULT: None,
            self.WHITE: (255, 255, 255),
            self.LIGHT_GRAY: (192, 192, 192),
            self.GRAY: (128, 128, 128),
            self.BLACK: (0, 0, 0),
            self.DARK_RED: (128, 0, 0),
            self.RED: (255, 0, 0),
            self.DARK_YELLOW: (128, 128, 0),
            self.YELLOW: (255, 255, 0),
            self.DARK_GREEN: (0, 128, 0),
            self.GREEN: (0, 255, 0),
            self.DARK_CYAN: (0, 128, 128),
            self.CYAN: (0, 255, 255),
            self.DARK_BLUE: (0, 0, 128),
            self.BLUE: (0, 0, 255),
            self.PURPLE: (128, 0, 128),
            self.MAGENTA: (255, 0, 255)
        }[self]

    @property
    def color(self) -> str:
        """
        Get hex representation of the color. Tested in CMD and verified on
        `ANSI Escape Code > Colors <https://en.wikipedia.org/wiki/ANSI_escape_code#Colors>`_.

        :return: Hex color in format "#RRGGBB".
        """
        rgb = self.rgb
        if rgb:
            return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
        else:
            return ""


def reset() -> None:
    """
    Reset all styles to the terminal defaults.
    """
    builtins.print(Style.RESET_ALL, sep="", end="")  # Print "nothing".


# noinspection PyShadowingBuiltins
def print(*args,
          sep: str = None, end: str = None,
          file: TextIO = None, flush: bool = None,
          color: Optional[Color] = Color.DEFAULT):
    """
    Print with optionally colored output.

    Prints the values to a stream, or to sys.stdout by default.

    :param sep:   String inserted between values, default a space.
    :param end:   String appended after the last value, default a newline.
    :param file:  A file-like object (stream); defaults to the current sys.stdout.
    :param flush: Whether to forcibly flush the stream.
    :param color: Color to use for colored output; defaults to no color (terminal default style).
                  If `None`, color from the previous call to this function will be used.
    """
    # First, the print was one-liner:
    #   `builtins.print(color.value if color else "", *args, sep=sep, end=end, file=file, flush=flush)`
    # however this added `sep` also between color and arguments which is incorrect.
    if color is not None:
        builtins.print(color.value, end="", file=file)
    builtins.print(*args, sep=sep, end=end, file=file, flush=flush)


def __test_print(backs: Union[Type[_Back], Type[Back]],
                 fronts: Union[Type[_Fore], Type[Fore]],
                 styles: Union[Type[_Style], Type[Style]]):
    for back in backs:
        for fore in fronts:
            for style in styles:
                print(fore.value + back.value + style.value +
                      "Fore: {:15} | Back: {:15} | Style: {:15} | █████ ████ ███ ██ █ █ █"
                      .format(fore.name, back.name, style.name))


def _test_print_all() -> None:
    """
    Print all supported colorama combinations.
    """
    print("####################################")
    print("# Print all colorama combinations  #")
    print("####################################")
    __test_print(_Back, _Fore, _Style)
    reset()


def _test_print() -> None:
    """
    Print color combinations which have been shown to be supported on few test machines.
    """
    print("####################################")
    print("# Print all supported combinations #")
    print("####################################")
    __test_print(Back, Fore, Style)
    reset()


def _test() -> None:
    print("####################################")
    print("# Print all Color values           #")
    print("####################################")
    for color in Color:
        print("Printing in {}".format(color.name), color=color)
        print("\tOne more time, this time with `None` as a color.", color=None)
        print("\tOne more time, this time without color provided.")
        print("\tAgain using color=`None`, however previous print shall reset the style to default.", color=None)
    reset()


def _test_arguments() -> None:
    print("####################################")
    print("# Print passing arguments          #")
    print("####################################")
    print()  # Empty line.
    print()  # Empty line.
    print(color=Color.RED)  # Empty line.
    print("Red?", color=None)  # "Red?" in red.
    print(tuple(), color=Color.BLUE)  # "()" in blue.
    print(tuple())  # "()" in default color.
    print(color=Color.GREEN)  # Empty line.
    print()  # Empty line.
    print("Done shall be non-colored.")  # printed in default color.


# `colorama.init()` checks for the OS where this script is running and configures itself
# accordingly. However there is a problem when using PyCharm on Windows: colorama properly
# detects Windows OS and configures colors for Win32, but PyCharm console is ANSI compliant
# and consequentially colored output does not work.
# Luckily, PyCharm defines special environment variable to detect it.
# https://stackoverflow.com/questions/29777737/how-to-check-if-python-unit-test-started-in-pycharm-or-not
if "PYCHARM_HOSTED" in os.environ:
    # Running in PyCharm.
    _convert = False  # Do not convert ANSI codes in the output into win32 calls.
    _strip = False  # Do not strip ANSI codes from the output.
else:
    _convert = None
    _strip = None
# Initialize colorama.
# If auto-reset is enabled, color is reset after every printed argument! Not only after every call to print().
colorama.init(autoreset=False, convert=_convert, strip=_strip)
# Reset style to default values to match `Color` class.
reset()

if __name__ == "__main__":
    _test_print_all()
    _test_print()
    _test()
    _test_arguments()
