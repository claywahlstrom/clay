"""
Music: for creating and playing music

Steps are relative to A.
Registers are in ovtaves with the lowest pitch of 55.


"""
from collections import OrderedDict as _od
import itertools as _it
import os as _os
import time as _time
import winsound as _ws

from clay import UNIX as _UNIX
from clay.fileops import save as _save
from clay.shellcmds import set_title


# scale types

MINOR = [0, 2, 3, 5, 7, 8, 10, 12]
MAJOR = [0, 2, 4, 5, 7, 9, 11, 12]
WHOLE_TONE = list(range(0, 13, 2))

# create steps from A dict
_letters = 'A A# B C C# D D# E F F# G G#'.split()
_counter = _it.count()
STEP_DICT = {note: next(_counter) for note in _letters}

# set enharmonic equalss
STEP_DICT['Bb'] = STEP_DICT['A#']
STEP_DICT['Db'] = STEP_DICT['C#']
STEP_DICT['Eb'] = STEP_DICT['D#']
STEP_DICT['Gb'] = STEP_DICT['F#']
STEP_DICT['Ab'] = STEP_DICT['G#']

# nav
KEY_DOWN = 's'
KEY_UP = 'w'

# data
LEN_FACTOR = 963

# create register frequencies
REGS = _od()
for _num in range(7):
    REGS[str(_num + 1)] = 55 * 2 ** _num

def get_hertz(reg, key):
    hertz = round(reg * 2 ** (key / 12))
    return int(hertz)

def get_note():
    note = input('Note? ').strip()
    length = eval(input('Length? ').strip())
    return note, length

if _UNIX:
    print("<module 'winsound.py'> not available")
else:
    from winsound import Beep as note # def

def notify(e):
    print(e)
    _time.sleep(2.25)

def play_full(scale, tempo):
    offset = STEP_DICT[scale.split()[0]]
    if scale.lower().endswith('major'):
        scale = [x+offset for x in MAJOR]
    else:
        scale = [x+offset for x in MINOR]

    for i in range(2):
        play_half(scale, tempo)
        scale.reverse()

def play_half(scale, tempo):
    for note in scale:
        _ws.Beep(get_hertz(REGS['4'], note), int(60 / tempo * 963))

class Song(object):
    """
    Receives optional file name, selection, and subdivision
    Defaults:
        file     :: type str()
        selected :: int(0)
        sub      :: float(0.25)
        tempo    :: int(60)
    Gives functionality including:
        writing a note
        editing a note
        setting the subdivision
        deleting notes
    """
    def __init__(self, file=str(), selected=0, sub=0.25, tempo=60):
        self.load()

        self.selected = selected
        self.sub = round(sub, 4) # 64th notes at minimum
        self.tempo = tempo

    def at_end(self):
        return self.selected >= len(self.notes) - 1

    def delete(self):
        self.notes.pop(-1)
        self.lens.pop(-1)
        self.selected -= 1

    def delta_note(self, move):
        exec('self.lens[self.selected] {}= self.sub'.format(move))

    def edit_end(self):
        note, length = get_note()
        self.notes[self.selected] = note
        self.lens[self.selected] = length

    def is_populated(self):
        return self.notes and self.lens

    def load(self):
        while True:
            file = input('load? ')
            if file in ('new', 'none'):
                notify('Creating a new template...')
                notes = list()
                lens = list()
                tempo = eval(input('tempo? '))
                break
            elif _os.path.exists(file):
                with open(file) as load:
                    rd = load.read().strip().split('\n')
                    notes, lens, tempo = eval(rd[0]), eval(rd[1]), int(rd[2])
                break
            else:
                print('Path doesn\'t exist, try again')


        self.file = file
        self.notes = notes
        self.lens = lens
        self.tempo = tempo

    def new_note(self):
        note, length = get_note()
        if self.at_end() or not(self.is_populated()): # add note
            self.notes.append(note)
            self.lens.append(length)
            if len(self.notes) > 1:
                self.selected += 1
        else: # modify note
            self.notes[self.selected] = note
            self.lens[self.selected] = length

    def play(self):
        for note, length in zip(self.notes, self.lens):
            _ws.Beep(get_hertz(REGS[note[-1]], STEP_DICT[note[:-1]]), int(length*LEN_FACTOR*60/self.tempo))

    def save(self):
        _save('\n'.join(map(str, [song.notes, song.lens, song.tempo])), 'notes.txt')
        set_title(add='File saved')
        
    def set_sub(self, newsub=None):
        if newsub == None:
            newsub = input('new sub? ').strip()
        try:
            self.sub = round(float(newsub), 4) # 64th notes at minimum
        except Exception as e:
            print(e)

    def set_tempo(self):
        try:
            self.tempo = int(input('new tempo? ').strip())
        except Exception as e:
            print(e)

if __name__ == '__main__':
    t = 120
    play_full('C# major', t)
    play_half(MINOR, t)
    
    print('BEEP!')
    note(880, 100)
