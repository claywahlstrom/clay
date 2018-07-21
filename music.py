
"""
Music: for creating and playing music

Steps are relative to A.
Registers are in ovtaves with the lowest pitch of 55.

TODO: comment Song

"""

from collections import OrderedDict as _od
import itertools as _it
import os as _os
import time as _time
import winsound as _ws

from clay.files import save as _save
from clay.shell import set_title, notify as _notify, isUnix as _isUnix

# scale types
NATURAL_MINOR = [0, 2, 3, 5, 7, 8, 10, 12]
MAJOR = [0, 2, 4, 5, 7, 9, 11, 12]
WHOLE_TONE = list(range(0, 13, 2))

# key signatures
KEY_SIGNATURE = {'flats': 'BEADGCF',
                 'sharps': 'FCGDAEB'}

# create steps from A dict
_letters = 'A A# B C C# D D# E F F# G G#'.split()
_counter = _it.count()
STEP_DICT = {note: next(_counter) for note in _letters}

# set enharmonic equals
STEP_DICT['Bb'] = STEP_DICT['A#']
STEP_DICT['Db'] = STEP_DICT['C#']
STEP_DICT['Eb'] = STEP_DICT['D#']
STEP_DICT['Gb'] = STEP_DICT['F#']
STEP_DICT['Ab'] = STEP_DICT['G#']

# data
LEN_FACTOR = 963

# create register frequencies
REGS = _od()
for _num in range(7):
    REGS[str(_num + 1)] = 55 * 2 ** _num

def get_hertz(reg, key):
    """Returns the hertz for the given key and register"""
    return int(reg * 2 ** (key / 12))

class Note(object):
    """Class Note can be used to keep track of information about a note."""
    def __init__(self, name='A4', length=0):
        """Default note is A 440 with length 0"""
        self.name = name
        self.length = length

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%s)' % (self.__class__.__name__, '{}, {}'.format(self.name, self.length))

if _isUnix():
    print("<module 'winsound.py'> not available")
else:
    from winsound import Beep as note # def

def play_note(note, register, length, tempo):
    """Plays note of type str or int at the given register with length and tempo"""
    if type(note) == str:
        note = STEP_DICT[note]
    _ws.Beep(get_hertz(REGS[register], note), int(length * 60 / tempo * LEN_FACTOR))

def play_scale(notes, tempo, register='4'):
    """Plays a scale from the given notes, tempo, default register is 4"""
    for note in notes:
        play_note(note, register, 1, tempo)

def play_scale_full(scale, tempo):
    """Plays a full scale of the given notes at the given tempo"""
    offset = STEP_DICT[scale.split()[0]]
    if scale.lower().endswith('major'):
        scale = [x + offset for x in MAJOR]
    else:
        scale = [x + offset for x in NATURAL_MINOR]

    scale += scale[::-1][1:] # decending notes
    play_scale(scale, tempo)

def play_scale_half(notes, tempo):
    """Plays a half scale of the given notes at the given tempo"""
    play_scale(notes, tempo)

class Song(object):
    """A class for writing and storing music.

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
        """Initializes a new Song object from the given file name"""
        self.selected = selected
        self.sub = round(sub, 4) # 64th note length limit
        self.load()

    def at_end(self):
        """Returns true if the selection is at the end of the song,
           false otherwise"""
        return self.selected + 1 >= len(self.notes)

    def change_length(self, direction):
        """Changes the length of the selected note
           by the subdivision in the given direction"""
        self.notes[self.selected] += self.sub * direction

    def delete(self):
        """Deletes the selected note from this song"""
        self.notes.pop(selected)
        self.selected -= 1

    def get_note(self):
        """Prompts the user for a note name and length value"""
        name = input('Note? ').strip()
        length = eval(input('Length? ').strip())
        return name, length

    def is_populated(self):
        """Returns true if this song is populated, false otherwise"""
        return len(self.notes) > 0

    def load(self):
        """Loads a notes file written in standard format"""
        file = 'notes{:03d}.txt'.format(int(input('load song #? ')))
        notes = list()
        if file == 'new':
            _notify('Creating a new template...', 0.5)
            tempo = eval(input('tempo? '))
        while not _os.path.exists(file) and file != 'new':
            print('Path doesn\'t exist, try again')
            file = 'notes{:03d}.txt'.format(input('load song #? '))
        if _os.path.exists(file):
            with open(file) as load:
                rd = load.read().strip().split('\n')
                for line in rd[:-1]:
                    parts = line.split()
                    notes.append(Note(parts[0], eval(parts[1])))
                tempo = int(rd[-1])

        self.file = file
        self.notes = notes
        self.tempo = tempo

    def mark(self, edit=False):
        """Creates a new note and appends it to this song"""
        name, length = self.get_note()
        if (self.at_end() or not(self.is_populated())) and not(edit): # add note
            self.notes.append(Note(name, length))
            if len(self.notes) > 1:
                self.selected += 1
        else: # modify note
            self.notes[self.selected].name = name
            self.notes[self.selected].length = length

    def play(self):
        """Plays this song using Windows' Beep"""
        # original
##                for note in self.notes:
##            _ws.Beep(get_hertz(REGS[note.name[-1]], STEP_DICT[note.name[:-1]]),
##                     int(note.length * LEN_FACTOR * 60 / self.tempo))
        for note in self.notes:
            play_note(note.name[:-1], note.name[-1], note.length, self.tempo) 

    def save(self):
        """Saves this song to a new file"""
        text = '\n'.join(('{} {}'.format(note.name, note.length) for note in self.notes)) + '\n' + str(self.tempo)
        _save(text, 'notes.txt', use_epoch=False)
        set_title(add='File saved')

    def select(self, direction):
        """Moves the selection up or down based on the given direction"""
        if direction == 'up':
            self.selected -= 1
        elif direction == 'down':
            self.selected += 1
        else:
            print('Illegal Argument Exception, try "up" or "down"')

    def set_sub(self, sub=0):
        """Prompts and sets the subdivision for this song. Cannot be less than 1/64th"""
        while sub < 1 / 64: # 64th notes at minimum
            sub = float(input('new sub? ').strip())

    def set_tempo(self):
        """Prompts and sets the tempo for this song"""
        self.tempo = int(input('new tempo? ').strip())

if __name__ == '__main__':
    t = 120
    play_scale_full('C# major', t)
    play_scale_half(NATURAL_MINOR, t)

    print('BEEP!')
    note(1530, 100)
