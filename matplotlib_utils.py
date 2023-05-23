from matplotlib.table import Table
from matplotlib.patches import Rectangle


def add_table(left, right, ax, pos, title=None):
    # left bottom width height
    l, b, w, h = pos
    rec = Rectangle((l, b), w, h, fc='w', ec='k', fill=True,
                    transform=ax.transAxes, zorder=11)

    if not isinstance(left, list):
        left = left.split(' ')
    if not isinstance(right, list):
        right = right.split(' ')
    if len(left) != len(right):
        print(left, right)
        raise ValueError('Length of left and right have to be the same')

    tb = Table(ax, bbox=pos, zorder=12, transform=ax.transAxes)
    width_cell, height_cell = 1, 1 / 3
    for i in range(len(left)):
        tb.add_cell(i, 0, width_cell, height_cell, text=left[i], loc='left')
        tb.add_cell(i, 1, width_cell, height_cell, text=right[i],
                    loc='right')
        tb.get_celld()[(i, 0)].visible_edges = ''
        tb.get_celld()[(i, 1)].visible_edges = ''
        # tb.auto_set_column_width((0, 1))
        tb.auto_set_font_size(False)
        tb.set_fontsize(8)

        # tb.get_celld()[(-1, -1)].visible_edges = 'LTR'
        # tb.get_celld()[(-1, -1)].set_bounds(0, 0, 2, 2)
        if title:
            ax.add_patch(Rectangle((l, b + h), w, h / 3, fill=False, transform=ax.transAxes,
                                   zorder=3, facecolor='w'))
            ax.text(l + w / 2, b + 1.1 * h, title,
                    transform=ax.transAxes, horizontalalignment='center',
                    weight='bold', fontsize='x-small')

    # Add rectangle and table
    ax.add_artist(rec)
    ax.add_table(tb)
