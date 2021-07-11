from os import stat
from typing import Dict, Optional, Union, List
import requests
import pyperclip
from tkinter import *
from functools import cache


NUMBERS_HANDS_FOR_POSTFLOP_VIEW = 500


class Stat:
    """"""
    def __init__(self, name: str, value: Union[int, str], color: str = '#000', 
                color_default_range: tuple[int] = None, count: Optional[int] = None) -> None:
        self._name = name
        self._value = value
        if value and type(value) != str:
            self._value = round(self._value)
        self._color = color
        if color_default_range:
            self.set_dynamic_color(color_default_range)
        self._count = count

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        if self._count:
            if int(self._count) < 10:
                return '-'
        return self._value
       
    @value.setter
    def value(self, value):
        self._value = value

    @property
    def count(self):
        return self._count

    @property
    def color(self):
        return self._color
    
    def set_dynamic_color(self, range: tuple[int]) -> None:
        if type(self._value) == int:
            if range[0] < range[-1]:
                if self._value < range[0]:
                    self._color = '#11f9fd'
                if self._value > range[-1]:
                    self._color = '#ed33ed'
            else:
                if self._value < range[-1]:
                    self._color = '#ed33ed'
                if self._value > range[0]:
                    self._color = '#11f9fd'



@cache
def get_player_info(player_name: str) -> List[Stat]:
    """Returns Json with detail-main-stats of player."""

    headers = {
    }

    r = requests.get(f'https://statname.net/player_search?auto=0&term={player_name}&rooms%5B%5D=888', headers=headers)
    if r.status_code == 200:
        id_player = r.url.split('=')[1]
        if id_player.isdigit():
            payload = {
                'date': '',
                'date_from': '',
                'date_to': '',
                'id': id_player,
                'namePlayer': '',
                'pokerRoom': '',
                'room': '6m',
                'type': 'NL',
                'stat': 'Base',
            }

            get_stats = requests.post('https://statname.net/main-details-stats', headers=headers, params=payload)

            if get_stats.status_code == 200:
                stats = get_stats.json()

                player_stats = [
                    [Stat('name', player_name[:4], '#fa0'), Stat('hands', stats['hands'], '#fff'), Stat('wtsd', stats['wtsd'], '#29f', (26, 28)), Stat('wonsd', stats['wonsd'], '#29f', (54, 50)), Stat('wwsf', stats['wwsf'], '#29f', (45, 48))],
                    [Stat('vpip', stats['vpip'], '#2ef', (23, 27)), Stat('pfr', stats['pfr'], '#2ef', (18, 22)), Stat('3bet', stats['s3bet'], 'red', (7,9)), Stat('fvs3bet', stats['fvs3bet'], '#2cdc1f', (54, 48)), Stat('4bet', stats['bet4Range'], 'red', (3, 4))],
                ]

                hands = stats['hands']
                if hands is None:
                    hands = 0
                else:
                    hands = int(stats['hands'])

                if hands < NUMBERS_HANDS_FOR_POSTFLOP_VIEW:
                    return player_stats

                get_details_stats = requests.post('https://statname.net/details-stats', headers=headers, params=payload)
                if get_details_stats.status_code == 200:
                    details_stats = get_details_stats.json()
                    flop_stats = details_stats['preFlop'][0]
                    turn_stats = details_stats['preFlop'][1]
                    river_stats = details_stats['preFlop'][2]

                    postflop_stats = [
                        [
                        Stat('flop_cb_ip', flop_stats['cb_ip']['value'], '#89f', count=flop_stats['cb_ip']['count']), 
                        Stat('flop_cb_oop', flop_stats['cb_oop']['value'], '#89f', count=flop_stats['cb_oop']['count']), 
                        Stat('flop_fvcb_ip', flop_stats['fvcb_ip']['value'], '#fff', count=flop_stats['fvcb_ip']['count'], color_default_range=(45, 35)),
                        Stat('flop_fvcb_oop', flop_stats['fvcb_oop']['value'], '#fff', count=flop_stats['fvcb_oop']['count'], color_default_range=(45, 35)),
                        Stat('flop_xr', flop_stats['xrnr']['value'], 'red', count=flop_stats['xrnr']['count']),
                        Stat('flop_afq', flop_stats['afq']['value'], 'yellow', count=flop_stats['afq']['count']),
                        ],

                        [
                        Stat('turn_cb_ip', turn_stats['cb_ip']['value'], '#89f', count=turn_stats['cb_ip']['count']), 
                        Stat('turn_cb_oop', turn_stats['cb_oop']['value'], '#89f', count=turn_stats['cb_oop']['count']), 
                        Stat('turn_fvcb_ip', turn_stats['fvcb_ip']['value'], '#fff', count=turn_stats['fvcb_ip']['count'], color_default_range=(45, 35)),
                        Stat('turn_fvcb_oop', turn_stats['fvcb_oop']['value'], '#fff', count=turn_stats['fvcb_oop']['count'], color_default_range=(45, 35)),
                        Stat('turn_xr', turn_stats['xrnr']['value'], 'red', count=turn_stats['xrnr']['count']),
                        Stat('turn_afq', turn_stats['afq']['value'], 'yellow', count=turn_stats['afq']['count']),
                        ],

                        [
                        Stat('river_cb_ip', river_stats['cb_ip']['value'], '#89f', count=river_stats['cb_ip']['count']),
                        Stat('river_cb_oop', river_stats['cb_oop']['value'], '#89f', count=river_stats['cb_oop']['count']),
                        Stat('river_fvcb_ip', river_stats['fvcb_ip']['value'], '#fff', count=river_stats['fvcb_ip']['count'], color_default_range=(45, 35)),
                        Stat('river_fvcb_oop', river_stats['fvcb_oop']['value'], '#fff', count=river_stats['fvcb_oop']['count'], color_default_range=(45, 35)),
                        Stat('river_xr', river_stats['xrnr']['value'], 'red', count=river_stats['xrnr']['count']),
                        Stat('river_afq', river_stats['afq']['value'], 'yellow', count=river_stats['afq']['count']),
                        ]
                    ]

                    # print(postflop_stats)

                    return player_stats + postflop_stats
        return None


def create_hud() -> None:
    """Get username from clipboard and change text of label."""
    global frame 

    nick = pyperclip.paste()
    stats = get_player_info(nick)

    for widget in frame.winfo_children():
        widget.destroy()

    if not stats:
        label = Label(frame, text='Player not found!', bg='#000', fg='#fff')
        label.config(font=("Courier", 14))
        label.pack()
    
    else:
        for index_line, line in enumerate(stats):
            for index_stat, stat in enumerate(line):
                label = Label(frame, text=str(stat.value).ljust(5), bg='#000', fg=stat.color, borderwidth=1, relief='groove')
                label.config(font=("Courier", 14, 'bold'))
                label.grid(row=index_line, column=index_stat)

    frame.after(1000, create_hud)


if __name__ == '__main__':
    root = Tk()
    root.configure(background='black')
    root.lift()

    frame = Frame(root)
    frame.configure(background='black')
    frame.pack()

    create_hud()

    root.mainloop()


