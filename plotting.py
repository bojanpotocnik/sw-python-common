"""
Convenience methods for plotting with matplotlib which I discovered I frequently use.
Some of them are really just for typing (`subplots` is one of them).
"""
import enum
import io
import os
import pathlib
import sys
import warnings
from typing import TYPE_CHECKING, Optional, Union, Sequence, Tuple, Dict, List, Callable, Iterable, Collection

import matplotlib
# `import matplotlib.pyplot as plt` is at the end of the file as the backend must be switched first.
import matplotlib.backend_bases
from matplotlib.axes import Axes
from matplotlib.backends.backend_template import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D

__author__ = "Bojan Potočnik"

if TYPE_CHECKING:  # To prevent cyclic and unused imports in runtime.
    import numpy as np

    Number = Union[int, float, np.number]
else:
    Number = Union[int, float, 'np.number']

_figure_count = 0


def figure(figure_title: str = None, window_title: str = None, fig: Optional[Figure] = None, **kwargs) -> Figure:
    """
    Create new `Figure <https://matplotlib.org/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure>`_
    or reuse it.

    :param figure_title: Centered title of the figure.
    :param window_title: Window title. If `None`, `figure_title` will be used; if empty string, it will not be set.
    :param fig:          Existing figure. If provided it will be cleared and reused.
    :param kwargs:       Any other parameters to pass to the `plt.figure()` when creating new figure.

    :return: Figure.
    """
    global _figure_count

    fig_to_reuse = fig

    if (not fig) or (not fig.canvas):
        fig: Figure = plt.figure(**kwargs)
        _figure_count += 1
    else:
        fig.clear()

    if not figure_title:
        figure_title = f"Figure {_figure_count - 1}"
    fig.suptitle(figure_title)

    if window_title is None:
        window_title = figure_title
    if window_title:
        try:
            fig.canvas.set_window_title(window_title)
        except AttributeError:
            msg = "Tried to reuse a Figure which was already closed"
            if fig_to_reuse:
                warnings.warn(msg)
                # Create new figure
                fig = figure(figure_title, window_title, None, **kwargs)
            else:
                raise ValueError(msg)

    fig.figure_title = figure_title
    fig.window_title = window_title

    return fig


class ShareAxis(enum.Enum):
    # noinspection SpellCheckingInspection
    """
    Controls sharing of properties among x (sharex) or y (sharey) axes.\n
    When subplots have a shared x-axis along a column, only the x tick labels of the bottom subplot are visible.
    Similarly, when subplots have a shared y-axis along a row, only the y tick labels of the first column
    subplot are visible.
    """
    ALL = "all"
    """x- or y-axis will be shared among all subplots."""
    NONE = "none"
    """Each subplot x- or y-axis will be independent."""
    ROW = "row"
    """Each subplot row will share an x- or y-axis."""
    COLUMN = "col"
    """Each subplot column will share an x- or y-axis."""


# noinspection SpellCheckingInspection
def subplots(fig: Figure, rows: int = 1, cols: int = 1,
             sharex: ShareAxis = ShareAxis.ALL, sharey: ShareAxis = ShareAxis.ALL, *,
             width_ratios: Optional[Collection[int]] = None, height_ratios: Optional[Collection[int]] = None,
             ) -> Union[Axes, List[Axes], List[List[Axes]]]:
    """
    Add a set of `subplots <https://matplotlib.org/api/_as_gen/matplotlib.figure.Figure.html#matplotlib.figure.Figure
    .subplots>`_ to the figure.

    :param fig:    Figure to add subplots to.
    :param rows:   Number of rows.
    :param cols:   Number of columns.
    :param sharex: Controls sharing of properties among x axes.
    :param sharey: Controls sharing of properties among y axes.

    :param width_ratios: Optional width ratios for subplots, passed to :class:`matplotlib.gridspec.GridSpec`.
    :param height_ratios: Optional width ratios for subplots, passed to :class:`matplotlib.gridspec.GridSpec`.

    :return: Single Axes object if only one subplot is constructed (`rows` = `cols` = 1), 1D numpy object array of
             Axes objects for Nx1 or 1xN subplots (`rows` > 1 or `cols` > 1) or 2D numpy object array of Axes
             objects for NxM subplots (where N=`rows` > 1 and M=`cols` > 1).
    """
    gridspec_kw = {}
    if width_ratios:
        gridspec_kw["width_ratios"] = list(width_ratios)
    if height_ratios:
        gridspec_kw["height_ratios"] = list(height_ratios)
    if not gridspec_kw:
        gridspec_kw = None

    return fig.subplots(rows, cols, sharex=sharex.value, sharey=sharey.value, squeeze=True, gridspec_kw=gridspec_kw)


def axes(host_ax: Axes, x_label: str = None,
         y_label_left: Union[str, Collection[str]] = None,
         y_label_right: Optional[Union[str, Collection[str]]] = None,
         offset: float = 0.055,
         tight: bool = None) -> List[Axes]:
    """
    Configure `Axes <https://matplotlib.org/api/axes_api.html#axis-labels-title-and-legend>`_ and its
    `Axis-es <https://matplotlib.org/api/axis_api.html>`_.

    :param host_ax: Axes (retrieved with :func:`subplots`).
    :param x_label: Label of the x-axis.
    :param y_label_left: If string, label of the only/single left y-axis. If multiple strings, multiple left y-axes
                         are created with 0 being the left-most (the farthest away from the plotting canvas).
    :param y_label_right: If provided and provided as string, second y-axis is generated. If provided as multiple
                          strings, multiple right y-axes are created with 0 being the left-most (the nearest to the
                          plotting canvas).
    :param offset: If multiple axes are generated on the same side, this offset is used to place the spine at the
                   specified Axes coordinate (from 0.0-1.0). As examples if this is 0.1, axes on left will have
                   positions -0.2, -0.1 and 0.0 and axes on the right 1.0, 1.1 and 1.2.
    :param tight: TODO: Whether to use tight layout.

    :return: Generated and configured (multiple) Axes, from the left-most Axes to the right-most Axes. The left-most
             axis (index 0) is instance of the provided host axis.
    """

    def make_patch_spines_invisible(_ax: Axes):
        """
        Having been created by :meth:`twinx`, second axis has its frame off, so the line of its detached spine is
        invisible. First, activate the frame but make the patch and spines invisible.
        """
        _ax.set_frame_on(True)
        _ax.patch.set_visible(False)
        for sp in _ax.spines.values():
            sp.set_visible(False)

    # Configure x-axis
    if x_label is not None:
        host_ax.set_xlabel(x_label)
    host_ax.grid(True, 'both')

    # Generate y-axes (that is only partly true as Axes instance contains both axis).
    axs_left: List[Axes] = []
    axs_right: List[Axes] = []

    # By default there is only one axis on the left, which is in fact already the host axis.
    if isinstance(y_label_left, str):
        host_ax.set_ylabel(y_label_left)
        axs_left.append(host_ax)
    elif y_label_left:
        # Narrow down the figure to prevent grid sticking outwards from the plotting canvas.
        # .tight_layout() below shall do that
        # > if tight:
        # >     host_ax.figure.subplots_adjust(left=(len(y_label_left) - 1) * offset)
        # Create multiple axes on the left
        for i, label in enumerate(y_label_left):
            # The left-most axis is the host axis.
            ax = host_ax if (i == 0) else host_ax.twinx()
            axs_left.append(ax)
            # Set proper position (offset the spine).
            ax.spines["left"].set_position(("axes", -(len(y_label_left) - i - 1) * offset))
            # Patch spines are modified only for the axes not touching the plotting canvas (right-most).
            if i < (len(y_label_left) - 1):
                make_patch_spines_invisible(ax)
            ax.spines["left"].set_visible(True)  # Show the left spine.
            ax.yaxis.set_label_position("left")
            ax.yaxis.set_ticks_position("left")
            ax.set_ylabel(label)

    if y_label_right:
        if isinstance(y_label_right, str):
            y_label_right = [y_label_right]
        # Narrow down the figure to prevent grid sticking outwards from the plotting canvas.
        # .tight_layout() below shall do that
        # > if tight:
        # >     host_ax.figure.subplots_adjust(right=1 - (len(y_label_right) - 1) * offset)
        # Create multiple axes on the right
        for i, label in enumerate(y_label_right):
            ax = host_ax.twinx()
            axs_right.append(ax)
            # Set proper position (offset the spine).
            ax.spines["right"].set_position(("axes", 1 + i * offset))
            # Patch spines are modified only for the axes not touching the plotting canvas (left-most).
            if i > 0:
                make_patch_spines_invisible(ax)
            ax.spines["right"].set_visible(True)  # Show the right spine.
            ax.yaxis.set_label_position("right")
            ax.yaxis.set_ticks_position("right")
            ax.set_ylabel(label)

    axs = axs_left + axs_right

    # Configure y-axes
    for ax_idx, ax_ in enumerate(axs):
        # Disable scientific notation
        ax_.get_yaxis().get_major_formatter().set_useOffset(False)

    fig = host_ax.get_figure()
    # noinspection PyProtectedMember
    if fig._suptitle and fig._suptitle.get_text():
        # https://stackoverflow.com/a/45161551/5616255
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    else:
        host_ax.get_figure().tight_layout()

    return axs


def set_camera(fig: Optional[Figure], ax: Axes3D, elevation: Optional[float], azimuth: Optional[float]) -> None:
    """
    Set the elevation and azimuth of the axes. This can be used to rotate the axes programmatically.
    See :meth:`Axes3D.view_init`.

    :param fig:       Figure used for redraw, if provided.
    :param ax:        3D axes instance.
    :param elevation: The elevation angle in the z plane.
                      If None, then the initial value is used which was specified in the Axes3D constructor.
    :param azimuth:   The azimuth angle in the x, y plane.
                      If None, then the initial value is used which was specified in the Axes3D constructor.
    """
    ax.view_init(elevation, azimuth)
    if fig:
        fig.canvas.draw_idle()


rotate_3d = set_camera


def set_color_y(axis: Axes, color: str, label: bool = True, tick_params: bool = True):
    if label:
        axis.yaxis.label.set_color(color)
    if tick_params:
        axis.tick_params('y', colors=color)


class LegendLocation(enum.Enum):
    """The location of the legend."""

    BEST = "best"
    UPPER_RIGHT = "upper right"
    UPPER_LEFT = "upper left"
    LOWER_LEFT = "lower left"
    LOWER_RIGHT = "lower right"
    RIGHT = "right"
    CENTER_LEFT = "center left"
    CENTER_RIGHT = "center right"
    LOWER_CENTER = "lower center"
    UPPER_CENTER = "upper center"
    CENTER = "center"


# noinspection SpellCheckingInspection
def legend(axes_: Sequence[Axes], loc: Union[LegendLocation, str] = LegendLocation.BEST,
           *args,
           fancybox: Optional[bool] = True, framealpha: Optional[float] = 0.7,
           **kwargs) -> None:
    # noinspection SpellCheckingInspection
    """
    Add combined legend for all specified axes. Useful when using double-y (twinx) axis.
    Idea from `Secondary axis with twinx(): how to add to legend? <https://stackoverflow.com/a/10129461/5616255>`_.

    :param axes_:      Axes of which legends to combine.
    :param loc:        The location of the legend.
    :param args:       Other arguments to pass to the `matplotlib.axes.legend()`.
    :param fancybox:   Control whether round edges should be enabled around the `FancyBboxPatch` which makes up the
                       legend's background.
                       Default is None, which will take the value from `rcParams["legend.fancybox"]`.
    :param framealpha: Control the alpha transparency of the legend's background. Default is None, which will take the
                       value from `rcParams["legend.framealpha"]`. If shadow is activated and framealpha is None,
                       the default value is ignored.

    :param kwargs: Other keyword arguments to pass to the `matplotlib.axes.legend()`.
    """
    # Get plotted objects and their labels
    lines = []
    labels = []
    for axis in axes_:
        lines_, labels_ = axis.get_legend_handles_labels()
        lines.extend(lines_)
        labels.extend(labels_)
    axes_[0].legend(lines, labels, *args, loc=(loc.value if isinstance(loc, LegendLocation) else loc),
                    fancybox=fancybox, framealpha=framealpha, **kwargs)


def maximize(fig: Optional[Figure] = None):
    if fig:
        mng = fig.canvas.manager
    else:
        mng = plt.get_current_fig_manager()
    mng_class = type(mng).__name__

    # noinspection SpellCheckingInspection
    if mng_class in ("FigureManagerTkAgg", "FigureManagerTk"):
        # from matplotlib.backends.backend_tkagg import FigureManagerTkAgg
        mng.window.state('zoomed')
    elif mng_class == "FigureManagerWx":
        # from matplotlib.backends.backend_wx import FigureManagerWx
        mng.frame.Maximize(True)
    elif mng_class == "FigureManagerQT":
        # from matplotlib.backends.backend_qt5 import FigureManagerQT
        mng.window.showMaximized()
    elif mng_class == "FigureManagerWebAgg":
        # from matplotlib.backends.backend_webagg_core import FigureManagerWebAgg
        raise NotImplementedError()
    elif mng_class == "FigureManagerPgf":
        # from matplotlib.backends.backend_pgf import FigureManagerPgf
        raise NotImplementedError()
    elif mng_class == "FigureManagerMac":
        # from matplotlib.backends.backend_macosx import FigureManagerMac
        raise NotImplementedError()
    elif mng_class == "FigureManagerGTK":
        # from matplotlib.backends.backend_gtk import FigureManagerGTK
        raise NotImplementedError()
    elif mng_class == "FigureManagerGTK3":
        # from matplotlib.backends.backend_gtk3 import FigureManagerGTK3
        raise NotImplementedError()
    elif "interagg" in plt.get_backend():
        warnings.warn("Maximizing matplotlib figures is not supported when "
                      "'Settings -> Tools -> Python Scientific -> Show plots in tool window' is enabled in PyCharm.")
    else:
        raise EnvironmentError("Unsupported matplotlib backend '{}' with '{}' manager"
                               .format(plt.get_backend(), mng_class))


def show(fig: Optional[Figure] = None):
    """
    Show the figure (if possible).
    """
    if is_interactive_possible():
        if fig:
            fig.show()
        else:
            plt.show()


def save_png(fig: Figure, path: Union[None, str, pathlib.Path],
             width: Union[int, float] = None, height: Union[int, float] = None, unit: str = 'px',
             print_info: bool = False) -> Union[str, io.BytesIO]:
    """
    Save PNG image of the figure.

    :param fig:        Figure to save.
    :param path:       Full path of the image to save. If directory (string ending in slash - '/' or '\\') then
                       the figure window title is used as a file name. If `None`, in-memory :class:`io.BytesIO`
                       file will be generated and returned.

    :param width:      Image width in `unit`. If not provided it will be left as it is.
    :param height:     Image height in `unit`. If not provided it will be left as it is.
    :param unit:       Unit of the image width and height, one of: 'px' (pixels), 'cm' (centimeters), 'in' (inch).

    :param print_info: Whether to print information about saved file.

    :return: Full path of the generated image if `path` was provided or in-memory :class:`io.BytesIO` file.
    """
    if path:
        directory, file_name = os.path.split(path)
        # Create the directory if not existent
        os.makedirs(directory, exist_ok=True)
        # If the provided path is only a directory, use window title as filename
        if not file_name:
            file_name = get_window_title(fig)
        # Image path must have .png extension!
        if os.path.splitext(file_name)[1] != ".png":
            file_name += ".png"
        path = os.path.join(directory, file_name)

    dpi = fig.get_dpi()

    if width or height:
        size = fig.get_size_inches()

        if unit == 'px':
            fig.set_size_inches((width or size[0]) / dpi, (height or size[1]) / dpi)

        elif unit in ('mm', 'cm', 'in', 'inch'):
            if unit == 'mm':
                width /= 25.4
                height /= 25.4
            elif unit == 'cm':
                width /= 2.54
                height /= 2.54
            # Unit is inches.
            fig.set_size_inches(width or size[0], height or size[1])

        else:
            raise ValueError(f"Unsupported size unit '{unit}'")

    width = fig.get_figwidth()
    height = fig.get_figheight()
    width_px = int(round(width * dpi))
    height_px = int(round(height * dpi))
    width_mm = width * 25.4
    height_mm = height * 25.4

    if path:
        fig.savefig(path, dpi=dpi)
        ret = path
        if print_info:
            print(f"Saved plot ({width_px}x{height_px} px = {width_mm:.1f}x{height_mm:.1f} mm @ {dpi} dpi)"
                  f" to '{os.path.normpath(path)}'")
    else:
        file = io.BytesIO()
        fig.savefig(file, dpi=dpi)
        file.seek(0)
        ret = file

    return ret


class Event(enum.Enum):
    """Matplotlib event."""

    MOUSE_BUTTON_PRESS = "button_press_event"
    """
    Event triggered when mouse button is pressed.
    Callback signature is `on_mouse_button_press(event: matplotlib.backend_bases.MouseEvent)`.
    """
    MOUSE_BUTTON_RELEASE = "button_release_event"
    """
    Event triggered when mouse button is released.
    Callback signature is `on_mouse_button_press(event: matplotlib.backend_bases.MouseEvent)`.
    """
    KEY_PRESS = "key_press_event"
    """
    Event triggered when key is pressed.
    Callback signature is `on_mouse_button_press(event: matplotlib.backend_bases.KeyEvent)`.
    """
    KEY_RELEASE = "key_release_event"
    """
    Event triggered when key is released.
    Callback signature is `on_mouse_button_press(event: matplotlib.backend_bases.KeyEvent)`.
    """
    MOUSE_MOVE = "motion_notify_event"
    """
    Event triggered when mouse motion is detected.
    Callback signature is `on_mouse_button_press(event: matplotlib.backend_bases.MouseEvent)`.
    """
    CLOSE = "close_event"
    """
    Event triggered when the figure closes.
    Callback signature is `on_figure_close(event: matplotlib.backend_bases.CloseEvent)`.
    """


def register_event(fig: Union[Figure, FigureCanvas],
                   event: Event, callback: Callable[[matplotlib.backend_bases.Event], None]) -> int:
    """
    Register `event handling <https://matplotlib.org/users/event_handling.html>`_ for the figure.
    One example is `close event <https://matplotlib.org/gallery/event_handling/close_event.html>`_.

    :param fig:      Figure which will trigger the events.
    :param event:    Event type.
    :param callback: Function called when event triggers.

    :return: Callback ID (used for unregistering callbacks).
    """
    return (fig.canvas if isinstance(fig, Figure) else fig).mpl_connect(event.value, callback)


def unregister_event(fig: Union[Figure, FigureCanvas], cid: int) -> None:
    """
    `Unregister <https://matplotlib.org/api/_as_gen/matplotlib.pyplot.disconnect.html>`_ the callback - disable
    `event handling <https://matplotlib.org/users/event_handling.html>`_ for the figure.

    :param fig: Figure which had this event registered.
    :param cid: Callback ID as returned by :func:`register_event`.
    """
    (fig.canvas if isinstance(fig, Figure) else fig).mpl_disconnect(cid)


_mouse_tracking_vertical_lines_cid: Dict[FigureCanvas, Tuple[int, int]] = {}
"""Saved callback IDs for :meth:`add_mouse_tracking_vertical_line`."""
_mouse_tracking_vertical_lines: Dict[FigureCanvas, Dict[Axes, Line2D]] = {}
"""Saved vertical lines for :meth:`add_mouse_tracking_vertical_line`."""


def add_mouse_tracking_vertical_line(fig: Figure, to_axes: Optional[Union[Axes, Iterable[Axes]]],
                                     x_converter: Optional[Callable[[Number], Number]] = None,
                                     **line_kwargs) -> None:
    """
    Enable drawing of vertical lines to all specified axes on current mouse position.

    :param fig:         Figure to use for capturing mouse move events. Vertical lines will only be drawn
                        when mouse is in the figure.
    :param to_axes:     One or multiple Axes which will be used for drawing vertical lines with `.axvline()`.
                        If `None`, all lines for this figure will be removed and events disabled.
    :param line_kwargs: Valid kwargs are :class:`matplotlib.lines.Line2D` properties, with the exception
                        of 'transform'. They will be passed to the `matplotlib.axes.Axes.axvline()` function.
    :param x_converter: Optional converter function. Input is current mouse X coordinate in the axis units
                        (not pixels), which is a float value even if the tick marks are integers (because
                        mouse can be between ticks). Ax example, this can be lambda which casts provided
                        float argument to integer to provide "snap to integer" functionality.
    """

    def remove_lines(canvas_axes: Dict[Axes, Line2D]) -> None:
        """Remove all lines for specified canvas axes."""
        for ax in tuple(canvas_axes.keys()):
            # Delete only line, not axis.
            if canvas_axes[ax]:
                canvas_axes[ax].remove()
                del canvas_axes[ax]  # This also removes the key.
                # noinspection PyTypeChecker
                canvas_axes[ax] = None

    # Callback function called when mouse is moved
    def on_mouse_move(event: matplotlib.backend_bases.MouseEvent):
        my_axes = _mouse_tracking_vertical_lines[event.canvas]
        # Remove all previously drawn lines for this axes.
        remove_lines(my_axes)
        # Only draw if mouse is in the figure (if it is not then x data is not provided).
        x = event.xdata
        if x is None:
            return
        if x_converter:
            x = x_converter(x)
        # Draw again if mouse is in the figure.
        for ax in my_axes:
            my_axes[ax] = ax.axvline(x=x, **line_kwargs)
        # Mark figure for redraw on next event
        event.canvas.draw_idle()

    def on_close(event: matplotlib.backend_bases.CloseEvent):
        if event.canvas not in _mouse_tracking_vertical_lines_cid:
            return
        # First, unregister all events.
        for cid in _mouse_tracking_vertical_lines_cid[event.canvas]:
            unregister_event(event.canvas, cid)
        del _mouse_tracking_vertical_lines_cid[event.canvas]
        # Then delete all vertical lines.
        remove_lines(_mouse_tracking_vertical_lines[event.canvas])
        del _mouse_tracking_vertical_lines[event.canvas]

    # Disable any existing events and remove lines by generating fake close event.
    on_close(matplotlib.backend_bases.CloseEvent(None, fig.canvas, None))

    if to_axes is None:
        return
    if isinstance(to_axes, Axes):
        to_axes = (to_axes,)
    elif not isinstance(to_axes, tuple):
        to_axes = tuple(to_axes)

    # Save references to all axes to which lines shall be plotted.
    # Use canvas instead of figure because that same canvas is also in the event provided to the callbacks.
    _mouse_tracking_vertical_lines[fig.canvas] = {ax: None for ax in to_axes if ax}

    # Register event to handle mouse move and draw lines.
    mouse_cid = register_event(fig, Event.MOUSE_MOVE, on_mouse_move)
    # Register event to clear the dictionary when the figure is closed.
    close_cid = register_event(fig, Event.CLOSE, on_close)
    # Save the event callback IDs to enable deletion.
    _mouse_tracking_vertical_lines_cid[fig.canvas] = (mouse_cid, close_cid)


def close(fig: Optional[Figure] = None):
    """Close the figure (if provided) or all figures."""
    if fig:
        plt.close(fig)
    else:
        plt.close()


def get_window_title(fig: Figure) -> str:
    # return fig.canvas.get_window_title()
    try:
        # noinspection PyUnresolvedReferences
        return fig.window_title
    except AttributeError:
        raise AttributeError("Trying to call plotting.get_window_title() with figure not created by plotting.figure()")


def is_interactive_possible() -> bool:
    """Check if plotting is actually possible (as example on virtual machine plot() raises Error)."""
    return not ((os.name == "posix") and ("DISPLAY" not in os.environ))


def is_interactive() -> bool:
    """
    Check if currently used `backend <https://matplotlib.org/faq/usage_faq.html#what-is-a-backend>`_ is an
    interactive backend.
    """
    return matplotlib.get_backend() in matplotlib.rcsetup.interactive_bk


def use_non_interactive() -> None:
    """
    Use non-interactive, "virtual" `backend <https://matplotlib.org/faq/usage_faq.html#what-is-a-backend>`_.
    Used if one `does not want the window to appear
    <https://matplotlib.org/faq/howto_faq.html#generate-images-without-having-a-window-appear>`_.
    """
    import matplotlib
    import importlib

    try:
        plt.switch_backend('Agg')
    except NameError:  # name 'plt' is not defined
        matplotlib.use('Agg', warn=False, force=True)

    # matplotlib.pyplot is not imported if interactive mode is not possible.
    # But if it is, the backend must be switched before importing pyplot!
    if 'matplotlib.pyplot' in sys.modules:
        if 'plt' in globals():
            globals()['plt'] = importlib.reload(plt)
        else:
            importlib.reload(matplotlib.pyplot)


# Check if plotting is possible and if it is not change backend to the "virtual" one to avoid raising errors.
# As example running some script on the virtual machine or the headless device would raise error.
if not is_interactive_possible():
    warnings.warn("Plotting is not possible in this environment, switching to matplotlib backend 'Agg'.")
    use_non_interactive()

# noinspection PyPep8
import matplotlib.pyplot as plt
