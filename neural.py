from music21 import converter, instrument, note, chord, stream
import math
import numpy
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import LSTM
from tensorflow.keras.callbacks import ModelCheckpoint
from keras.utils import np_utils
import sys



grand_offset = 0.5
sequences = int(12*(0.5)/grand_offset)
#sequences=24

# output = []
# output.append(note.Note('D5-'))
# output.append(note.Note('G2'))
# output[0].offset = 0
# output[1].offset = 10
#
# midi_stream = stream.Stream(output)
# midi_stream.write('midi', fp='test_output.midi')


def round_nearest(x, t = 0):
    if t == 0:
        a = grand_offset
    else:
        a = t
    return round(round(x / a) * a, -int(math.floor(math.log10(a))))


def analysis(file):
    total = 0
    major = 0
#    file = "kiki.mid"
    dict = {}
    midi = converter.parse(file)
    key = midi.analyze('key')
    notes_to_parse = None
    parts = instrument.partitionByInstrument(midi)
    #print(parts.keySignature)
    #print("haha")
    if parts: # file has instrument parts
        notes_to_parse = parts.parts[0].recurse()
    else: # file has notes in a flat structure
        notes_to_parse = midi.flat.notes
    for element in notes_to_parse:
        if isinstance(element, note.Note):
            num = float(element.offset)
    #        print(str(element.pitch) + " " + str(num))
            num = round_nearest(num)
            if num not in dict.keys():
                dict[num] = []
            dict[num].append(str(element.pitch))
        elif isinstance(element, chord.Chord):
    
            num = float(element.offset)
            num = round_nearest(num)
            # print(str(element) + " " + str(num))
            for p in element.pitches:
                if num not in dict.keys():
                    dict[num] = []
                dict[num].append(str(p))
            temp_name = str(element.commonName)
            temp_name = temp_name.lower()
            
            if temp_name.find('major') != -1 or temp_name.find('minor') != -1:
                total = total + 1
            if temp_name.find('major') != -1:
                major = major + 1
    key_name = str(key.tonic.name) + " " + str(key.mode)
    return major*1.0/total, key_name, len(dict)

#print(analysis(""))
    

def process_input(file):
    notes = []
    dict = {}
#    file = "kiki.mid"
    midi = converter.parse(file)
    notes_to_parse = None
    parts = instrument.partitionByInstrument(midi)
    #print(parts.keySignature)
    #print("haha")
    if parts: # file has instrument parts
        notes_to_parse = parts.parts[0].recurse()
    else: # file has notes in a flat structure
        notes_to_parse = midi.flat.notes
    for element in notes_to_parse:
        if isinstance(element, note.Note):
            num = float(element.offset)
    #        print(str(element.pitch) + " " + str(num))
            num = round_nearest(num)
            if num not in dict.keys():
                dict[num] = []
            dict[num].append(str(element.pitch))
        elif isinstance(element, chord.Chord):
    
            num = float(element.offset)
            num = round_nearest(num)
            # print(str(element) + " " + str(num))
            for p in element.pitches:
                if num not in dict.keys():
                    dict[num] = []
                dict[num].append(str(p))
#            print(element.commonName)
    
            # print(str(element) + " " + str(element.bass()) + " " + str(element.root()))
            # notes.append('.'.join(str(n) for n in element.normalOrder))
    
    maxKey =list(dict.items())[-1][0]
    for i in numpy.arange(0,maxKey+grand_offset,grand_offset):
        if i not in dict.keys():
            temp = round_nearest(i)
            dict[temp] = []
            dict[temp].append(0)
            # print(i)
    
    notes = []
    offset = 0.0
    for i in dict.items():
        temp = dict[offset]
        if len(temp) == 1:
            notes.append(str(temp[0]))
        else:
            temp = sorted(temp)
            notes.append('.'.join(str(n) for n in temp))
        offset = offset+grand_offset
        offset = round_nearest(offset)
    
    return notes


def convert_to_stream(notes):
    result = []
    offset = 0.0
    for n in notes:
        if n != "0":
            ns = str(n).split('.')
            if len(ns) == 1:
                current = note.Note(ns[0])
                current.offset = offset
                result.append(current)
            else:
                current = chord.Chord(ns)
                current.offset = offset
                result.append(current)
        offset = offset + grand_offset
        offset = round_nearest(offset)
        #    print(tempo)
    return result

def writeFile(fileName,notes):
    midi_stream = stream.Stream(notes)
    midi_stream.write('midi', fp=fileName)



#print(notes)
#temp = convert_to_stream(notes)
##print(temp)
#midi_stream = stream.Stream(temp)
#midi_stream.write('midi', fp='original.mid')


def process_data(notes):
    sequence_length = sequences
    # get all pitch names
    pitchnames = sorted(set(item for item in notes))
    n_vocab = len(pitchnames)
    # create a dictionary to map pitches to integers
    note_to_int = {}
    for i in range(len(pitchnames)):
        note_to_int[pitchnames[i]] = i
    network_input = []
    network_output = []
    # create input sequences and the corresponding outputs
    for i in range(0, len(notes) - sequence_length, 1):
        sequence_in = notes[i:i + sequence_length]
        sequence_out = notes[i + sequence_length]
        network_input.append([note_to_int[char] for char in sequence_in])
        network_output.append(note_to_int[sequence_out])
    n_patterns = len(network_input)
    # reshape the input into a format compatible with LSTM layers
    network_input = numpy.reshape(network_input, (n_patterns, sequence_length, 1))
    # normalize input
    network_input = network_input / float(n_vocab)
    network_output = np_utils.to_categorical(network_output)
    return network_input, network_output, n_vocab, pitchnames


def train(file, output):
    notes = process_input(file)
    temp = convert_to_stream(notes)
    #print(temp)
    midi_stream = stream.Stream(temp)
    midi_stream.write('midi', fp='original.mid')
    network_input, network_output, vocab, pitchnames = process_data(notes)


# generate 500 notes
    

#
    model = Sequential()
    model.add(LSTM(256,input_shape=(network_input.shape[1], network_input.shape[2]),return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(512, return_sequences=True))
    model.add(Dropout(0.3))
    model.add(LSTM(256))
    model.add(Dense(256))
    model.add(Dropout(0.3))
    model.add(Dense(vocab,activation='softmax'))
    #model.load_weights(filename)
    model.compile(loss='categorical_crossentropy', optimizer='rmsprop')
    
    filepath = "weights-improvement-{epoch:02d}-{loss:.4f}-bigger.hdf5"
    checkpoint = ModelCheckpoint(
        filepath, monitor='loss', 
        verbose=0,        
        save_best_only=True,        
        mode='min'
    )    
    callbacks_list = [checkpoint]     
    model.fit(network_input, network_output, epochs=100, batch_size=64, callbacks=callbacks_list)
    
    
    
    print("Done traninig")
    print("Generating")
    start = numpy.random.randint(0, len(network_input)-1)
    int_to_note = {}
    for i in range(len(pitchnames)):
            int_to_note[i] = pitchnames[i]
        
    pattern = network_input[start]
    prediction_output = []
    # generate 500 notes
    for note_index in range(200):
        print(note_index)
        prediction_input = numpy.reshape(pattern, (1, len(pattern), 1))
    #    prediction_input = prediction_input/float(vocab)
        prediction = model.predict(prediction_input, verbose=0)
        index = numpy.argmax(prediction)
        result = int_to_note[index]
        prediction_output.append(result)
        index = index/float(vocab)
        pattern = numpy.append(pattern, index )
        pattern = pattern[1:]
        pattern = pattern.reshape((len(pattern),1))
    
    print(prediction_output)   
    stream_mid = convert_to_stream(prediction_output)
    midi_stream = stream.Stream(stream_mid)
    output_path = file[:len(file)-4] + 's_output.mid'
    midi_stream.write('midi', fp=output_path)


#train('kiki.mid', '')














